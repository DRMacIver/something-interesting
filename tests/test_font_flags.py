"""Production flag identities, reviewed outlines, aliases and boundaries."""
import json,hashlib
from pathlib import Path
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
FONT=ROOT/'assets/fonts/dad-emoji.woff2'
INK=ROOT/'assets/fonts/dad-emoji-ink.woff2'
CASES=[]
for kind,prefix in [('general','general-flags'),('regional','region-flags')]:
    record=json.loads((ROOT/f'output/font-review/pen-translation/{prefix}-candidate.json').read_text())
    for entry in record['flags']:CASES.append((kind,prefix,entry))
assert len(CASES)==270

@pytest.fixture(scope='module')
def font():return TTFont(FONT)

@pytest.fixture(scope='module')
def references():
    result={}
    for prefix in ['general-flags','region-flags']:
        path=ROOT/f'output/font-review/pen-translation/{prefix}-candidate.woff2'
        report=json.loads(path.with_suffix('.json').read_text())
        assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256']
        result[prefix]=TTFont(path)
    return result

@pytest.mark.parametrize('kind,prefix,entry',CASES,ids=[kind+'-'+e['region'] for kind,_,e in CASES])
def test_flag_matches_reviewed_compiled_layers_and_forms(kind,prefix,entry,font,references):
    donor=references[prefix];name='flag.'+kind+'.'+entry['region'];old=entry['glyphName']
    actual_layers=font['COLR'].ColorLayers[name];expected_layers=donor['COLR'].ColorLayers[old]
    assert len(actual_layers)==len(expected_layers)
    for actual,expected in [(name,old),*[(a.name,b.name) for a,b in zip(actual_layers,expected_layers)]]:
        a=font['glyf'][actual];b=donor['glyf'][expected]
        assert a.numberOfContours==b.numberOfContours
        # Empty layers have no coordinates/endPts attributes after decoding.
        # Compare the complete public outline representation for both empty
        # and nonempty glyphs, including point flags.
        ac,ae,af=a.getCoordinates(font['glyf'])
        bc,be,bf=b.getCoordinates(donor['glyf'])
        assert list(ac)==list(bc)
        assert list(ae)==list(be)
        assert list(af)==list(bf)
        assert font['hmtx'][actual]==donor['hmtx'][expected]
    for a,b in zip(actual_layers,expected_layers):
        ac=font['CPAL'].palettes[0][a.colorID];bc=donor['CPAL'].palettes[0][b.colorID]
        assert (ac.red,ac.green,ac.blue,ac.alpha)==(bc.red,bc.green,bc.blue,bc.alpha)
    canonical=shape(FONT,entry['sequence'],True)
    assert len(canonical)==1 and font.getGlyphName(canonical[0][0])==name
    for text in entry.get('qualificationForms',[entry['sequence']]):
        assert shape(FONT,text,True)==canonical
        assert shape(INK,text,True)==canonical
        assert shape(FONT,'😀'+text+'😀',True)==shape(FONT,'😀',True)+canonical+shape(FONT,'😀',True)


def test_all_flag_adjacencies_preserve_both_sequences():
    forms=[]
    for kind in ['general','regional']:
        spec=json.loads((ROOT/f'data/font-sources/noto-emoji-{kind}-flags-svg.json').read_text())
        forms.extend(t for e in spec['files'] for t in e.get('include_sequences',[]))
    assert len(forms)==276
    expected={t:shape(FONT,t,True) for t in forms}
    assert all(len(g)==1 and g[0][0] for g in expected.values())
    for first,a in expected.items():
        for second,b in expected.items():
            for path in [FONT,INK]:assert shape(path,first+second,True)==a+b,(first,second,path)


def test_flags_do_not_change_any_previous_sequence_identity_or_position(font):
    baseline=json.loads((ROOT/'output/font-review/pen-translation/pre-flags-shaping.json').read_text())
    assert len(baseline['cases'])==5088
    for entry in baseline['cases']:
        for path in [FONT,INK]:
            actual=[dict(name=font.getGlyphName(g[0]),position=list(g[1:])) for g in shape(path,entry['text'],True)]
            assert actual==entry['glyphs'],entry['text']
