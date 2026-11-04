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
from native_contour_pressure import transform as flex
from prototype_unifont_lettering import topology

from dense_skeleton_edt import reink_candidates,validate_reconstruction

def candidate(source,text,output):
    font=TTFont(source);before=shaped(font,text);records=[]
    inputs={name:raster(font,name) for name,*_ in before}
    for name,item in inputs.items():
        if not item:continue
        mask,transform=item;original=font['glyf'][name]
        accepted=False;last='No guarded complete skeleton candidate'
        seed=int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big')
        for new,checks in reink_candidates(mask,seed):
            base=outline(new,transform)
            for amplitude in (.005,.003,0):
                font['glyf'][name]=base
                if amplitude:
                    altered,meta=flex(font,name,amplitude=amplitude)
                    font['glyf'][name]=altered
                else:meta={'amplitude':0}
                rendered,_=raster(font,name,viewport=(*transform,mask.shape[1],mask.shape[0]))
                try: vector=validate_reconstruction(mask,rendered)
                except ValueError as error:last=str(error);continue
                records.append({'glyph':name,'status':'candidate',**checks,'vectorChecks':vector,'flex':meta})
                accepted=True;break
            if accepted:break
        if not accepted:
            font['glyf'][name]=original;records.append({'glyph':name,'status':'retained','reason':last})
    assert shaped(font,text)==before
    for rec in font['name'].names:
        if rec.nameID in {1,3,4,6,16,17}:rec.string='Dad Skeleton Pen Experiment'.encode(rec.getEncoding(),errors='replace')
    font.flavor=None;output.parent.mkdir(parents=True,exist_ok=True);font.save(output)
    original=TTFont(source)
    tables={tag:original.getTableData(tag)==font.getTableData(tag) for tag in ('GSUB','GPOS','GDEF','hmtx') if tag in original}
    return {'source':str(source),'sourceSha256':hashlib.sha256(Path(source).read_bytes()).hexdigest(),'output':str(output),'text':text,'shapingUnchanged':True,'nativeTableChecks':tables,'glyphs':records}


def main():
    from render_specimen import render
    out=Path('output/font-review/skeleton-edt-dense-pen');records=[];samples=[]
    for row in json.loads(Path('docs/source-style-review.json').read_text())['sources']:
        if row['number'] not in {176,183,197,198,199}:continue
        source=Path(row['fonts'][0]['file']);text=row['sample']
        rec=candidate(source,text,out/f"{row['number']}.ttf");rec['sourceNumber']=row['number'];records.append(rec)
        for label,path in [('SOURCE',source),(f"SKELETON PEN {sum(g['status']=='candidate' for g in rec['glyphs'])}/{len(rec['glyphs'])} ADAPTED",Path(rec['output']))]:samples.append({'label':f"{row['number']} {label}",'font':str(path),'text':text})
        (out/'review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(row['number'],'complete',flush=True)
    (out/'spec.json').write_text(json.dumps({'samples':samples},ensure_ascii=False,indent=2)+'\n')
    render(samples,out/'comparison')

if __name__=='__main__':main()
