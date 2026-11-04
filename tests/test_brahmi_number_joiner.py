"""Number joiner must shape native numeral ligatures, not its isolated carrier."""
import json
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import ROOT, shape


@pytest.mark.parametrize('points', [
    (0x11064, 0x1107F, 0x11053),
    (0x11065, 0x1107F, 0x11054),
])
def test_brahmi_number_joiner_preserves_native_numeric_ligature(points):
    manifest = json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ')[1].rstrip(';\n'))
    entry = next(e for e in manifest['fonts'] if e['source'].endswith('/NotoSansBrahmi-Regular.ttf'))
    source, output = ROOT/entry['source'], ROOT/entry['file']
    text = ''.join(map(chr, points))
    native, current = shape(source, text, True), shape(output, text, True)
    # The pinned source itself must form one native ligature. Different subset
    # glyph IDs are legitimate; advances and placement must remain native.
    assert len(native) == len(current) == 1
    assert native[0][0] and current[0][0]
    assert current[0][1:] == native[0][1:]
    font = TTFont(output)
    diagnostic = font.getGlyphID(font.getBestCmap()[0x1107F])
    assert current[0][0] != diagnostic
