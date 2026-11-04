"""Isolated native skeleton re-inking study. No serif branch is removed.
Native components, counters and short-stroke skeletons are mandatory guards.
"""
import hashlib,json,math
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import medial_axis
from fontTools.ttLib import TTFont
from supplemental_pressure import shaped,raster,outline
from prototype_unifont_lettering import topology

def validate_reconstruction(before,after):
    if topology(before)!=topology(after):raise ValueError("Changed topology")
    a,count=ndi.label(before,structure=np.ones((3,3)));b,_=ndi.label(after,structure=np.ones((3,3)))
    seen=set();ratios=[]
    for i in range(1,count+1):
        ids=set(np.unique(b[a==i]))-{0}
        if len(ids)!=1 or seen&ids:raise ValueError("Merged or lost native component")
        j=ids.pop();seen.add(j);ratio=float((b==j).sum()/(a==i).sum());ratios.append(ratio)
        if not .75<=ratio<=1.20:raise ValueError("Component mass outside finer-ink bounds")
    holes=ndi.binary_fill_holes(before)&~before;new=ndi.binary_fill_holes(after)&~after
    labels,count=ndi.label(holes);retention=[]
    for i in range(1,count+1):
        h=labels==i;fraction=float((h&new).sum()/h.sum());retention.append(fraction)
        if fraction<.75:raise ValueError("Counter retention below75percent")
    return dict(componentAreaRatios=ratios,counterOverlap=retention,minimumComponentAreaRatio=.75)



def reink(mask,seed):
    skeleton,dist=medial_axis(mask,return_distance=True,rng=0)
    labels,count=ndi.label(mask,structure=np.ones((3,3)))
    y,x=np.mgrid[:mask.shape[0],:mask.shape[1]]
    phase=seed/2**32*math.tau
    wave=.65*np.sin(x/157+y/211+phase)+.35*np.sin(x/269-y/173-phase)
    background=medial_axis(~mask,rng=0)
    clearance=ndi.distance_transform_edt(~background)
    maxradius=dist+np.maximum(0,clearance-dist)*.25
    baseline=np.zeros(mask.shape)
    for label in range(1,count+1):
        points=skeleton&(labels==label)
        if points.any():baseline[points]=np.median(dist[points])
    for strength in (1,.75,.5,.25,.125):
        radius=np.maximum(.75,dist*(1-strength)+baseline*strength*(1+.18*wave))
        radius=np.minimum(radius,maxradius)
        # Re-ink all native centerlines as overlapping round pen disks. Small
        # terminal fans remain in place; no semantic tick is pruned.
        new=np.zeros_like(mask)
        for cy,cx in np.argwhere(skeleton):
            r=float(radius[cy,cx]-.35);reach=math.ceil(r)
            yy0=max(0,cy-reach);yy1=min(mask.shape[0],cy+reach+1)
            xx0=max(0,cx-reach);xx1=min(mask.shape[1],cx+reach+1)
            dy,dx=np.ogrid[yy0-cy:yy1-cy,xx0-cx:xx1-cx]
            new[yy0:yy1,xx0:xx1]|=dx*dx+dy*dy<=r*r
        new|=skeleton
        try:checks=validate_reconstruction(mask,new)
        except ValueError:continue
        return new,{'strength':strength,'sourceTopology':topology(mask),'skeletonPixels':int(skeleton.sum()),'skeletonRetained':bool(np.all(new[skeleton])),'branchesPruned':0,**checks}
    raise ValueError('No complete skeleton re-inking preserves native component/counter guards')


def candidate(source,text,output):
    font=TTFont(source);before=shaped(font,text);records=[]
    inputs={name:raster(font,name) for name,*_ in before}
    for name,item in inputs.items():
        if not item:continue
        mask,transform=item;original=font['glyf'][name]
        try:
            new,checks=reink(mask,int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big'))
            font['glyf'][name]=outline(new,transform)
            rendered,_=raster(font,name,viewport=(*transform,mask.shape[1],mask.shape[0]))
            checks['vectorChecks']=validate_reconstruction(mask,rendered)
            records.append({'glyph':name,'status':'candidate',**checks})
        except ValueError as error:
            font['glyf'][name]=original;records.append({'glyph':name,'status':'retained','reason':str(error)})
    assert shaped(font,text)==before
    for rec in font['name'].names:
        if rec.nameID in {1,3,4,6,16,17}:rec.string='Dad Skeleton Pen Experiment'.encode(rec.getEncoding(),errors='replace')
    font.flavor=None;output.parent.mkdir(parents=True,exist_ok=True);font.save(output)
    return {'source':str(source),'output':str(output),'text':text,'shapingUnchanged':True,'glyphs':records}


def main():
    from render_specimen import render
    out=Path('output/font-review/skeleton-fine-dense-pen');records=[];samples=[]
    for row in json.loads(Path('docs/source-style-review.json').read_text())['sources']:
        if row['number'] not in {176,183,198,199}:continue
        source=Path(row['fonts'][0]['file']);text=row['sample'][:2]
        rec=candidate(source,text,out/f"{row['number']}.ttf");rec['sourceNumber']=row['number'];records.append(rec)
        for label,path in [('SOURCE',source),('SKELETON PEN',Path(rec['output']))]:samples.append({'label':f"{row['number']} {label}",'font':str(path),'text':text})
        (out/'review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(row['number'],'complete',flush=True)
    (out/'spec.json').write_text(json.dumps({'samples':samples},ensure_ascii=False,indent=2)+'\n')
    render(samples,out/'comparison')

if __name__=='__main__':main()
