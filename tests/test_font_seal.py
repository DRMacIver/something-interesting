"""Seal mapping checks are separate from visual/linguistic review."""
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'build/unicode-sources/kaiyuan'


def test_every_built_seal_has_matching_source_identity_and_nonempty_outline():
    rows = {int(r['codepoint'],16):r for r in csv.DictReader((SOURCE/'data/provenance/glyphs.csv').open()) if r['codepoint']}
    refs = {}
    for line in (ROOT/'data/unicode/18.0.0/SealSources.txt').read_text().splitlines():
        if '\tkSEAL_CCZSrc\t' in line:
            cp,_,seq = line.split('\t')
            refs[int(cp[2:],16)] = seq
    font = TTFont(SOURCE/'DadSealSource-Regular.ttf')
    cmap = font.getBestCmap()
    report = json.loads((ROOT/'docs/seal-source-review.json').read_text())
    assert len(cmap) == report['mapped']
    assert sum(report['source_review_status'].values()) == len(cmap)
    for cp in [0x3F2B9, 0x3F2BA, 0x3F218, 0x3EEB1, 0x3EFC6, 0x3E25D, 0x3E4E9, 0x3E69A, 0x3EEB3, 0x3EEB6]:
        assert cp not in cmap
        assert any(r['codepoint'] == f'{cp:05X}' and 'crop' in r['reason']
                   for r in report['rejected'])
    for cp,name in cmap.items():
        assert rows[cp]['sequence'] == refs[cp]
        assert rows[cp]['status'] in {'approved','manual','aligned'}
        assert font.getGlyphID(name) != 0
        assert font['glyf'][name].numberOfContours > 0
        svg = ET.fromstring((SOURCE/'glyphs'/f'u{cp:05X}.svg').read_text())
        assert svg.get('data-source') == 'ccz '+refs[cp]


@pytest.mark.parametrize('cp',[0x3D000,0x3D002,0x3D003,0x3D004])
def test_svg_to_font_conversion_preserves_sign_extents(cp):
    font = TTFont(SOURCE/'DadSealSource-Regular.ttf')
    glyphs = font.getGlyphSet()
    name = font.getBestCmap()[cp]
    actual = BoundsPen(glyphs)
    glyphs[name].draw(actual)
    source = BoundsPen(None)
    svg = ET.fromstring((SOURCE/'glyphs'/f'u{cp:05X}.svg').read_text())
    for item in svg.findall('{http://www.w3.org/2000/svg}path'):
        parse_path(item.attrib['d'],TransformPen(source,(1,0,0,-1,0,0)))
    assert actual.bounds == pytest.approx(source.bounds, abs=1.5)
