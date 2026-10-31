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
