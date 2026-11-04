"""Higher flag counts retain native stem attachment and distinct drawings."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape, ROOT
from test_font_cuneiform import outline
from test_font_hebrew_marks import positioned


def pair():
    e = next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoMusic-Regular.ttf'))
    return e, TTFont(ROOT / e['file'])


def test_flags_keep_stem_edge_bottom_alignment_and_native_advance():
    e, f = pair(); p = ROOT / e['file']
    heights = []
    for cp in range(0x1D250, 0x1D253):
        ink = outline(f, cp)
        assert ink[0] and ink[2] == 0
        assert f['glyf'][f.getBestCmap()[cp]].numberOfContours == cp - 0x1D250 + 6
        assert f['GDEF'].table.GlyphClassDef.classDefs[f.getBestCmap()[cp]] == 3
        heights.append(ink[1][3] - ink[1][1])
        for head in [0x1D157, 0x1D158, 0x1D143, 0x1D144, 0x1D155]:
            base = chr(head) + '\U0001d165'
            a = positioned(f, p, base + chr(cp), cp)
            b = positioned(f, p, base + '\U0001d172', 0x1D172)
            assert a[0] == b[0] and a[1] == b[1]
            assert a[3] > b[3]
            assert sum(g[1] for g in shape(p, base + chr(cp))) == sum(g[1] for g in shape(p, base + '\U0001d172'))
            assert all(g[0] for g in shape(p, base + chr(cp)))
    assert heights[0] < heights[1] < heights[2]
    assert len({repr(outline(f, cp)[0]) for cp in range(0x1D250, 0x1D253)}) == 3


def test_dots_tremolo_and_articulations_retain_contextual_positions():
    e, f = pair(); p = ROOT / e['file']
    for cp in range(0x1D250, 0x1D253):
        for other in [0x1D16D, 0x1D169, 0x1D17B, 0x1D127, 0x1D128]:
            base = '\U0001d158\U0001d165'
            new, old = base + chr(cp) + chr(other), base + '\U0001d172' + chr(other)
            # Tremolo may select a native low variant: compare shaped glyphs,
            # not just the un-substituted cmap name.
            new_id = f.getGlyphID(f.getBestCmap()[cp])
            old_id = f.getGlyphID(f.getBestCmap()[0x1D172])
            actual = [(old_id if gid == new_id else gid, *pos) for gid, *pos in shape(p, new, True)]
            assert actual == shape(p, old, True)
            assert all(g[0] for g in shape(p, new))
    for text in ['\U0001d158\U0001d165\U0001d172', '\U0001d164\U0001d16d', '\U0001d160\U0001d17b']:
        assert shape(ROOT / e['source'], text) == shape(p, text)
