"""Four/five tremolo strokes fitted to the native three-stroke stem area."""
from fontTools.pens.ttGlyphPen import TTGlyphPen
from music_mark_rules import extend_mark_rules

POINTS = {0x1D25B: 4, 0x1D25C: 5}


def add_marks(font):
    old = font.getBestCmap()[0x1D169]
    glyph = font['glyf'][old]
    # Pin the native slant and occupied region before constructing denser forms.
    assert list(glyph.coordinates[:4]) == [(50, 463), (348, 616), (348, 540), (50, 387)]
    for cp, count in POINTS.items():
        new = f'u{cp:05X}'
        thick = 56 if count == 4 else 40
        step = (481 - 153 - thick) / (count - 1)
        pen = TTGlyphPen(None)
        for i in range(count):
            bottom = round(387 + i * step)
            pen.moveTo((50, bottom + thick))
            pen.lineTo((348, bottom + 153 + thick))
            pen.lineTo((348, bottom + 153))
            pen.lineTo((50, bottom)); pen.closePath()
        from copy import deepcopy
        order = list(font.getGlyphOrder())
        font['glyf'][new] = pen.glyph(); font['glyf'][new + '_low'] = deepcopy(font['glyf'][new])
        font.setGlyphOrder(order + [new, new + '_low'])
        font['hmtx'][new] = font['hmtx'][new + '_low'] = (0, 50)
        outputs = {old: new, old + '_low': new + '_low'}
        extend_mark_rules(font, old, new, outputs)
        extend_mark_rules(font, old + '_low', new + '_low', outputs)
        _retain_reordered_count(font, old, new)
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format == 12: table.cmap[cp] = new


def _retain_reordered_count(font, old, new):
    # Native lookup 13 moves a tremolo across a stem by deleting and reinserting
    # it. Each new count needs its own insertion, not the three-stroke output.
    from copy import deepcopy
    table = font['GSUB'].table
    insertion = table.LookupList.Lookup[1]
    assert insertion.LookupType == 2
    assert insertion.SubTable[0].mapping['u1D165'] == ['u1D165', old]
    clone = deepcopy(insertion)
    for sub in clone.SubTable:
        sub.mapping = {k: [new if v == old else v for v in values] for k, values in sub.mapping.items()}
    index = len(table.LookupList.Lookup)
    table.LookupList.Lookup.append(clone); table.LookupList.LookupCount = index + 1
    context = table.LookupList.Lookup[13]
    matches = [s for s in context.SubTable if s.Format == 3 and old in s.Coverage[0].glyphs]
    assert len(matches) == 1
    original = matches[0]
    original.Coverage[0].glyphs.remove(new)
    replacement = deepcopy(original); replacement.Coverage[0].glyphs = [new]
    for record in replacement.SubstLookupRecord:
        if record.LookupListIndex == 1: record.LookupListIndex = index
    context.SubTable.append(replacement); context.SubTableCount = len(context.SubTable)
