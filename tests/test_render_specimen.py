"""Offline review artifacts must contain native shaped ink, not font fallback."""
import importlib.util
import io
import json
from pathlib import Path

from PIL import Image
import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('render_specimen',ROOT/'tools/font/render_specimen.py')
renderer = importlib.util.module_from_spec(spec); spec.loader.exec_module(renderer)


def test_woff2_and_native_arabic_positions_match_independent_sfnt_shaping():
    manifest = json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ')[1].rstrip(';\n'))
    f = next(f for f in manifest['fonts'] if f['source'].endswith('/ArefRuqaa-Regular.ttf'))
    path = ROOT/f['file']; text = 'مَرْحَبًا'
    actual = renderer.Font(path).shape(text,22)
    source = TTFont(path); source.flavor = None
    stream = io.BytesIO(); source.save(stream)
    face = hb.Face(stream.getvalue()); assert face.glyph_count > 0
    buffer = hb.Buffer(); buffer.add_str(text); buffer.guess_segment_properties()
    hb.shape(hb.Font(face),buffer)
    assert actual['direction'] == 'rtl'
    assert actual['glyphs'] == [dict(name=source.getGlyphName(g.codepoint),gid=g.codepoint,cluster=g.cluster,
        advance=[p.x_advance,p.y_advance],offset=[p.x_offset,p.y_offset])
        for g,p in zip(buffer.glyph_infos,buffer.glyph_positions)]
    assert len(actual['paths']) > 0 and actual['bounds'][3] > actual['bounds'][1]


def test_real_png_svg_json_and_colour_layers(tmp_path):
    path = ROOT/'assets/fonts/dad-emoji.woff2'
    f = renderer.Font(path)
    assert f.hb.face.glyph_count > 0
    shaped = f.shape('💙',44)
    assert shaped['paths'] and shaped['bounds'][2] > shaped['bounds'][0]
    astronaut = f.shape('👩🏽‍🚀',44)
    assert len(astronaut['glyphs']) == 1 and len(astronaut['paths']) > 1
    report = renderer.render([{'label':'BLUE HEART','font':str(path),'text':'💙'}],tmp_path/'review')
    img = Image.open(tmp_path/'review.png').convert('RGB')
    assert img.size == (report['width'],report['height'])
    pixels = list(img.get_flattened_data())
    assert any(b > r+20 and b > g for r,g,b in pixels), 'meaningful blue must survive COLR expansion'
    assert any(min(rgb) < 80 for rgb in pixels), 'outlined ink must be present'
    assert '<text' not in (tmp_path/'review.svg').read_text(), 'SVG must not depend on host fonts'
    record = json.loads((tmp_path/'review.json').read_text())
    assert record['samples'][0]['runs'][0]['sha256'] == f.sha256
    assert record['limitations']


def test_tall_marks_have_unclipped_image_padding(tmp_path):
    f = ROOT/'assets/fonts/dad-lettering-unicode.woff2'
    renderer.render([{'label':'MARKS','font':str(f),'text':'A\u0301\u0302\u0303\u0323'}],tmp_path/'marks')
    img = Image.open(tmp_path/'marks.png').convert('RGB')
    # All painted ink, including headings and rules, has padding on every edge.
    assert all(pixel == (255,255,255) for pixel in img.crop((0,0,img.width,8)).get_flattened_data())
    assert all(pixel == (255,255,255) for pixel in img.crop((0,img.height-8,img.width,img.height)).get_flattened_data())
    assert all(pixel == (255,255,255) for pixel in img.crop((0,0,8,img.height)).get_flattened_data())


def test_missing_glyph_fails_without_fallback(tmp_path):
    with pytest.raises(ValueError,match='Missing shaped glyph'):
        renderer.render([{'font':str(ROOT/'assets/fonts/dad-lettering-unicode.woff2'),'text':'\U0010ffff'}],tmp_path/'missing')
    assert not (tmp_path/'missing.png').exists()


def test_atlas_uses_project_graphemes_and_aliases():
    samples = renderer.atlas_samples(1)
    assert len(samples) == 12
    assert ''.join(r['text'] for r in samples[0]['runs']) == 'مرحبا بالعالم'
    assert all(Path(renderer.local_path(r['font'])).is_file() for s in samples for r in s['runs'])
    with pytest.raises(ValueError,match='Atlas page'):
        renderer.atlas_samples(0)
