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
REFERENCES={family:json.loads((ROOT/f'output/font-review/pen-translation/{family}-candidate.json').read_text()) for family in ['office-locks','tools-instruments','places-weather','other-objects','globes','phoenix','air-water','road-infrastructure','ground-vehicles']}
CASES=[(family,e) for family,report in REFERENCES.items() for e in report['flags']]
assert len(CASES)==64


@pytest.fixture(scope='module')
def fonts():
    donors={}
    for family,report in REFERENCES.items():
        path=ROOT/f'output/font-review/pen-translation/{family}-candidate.woff2'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
        donors[family]=TTFont(path)
    return TTFont(FONT),donors


@pytest.mark.parametrize('family,entry',CASES,ids=[family+'-'+e['region'] for family,e in CASES])
def test_final_objects_match_reviewed_art_and_forms(family,entry,fonts):
    font,donors=fonts;donor=donors[family]
    name=font.getBestCmap()[int(entry['region'],16)] if family!='phoenix' else 'phoenix.'+entry['region']
    old=entry['glyphName']
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


def test_all_final_object_adjacencies_preserve_both_forms():
    forms=[text for _,e in CASES for text in e['qualificationForms']]
    assert len(forms)==79
    expected={text:shape(FONT,text,True) for text in forms}
    assert all(len(glyphs)==1 and glyphs[0][0] for glyphs in expected.values())
    for first,a in expected.items():
        for second,b in expected.items():
            for path in [FONT,INK]:assert shape(path,first+second,True)==a+b,(first,second,path)


def test_final_objects_preserve_all_previous_5419_identities_and_positions():
    baseline=json.loads((ROOT/'output/font-review/pen-translation/pre-final-object-integration-shaping.json').read_text())
    assert len(baseline['cases'])==5419
    font=TTFont(FONT)
    for entry in baseline['cases']:
        for path in [FONT,INK]:
            actual=[dict(name=font.getGlyphName(g[0]),position=list(g[1:])) for g in shape(path,entry['text'],True)]
            assert actual==entry['glyphs'],entry['text']


def test_phoenix_only_joins_the_exact_bird_joiner_fire_sequence():
    font=TTFont(FONT)
    for path in [FONT,INK]:
        joined=shape(path,'🐦‍🔥',True)
        assert len(joined)==1 and font.getGlyphName(joined[0][0])=='phoenix.1f426_200d_1f525'
        assert shape(path,'🐦🔥',True)==shape(path,'🐦',True)+shape(path,'🔥',True)
        assert shape(path,'🐦‍🔥🐦‍🔥',True)==joined+joined


def test_promoted_plane_and_rainbow_preserve_their_existing_joined_forms():
    font=TTFont(FONT)
    for cp,name in [(0x2708,'component.2708'),(0x1f308,'flag-component.u1F308')]:
        assert font.getBestCmap()[cp]==name and font['glyf'][name].numberOfContours>0
        manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
        assert cp not in manifest['componentOnly']
    for path in [FONT,INK]:
        for text in ['🏳️‍🌈','🏳‍🌈','🧑‍✈️','👨‍✈️','👩‍✈️','👨🏻‍✈️','👩🏿‍✈️']:
            assert len(shape(path,text,True))==1,text
