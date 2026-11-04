"""Structural identity and shared cell geometry for the custom grid font."""
import hashlib
import json
import re
import importlib.util
from pathlib import Path
from native_sfnt_loader import evidence_ttfont as TTFont
import pytest
ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT/'assets/fonts/dad-grid.woff2'

@pytest.fixture(scope='module')
def font(): return TTFont(PATH)


def test_complete_grid_inventory_and_cell_bounds(font):
    cmap = font.getBestCmap()
    source = json.loads((ROOT/'data/font-sources/unicodia.json').read_text())
    legacy = next(e for e in source['files'] if e.get('build_target')=='grid')
    expected = {cp for a,b in legacy['include_ranges'] for cp in range(a,b+1)}
    assert len(expected) == 901
    assert set(cmap) == set(range(0x2500,0x25a0)) | set(range(0x2800,0x2900)) | expected
    for cp, name in cmap.items():
        glyph = font['glyf'][name]
        assert font['hmtx'][name][0] == 600
        if cp == 0x2800:
            assert glyph.numberOfContours == 0
        else:
            assert glyph.numberOfContours > 0
            assert 0 <= glyph.xMin < glyph.xMax <= 600
            assert -200 <= glyph.yMin < glyph.yMax <= 800
            assert font['hmtx'][name][1] == glyph.xMin


def test_braille_all_256_patterns_have_the_exact_named_dots(font):
    # Unicode dot numbers, including 7/8 below the usual six-dot cell.
    expected = [(185,650),(185,420),(185,190),(415,650),(415,420),(415,190),(185,-40),(415,-40)]
    for mask in range(256):
        glyph = font['glyf'][font.getBestCmap()[0x2800+mask]]
        assert glyph.numberOfContours == mask.bit_count()
        if not mask: continue
        coordinates, ends, _ = glyph.getCoordinates(font['glyf'])
        centres=[]; start=0
        for end in ends:
            xs,ys=zip(*coordinates[start:end+1]);start=end+1
            centres.append(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2))
        dots=[point for bit,point in enumerate(expected) if mask & (1<<bit)]
        for actual, point in zip(centres,dots,strict=True):
            assert actual == pytest.approx(point,abs=2)


def test_blocks_retain_exact_fractions_and_box_lines_reach_cell_edges(font):
    def bounds(cp):
        g=font['glyf'][font.getBestCmap()[cp]]
        return g.xMin,g.yMin,g.xMax,g.yMax
    assert bounds(0x2588) == (0,-200,600,800)
    assert bounds(0x2580) == pytest.approx((0,300,600,800),abs=1)
    assert bounds(0x2584) == pytest.approx((0,-200,600,300),abs=1)
    assert bounds(0x258c) == (0,-200,300,800)
    for cp in (0x2500,0x2501,0x2550):
        x0,_,x1,_=bounds(cp); assert (x0,x1)==(0,600)
    for cp in (0x2502,0x2503,0x2551):
        _,y0,_,y1=bounds(cp); assert (y0,y1)==(-200,800)
    light=bounds(0x2500);heavy=bounds(0x2501)
    assert heavy[3]-heavy[1] > 1.5*(light[3]-light[1])


def test_grid_build_is_reproducible_and_retains_licence():
    spec=importlib.util.spec_from_file_location('build_grid',ROOT/'tools/font/build_grid.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    before=hashlib.sha256(PATH.read_bytes()).hexdigest()
    module.build()
    assert hashlib.sha256(PATH.read_bytes()).hexdigest()==before
    font=TTFont(PATH)
    assert font['name'].getDebugName(1)=='Dad Grid'
    assert 'Open Font License' in font['name'].getDebugName(13)


def test_all_named_mosaic_patterns_have_exactly_the_requested_cells(font):
    from fontTools.pens.pointInsidePen import PointInsidePen
    glyphs = font.getGlyphSet()
    checked = 0
    for line in (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines():
        fields = line.split(';')
        match = re.fullmatch(r'(SEPARATED )?BLOCK (QUADRANT|SEXTANT|OCTANT)-([1-8]+)', fields[1])
        if not match: continue
        cp = int(fields[0],16)
        rows = {'QUADRANT':2,'SEXTANT':3,'OCTANT':4}[match[2]]
        bits = set(map(int,match[3]))
        for cell in range(1,rows*2+1):
            row,col = divmod(cell-1,2)
            center = (150+col*300,800-(row+0.5)*1000/rows)
            pen = PointInsidePen(glyphs,center)
            glyphs[font.getBestCmap()[cp]].draw(pen)
            assert pen.getResult() == (cell in bits), (hex(cp),cell)
        checked += 1
    assert checked == 368


def test_separated_full_blocks_retain_gutters(font):
    from fontTools.pens.pointInsidePen import PointInsidePen
    glyphs = font.getGlyphSet()
    # Complete separated quadrant pattern: centre is a gutter, all quarters ink.
    glyph = glyphs[font.getBestCmap()[0x1cc2f]]
    for point, expected in [((300,300),False),((150,550),True),((450,50),True)]:
        pen=PointInsidePen(glyphs,point);glyph.draw(pen)
        assert pen.getResult() == expected


def test_sixteenth_blocks_have_the_correct_fraction_and_position(font):
    for i,cp in enumerate(range(0x1ce90,0x1cea0)):
        row,col=divmod(i,4)
        g=font['glyf'][font.getBestCmap()[cp]]
        assert (g.xMin,g.yMin,g.xMax,g.yMax) == pytest.approx(
            (col*150,800-(row+1)*250,(col+1)*150,800-row*250),abs=1)


def test_legacy_expansion_distinguishes_joining_parts_and_excludes_nonstandard_emoji(font):
    manifest=json.loads((ROOT/'js/grid-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    structural={cp for a,b in manifest['structuralRanges'] for cp in range(a,b+1)}
    cmap=font.getBestCmap()
    for cp in [0x1cc05,0x1cc30,0x1cca6,0x1ccb2,0x1cde6,0x1fbe0]:assert cp in structural
    for cp in [0x1cc00,0x1cc4a,0x1cc92,0x1ccd6,0x1f8b2]:
        assert cp in cmap and cp not in structural
    # Upstream documents its U+1F934 as an unencoded Prince emblem, not the emoji.
    for cp in [0x1f934,0x1f34e,0x1f34f,0x23eb,0x23ec]:assert cp not in cmap
