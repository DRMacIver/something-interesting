from font_baseline_checks import pinned_packaging_font
import io
import sys
import json
from pathlib import Path

import uharfbuzz as hb
from native_sfnt_loader import evidence_ttfont as TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from fullwidth_zero import add_fullwidth_zero


def test_fullwidth_variant_preserves_native_zero_shapes_and_em_wide_advance():
    font=TTFont(ROOT/'build/unicode-sources/noto/NotoSansMath-Regular.ttf')
    original_cmap=dict(font.getBestCmap())
    variant=next(name for t in font['cmap'].tables if t.format==14 for cp,name in t.uvsDict[0xfe00] if cp==ord('0'))
    before={name:(list(font['glyf'][name].coordinates),font['hmtx'][name]) for name in [original_cmap[ord('0')],variant]}
    add_fullwidth_zero(font)
    assert {cp:name for cp,name in font.getBestCmap().items() if cp!=0xff10}==original_cmap
    em=font['head'].unitsPerEm
    for old,new in [(original_cmap[ord('0')],'fullwidthZero.default'),(variant,'fullwidthZero.shortDiagonal')]:
        coords,(advance,bearing)=before[old];shift=(em-advance)//2
        assert list(font['glyf'][new].coordinates)==[(x+shift,y) for x,y in coords]
        assert font['hmtx'][new]==(em,bearing+shift)
        assert list(font['glyf'][old].coordinates)==coords
        assert font['hmtx'][old]==(advance,bearing)
    data=io.BytesIO();font.save(data);face=hb.Font(hb.Face(data.getvalue()))
    for text,name in [('０','fullwidthZero.default'),('０\ufe00','fullwidthZero.shortDiagonal')]:
        buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(face,buf)
        assert [g.codepoint for g in buf.glyph_infos]==[font.getGlyphID(name)]
        assert [p.x_advance for p in buf.glyph_positions]==[em]


def test_packaged_fullwidth_variant_retains_translation_and_full_cell_metrics():
    from test_font_scripts import shape
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    entry=next(e for e in manifest['fonts'] if any(a<=0xff10<=b for a,b in e.get('nativeVariations',{}).get('65024',[])))
    assert entry['source'].endswith('/NotoSansMath-Regular.ttf')
    assert any(d['sequence']=='０\ufe00' for d in entry['variationDerivations'])
    font=TTFont(ROOT/entry['file']);source=TTFont(ROOT/entry['source'])
    native=next(n for t in source['cmap'].tables if t.format==14 for cp,n in t.uvsDict[0xfe00] if cp==ord('0'))
    name=next(n for t in font['cmap'].tables if t.format==14 for cp,n in t.uvsDict[0xfe00] if cp==0xff10)
    shift=(source['head'].unitsPerEm-source['hmtx'][native][0])//2
    packaged_native=pinned_packaging_font(entry)
    native_variant=next(n for t in packaged_native['cmap'].tables if t.format==14 for cp,n in t.uvsDict[0xfe00] if cp==0xff10)
    assert list(packaged_native['glyf'][native_variant].coordinates)==[(x+shift,y) for x,y in source['glyf'][native].coordinates]
    assert packaged_native['hmtx'][native_variant]==font['hmtx'][name]
    assert font['hmtx'][name][0]==font['head'].unitsPerEm
    shaped=shape(ROOT/entry['file'],'０\ufe00',True)
    assert shaped==[(font.getGlyphID(name),font['head'].unitsPerEm,0,0,0)]


def test_fullwidth_marks_stack_above_and_below_without_changing_native_stacks(tmp_path):
    from math_mark_checks import assert_accent_geometry
    from test_font_scripts import shape
    source=ROOT/'build/unicode-sources/noto/NotoSansMath-Regular.ttf'
    font=TTFont(source);add_fullwidth_zero(font)
    path=tmp_path/'math.ttf';font.save(path)
    for base in ['０','０\ufe00','0','0\ufe00']:
        assert_accent_geometry(font,path,base)
    # Existing source anchors keep their actual native positions and spacing.
    for base in ['α','x','A']:
        for suffix in ['\u0301','\u0302\u0307','\u0323\u0323']:
            assert shape(path,base+suffix,True)==shape(source,base+suffix,True)
    assert_accent_geometry(font,path,'α',check_center=False)


def test_packaged_fullwidth_accents_have_clear_stacking():
    from math_mark_checks import assert_accent_geometry
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    entry=next(e for e in manifest['fonts'] if any(a<=0xff10<=b for a,b in e.get('nativeVariations',{}).get('65024',[])))
    path=ROOT/entry['file'];font=TTFont(path)
    for base in ['０','０\ufe00']:
        assert_accent_geometry(font,path,base)
