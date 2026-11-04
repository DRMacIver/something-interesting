"""Promoted components must preserve all previous flags and person variants."""
import hashlib
import json

import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import ROOT,shape

FONT=ROOT/'assets/fonts/dad-emoji.woff2'
INK=ROOT/'assets/fonts/dad-emoji-ink.woff2'
FOLDER=ROOT/'output/font-review/pen-translation'
REPORT=json.loads((FOLDER/'standalone-components-candidate.json').read_text())


@pytest.fixture(scope='module')
def fonts():
    path=FOLDER/'standalone-components-candidate.woff2'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==REPORT['sha256']
    return TTFont(FONT),TTFont(path)


@pytest.mark.parametrize('entry',REPORT['flags'],ids=[r['region'] for r in REPORT['flags']])
def test_promoted_singletons_match_reviewed_fallback_layers_and_metrics(entry,fonts):
    font,donor=fonts
    cp=int(entry['region'],16);name=font.getBestCmap()[cp];old=entry['glyphName']
    expected=donor['COLR'].ColorLayers[old];actual=font['COLR'].ColorLayers[name]
    assert len(actual)==len(expected)
    for a,b in [(name,old),*[(a.name,b.name) for a,b in zip(actual,expected)]]:
        ga,gb=font['glyf'][a],donor['glyf'][b]
        ac,ae,af=ga.getCoordinates(font['glyf']);bc,be,bf=gb.getCoordinates(donor['glyf'])
        assert (list(ac),list(ae),list(af))==(list(bc),list(be),list(bf))
        assert font['hmtx'][a]==donor['hmtx'][b]
    for a,b in zip(actual,expected):
        ca,cb=font['CPAL'].palettes[0][a.colorID],donor['CPAL'].palettes[0][b.colorID]
        assert (ca.red,ca.green,ca.blue)==(cb.red,cb.green,cb.blue)
    for path in [FONT,INK]:
        shaped=shape(path,chr(cp),True)
        assert len(shaped)==1 and font.getGlyphName(shaped[0][0])==name
        assert shaped[0][1]>0


def test_every_previous_5498_form_keeps_named_glyphs_and_all_positions(fonts):
    font,_=fonts
    baseline=json.loads((FOLDER/'pre-standalone-component-integration-shaping.json').read_text())
    assert len(baseline['cases'])==5498
    for entry in baseline['cases']:
        for path in [FONT,INK]:
            actual=[dict(name=font.getGlyphName(g[0]),position=list(g[1:])) for g in shape(path,entry['text'],True)]
            assert actual==entry['glyphs'],(entry['text'],path)


def test_all_35_promotions_are_advertised_and_not_invisible_components():
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    points={int(e['region'],16) for e in REPORT['flags']}
    assert len(points)==35 and not points.intersection(manifest['componentOnly'])
    assert {chr(cp) for cp in points}<=set(manifest['sequences'])
    assert len(manifest['sequences'])==5533
    review=json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    actual={int(e['codepoint'][2:],16) for e in review['glyphs'] if e.get('category')=='standalone_components'}
    assert actual==points
