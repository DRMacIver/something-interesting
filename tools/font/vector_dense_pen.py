"""Review-only native-vector smooth pen flex; no contour reconstruction.
Retains source contour points, quadratic curves, counters and short strokes.
"""
from copy import deepcopy
import hashlib,json,math
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates
from supplemental_pressure import shaped,raster
from prototype_unifont_lettering import validate_reconstruction


def candidate(source,text,output):
    font=TTFont(source);sourcefont=TTFont(source);before=shaped(font,text);em=font['head'].unitsPerEm
    originals={name:deepcopy(font['glyf'][name]) for name,*_ in before};records=[]
    for name,original in originals.items():
        item=raster(font,name)
        if not item:continue
        mask,transform=item
        coords,ends,flags=original.getCoordinates(font['glyf'])
        phase=int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big')/2**32*math.tau
        for strength in (1,.75,.5,.25,.125):
            new=[]
            for x,y in coords:
                # Native em coordinates, low frequency and small derivative:
                # globally smooth flex, no independent point jitter.
                px=x/em;py=y/em
                dx=.014*math.sin(py*5.2+phase)+.006*math.sin(px*4.1+py*2.7-phase)
                dy=.012*math.sin(px*5.1-phase)+.005*math.sin(py*3.7-px*2.4+phase)
                new.append((round(x+dx*em*strength),round(y+dy*em*strength)))
            g=Glyph();g.program=Program();g.program.fromBytecode([]);g.numberOfContours=len(ends);g.coordinates=GlyphCoordinates(new);g.endPtsOfContours=ends;g.flags=flags
            font['glyf'][name]=g
            # A common expanded viewport accommodates actual changed bounds.
            left,top,scale=transform; viewport=(left-24,top+24,scale,mask.shape[1]+48,mask.shape[0]+48)
            old,_=raster(sourcefont,name,viewport=viewport)
            changed,_=raster(font,name,viewport=viewport)
            try:checks=validate_reconstruction(old,changed)
            except ValueError:continue
            records.append({'glyph':name,'status':'candidate','strength':strength,**checks});break
        else:
            font['glyf'][name]=original;records.append({'glyph':name,'status':'retained'})
    assert shaped(font,text)==before
    for rec in font['name'].names:
        if rec.nameID in {1,3,4,6,16,17}:rec.string='Dad Vector Pen Experiment'.encode(rec.getEncoding(),errors='replace')
    font.flavor=None;output.parent.mkdir(parents=True,exist_ok=True);font.save(output)
    return {'source':str(source),'output':str(output),'text':text,'shapingUnchanged':True,'glyphs':records}


def main():
    from render_specimen import render
    output=Path('output/font-review/vector-dense-pen');samples=[];records=[]
    for row in json.loads(Path('docs/source-style-review.json').read_text())['sources']:
        if row['number'] not in {176,183,198,199}:continue
        source=Path(row['fonts'][0]['file']);text=row['sample'][:4]
        rec=candidate(source,text,output/f"{row['number']}.ttf");rec['sourceNumber']=row['number'];records.append(rec)
        for label,path in [('SOURCE',source),('VECTOR PEN',Path(rec['output']))]:samples.append({'label':f"{row['number']} {label}",'font':str(path),'text':text})
        (output/'review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(row['number'],'complete',flush=True)
    (output/'spec.json').write_text(json.dumps({'samples':samples},ensure_ascii=False,indent=2)+'\n')
    render(samples,output/'comparison')

if __name__=='__main__':main()
