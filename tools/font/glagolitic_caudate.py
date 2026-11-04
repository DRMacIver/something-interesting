"""Fit OFL caudate chrivi forms to native Glagolitic heights and mark anchors."""
from copy import deepcopy
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from hebrew_marks import bounds

POINTS = {0x2C2F: 0x2C1D, 0x2C5F: 0x2C4D}


def add_letters(font, donor):
    notice = '\n'.join(sorted({n.toUnicode() for n in donor['name'].names if n.nameID == 0}))
    for record in font['name'].names:
        if record.nameID == 0 and notice not in record.toUnicode():
            record.string = (record.toUnicode() + '\n' + notice).encode(record.getEncoding())
    for cp, reference in POINTS.items():
        old = font.getBestCmap()[reference]; new = f'uni{cp:04X}'
        source = donor.getBestCmap()[cp]
        native_box = bounds(font, old); source_box = bounds(donor, source)
        scale = native_box[3] / source_box[3]
        recording = DecomposingRecordingPen(donor.getGlyphSet())
        donor.getGlyphSet()[source].draw(recording)
        pen = TTGlyphPen(None)
        recording.replay(TransformPen(pen, (scale, 0, 0, scale, 0, 0)))
        order = list(font.getGlyphOrder()); font['glyf'][new] = pen.glyph()
        font.setGlyphOrder(order + [new])
        advance = round(donor['hmtx'][source][0] * scale)
        font['hmtx'][new] = (advance, round(source_box[0] * scale))
        box = bounds(font, new)
        dx = (box[0] + box[2] - native_box[0] - native_box[2]) / 2
        gdef = font['GDEF'].table.GlyphClassDef.classDefs
        if old in gdef: gdef[new] = gdef[old]
        for lookup in font['GPOS'].table.LookupList.Lookup:
            assert lookup.LookupType in (4, 6)
            if lookup.LookupType != 4: continue
            for sub in lookup.SubTable:
                if old not in sub.BaseCoverage.glyphs: continue
                record = deepcopy(sub.BaseArray.BaseRecord[sub.BaseCoverage.glyphs.index(old)])
                for anchor in record.BaseAnchor:
                    if anchor: anchor.XCoordinate += round(dx)
                sub.BaseCoverage.glyphs.append(new); sub.BaseArray.BaseRecord.append(record)
                sub.BaseArray.BaseCount = len(sub.BaseArray.BaseRecord)
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format in (4, 12): table.cmap[cp] = new
    # Cyrillic-script combining marks can be itemized separately from the
    # Glagolitic base by browsers. Inherited tilde + a private drawing UVS
    # selects the original mark glyph without splitting the shaping run.
    from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
    uvs = CmapSubtable.newSubtable(14)
    uvs.platformID = 0; uvs.platEncID = 5; uvs.language = 0
    uvs.cmap = {}
    uvs.uvsDict = {0xE0170 + i: [(0x303, font.getBestCmap()[cp])]
                   for i, cp in enumerate((0x483, 0x484, 0x487))}
    font['cmap'].tables.append(uvs)
