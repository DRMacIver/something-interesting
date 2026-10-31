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
    assert "I.pronoun" in names


@pytest.mark.parametrize("text", ["IS", "HI", "THINK", "IT'S"])
def test_i_inside_words_is_plain(shaper, text):
    names, _ = shape(shaper, text)
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
