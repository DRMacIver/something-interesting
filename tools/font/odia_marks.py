"""Add historical Kui tone dots using Odia's native overline attachment rules."""
from copy import deepcopy
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from hebrew_marks import bounds

POINTS = {0x0B53, 0x0B54}


def add_marks(font, donor):
    reference = font.getBestCmap()[0x0B55]
    old = bounds(font, reference)
    notice = '\n'.join(sorted({n.toUnicode() for n in donor['name'].names if n.nameID == 0}))
    for record in font['name'].names:
        if record.nameID == 0 and notice not in record.toUnicode():
            record.string = (record.toUnicode() + '\n' + notice).encode(record.getEncoding())
    scale = font['head'].unitsPerEm / donor['head'].unitsPerEm
    for cp in sorted(POINTS):
        assert cp not in font.getBestCmap()
        name = f'uni{cp:04X}'
        pen = TTGlyphPen(None)
        donor.getGlyphSet()[donor.getBestCmap()[cp]].draw(
            TransformPen(Cu2QuPen(pen, max_err=.5), (scale, 0, 0, scale, 0, 0)))
        order = list(font.getGlyphOrder())
        font['glyf'][name] = pen.glyph()
        font.setGlyphOrder(order + [name])
        font['hmtx'][name] = (0, 0)
        new = bounds(font, name)
        dx = round((old[0] + old[2] - new[0] - new[2]) / 2)
        dy = round(old[1] - new[1])
        aligned = TTGlyphPen(None)
        font.getGlyphSet()[name].draw(TransformPen(aligned, (1, 0, 0, 1, dx, dy)))
        font['glyf'][name] = aligned.glyph()
        new = bounds(font, name)
        font['hmtx'][name] = (0, round(new[0]))
        gdef = font['GDEF'].table
        gdef.GlyphClassDef.classDefs[name] = 3
        attach = getattr(gdef, 'MarkAttachClassDef', None)
        if attach and reference in attach.classDefs:
            attach.classDefs[name] = attach.classDefs[reference]
        sets = getattr(gdef, 'MarkGlyphSetsDef', None)
        if sets:
            for coverage in sets.Coverage:
                if reference in coverage.glyphs:
                    coverage.glyphs.append(name)
        counts = {4: 0, 6: 0}
        for lookup in font['GPOS'].table.LookupList.Lookup:
            for sub in lookup.SubTable:
                kind = lookup.LookupType
                if kind == 9:
                    kind, sub = sub.ExtensionLookupType, sub.ExtSubTable
                if kind not in counts:
                    continue
                coverage = sub.MarkCoverage if kind == 4 else sub.Mark1Coverage
                array = sub.MarkArray if kind == 4 else sub.Mark1Array
                if reference in coverage.glyphs:
                    record = deepcopy(array.MarkRecord[coverage.glyphs.index(reference)])
                    coverage.glyphs.append(name)
                    array.MarkRecord.append(record)
                    array.MarkCount = len(array.MarkRecord)
                    counts[kind] += 1
                if kind == 6 and reference in sub.Mark2Coverage.glyphs:
                    record = deepcopy(sub.Mark2Array.Mark2Record[sub.Mark2Coverage.glyphs.index(reference)])
                    for anchor in record.Mark2Anchor:
                        if anchor:
                            anchor.YCoordinate += round(new[3] - old[3])
                    sub.Mark2Coverage.glyphs.append(name)
                    sub.Mark2Array.Mark2Record.append(record)
                    sub.Mark2Array.Mark2Count = len(sub.Mark2Array.Mark2Record)
        assert counts == {4: 2, 6: 1}, counts
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format in (4, 12):
                table.cmap[cp] = name
    _complete_vowel_anchors(font)
    from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
    uvs = CmapSubtable.newSubtable(14)
    uvs.platformID, uvs.platEncID, uvs.language = 0, 5, 0
    uvs.cmap = {}
    uvs.uvsDict = {0xE0140 + i: [(0x0B55, font.getBestCmap()[cp])]
                   for i, cp in enumerate(sorted(POINTS))}
    font['cmap'].tables.append(uvs)


def _complete_vowel_anchors(font):
    """Supply the historically documented vowel hosts missing in the source.

    These lookups contain only the new dots, preserving all older typography.
    Bounds establish a centered placement with 73 font units of top clearance.
    """
    from fontTools.ttLib.tables import otTables as ot
    def anchor(x, y):
        a = ot.Anchor(); a.Format = 1
        a.XCoordinate, a.YCoordinate = round(x), round(y)
        return a
    def coverage(names):
        c = ot.Coverage(); c.glyphs = names; return c
    def add_lookup(kind, hosts, feature_tag):
        s = ot.MarkBasePos() if kind == 4 else ot.MarkMarkPos()
        s.Format, s.ClassCount = 1, 1
        marks = [font.getBestCmap()[cp] for cp in sorted(POINTS)]
        array = ot.MarkArray(); array.MarkRecord = []
        for name in marks:
            r = ot.MarkRecord(); r.Class = 0; r.MarkAnchor = anchor(0, 727)
            array.MarkRecord.append(r)
        array.MarkCount = len(marks)
        if kind == 4:
            s.MarkCoverage, s.MarkArray = coverage(marks), array
            s.BaseCoverage = coverage(hosts)
            s.BaseArray = ot.BaseArray(); s.BaseArray.BaseRecord = []
        else:
            s.Mark1Coverage, s.Mark1Array = coverage(marks), array
            s.Mark2Coverage = coverage(hosts)
            s.Mark2Array = ot.Mark2Array(); s.Mark2Array.Mark2Record = []
        for name in hosts:
            b = bounds(font, name); a = anchor((b[0] + b[2]) / 2, b[3] + 20)
            if kind == 4:
                r = ot.BaseRecord(); r.BaseAnchor = [a]; s.BaseArray.BaseRecord.append(r)
            else:
                r = ot.Mark2Record(); r.Mark2Anchor = [a]; s.Mark2Array.Mark2Record.append(r)
        if kind == 4: s.BaseArray.BaseCount = len(hosts)
        else: s.Mark2Array.Mark2Count = len(hosts)
        lookup = ot.Lookup(); lookup.LookupType = kind; lookup.LookupFlag = 0
        lookup.SubTable = [s]; lookup.SubTableCount = 1
        table = font['GPOS'].table
        index = len(table.LookupList.Lookup)
        table.LookupList.Lookup.append(lookup); table.LookupList.LookupCount = index + 1
        count = 0
        for feature in table.FeatureList.FeatureRecord:
            if feature.FeatureTag == feature_tag:
                feature.Feature.LookupListIndex.append(index)
                feature.Feature.LookupCount += 1; count += 1
        assert count
    cmap = font.getBestCmap()
    add_lookup(4, [cmap[cp] for cp in (0xB05, 0xB06, 0xB0F, 0xB3E, 0xB47)], 'mark')
    add_lookup(6, [n for n in font.getGlyphOrder() if n == cmap[0xB3F] or n.startswith('iMatra')], 'mkmk')
