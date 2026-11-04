"""Attach UFS Hebrew points to the corresponding native Rashi mark classes."""
from copy import deepcopy
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen

POINTS={0x5c8:0x5b0,0x5c9:0x5bc}


def bounds(font,name):
    gs=font.getGlyphSet();p=BoundsPen(gs);gs[name].draw(p);return p.bounds


def add_marks(font,donor):
    notice='\n'.join(sorted({n.toUnicode() for n in donor['name'].names if n.nameID==0}))
    for record in font['name'].names:
        if record.nameID==0 and notice not in record.toUnicode():
            record.string=(record.toUnicode()+'\n'+notice).encode(record.getEncoding())
    cmap=font.getBestCmap();donor_cmap=donor.getBestCmap();gs=donor.getGlyphSet()
    scale=font['head'].unitsPerEm/donor['head'].unitsPerEm
    for cp,reference_cp in POINTS.items():
        assert cp not in cmap
        name=f'uni{cp:04X}';reference=cmap[reference_cp];old=bounds(font,reference)
        pen=TTGlyphPen(None)
        gs[donor_cmap[cp]].draw(TransformPen(Cu2QuPen(pen,max_err=.5),(scale,0,0,scale,0,0)))
        order=list(font.getGlyphOrder());font['glyf'][name]=pen.glyph();font.setGlyphOrder(order+[name])
        font['hmtx'][name]=(0,0);new=bounds(font,name);font['hmtx'][name]=(0,round(new[0]))
        dx=round((new[0]+new[2]-old[0]-old[2])/2)
        # Sheva retains clearance below the base; dagesh remains centered inside it.
        dy=round(new[3]-old[3] if cp==0x5c8 else (new[1]+new[3]-old[1]-old[3])/2)
        # Normalize the glyph's origin as well as its attachment geometry.
        # Bases without a native anchor then retain the reference's fallback position.
        aligned=TTGlyphPen(None)
        font.getGlyphSet()[name].draw(TransformPen(aligned,(1,0,0,1,-dx,-dy)))
        font['glyf'][name]=aligned.glyph()
        aligned_bounds=bounds(font,name);font['hmtx'][name]=(0,round(aligned_bounds[0]))
        gdef=font['GDEF'].table;gdef.GlyphClassDef.classDefs[name]=3
        attach=getattr(gdef,'MarkAttachClassDef',None)
        if attach and reference in attach.classDefs:attach.classDefs[name]=attach.classDefs[reference]
        sets=getattr(gdef,'MarkGlyphSetsDef',None)
        if sets:
            for coverage in sets.Coverage:
                if reference in coverage.glyphs:coverage.glyphs.append(name)
        count=0
        for lookup in font['GPOS'].table.LookupList.Lookup:
            for sub in lookup.SubTable:
                kind=lookup.LookupType
                if kind==9:kind,sub=sub.ExtensionLookupType,sub.ExtSubTable
                if kind!=4 or reference not in sub.MarkCoverage.glyphs:continue
                record=deepcopy(sub.MarkArray.MarkRecord[sub.MarkCoverage.glyphs.index(reference)])
                sub.MarkCoverage.glyphs.append(name);sub.MarkArray.MarkRecord.append(record)
                sub.MarkArray.MarkCount=len(sub.MarkArray.MarkRecord);count+=1
        assert count==1,(hex(cp),count)
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format in [4,12]:table.cmap[cp]=name
