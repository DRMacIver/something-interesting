from font_baseline_checks import pinned_packaging_font
import sys
from pathlib import Path
import json
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from variation_marks import additional_marks


def test_marks_are_added_only_to_a_chunk_with_an_actual_variation_base():
    font=TTFont(ROOT/'build/unicode-sources/wenkai/fonts/TTF/LXGWWenKai-Regular.ttf')
    marks={0x301,0x302,0x307}
    assert marks<=font.getBestCmap().keys()
    assert additional_marks(font,{0x2018},marks)==marks
    assert additional_marks(font,{0x2018,0x301},marks)=={0x302,0x307}
    assert additional_marks(font,{ord('A')},marks)==set()


def test_packaged_marked_variants_preserve_source_glyphs_and_positions():
    from test_font_scripts import shape
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    for text,source_text in [('‘\ufe02\u0301','‘\ufe00\u0301'),('’\ufe02\u0302\u0307','’\ufe00\u0302\u0307'),('㐂\U000e0101\u3099','㐂\U000e0101\u3099')]:
        base,selector=map(ord,list(text)[:2]);points=set(map(ord,text[2:]))
        entry=next(e for e in manifest['fonts'] if any(a<=base<=b for a,b in e.get('nativeVariations',{}).get(str(selector),[])) and all(any(a<=cp<=b for a,b in e['ranges']) for cp in points))
        original=ROOT/entry['source'];path=ROOT/entry['file']
        source,font=TTFont(original),TTFont(path)
        before,after=shape(original,source_text,True),shape(path,text,True)
        assert len(before)==len(after)
        native=pinned_packaging_font(entry)
        gs,actual=source.getGlyphSet(),native.getGlyphSet()
        for a,b in zip(before,after):
            assert a[0] and b[0]
            assert a[1:]==b[1:],text
            pa,pb=DecomposingRecordingPen(gs),DecomposingRecordingPen(actual)
            gs[source.getGlyphName(a[0])].draw(pa);actual[native.getGlyphName(b[0])].draw(pb)
            assert pa.value==pb.value,text
