"""Checks on the built web font: coverage, and that shaping does what the
lettering needs."""

import io
from pathlib import Path

import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont

FONT = Path(__file__).parent.parent / "assets" / "fonts" / "dad-lettering.woff2"


@pytest.fixture(scope="module")
def font():
    return TTFont(FONT)


@pytest.fixture(scope="module")
def shaper(font):
    # HarfBuzz can't read WOFF2 directly, so hand it the decompressed font.
    buffer = io.BytesIO()
    font.flavor = None
    font.save(buffer)
    face = hb.Face(buffer.getvalue())
    return hb.Font(face), font.getGlyphOrder()


def shape(shaper, text):
    hb_font, order = shaper
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb_font, buf, {})
    names = [order[info.codepoint] for info in buf.glyph_infos]
    advances = [pos.x_advance for pos in buf.glyph_positions]
    return names, advances


def base(name):
    return name.split(".alt")[0]


def test_covers_letters_digits_and_punctuation(font):
    cmap = font.getBestCmap()
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?'\"-:;() …–—’“”":
        assert ord(char) in cmap, char


def test_lowercase_uses_the_capitals(font):
    cmap = font.getBestCmap()
    for char in "abcdefghijklmnopqrstuvwxyz":
        assert cmap[ord(char)] == cmap[ord(char.upper())]


@pytest.mark.parametrize("text", ["I", "I'M DONE", "SO I SAID", "AND I.", "i think"])
def test_pronoun_i_has_serifs(shaper, text):
    names, _ = shape(shaper, text)
    assert "I.pronoun" in map(base, names)


@pytest.mark.parametrize("text", ["IS", "HI", "THINK", "IT'S"])
def test_i_inside_words_is_plain(shaper, text):
    names = list(map(base, shape(shaper, text)[0]))
    assert "I.pronoun" not in names
    assert "I" in names


def test_kerning_changes_some_pairs(font, shaper):
    kerned = set()
    for a in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        for b in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            _, advances = shape(shaper, a + b)
            if advances[0] != font["hmtx"][font.getBestCmap()[ord(a)]][0]:
                kerned.add(a + b)
    assert kerned


def test_repeated_letters_use_different_forms(shaper):
    names, _ = shape(shaper, "AAAA")
    assert len(set(names)) == 4


def test_alternates_continue_across_words(shaper):
    names, _ = shape(shaper, "A A")
    assert names[0] != names[2]


def test_alternates_are_kerned_like_the_original(shaper):
    # A plain pair and the same pair in the middle of a word, where both
    # letters are alternates, get the same spacing between them.
    plain, plain_advances = shape(shaper, "AV")
    later, later_advances = shape(shaper, "EAV")
    assert later[1] != plain[0] or later[2] != plain[1]
    font, order = shaper
    assert plain_advances[0] - font.get_glyph_h_advance(order.index(plain[0])) == (
        later_advances[1] - font.get_glyph_h_advance(order.index(later[1]))
    )


def test_slash_is_a_stroke_leaning_right_from_the_baseline_to_cap_height(font):
    # Without its own glyph, the browser letters / in some other font.
    cmap = font.getBestCmap()
    assert ord("/") in cmap
    glyphs = font.getGlyphSet()
    from fontTools.pens.recordingPen import RecordingPen

    pen = RecordingPen()
    glyphs[cmap[ord("/")]].draw(pen)
    points = [p for _, args in pen.value for p in args]
    xs = [x for x, _ in points]
    ys = [y for _, y in points]
    cap = font["OS/2"].sCapHeight
    # From the baseline up to about cap height, not down below the line.
    assert min(ys) > -0.1 * cap
    assert 0.85 * cap < max(ys) < 1.15 * cap
    # Leaning right: the top is further right than the bottom.
    top = [x for x, y in points if y > 0.8 * max(ys)]
    bottom = [x for x, y in points if y < 0.2 * max(ys)]
    assert min(top) > max(bottom) - 0.05 * cap


def test_covers_every_printable_ascii_character(font):
    # Anything missing is lettered in the browser's fallback font instead.
    cmap = font.getBestCmap()
    missing = [chr(c) for c in range(33, 127) if c not in cmap]
    assert not missing, " ".join(missing)


def stroke_weight(font, char):
    """Roughly how thick a glyph's strokes are: twice its ink area over the
    length of its outline (for a long stroke, its width)."""
    from fontTools.pens.areaPen import AreaPen
    from fontTools.pens.perimeterPen import PerimeterPen

    glyphs = font.getGlyphSet()
    glyph = glyphs[font.getBestCmap()[ord(char)]]
    area, perimeter = AreaPen(glyphs), PerimeterPen(glyphs)
    glyph.draw(area)
    glyph.draw(perimeter)
    return 2 * abs(area.value) / perimeter.value


def test_digits_are_no_bolder_than_the_letters(font):
    # The book's few hand-lettered numbers are often in heavier lettering.
    letters = sorted(stroke_weight(font, c) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    typical = letters[len(letters) // 2]
    heavy = {c: round(stroke_weight(font, c)) for c in "0123456789" if stroke_weight(font, c) > 1.1 * typical}
    assert not heavy, f"letters' typical weight is {typical:.0f}: {heavy}"
