"""Isolated native CFF pressure candidates; no production font replacement.

Preserves native shaping and attachment coordinates and fits candidate ink to
its native bounds. Raster component/counter guards reject unsafe drawings.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from supplemental_pressure import ROOT, raster, pressure, outline, shaped
from prototype_unifont_lettering import validate_reconstruction


def candidate(source, text, output, amount=.45):
    native=TTFont(source,recalcTimestamp=False)
    if 'CFF ' not in native: raise ValueError('Native CFF outlines required')
    font=TTFont(source,recalcTimestamp=False)
    before=shaped(native,text)
    if any(name==native.getGlyphName(0) for name,*_ in before):
        raise ValueError('Missing native glyph in candidate field')
    tables={t:native[t].compile(native) for t in ('GPOS','GSUB','GDEF','hmtx') if t in native}
    records=[]
    for name in dict.fromkeys(row[0] for row in before):
        item=raster(native,name)
        if item is None: continue
        mask,transform=item;left,top,scale=transform
        xx=np.arange(mask.shape[1])+left;advance=native['hmtx'][name][0]*scale
        protected=np.minimum(1,np.minimum(abs(xx),abs(xx-advance))/20)[None,:]
        bp=BoundsPen(native.getGlyphSet());native.getGlyphSet()[name].draw(bp)
        old=bp.bounds
        topdict=font['CFF '].cff.topDictIndex[0];original=topdict.CharStrings[name]
        errors=[]
        for reduction in (1,.5,.25):
            try:
                changed,checks=pressure(mask,amount*reduction,int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big'),protected)
                glyph=outline(changed,transform);glyph.recalcBounds(None)
                new=(glyph.xMin,glyph.yMin,glyph.xMax,glyph.yMax)
                sx=(old[2]-old[0])/(new[2]-new[0]);sy=(old[3]-old[1])/(new[3]-new[1])
                if not .85<=sx<=1.15 or not .85<=sy<=1.15: raise ValueError('Attachment frame would move too far')
                # CFF coordinates can retain fractional native extrema.
                for i,(x,y) in enumerate(glyph.coordinates):
                    glyph.coordinates[i]=(old[0]+(x-new[0])*sx,old[1]+(y-new[1])*sy)
                pen=T2CharStringPen(font['hmtx'][name][0],None,roundTolerance=0)
                glyph.draw(pen,None)
                proposed=pen.getCharString(private=original.private,globalSubrs=original.globalSubrs)
                topdict.CharStrings[name]=proposed
                vector,_=raster(font,name,viewport=(*transform,mask.shape[1],mask.shape[0]))
                vector_checks=validate_reconstruction(mask,vector)
                small,view=raster(native,name,384)
                painted,_=raster(font,name,384,viewport=(*view,small.shape[1],small.shape[0]))
                detail=validate_reconstruction(small,painted)
                if not np.any(vector!=mask):raise ValueError('No visible vector pressure')
                records.append(dict(glyph=name,status='candidate',pressure=checks,vector=vector_checks,scale384=detail))
                break
            except (ValueError,ZeroDivisionError) as error:
                topdict.CharStrings[name]=original;errors.append(str(error))
        else:records.append(dict(glyph=name,status='native-retained',reasons=errors))
    assert shaped(font,text)==before
    assert all(font[t].compile(font)==raw for t,raw in tables.items())
    for rec in font['name'].names:
        if rec.nameID in {1,3,4,6,16,17}:rec.string='Dad Cubic Pressure Experiment'.encode(rec.getEncoding(),errors='replace')
    cff=font['CFF '].cff;cff.fontNames=['DadCubicPressureExperiment']
    for topdict in cff.topDictIndex:topdict.FamilyName=topdict.FullName='Dad Cubic Pressure Experiment'
    output.parent.mkdir(parents=True,exist_ok=True);font.flavor=None;font.save(output)
    return dict(source=str(source),sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),output=str(output),text=text,glyphs=records,shapingUnchanged=True,limitations=['Only the shaped sample is treated; not production coverage','Bounding-frame preservation and topology do not establish semantic identity or style acceptance'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--text',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--amount',type=float,default=.45);a=p.parse_args()
    r=candidate(a.source,a.text,a.output,a.amount);a.output.with_suffix('.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
