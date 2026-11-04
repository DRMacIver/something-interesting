from fontTools.pens.ttGlyphPen import TTGlyphPen
import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/font'))
from optical_anchors import accent_centres


def polygon(points):
    pen = TTGlyphPen(None)
    pen.moveTo(points[0])
    for point in points[1:]:
        pen.lineTo(point)
    pen.closePath()
    glyph = pen.glyph()
    return SimpleNamespace(draw=lambda target: glyph.draw(target, {}))


def test_accents_follow_the_lean_in_opposite_directions_above_and_below():
    glyph = polygon([(0, 0), (400, 0), (200, 700), (-200, 700)])
    above, below = accent_centres(glyph, {}, (-200, 0, 400, 700))
    assert above < 100 < below
    assert (above, below) == (20, 180)


def test_upright_letters_keep_the_same_centre():
    glyph = polygon([(0, 0), (400, 0), (400, 700), (0, 700)])
    assert accent_centres(glyph, {}, (0, 0, 400, 700)) == (200, 200)
