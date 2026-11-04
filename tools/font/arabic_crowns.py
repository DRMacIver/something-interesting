"""Integrate the pinned crown-letter drawings with Scheherazade joining.

Only initial forms are attested in ordinary text (Unicode 18 §9.2). Keep that
source drawing in isolated contexts too; do not invent a separate historic form.
"""
from copy import deepcopy
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from arabic_marks import bounds

BASES=[0x628,0x67e,0x62a,0x62b,0x62c,0x62d,0x62e,0x633,0x634,0x635,0x636,0x637,0x638,0x639,0x63a,0x641,0x642,0x643,0x645,0x646,0x647,0x64a]
POINTS=set(range(0x10ed9,0x10eef))


def tail_center(glyph,glyphs):
    pen=DecomposingRecordingPen(glyphs);glyph.draw(pen)
    previous=None;candidates=[]
    for op,args in pen.value:
        if op=='lineTo' and previous:
            x,y=args[0];px,py=previous
            if -64<=y-py<=-58 and abs(x-px)<10 and max(x,px)<40 and max(y,py)<150:
                candidates.append(((x+px)/2,(y+py)/2))
        if op in {'moveTo','lineTo','curveTo','qCurveTo'}:previous=args[-1]
        elif op in {'closePath','endPath'}:previous=None
    assert len(candidates)==1,candidates
    return candidates[0]


def add_crowns(font,donor):
    cmap=font.getBestCmap();source=donor.getBestCmap();gs=donor.getGlyphSet()
    scale=font['head'].unitsPerEm/donor['head'].unitsPerEm
    assert font['head'].unitsPerEm==2048
    variation=next(t for t in font['cmap'].tables if t.format==14)
    for i,cp in enumerate(sorted(POINTS)):
        name=f'uni{cp:X}';base=BASES[i];reference=cmap[base]+'.init'
        assert reference in font.getGlyphOrder(),reference
        old=bounds(font,reference)
        tx,ty=tail_center(gs[source[cp]],gs)
        dx,dy=-30-tx*scale,91-ty*scale
        pen=TTGlyphPen(None)
        gs[source[cp]].draw(TransformPen(Cu2QuPen(pen,max_err=0.5),(scale,0,0,scale,dx,dy)))
        order=list(font.getGlyphOrder());font['glyf'][name]=pen.glyph();font.setGlyphOrder(order+[name])
        advance=round(donor['hmtx'][source[cp]][0]*scale+dx)
        font['glyf'][name].recalcBounds(font['glyf'])
        font['hmtx'][name]=(advance,font['glyf'][name].xMin)
        new=bounds(font,name)
        font['GDEF'].table.GlyphClassDef.classDefs[name]=1
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format==12:table.cmap[cp]=name
        variation.uvsDict[0xe0120+i]=[(base,name)]
        # Preserve native mark classes and optical clearances, moving anchors
        # to the crown's larger ink envelope. Crown letters are not ligatures.
        added=0
        for lookup in font['GPOS'].table.LookupList.Lookup:
            for sub in lookup.SubTable:
                kind=lookup.LookupType
                if kind==9:kind,sub=sub.ExtensionLookupType,sub.ExtSubTable
                if kind!=4 or reference not in sub.BaseCoverage.glyphs:continue
                record=deepcopy(sub.BaseArray.BaseRecord[sub.BaseCoverage.glyphs.index(reference)])
                for anchor in record.BaseAnchor:
                    if anchor:
                        anchor.XCoordinate+=round((new[0]+new[2]-old[0]-old[2])/2)
                        edge=3 if anchor.YCoordinate>(old[1]+old[3])/2 else 1
                        anchor.YCoordinate+=round(new[edge]-old[edge])
                sub.BaseCoverage.glyphs.append(name);sub.BaseArray.BaseRecord.append(record)
                sub.BaseArray.BaseCount=len(sub.BaseArray.BaseRecord);added+=1
        assert added,(hex(cp),reference)
