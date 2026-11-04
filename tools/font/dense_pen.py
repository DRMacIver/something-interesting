"""Isolated dense-script pen study: bounded width normalization and smooth drift.
No stroke/component is deleted deliberately. All sample candidates require
raster AND reconstructed-vector topology/counter guards and native layout tables.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import medial_axis
from fontTools.ttLib import TTFont
from supplemental_pressure import raster, outline, shaped
from prototype_unifont_lettering import validate_reconstruction


def treatment(mask, seed, strength=1):
    inside=ndi.distance_transform_edt(mask);outside=ndi.distance_transform_edt(~mask)
    field=np.where(mask,inside-.5,.5-outside)
    skeleton=medial_axis(mask,rng=0)
    background_skeleton=medial_axis(~mask,rng=0)
    holes=ndi.binary_fill_holes(mask)&~mask
    nearest=ndi.distance_transform_edt(~skeleton,return_distances=False,return_indices=True)
    radius=inside[tuple(nearest)]
    labels,count=ndi.label(mask,structure=np.ones((3,3)))
    owner=labels[tuple(ndi.distance_transform_edt(~mask,return_distances=False,return_indices=True))]
    target=radius.copy()
    for component in range(1,count+1):
        points=skeleton&(labels==component)
        if not points.any():continue
        # Preserve detached dots and short native strokes; normalize contrast
        # only inside larger strokes, independently of other components.
        characteristic=float(np.median(inside[points]))
        region=owner==component
        target[region]=radius[region]*.45+characteristic*.55
    y,x=np.mgrid[:mask.shape[0],:mask.shape[1]]
    phase=(seed%997)/997*np.pi*2
    wave=.65*np.sin(x/131+y/179+phase)+.35*np.sin(x/83-y/227-phase)
    # Width contrast becomes pressure contrast rather than typographic serif
    # contrast. Round only sub-stroke corners; preserve long stroke placement.
    delta=(target-radius)+target*.28*wave
    smooth=ndi.gaussian_filter(field,2.0)
    dx=5*np.sin(x/229+y/257+phase)
    dy=4*np.sin(x/277-y/233-phase)
    for reduction in (1,.75,.5,.25,.125):
        amount=strength*reduction
        shifted=ndi.map_coordinates(smooth,[y+dy*amount,x+dx*amount],order=1,mode='constant',cval=-24)
        candidate=field+amount*(shifted-field+delta)>=0
        # Preserve native stroke skeletons and all existing counter interiors.
        # Background skeletons protect narrow separations between components.
        candidate[skeleton]=True
        candidate[background_skeleton|holes]=False
        try:checks=validate_reconstruction(mask,candidate)
        except ValueError:continue
        return candidate,{'strength':amount,'changedPixels':int(np.sum(mask!=candidate)),**checks}
    raise ValueError('No dense-pen candidate preserves parts/counters/area')


def candidate(source,text,output):
    font=TTFont(source);before=shaped(font,text)
    inputs={name:raster(font,name) for name,*_ in before};records=[]
    for name,item in inputs.items():
        if item is None:continue
        mask,transform=item;original=font['glyf'][name]
        try:
            new,check=treatment(mask,int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big'))
            font['glyf'][name]=outline(new,transform)
            vector,_=raster(font,name,viewport=(*transform,mask.shape[1],mask.shape[0]))
            check['vectorChecks']=validate_reconstruction(mask,vector)
            records.append({'glyph':name,'status':'candidate',**check})
        except ValueError as error:
            font['glyf'][name]=original;records.append({'glyph':name,'status':'retained','reason':str(error)})
    assert shaped(font,text)==before
    for rec in font['name'].names:
        if rec.nameID in {1,3,4,6,16,17}:rec.string='Dad Dense Pen Experiment'.encode(rec.getEncoding(),errors='replace')
    font.flavor=None;output.parent.mkdir(parents=True,exist_ok=True);font.save(output)
    return {'source':str(source),'sourceSha256':hashlib.sha256(Path(source).read_bytes()).hexdigest(),'output':str(output),'text':text,'shapingUnchanged':True,'glyphs':records}


def main():
    from render_specimen import render
    output=Path('output/font-review/dense-pen-protected');records=[];samples=[]
    for row in json.loads(Path('docs/source-style-review.json').read_text())['sources']:
        if row['number'] not in {176,183,198,199}:continue
        source=Path(row['fonts'][0]['file']);text=row['sample'][:4]
        rec=candidate(source,text,output/f"{row['number']}.ttf");rec['sourceNumber']=row['number'];records.append(rec)
        for label,path in [('SOURCE',source),('DENSE PEN',Path(rec['output']))]:
            samples.append({'label':f"{row['number']} {label}",'font':str(path),'text':text})
        (output/'review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
        print(row['number'],'complete',flush=True)
    (output/'spec.json').write_text(json.dumps({'samples':samples},ensure_ascii=False,indent=2)+'\n')
    render(samples,output/'comparison')

if __name__=='__main__':main()
