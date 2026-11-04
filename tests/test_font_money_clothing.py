"""Reviewed money/accessory art and preservation of previous production forms."""
import hashlib
import json
from pathlib import Path
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape

ROOT=Path(__file__).resolve().parents[1]
FONT=ROOT/'assets/fonts/dad-emoji.woff2'
INK=ROOT/'assets/fonts/dad-emoji-ink.woff2'
REFERENCES={family:json.loads((ROOT/f'output/font-review/pen-translation/{family}-candidate.json').read_text()) for family in ['money','clothing']}
CASES=[(family,e) for family,report in REFERENCES.items() for e in report['flags']]
assert len(CASES)==19


@pytest.fixture(scope='module')
def fonts():
    donors={}
    for family,report in REFERENCES.items():
        path=ROOT/f'output/font-review/pen-translation/{family}-candidate.woff2'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
        donors[family]=TTFont(path)
    return TTFont(FONT),donors


@pytest.mark.parametrize('family,entry',CASES,ids=[family+'-'+e['region'] for family,e in CASES])
def test_money_clothing_matches_reviewed_art_and_forms(family,entry,fonts):
    font,donors=fonts;donor=donors[family]
    name=family+'.'+entry['region'];old=entry['glyphName']
    actual=font['COLR'].ColorLayers[name];expected=donor['COLR'].ColorLayers[old]
    assert len(actual)==len(expected)
    for a_name,b_name in [(name,old),*[(a.name,b.name) for a,b in zip(actual,expected)]]:
        a=font['glyf'][a_name];b=donor['glyf'][b_name]
        assert a.numberOfContours==b.numberOfContours
        ac,ae,af=a.getCoordinates(font['glyf']);bc,be,bf=b.getCoordinates(donor['glyf'])
        assert (list(ac),list(ae),list(af))==(list(bc),list(be),list(bf))
        assert font['hmtx'][a_name]==donor['hmtx'][b_name]
    for a,b in zip(actual,expected):
        ac=font['CPAL'].palettes[0][a.colorID];bc=donor['CPAL'].palettes[0][b.colorID]
        assert (ac.red,ac.green,ac.blue,ac.alpha)==(bc.red,bc.green,bc.blue,bc.alpha)
    canonical=shape(FONT,entry['sequence'],True)
    assert len(canonical)==1 and font.getGlyphName(canonical[0][0])==name
    for text in entry['qualificationForms']:
        assert shape(FONT,text,True)==canonical
        assert shape(INK,text,True)==canonical
        assert shape(FONT,'😀'+text+'😀',True)==shape(FONT,'😀',True)+canonical+shape(FONT,'😀',True)


def test_all_money_clothing_adjacencies_preserve_both_forms():
    forms=[text for _,e in CASES for text in e['qualificationForms']]
    assert len(forms)==21
    expected={text:shape(FONT,text,True) for text in forms}
    assert all(len(glyphs)==1 and glyphs[0][0] for glyphs in expected.values())
    for first,a in expected.items():
        for second,b in expected.items():
            for path in [FONT,INK]:assert shape(path,first+second,True)==a+b,(first,second,path)


def test_money_clothing_preserves_all_previous_5398_identities_and_positions():
    baseline=json.loads((ROOT/'output/font-review/pen-translation/pre-object-expansion-shaping.json').read_text())
    assert len(baseline['cases'])==5398
    font=TTFont(FONT)
    for entry in baseline['cases']:
        for path in [FONT,INK]:
            actual=[dict(name=font.getGlyphName(g[0]),position=list(g[1:])) for g in shape(path,entry['text'],True)]
            assert actual==entry['glyphs'],entry['text']
