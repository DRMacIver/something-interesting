"""Compiled expression identities, semantic colours and joined sequences."""
from pathlib import Path
import hashlib,importlib,json
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
SOURCES=json.loads((ROOT/'data/font-sources/noto-emoji-family-tiles-svg.json').read_text())['files']
CASES=[(key,'emoji_family_tiles_svg') for key in ['1f468_200d_1f469_200d_1f466', '1f468_200d_1f469_200d_1f467', '1f468_200d_1f469_200d_1f467_200d_1f466', '1f468_200d_1f469_200d_1f466_200d_1f466', '1f468_200d_1f469_200d_1f467_200d_1f467', '1f468_200d_1f468_200d_1f466', '1f468_200d_1f468_200d_1f467', '1f468_200d_1f468_200d_1f467_200d_1f466', '1f468_200d_1f468_200d_1f466_200d_1f466', '1f468_200d_1f468_200d_1f467_200d_1f467', '1f469_200d_1f469_200d_1f466', '1f469_200d_1f469_200d_1f467', '1f469_200d_1f469_200d_1f467_200d_1f466', '1f469_200d_1f469_200d_1f466_200d_1f466', '1f469_200d_1f469_200d_1f467_200d_1f467', '1f468_200d_1f466', '1f468_200d_1f466_200d_1f466', '1f468_200d_1f467', '1f468_200d_1f467_200d_1f466', '1f468_200d_1f467_200d_1f467', '1f469_200d_1f466', '1f469_200d_1f466_200d_1f466', '1f469_200d_1f467', '1f469_200d_1f467_200d_1f466', '1f469_200d_1f467_200d_1f467']]
assert len(CASES)==len(SOURCES)==25

@pytest.fixture(scope='module')
def font():return TTFont(PATH)

@pytest.mark.parametrize('key,module_name',CASES)
def test_compiled_family_tile_matches_reviewed_source(key,module_name,font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from build_emoji import outline
 from emoji_sequences import qualified_forms
 module=importlib.import_module(module_name);(white,*colours,ink),r=module.prepare(key)
 canonical=''.join(chr(int(cp,16)) for cp in key.split('_'))
 name='family-tile.'+key
 if len(canonical)==1:assert font.getBestCmap()[ord(canonical)]==name
 assert r['appliedStrength']>0 and not r['fallback']
 assert font['glyf'][name].numberOfContours==r['sourceComponents']+r['sourceHoles']
 ys,xs=np.nonzero(white);transform=xs.min(),ys.min(),760/max(np.ptp(xs)+1,np.ptp(ys)+1)
 rgbs=r.get('rgbs',[r['rgb']] if 'rgb' in r else []);assert len(colours)==len(rgbs)
 specifications=[('white',white,(255,255,255)),*[(f'colour{i}',mask,tuple(rgb)) for i,(mask,rgb) in enumerate(zip(colours,rgbs))],('ink',ink,(17,17,17))]
 layers=font['COLR'].ColorLayers[name];assert len(layers)==len(specifications)
 for layer,(suffix,mask,rgb) in zip(layers,specifications):
  assert layer.name==name+'.'+suffix
  colour=font['CPAL'].palettes[0][layer.colorID];assert (colour.red,colour.green,colour.blue)==rgb and colour.alpha==255
  rebuilt=outline(mask,transform);actual=font['glyf'][layer.name]
  assert tuple(actual.coordinates)==tuple(rebuilt.coordinates)
  assert actual.endPtsOfContours==rebuilt.endPtsOfContours
 source=r['source'];raw=(ROOT/source['path']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==source['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==source['git_blob_sha1']
 forms=qualified_forms(ROOT,canonical);assert set(forms)==set(source['include_sequences'])
 result=shape(PATH,canonical,True)
 assert len(result)==1 and font.getGlyphName(result[0][0])==name and result[0][1]>0
 for text in forms:
  assert shape(PATH,text,True)==result
  assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==result
  assert shape(PATH,text+text,True)==result+result
  assert shape(PATH,'😀'+text+'😀',True)==shape(PATH,'😀',True)+result+shape(PATH,'😀',True)




def test_all_family_prefixes_and_adjacent_sequences(font):
    texts=[e['sequence'] for e in SOURCES]
    for first in texts:
        a=shape(PATH,first,True)
        for second in texts:
            b=shape(PATH,second,True)
            assert len(a)==len(b)==1
            for path in [PATH,ROOT/'assets/fonts/dad-emoji-ink.woff2']:
                assert shape(path,first+second,True)==a+b
        for path in [PATH,ROOT/'assets/fonts/dad-emoji-ink.woff2']:
            assert shape(path,'👨'+first+'👧',True)==shape(path,'👨',True)+a+shape(path,'👧',True)


def test_source_circles_match_men_and_boys():
    import xml.etree.ElementTree as ET
    for source in SOURCES:
        text=source['sequence']
        circles=[e for e in ET.fromstring((ROOT/source['path']).read_bytes()).iter() if e.tag.split('}')[-1]=='circle']
        # Women's and girls' head/hair silhouettes are paths; only men and boys
        # use complete circles in this independently inspected native set.
        assert sum(float(e.attrib['r'])>14 for e in circles)==text.count('👨')
        assert sum(float(e.attrib['r'])<14 for e in circles)==text.count('👦')
