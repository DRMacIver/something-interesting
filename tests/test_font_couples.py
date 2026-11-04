"""Couple ligatures retain both people's tones, contours and boundaries."""
import hashlib,json
from pathlib import Path
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'

@pytest.fixture(scope='module')
def font(): return TTFont(PATH)

@pytest.mark.parametrize('key',['1f48f', '1f469_200d_2764_200d_1f48b_200d_1f468', '1f468_200d_2764_200d_1f48b_200d_1f468', '1f469_200d_2764_200d_1f48b_200d_1f469', '1f491', '1f469_200d_2764_200d_1f468', '1f468_200d_2764_200d_1f468', '1f469_200d_2764_200d_1f469'])
def test_compiled_couples_geometry_and_tone_pairs(key,font,monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_couples import couple_forms,tone_pair
    from emoji_couples_svg import prepare
    from build_emoji import outline
    masks,report=prepare(key)
    assert hashlib.sha256((ROOT/report['heartPaletteSource']).read_bytes()).hexdigest()==report['heartPaletteSha256']
    white,*materials,ink=masks
    regions=dict(zip(report['colourNames'],materials));left,right,red=(regions[k] for k in ['left','right','red'])
    assert not report['fallback'] and report['appliedStrength']>0
    assert not np.any(left&right)
    ys,xs=np.nonzero(white)
    transform=xs.min(),ys.min(),760/max(np.ptp(xs)+1,np.ptp(ys)+1)
    name='couples.'+key
    for suffix,mask in [('white',white),*regions.items(),('ink',ink)]:
        expected=outline(mask,transform);actual=font['glyf'][name+'.'+suffix]
        assert tuple(actual.coordinates)==tuple(expected.coordinates)
        assert actual.endPtsOfContours==expected.endPtsOfContours
    expected=outline(ink,transform)
    assert expected.numberOfContours==report['sourceComponents']+report['sourceHoles']
    skin=json.loads((ROOT/'output/imagegen/emoji-production/skin-palette-source.json').read_text())['skinTones']
    forms=couple_forms(ROOT)[key]
    assert len(forms)==(46 if key in {'1f48f','1f491'} else 52) and set(forms)==set(report['source']['include_sequences'])
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
        wanted += [(name+'.red',tuple(report['rgbs'][report['colourNames'].index('red')])),(name+'.ink',(17,17,17))]
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


def test_entire_rgi_family_subgroup_is_custom_and_shapes_as_one(font):
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    required=[];subgroup=None
    for line in (ROOT/'data/unicode/18.0.0/emoji/emoji-test.txt').read_text().splitlines():
        if line.startswith('# subgroup: '):subgroup=line.split(': ',1)[1]
        if subgroup=='family' and '; fully-qualified' in line:
            required.append(''.join(chr(int(cp,16)) for cp in line.split(';')[0].split()))
    assert len(required)==337 and set(required)<=set(manifest['sequences'])
    for text in required:
        result=shape(PATH,text,True)
        assert len(result)==1 and result[0][0]>0 and result[0][1]>0
        assert font['glyf'][font.getGlyphName(result[0][0])].numberOfContours>0
