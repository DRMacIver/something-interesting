"""Optical size must scale native fields uniformly, including mark positions."""
import io
import sys
from pathlib import Path

import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/font'))
from source_optics import apply


def shaped(font, text):
    font.flavor = None
    stream = io.BytesIO(); font.save(stream)
    hfont = hb.Font(hb.Face(stream.getvalue()))
    buffer = hb.Buffer(); buffer.add_str(text); buffer.guess_segment_properties()
    hb.shape(hfont, buffer)
    return [(g.codepoint,p.x_advance,p.y_advance,p.x_offset,p.y_offset)
            for g,p in zip(buffer.glyph_infos,buffer.glyph_positions)]


@pytest.mark.parametrize('path,text,expected_scale',[
    ('assets/fonts/scripts/b8ef0ccbaaf6.woff2','مَرْحَبًا بالعالم',1.16),
    ('assets/fonts/scripts/0c8e6a663cf0.woff2','세상은 신기한 일로 가득해요',1.16),
    ('assets/fonts/scripts/4eec163ff41b.woff2','\U00011db4\u0324\u0303\U00011dd9',1.10),
    ('assets/fonts/scripts/7d309b636746.woff2','𐽰𐽱𐽲𐽳 𐽴𐽵𐽶',1.35),
])
def test_optical_em_keeps_native_shaping_and_design_geometry(path,text,expected_scale):
    import json
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ')[1].rstrip(';\n'))
    entry=next(e for e in manifest['fonts'] if e['file']==path)
    f=TTFont(ROOT/path,recalcTimestamp=False)
    # Exercise a fresh derivative rather than applying the production recipe twice.
    if entry.get('opticalSize'):
        f['head'].unitsPerEm=entry['opticalSize']['originalUnitsPerEm']
    before=shaped(f,text)
    tables={tag:f[tag].compile(f) for tag in ('glyf','hmtx','GSUB','GPOS') if tag in f}
    original=f['head'].unitsPerEm
    record=apply(f,entry['source'])
    assert all(g[0] for g in before)
    assert shaped(f,text)==before, 'native joins, mark offsets and advance ratios must survive'
    assert abs(original/f['head'].unitsPerEm-expected_scale)<.002
    assert record['scale']==original/f['head'].unitsPerEm
    assert all(f[tag].compile(f)==data for tag,data in tables.items())


def test_unreviewed_source_is_unchanged():
    f=TTFont(ROOT/'assets/fonts/dad-lettering-unicode.woff2')
    original=f['head'].unitsPerEm
    assert apply(f,'Unknown.ttf') is None
    assert f['head'].unitsPerEm==original
