"""Visible standalone extenders without changing native Arabic font programs."""

from font_baseline_checks import pinned_packaging_font
import json
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.boundsPen import BoundsPen
from test_font_scripts import ROOT,shape


def entries():
    return json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))['fonts']


def test_standalone_kufi_tatweel_has_real_source_ink_and_native_advance():
    entry=next(e for e in entries() if e['source'].endswith('/NotoKufiArabic-Regular.ttf'))
    source=TTFont(ROOT/entry['source']);font=TTFont(ROOT/entry['file'])
    native=pinned_packaging_font(entry)
    a,b=source.getBestCmap()[0x640],font.getBestCmap()[0x640]
    native_name=native.getBestCmap()[0x640]
    pa,pb=DecomposingRecordingPen(source.getGlyphSet()),DecomposingRecordingPen(native.getGlyphSet())
    source.getGlyphSet()[a].draw(pa);native.getGlyphSet()[native_name].draw(pb)
    assert pa.value==pb.value and pa.value
    assert source['hmtx'][a]==native['hmtx'][native_name]==font['hmtx'][b]
    pen=BoundsPen(font.getGlyphSet());font.getGlyphSet()[b].draw(pen)
    assert pen.bounds[2]>pen.bounds[0] and pen.bounds[3]>pen.bounds[1]
    rows=shape(ROOT/entry['file'],'ـ',True)
    assert len(rows)==1 and rows[0][0]>0 and rows[0][1]>0
    assert shape(ROOT/entry['file'],'ـَ')==shape(ROOT/entry['source'],'ـَ')
    for text in ['بـب','بــب','بَـب','ب\u200dـب']:
        assert shape(ROOT/entry['file'],text)==shape(ROOT/entry['source'],text)
    assert sum(r[1] for r in shape(ROOT/entry['file'],'بـب'))>sum(r[1] for r in shape(ROOT/entry['file'],'بب'))


def test_aref_connected_arabic_and_extenders_keep_original_shaping():
    entry=next(e for e in entries() if e['source'].endswith('/ArefRuqaa-Regular.ttf'))
    for text in ['بـب','بــب','بَـب','ب\u200dـب','ب\u061cـب','مرحـبا']:
        assert shape(ROOT/entry['source'],text)==shape(ROOT/entry['file'],text),text
