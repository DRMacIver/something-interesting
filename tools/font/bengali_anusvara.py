"""Attach the historical Bengali above-anusvara in the complete native font."""
from copy import deepcopy
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from hebrew_marks import bounds

POINT = 0x11DF0
SELECTOR = 0xE0151


def add_mark(font, donor):
    _add_form(font, donor, False)
    _add_form(font, donor, True)


def _add_form(font, donor, high):
    old = font.getBestCmap()[0x981]
    new = 'anusvaraAbove-beng' + ('.high' if high else '')
    notice = '\n'.join(sorted({n.toUnicode() for n in donor['name'].names if n.nameID == 0}))
    for record in font['name'].names:
        if record.nameID == 0 and notice not in record.toUnicode():
            record.string = (record.toUnicode() + '\n' + notice).encode(record.getEncoding())
    scale = font['head'].unitsPerEm / donor['head'].unitsPerEm
    pen = TTGlyphPen(None)
    donor.getGlyphSet()[donor.getBestCmap()[POINT]].draw(
        TransformPen(Cu2QuPen(pen, max_err=.5), (scale, 0, 0, scale, 0, 0)))
    order = list(font.getGlyphOrder())
    font['glyf'][new] = pen.glyph(); font.setGlyphOrder(order + [new])
    font['hmtx'][new] = (0, 0)
    a, b = bounds(font, old), bounds(font, new)
    dx, dy = round((a[0] + a[2] - b[0] - b[2]) / 2), round(a[1] - b[1])
    # Keep the separate-ring form clear of tall native headlines.
    dy += 30
    if high: dy += 300
    aligned = TTGlyphPen(None)
    font.getGlyphSet()[new].draw(TransformPen(aligned, (1, 0, 0, 1, dx, dy)))
    font['glyf'][new] = aligned.glyph(); font['hmtx'][new] = (0, round(bounds(font, new)[0]))
    def cover(c):
        if old in c.glyphs: c.glyphs.append(new)
    gdef = font['GDEF'].table
    gdef.GlyphClassDef.classDefs[new] = 3
    attach = getattr(gdef, 'MarkAttachClassDef', None)
    if attach and old in attach.classDefs: attach.classDefs[new] = attach.classDefs[old]
    if getattr(gdef, 'MarkGlyphSetsDef', None):
        for c in gdef.MarkGlyphSetsDef.Coverage: cover(c)
    counts = {4: 0, 6: 0}
    for lookup in font['GPOS'].table.LookupList.Lookup:
        for s in lookup.SubTable:
            kind = lookup.LookupType
            if kind in (4, 6):
                c, array = (s.MarkCoverage, s.MarkArray) if kind == 4 else (s.Mark1Coverage, s.Mark1Array)
                if old in c.glyphs:
                    array.MarkRecord.append(deepcopy(array.MarkRecord[c.glyphs.index(old)]))
                    c.glyphs.append(new); array.MarkCount = len(array.MarkRecord); counts[kind] += 1
            elif kind == 8:
                assert s.Format == 3
                for key, value in vars(s).items():
                    if key.endswith('Coverage'):
                        for c in value: cover(c)
            elif kind == 1 and old in s.Coverage.glyphs:
                if s.Format == 2:
                    s.Value.append(deepcopy(s.Value[s.Coverage.glyphs.index(old)]))
                    s.ValueCount = len(s.Value)
                cover(s.Coverage)
    assert counts == {4: 2, 6: 1}, counts
    for table in font['cmap'].tables:
        if table.isUnicode() and table.format == 12 and not high: table.cmap[POINT] = new
        if table.format == 14: table.uvsDict[SELECTOR + int(high)] = [(0x981, new)]
