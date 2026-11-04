"""Compiled Yangqin signs retain the documented stroke counts and shared base."""
import json
from pathlib import Path
import numpy as np
import pymupdf
from scipy import ndimage
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from test_font_scripts import shape

ROOT = Path(__file__).resolve().parents[1]


def entry(cp):
    manifest = json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    return next(e for e in manifest['fonts'] if 'LXGWWenKai' in e['source']
                and any(a <= cp <= b for a,b in e['ranges']))


def ink(cp):
    font = TTFont(ROOT/entry(cp)['file']); glyphs = font.getGlyphSet()
    pen = SVGPathPen(glyphs); glyphs[font.getBestCmap()[cp]].draw(pen)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000"><rect width="100%" height="100%" fill="white"/><path transform="translate(0 850) scale(1 -1)" d="{pen.getCommands()}"/></svg>'
    doc = pymupdf.open(stream=svg.encode(),filetype='svg')
    pdf = pymupdf.open('pdf',doc.convert_to_pdf()); pix = pdf[0].get_pixmap(alpha=False)
    return np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3).max(axis=2) < 128


def test_yangqin_uprights_cross_and_baseline():
    baseline = ink(0x3026)
    for cp, uprights in [(0x16FF4,2),(0x16FF5,3),(0x16FF6,None)]:
        mask = ink(cp)
        assert np.array_equal(mask[850-340:850-300],baseline[850-340:850-300])
        assert ndimage.label(mask)[1] == 1  # All strokes meet the baseline.
        for y in [450,600,650]:
            assert ndimage.label(mask[850-y])[1] == (uprights or 2)
        assert ndimage.label(mask[850-510])[1] == (uprights or 1)
        shaped = shape(ROOT/entry(cp)['file'],chr(cp),True)
        assert len(shaped) == 1 and shaped[0][0] != 0 and shaped[0][1] == 1000


def test_existing_suzhou_six_is_unchanged():
    e = entry(0x3026)
    drawings = []
    for path in [ROOT/e['source'],ROOT/e['file']]:
        font = TTFont(path); glyphs = font.getGlyphSet()
        pen = DecomposingRecordingPen(glyphs)
        glyphs[font.getBestCmap()[0x3026]].draw(pen)
        drawings.append(pen.value)
    assert drawings[0] == drawings[1]
