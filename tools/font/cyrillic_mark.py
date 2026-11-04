"""Attach the licensed supplemental Cyrillic mark within Noto's native layout.

Reuse the above-letter mark class of U+2DE9. Translate its attachment points
by the ink bounds difference, preserving the source font's optical clearance.
"""
from copy import deepcopy
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable


def add_mark(font, donor):
    name = 'uni1E08F'
    reference = font.getBestCmap()[0x2DE9]
    donor_name = donor.getBestCmap()[0x1E08F]
    def bounds(f, n):
        gs = f.getGlyphSet()
        pen = BoundsPen(gs)
        gs[n].draw(pen)
        return pen.bounds
    old = bounds(font, reference)
    new = bounds(donor, donor_name)
    assert font['head'].unitsPerEm == donor['head'].unitsPerEm
    gs = donor.getGlyphSet()
    recording = DecomposingRecordingPen(gs)
    gs[donor_name].draw(recording)
    pen = TTGlyphPen(None)
    recording.replay(pen)
    order = list(font.getGlyphOrder())
    font['glyf'][name] = pen.glyph()
    font.setGlyphOrder(order + [name])
    font['hmtx'][name] = (0, round(new[0]))
    cmap = CmapSubtable.newSubtable(12)
    cmap.platformID, cmap.platEncID, cmap.language = 3, 10, 0
    cmap.cmap = dict(font.getBestCmap())
    cmap.cmap[0x1E08F] = name
    font['cmap'].tables = [t for t in font['cmap'].tables if (t.platformID,t.platEncID,t.language)!=(3,10,0)] + [cmap]
    for table in font['cmap'].tables:
        if table.isUnicode() and table.format == 12:
            table.cmap[0x1E08F] = name
    font['GDEF'].table.GlyphClassDef.classDefs[name] = 3
    for coverage in font['GDEF'].table.MarkGlyphSetsDef.Coverage:
        if reference in coverage.glyphs:
            coverage.glyphs.append(name)
    dx = round((new[0]+new[2]-old[0]-old[2])/2)
    counts = {4:0,5:0,6:0}
    for lookup in font['GPOS'].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            kind = lookup.LookupType
            if kind == 9:
                kind,sub = sub.ExtensionLookupType,sub.ExtSubTable
            for cov,arr,recs,count,upper in [
                ('MarkCoverage','MarkArray','MarkRecord','MarkCount',False),
                ('Mark1Coverage','Mark1Array','MarkRecord','MarkCount',False),
                ('Mark2Coverage','Mark2Array','Mark2Record','Mark2Count',True)]:
                coverage = getattr(sub,cov,None)
                if coverage is None or reference not in coverage.glyphs:
                    continue
                array = getattr(sub,arr)
                records = getattr(array,recs)
                record = deepcopy(records[coverage.glyphs.index(reference)])
                anchors = record.Mark2Anchor if upper else [record.MarkAnchor]
                for anchor in anchors:
                    if anchor:
                        anchor.XCoordinate += dx
                        anchor.YCoordinate += round(new[3 if upper else 1]-old[3 if upper else 1])
                coverage.glyphs.append(name)
                records.append(record)
                setattr(array,count,len(records))
                counts[kind] += 1
    assert counts[4] and counts[6], counts
