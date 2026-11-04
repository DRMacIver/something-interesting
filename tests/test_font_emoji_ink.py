"""Optical ink must shape exactly like the colour font without recolouring it."""
import hashlib,json,sys
from pathlib import Path
from native_sfnt_loader import evidence_ttfont as TTFont
ROOT=Path(__file__).resolve().parents[1]


def test_ink_companion_preserves_every_outline_metric_and_substitution(monkeypatch):
    colour=TTFont(ROOT/'assets/fonts/dad-emoji.woff2')
    path=ROOT/'assets/fonts/dad-emoji-ink.woff2';ink=TTFont(path)
    assert 'COLR' not in ink and 'CPAL' not in ink
    assert ink['name'].getDebugName(1)=='Dad Emoji Ink'
    assert ink.getGlyphOrder()==colour.getGlyphOrder()
    for tag in ['glyf','hmtx','hhea','cmap','GSUB']:
        assert ink.getTableData(tag)==colour.getTableData(tag),tag
    original=path.read_bytes()
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_emoji_ink import build_ink
    result=build_ink()
    assert path.read_bytes()==original
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    assert manifest['companions']==[result]
    assert result['sha256']==hashlib.sha256(original).hexdigest()
