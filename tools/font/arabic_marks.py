"""Graft licensed UFS marks into Scheherazade's native attachment system.

Use sukun/kasra attachment classes for above/below marks respectively. Keep
source drawings, scaling em units and converting cubic curves within 0.5 units.
Translated anchors retain the host font's optical clearance and stacking rules.
"""
from copy import deepcopy
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

ABOVE = {0x10ecb,0x10ece,0x10ecf,0x10ef3,0x10ef5,0x10ef7,0x10ef8,0x10ef9}
BELOW = {0x10ecc,0x10ecd,0x10ef0,0x10ef1,0x10ef2,0x10ef4,0x10ef6}
POINTS = ABOVE | BELOW


def bounds(font,name):
    gs=font.getGlyphSet(); pen=BoundsPen(gs);gs[name].draw(pen)
    return pen.bounds


def add_marks(font,donor):
    scale=font['head'].unitsPerEm/donor['head'].unitsPerEm
    cmap=dict(font.getBestCmap());donor_cmap=donor.getBestCmap()
    donor_glyphs=donor.getGlyphSet()
    for cp in sorted(POINTS):
        assert cp not in cmap
        name=f'uni{cp:X}'
        reference=cmap[0x652 if cp in ABOVE else 0x650]
        old=bounds(font,reference)
        pen=TTGlyphPen(None)
        donor_glyphs[donor_cmap[cp]].draw(TransformPen(Cu2QuPen(pen,max_err=0.5), (scale,0,0,scale,0,0)))
        order=list(font.getGlyphOrder())
        font['glyf'][name]=pen.glyph();font.setGlyphOrder(order+[name])
        font['hmtx'][name]=(0,0)
        new=bounds(font,name)
        font['hmtx'][name]=(0,round(new[0]))
        cmap[cp]=name
        gdef=font['GDEF'].table
        gdef.GlyphClassDef.classDefs[name]=3
        attach=getattr(gdef,'MarkAttachClassDef',None)
        if attach and reference in attach.classDefs:attach.classDefs[name]=attach.classDefs[reference]
        sets=getattr(gdef,'MarkGlyphSetsDef',None)
        if sets:
            for coverage in sets.Coverage:
                if reference in coverage.glyphs:coverage.glyphs.append(name)
        dx=round((new[0]+new[2]-old[0]-old[2])/2)
        # The crown surrounds the letter's top (Unicode 18 §9.2.9), rather
        # than occupying an ordinary above-accent slot. Its arch rises a
        # quarter em beyond the host's top attachment line.
        crown_incoming = new[3] - font['head'].unitsPerEm / 4
        incoming=1 if cp in ABOVE else 3
        outgoing=3 if cp in ABOVE else 1
        counts={4:0,5:0,6:0}
        crown_stack=None
        crown_incoming_record=None
        for lookup in font['GPOS'].table.LookupList.Lookup:
            for sub in lookup.SubTable:
                kind=lookup.LookupType
                if kind==9:kind,sub=sub.ExtensionLookupType,sub.ExtSubTable
                for cov,arr,recs,count,stack in [
                    ('MarkCoverage','MarkArray','MarkRecord','MarkCount',False),
                    ('Mark1Coverage','Mark1Array','MarkRecord','MarkCount',False),
                    ('Mark2Coverage','Mark2Array','Mark2Record','Mark2Count',True)]:
                    coverage=getattr(sub,cov,None)
                    if coverage is None or reference not in coverage.glyphs:continue
                    array=getattr(sub,arr);records=getattr(array,recs)
                    record=deepcopy(records[coverage.glyphs.index(reference)])
                    anchors=record.Mark2Anchor if stack else [record.MarkAnchor]
                    edge=outgoing if stack else incoming
                    for anchor in anchors:
                        if anchor:
                            anchor.XCoordinate+=dx
                            delta = crown_incoming-old[1] if cp == 0x10ef9 and not stack and kind in {4,5} else new[edge]-old[edge]
                            anchor.YCoordinate+=round(delta)
                    if cp == 0x10ef9 and kind == 6 and cov == 'Mark1Coverage':
                        # A crown frames the base even when ordinary vowel
                        # accents precede it after canonical reordering.
                        crown_stack=deepcopy(lookup)
                        crown_incoming_record=record
                        continue
                    coverage.glyphs.append(name);records.append(record)
                    setattr(array,count,len(records));counts[kind]+=1
        assert counts[4] and counts[6],(hex(cp),counts)
        if crown_stack is not None:
            # Repeated crowns stack with each other; other accents must not
            # capture the crown's incoming attachment.
            sub=crown_stack.SubTable[0]
            if crown_stack.LookupType==9:sub=sub.ExtSubTable
            ref_index=sub.Mark2Coverage.glyphs.index(reference)
            outgoing_record=deepcopy(sub.Mark2Array.Mark2Record[ref_index])
            for anchor in outgoing_record.Mark2Anchor:
                if anchor:
                    anchor.XCoordinate+=dx
                    anchor.YCoordinate+=round(new[3]-old[3])
            sub.Mark1Coverage.glyphs=[name]
            sub.Mark1Array.MarkRecord=[crown_incoming_record];sub.Mark1Array.MarkCount=1
            sub.Mark2Coverage.glyphs=[name]
            sub.Mark2Array.Mark2Record=[outgoing_record];sub.Mark2Array.Mark2Count=1
            lookups=font['GPOS'].table.LookupList
            index=len(lookups.Lookup);lookups.Lookup.append(crown_stack);lookups.LookupCount=len(lookups.Lookup)
            for feature in font['GPOS'].table.FeatureList.FeatureRecord:
                if feature.FeatureTag=='mkmk':
                    feature.Feature.LookupListIndex.append(index)
                    feature.Feature.LookupCount=len(feature.Feature.LookupListIndex)
    full=CmapSubtable.newSubtable(12)
    full.platformID,full.platEncID,full.language=3,10,0
    full.cmap=cmap
    font['cmap'].tables=[t for t in font['cmap'].tables if (t.platformID,t.platEncID,t.language)!=(3,10,0)]+[full]
    for table in font['cmap'].tables:
        if table.isUnicode() and table.format==12:table.cmap.update(cmap)

    # Older browser Unicode tables do not classify these Unicode 18 marks.
    # UVS aliases keep the source text intact while giving native shaping a
    # known Arabic mark category and selecting the same supplemental drawing.
    variation=CmapSubtable.newSubtable(14)
    variation.platformID,variation.platEncID,variation.language=0,5,0
    variation.cmap={}
    variation.uvsDict={0xE0100+i:[(0x652 if cp in ABOVE else 0x650,cmap[cp])]
                       for i,cp in enumerate(sorted(POINTS))}
    font['cmap'].tables.append(variation)
