"""New numeric signs preserve source drawings and meaningful size differences."""
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.boundsPen import BoundsPen
from test_font_scripts import manifest, shape, ROOT
from font_baseline_checks import pinned_packaging_font


def entry(source):
    return next(e for e in manifest()['fonts'] if source in e['source'])


def outline(font, cp):
    glyphs = font.getGlyphSet()
    name = font.getBestCmap()[cp]
    pen = DecomposingRecordingPen(glyphs)
    glyphs[name].draw(pen)
    bounds = BoundsPen(glyphs)
    glyphs[name].draw(bounds)
    return pen.value, bounds.bounds, font['hmtx'][name][0]


def test_complete_archaic_inventory_has_real_preserved_outlines():
    e = entry('ArchaicCuneiformNumerals')
    source, packaged = TTFont(ROOT/e['source']), TTFont(ROOT/e['file'])
    native = pinned_packaging_font(e)
    required = set(range(0x12550, 0x12687))
    assert set(packaged.getBestCmap()) == required
    for cp in required:
        drawn = outline(packaged, cp)
        assert drawn[0] and drawn[1] is not None and drawn[2] > 0, hex(cp)
        assert outline(native, cp) == outline(source, cp)
        original_glyph=native['glyf'][native.getBestCmap()[cp]]
        current_glyph=packaged['glyf'][packaged.getBestCmap()[cp]]
        fields=('xMin','yMin','xMax','yMax')
        frame=tuple(getattr(original_glyph,field) for field in fields)
        assert tuple(getattr(current_glyph,field) for field in fields)==frame,hex(cp)
        assert drawn[2]==outline(native,cp)[2]
        # Pressure may change a quadratic's true extremum inside its exact
        # original integer attachment frame; no curve/area epsilon is used.
        x0,y0,x1,y1=drawn[1]
        assert frame[0]<=x0<=x1<=frame[2] and frame[1]<=y0<=y1<=frame[3],hex(cp)
    text = ''.join(map(chr, sorted(required)))
    assert shape(ROOT/e['source'], text) == shape(ROOT/e['file'], text)
    assert all(g[0] for g in shape(ROOT/e['file'], text))


def test_tenu_numerals_preserve_distinct_drawings():
    e = entry('UnicodiaCunei')
    source, packaged = TTFont(ROOT/e['source']), TTFont(ROOT/e['file'])
    native = pinned_packaging_font(e)
    required = [0x1246F, *range(0x12475, 0x12480)]
    drawings = []
    for cp in required:
        drawn = outline(packaged, cp)
        assert drawn[0] and drawn[1] is not None and drawn[2] > 0
        assert outline(native, cp) == outline(source, cp)
        assert drawn[1:] == outline(native, cp)[1:]
        drawings.append(repr(drawn[0]))
    assert len(set(drawings)) == 12


def test_higher_numerals_are_not_squeezed_to_chart_cell_width():
    # Unicode's chart notes explicitly warn that higher numbers were reduced
    # for chart cells. Text should retain the reference font's relative size.
    e = entry('ArchaicCuneiformNumerals')
    font = TTFont(ROOT/e['file'])
    one, nine = outline(font, 0x12550), outline(font, 0x12558)
    assert nine[2] > 2 * one[2]
    assert len({repr(outline(font, cp)[0]) for cp in range(0x12550, 0x12559)}) == 9
