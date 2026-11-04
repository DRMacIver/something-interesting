"""Production book/mail art, qualifications and previous shaping identities."""
import hashlib
import json
from pathlib import Path
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape

ROOT=Path(__file__).resolve().parents[1]
FONT=ROOT/'assets/fonts/dad-emoji.woff2'
INK=ROOT/'assets/fonts/dad-emoji-ink.woff2'
CANDIDATE=ROOT/'output/font-review/pen-translation/book-mail-candidate.woff2'
REFERENCE=json.loads(CANDIDATE.with_suffix('.json').read_text())
assert len(REFERENCE['flags'])==30


@pytest.fixture(scope='module')
def fonts():
    assert hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()==REFERENCE['sha256']
    return TTFont(FONT),TTFont(CANDIDATE)


@pytest.mark.parametrize('entry',REFERENCE['flags'],ids=[e['region'] for e in REFERENCE['flags']])
def test_book_mail_matches_reviewed_font_and_qualification_forms(entry,fonts):
    font,donor=fonts
    name='book-mail.'+entry['region'];old=entry['glyphName']
    actual_layers=font['COLR'].ColorLayers[name]
    expected_layers=donor['COLR'].ColorLayers[old]
    assert len(actual_layers)==len(expected_layers)
    for actual,expected in [(name,old),*[(a.name,b.name) for a,b in zip(actual_layers,expected_layers)]]:
        a=font['glyf'][actual];b=donor['glyf'][expected]
        assert a.numberOfContours==b.numberOfContours
        ac,ae,af=a.getCoordinates(font['glyf']);bc,be,bf=b.getCoordinates(donor['glyf'])
        assert (list(ac),list(ae),list(af))==(list(bc),list(be),list(bf))
        assert font['hmtx'][actual]==donor['hmtx'][expected]
    for a,b in zip(actual_layers,expected_layers):
        ac=font['CPAL'].palettes[0][a.colorID];bc=donor['CPAL'].palettes[0][b.colorID]
        assert (ac.red,ac.green,ac.blue,ac.alpha)==(bc.red,bc.green,bc.blue,bc.alpha)
    canonical=shape(FONT,entry['sequence'],True)
    assert len(canonical)==1 and font.getGlyphName(canonical[0][0])==name
    for text in entry['qualificationForms']:
        assert shape(FONT,text,True)==canonical
        assert shape(INK,text,True)==canonical
        assert shape(FONT,'😀'+text+'😀',True)==shape(FONT,'😀',True)+canonical+shape(FONT,'😀',True)


def test_every_book_mail_adjacency_preserves_both_glyphs():
    forms=[text for e in REFERENCE['flags'] for text in e['qualificationForms']]
    assert len(forms)==34
    expected={text:shape(FONT,text,True) for text in forms}
    assert all(len(glyphs)==1 and glyphs[0][0] for glyphs in expected.values())
    for first,a in expected.items():
        for second,b in expected.items():
            for path in [FONT,INK]:assert shape(path,first+second,True)==a+b,(first,second,path)


def test_book_mail_does_not_change_previous_5364_identities_or_positions():
    baseline=json.loads((ROOT/'output/font-review/pen-translation/pre-book-mail-shaping.json').read_text())
    assert len(baseline['cases'])==5364
    font=TTFont(FONT)
    for entry in baseline['cases']:
        for path in [FONT,INK]:
            actual=[dict(name=font.getGlyphName(g[0]),position=list(g[1:])) for g in shape(path,entry['text'],True)]
            assert actual==entry['glyphs'],entry['text']
