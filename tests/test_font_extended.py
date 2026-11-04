"""Shaping regressions for the original lettering's Unicode extension."""
import io
from pathlib import Path

import pytest
import uharfbuzz as hb
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import RecordingPen

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def font():
    return TTFont(ROOT / "assets/fonts/dad-lettering-unicode.woff2")


def shape(font, text):
    stream = io.BytesIO()
    font.flavor = None
    font.save(stream)
    shaper = hb.Font(hb.Face(stream.getvalue()))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(shaper, buf)
    order = font.getGlyphOrder()
    return [(order[i.codepoint], p.x_advance, p.x_offset, p.y_offset)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


def test_approved_accent_specimen_has_glyphs(font):
    text = "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØŒÙÚÛÜÝŸŁŠŽ¿¡"
    assert all(row[0] != ".notdef" for row in shape(font, text))


def test_original_outlines_and_advances_are_unchanged(font):
    original = TTFont(ROOT / "data/font-sources/dad-lettering-base.woff2")
    old_glyphs, new_glyphs = original.getGlyphSet(), font.getGlyphSet()
    for name in original.getGlyphOrder():
        a, b = RecordingPen(), RecordingPen()
        old_glyphs[name].draw(a)
        new_glyphs[name].draw(b)
        assert a.value == b.value, name
        assert original["hmtx"].metrics[name] == font["hmtx"].metrics[name]


def test_joined_letters_keep_the_native_e_right_bearing(font):
    from fontTools.pens.boundsPen import BoundsPen
    glyphs = font.getGlyphSet()
    def bearing(name):
        pen = BoundsPen(glyphs)
        glyphs[name].draw(pen)
        return font['hmtx'][name][0] - pen.bounds[2]
    target = bearing(font.getBestCmap()[ord('E')])
    for char in 'ÆæŒœ':
        name = font.getBestCmap()[ord(char)]
        assert abs(bearing(name)-target) <= 1
        charstring = font['CFF '].cff.topDictIndex[0].CharStrings[name]
        charstring.draw(RecordingPen())
        assert charstring.width == font['hmtx'][name][0]


def test_ring_above_a_tracks_its_apex(font):
    from fontTools.pens.boundsPen import BoundsPen
    from optical_anchors import accent_centres
    glyphs = font.getGlyphSet()
    name = shape(font, 'A')[0][0]
    pen = BoundsPen(glyphs)
    glyphs[name].draw(pen)
    apex, _ = accent_centres(glyphs[name], glyphs, pen.bounds, top_fraction=.05)
    rows = shape(font, 'A\u030a')
    # HarfBuzz composes A-ring; its topmost ink should be centred on the apex.
    ring = BoundsPen(glyphs)
    glyphs[rows[0][0]].draw(ring)
    from optical_anchors import accent_centres as centres
    ring_centre, _ = centres(glyphs[rows[0][0]], glyphs, ring.bounds, top_fraction=.05)
    assert abs(ring_centre-apex) < 12


@pytest.mark.parametrize("composed,decomposed", [("É", "E\u0301"), ("ñ", "n\u0303"),
                                                ("Ǻ", "A\u030a\u0301"), ("ậ", "a\u0323\u0302")])
def test_canonical_equivalents_shape_identically(font, composed, decomposed):
    assert shape(font, composed) == shape(font, decomposed)


def test_combining_marks_stack_with_zero_advance(font):
    above = shape(font, "X\u0301\u0302\u0303\u0304")
    assert all(row[1] == 0 for row in above[1:])
    assert all(a[3] < b[3] for a, b in zip(above[1:], above[2:]))
    below = shape(font, "X\u0323\u0324\u0325")
    assert all(row[1] == 0 for row in below[1:])
    assert all(a[3] > b[3] for a, b in zip(below[1:], below[2:]))


def test_overlay_marks_cross_the_letters(font):
    result = shape(font, "X\u0334\u0335\u0336")
    assert all(row[1] == 0 for row in result[1:])
    assert all(100 < row[3] < 600 for row in result[1:])


def test_contextual_original_lettering_is_retained(font):
    assert len({row[0] for row in shape(font, "AAAA")}) == 4
    assert "I.pronoun" in [row[0].split(".alt")[0] for row in shape(font, "I THINK")]


def test_new_general_marks_are_real_zero_advance_glyphs(font):
    import json
    from fontTools.pens.boundsPen import BoundsPen
    data=json.loads((ROOT/'data/font-sources/unicodia.json').read_text())
    entry=next(e for e in data['files'] if e['path'].endswith('/UnicodiaFunky.ttf'))
    cps=[cp for a,b in entry['script_exclude_ranges'] for cp in range(a,b+1) if cp != 0x1e08f]  # Cyrillic mark belongs to the native Cyrillic font.
    assert len(cps)==39
    glyphs=font.getGlyphSet()
    for cp in cps:
        name=font.getBestCmap()[cp]
        pen=BoundsPen(glyphs);glyphs[name].draw(pen)
        assert pen.bounds is not None
        assert font['hmtx'][name][0]==0
        rows=shape(font,'X'+chr(cp))
        assert len(rows)==2 and rows[1][1]==0 and rows[1][0]!='.notdef'
        assert rows[1][3] != 0


def test_side_parentheses_enclose_the_diacritic_without_an_extra_stack_level(font):
    from fontTools.pens.boundsPen import BoundsPen
    glyphs=font.getGlyphSet()
    for ring,left,right in [(0x30a,0x1ac1,0x1ac2),(0x325,0x1ac3,0x1ac4)]:
        ring_name=font.getBestCmap()[ring]
        p=BoundsPen(glyphs);glyphs[ring_name].draw(p)
        for cp in [left,right]:
            rows=shape(font,'X'+chr(ring)+chr(cp))
            assert rows[1][2:]==rows[2][2:]
            name=font.getBestCmap()[cp]
            q=BoundsPen(glyphs);glyphs[name].draw(q)
            if cp==left: assert q.bounds[2]<p.bounds[0]
            else: assert q.bounds[0]>p.bounds[2]


def test_new_compound_marks_stack_above_and_below(font):
    above=shape(font,'X\u1ac6\u1ad0\u1ae4')
    below=shape(font,'X\u1add\u1ae6\u1aee')
    assert all(r[1]==0 for r in above[1:]+below[1:])
    assert above[1][3]<above[2][3]<above[3][3]
    assert below[1][3]>below[2][3]>below[3][3]
