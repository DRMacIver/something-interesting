"""Compiled geometric identities, semantic colours and relative sizes."""
from pathlib import Path
import hashlib,importlib,json
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
SOURCES=json.loads((ROOT/'data/font-sources/noto-emoji-geometric-svg.json').read_text())['files']
FAMILIES={'geometric':{'1f537', '1f539', '1f536', '1f538', '1f51f', '1f518', '1f532', '1f53a', '1f53b', '1f533', '1f4a0'}}
CASES=[(key,'emoji_'+family+'_svg') for family,keys in FAMILIES.items() for key in sorted(keys)]
assert len(CASES)==len(SOURCES)==11
assert {key for key,_ in CASES}=={Path(e['path']).stem.removeprefix('emoji_u') for e in SOURCES}

@pytest.fixture(scope='module')
def font():return TTFont(PATH)

@pytest.mark.parametrize('key,module_name',CASES)
def test_compiled_geometric_matches_reviewed_source(key,module_name,font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from build_emoji import outline
 from emoji_sequences import qualified_forms
 module=importlib.import_module(module_name);(white,*colours,ink),r=module.prepare(key)
 cp=int(key,16);name=font.getBestCmap()[cp]
 assert name=='geometric.'+key
 assert r['appliedStrength']>0 and not r['fallback']
 assert font['glyf'][name].numberOfContours==sum(module.REVIEWED_TOPOLOGY[key])
 ys,xs=np.nonzero(white);height=r['opticalHeight'];scale=height/max(np.ptp(xs)+1,np.ptp(ys)+1)
 transform=xs.min(),ys.min()-(760-height)/(2*scale),scale
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
 forms=qualified_forms(ROOT,chr(cp));assert set(forms)==set(source['include_sequences'])
 result=shape(PATH,chr(cp),True)
 assert len(result)==1 and font.getGlyphName(result[0][0])==name and result[0][1]>0
 for text in forms:
  assert shape(PATH,text,True)==result
  assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==result
  assert shape(PATH,text+text,True)==result+result
  assert shape(PATH,'😀'+text+'😀',True)==shape(PATH,'😀',True)+result+shape(PATH,'😀',True)


@pytest.mark.parametrize('large,small',[(0x1F536,0x1F538),(0x1F537,0x1F539)])
def test_small_diamond_retains_semantic_size_and_vertical_centre(large,small,font):
 cmap=font.getBestCmap();big=font['glyf'][cmap[large]];little=font['glyf'][cmap[small]]
 assert .36<(little.yMax-little.yMin)/(big.yMax-big.yMin)<.43
 assert abs((little.yMax+little.yMin)-(big.yMax+big.yMin))<8
 assert font['hmtx'][cmap[small]][0]<font['hmtx'][cmap[large]][0]*.55

def test_ten_tile_has_comic_digits(monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_geometric_svg import prepare
 _,record=prepare('1f51f')
 assert ''.join(e['character'] for e in record['comicLettering']['letters'])=='10'
