import sys
import io
import json
from pathlib import Path

import uharfbuzz as hb
from native_sfnt_loader import evidence_ttfont as TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from sibe_quotes import QUOTES,add_horizontal_sibe_quotes


def test_horizontal_sibe_reuses_exact_narrow_quotes_without_changing_original_uvs():
    font=TTFont(ROOT/'build/unicode-sources/wenkai/fonts/TTF/LXGWWenKai-Regular.ttf')
    original={s:list(rows) for t in font['cmap'].tables if t.format==14 for s,rows in t.uvsDict.items()}
    cmap=dict(font.getBestCmap())
    add_horizontal_sibe_quotes(font)
    tables={s:rows for t in font['cmap'].tables if t.format==14 for s,rows in t.uvsDict.items()}
    assert font.getBestCmap()==cmap
    assert {s:rows for s,rows in tables.items() if s!=0xfe02}==original
    assert dict(tables[0xfe02])=={cp:dict(original[0xfe00])[cp] for cp in QUOTES}
    data=io.BytesIO();font.save(data);face=hb.Font(hb.Face(data.getvalue()))
    def shape(text):
        buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(face,buf)
        return [(g.codepoint,p.x_advance,p.x_offset,p.y_offset) for g,p in zip(buf.glyph_infos,buf.glyph_positions)]
    for cp in QUOTES:
        for before,after in [('', ''),('A','B'),('字','字')]:
            assert shape(before+chr(cp)+'\ufe02'+after)==shape(before+chr(cp)+'\ufe00'+after)


def test_packaged_sibe_aliases_keep_exact_narrow_positions_and_record_horizontal_scope():
    from test_font_scripts import shape
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    for cp in QUOTES:
        entry=next(e for e in manifest['fonts'] if any(a<=cp<=b for a,b in e.get('nativeVariations',{}).get('65026',[])))
        path=ROOT/entry['file']
        assert any(d['sequence']==chr(cp)+'\ufe02' and d['drawingSequence']==chr(cp)+'\ufe00' and 'horizontal' in d['scope'] for d in entry['variationDerivations'])
        for before,after in [('', ''),('A','B'),('字','字')]:
            assert shape(path,before+chr(cp)+'\ufe02'+after,True)==shape(path,before+chr(cp)+'\ufe00'+after,True)
