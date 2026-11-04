"""Holding-hands ligatures retain both people's tones, contours and boundaries."""
import json
from pathlib import Path
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'

@pytest.fixture(scope='module')
def font(): return TTFont(PATH)

@pytest.mark.parametrize('key',['1f9d1_200d_1f91d_200d_1f9d1','1f46d','1f46b','1f46c'])
def test_compiled_holding_hands_geometry_and_tone_pairs(key,font,monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_holding_hands import holding_forms,tone_pair
    from emoji_holding_hands_svg import prepare
    from build_emoji import outline
    masks,report=prepare(key)
    white,left,right,ink=masks
    assert not report['fallback'] and report['appliedStrength']>0
    assert not np.any(left&right)
    ys,xs=np.nonzero(white)
    transform=xs.min(),ys.min(),760/max(np.ptp(xs)+1,np.ptp(ys)+1)
    name='holding-hands.'+key
    for suffix,mask in zip(['white','left','right','ink'],masks):
        expected=outline(mask,transform);actual=font['glyf'][name+'.'+suffix]
        assert tuple(actual.coordinates)==tuple(expected.coordinates)
        assert actual.endPtsOfContours==expected.endPtsOfContours
    expected=outline(ink,transform)
    assert expected.numberOfContours==report['sourceComponents']+report['sourceHoles']
    skin=json.loads((ROOT/'output/imagegen/emoji-production/skin-palette-source.json').read_text())['skinTones']
    forms=holding_forms(ROOT)[key]
    assert len(forms)==26 and set(forms)==set(report['source']['include_sequences'])
    seen=set()
    for text in forms:
        a,b=tone_pair(text);variant=name+(f'.tones{a}{b}' if a else '')
        result=shape(PATH,text,True)
        assert len(result)==1 and result[0][1]>0
        assert font.getGlyphName(result[0][0])==variant
        seen.add(variant)
        actual=font['glyf'][variant]
        assert tuple(actual.coordinates)==tuple(expected.coordinates)
        assert actual.endPtsOfContours==expected.endPtsOfContours
        wanted=[(name+'.white',(255,255,255))]
        if a: wanted += [(name+'.left',tuple(skin[a-1])),(name+'.right',tuple(skin[b-1]))]
        wanted += [(name+'.ink',(17,17,17))]
        layers=font['COLR'].ColorLayers[variant]
        assert len(layers)==len(wanted)
        for layer,(layername,rgb) in zip(layers,wanted):
            assert layer.name==layername
            c=font['CPAL'].palettes[0][layer.colorID]
            assert (c.red,c.green,c.blue)==rgb and c.alpha==255
        for path in [PATH,ROOT/'assets/fonts/dad-emoji-ink.woff2']:
            assert shape(path,text,True)==result
            assert shape(path,text+text,True)==result+result
            assert shape(path,'🧑🏻'+text+'👩🏿',True)==shape(path,'🧑🏻',True)+result+shape(path,'👩🏿',True)
    assert len(seen)==26
