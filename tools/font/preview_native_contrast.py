"""Local-only sample review of fast nonjoining native contour fields."""
import io
import json
import time
from pathlib import Path
from fontTools.ttLib import TTFont
from native_contrast_pen import transform
import check_supplemental_fields
from skeleton_fine_dense_pen import validate_reconstruction as fine_validate
check_supplemental_fields.validate_reconstruction=fine_validate
from supplemental_adapter import preserve_native_bounds,ROOT
from supplemental_pressure import shaped,raster
from skeleton_fine_dense_pen import validate_reconstruction
from render_specimen import render
from check_supplemental_fields import check


def main():
    rows=json.loads((ROOT/'docs/source-style-review.json').read_text())['sources'];out=ROOT/'output/font-review/native-contrast-pen';out.mkdir(parents=True,exist_ok=True)
    records=[];samples=[]
    for number in (176,183,197,198,199):
        row=next(r for r in rows if r['number']==number);source=ROOT/row['fonts'][0]['file'];text=row['sample']
        for amplitude in (.006,.01):
            font=TTFont(source,recalcTimestamp=False);positions=shaped(font,text);font.flavor=None;stream=io.BytesIO();font.save(stream);native=TTFont(io.BytesIO(stream.getvalue()),recalcTimestamp=False);native.setGlyphOrder(font.getGlyphOrder());glyphs=[];elapsed=0
            for name in dict.fromkeys(g[0] for g in positions):
                start=time.monotonic();result=transform(native,name,amplitude);elapsed+=time.monotonic()-start
                if result is None:continue
                glyph,rec=result;glyph=preserve_native_bounds(glyph,native,name);font['glyf'][name]=glyph
                before,viewport=raster(native,name);after,_=raster(font,name,viewport=(*viewport,before.shape[1],before.shape[0]))
                try:rec.update(status='candidate',checks=validate_reconstruction(before,after))
                except ValueError as error:font['glyf'][name]=native['glyf'][name];rec.update(status='native-retained-guard',reason=str(error))
                rec['glyph']=name;glyphs.append(rec)
            assert shaped(font,text)==positions
            for name in font['name'].names:
                if name.nameID in (1,3,4,6,16):name.string='Dad Contour Study'.encode(name.getEncoding(),errors='replace')
            output=out/f'{number}-{amplitude}.ttf';font.save(output);whole=check(source,output,text)
            rec=dict(source=str(source),output=str(output),sourceNumber=number,text=text,amplitude=amplitude,glyphs=glyphs,wholeField=whole,transformSeconds=elapsed)
            records.append(rec);print(number,amplitude,elapsed,whole['status'],flush=True)
            accepted=sum(g['status']=='candidate' for g in glyphs)
            for label,path in [('native',source),(f'normal pen {amplitude} {accepted}/{len(glyphs)} adapted',output)]:samples.append(dict(label=f'{number} {Path(row["source"]).stem} {label}',font=str(path),text=text))
    (out/'review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    for i in range(0,len(samples),4):render(samples[i:i+4],out/f'page-{i//4+1}')

if __name__=='__main__':main()
