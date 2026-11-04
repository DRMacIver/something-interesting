"""Compiled sign identities, semantic colours and medical-component shaping."""
from pathlib import Path
import hashlib,importlib,json
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
SOURCES=json.loads((ROOT/'data/font-sources/noto-emoji-game-medical-svg.json').read_text())['files']
FAMILIES={'game_medical':{'2665', '2666', '1f52b', '265f', '1fa79', '2660', '2663', '1f004', '1fa78'}}
CASES=[(key,'emoji_'+family+'_svg') for family,keys in FAMILIES.items() for key in sorted(keys)]
assert len(CASES)==len(SOURCES)==9
assert {key for key,_ in CASES}=={Path(e['path']).stem.removeprefix('emoji_u') for e in SOURCES}

@pytest.fixture(scope='module')
def font():return TTFont(PATH)

@pytest.mark.parametrize('key,module_name',CASES)
def test_compiled_game_medical_matches_reviewed_source(key,module_name,font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from build_emoji import outline
 from emoji_sequences import qualified_forms
 module=importlib.import_module(module_name);(white,*colours,ink),r=module.prepare(key)
 cp=int(key,16);name=font.getBestCmap()[cp]
 assert name==('component.1FA79' if cp==0x1FA79 else 'game-medical.'+key)
 assert r['appliedStrength']>0 and not r['fallback']
 assert font['glyf'][name].numberOfContours==sum(module.REVIEWED_TOPOLOGY[key])
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
 forms=qualified_forms(ROOT,chr(cp));assert set(forms)==set(source['include_sequences'])
 result=shape(PATH,chr(cp),True)
 assert len(result)==1 and font.getGlyphName(result[0][0])==name and result[0][1]>0
 for text in forms:
  assert shape(PATH,text,True)==result
  assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==result
  assert shape(PATH,text+text,True)==result+result
  assert shape(PATH,'😀'+text+'😀',True)==shape(PATH,'😀',True)+result+shape(PATH,'😀',True)

@pytest.mark.parametrize('group,count',[('game',24),('medical',7)])
def test_complete_game_medical_subgroups_are_distinct_drawings(group,count,font):
 manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
 required=[];subgroup=None
 for line in (ROOT/'data/unicode/18.0.0/emoji/emoji-test.txt').read_text().splitlines():
  if line.startswith('# subgroup: '):subgroup=line.split(': ',1)[1]
  if subgroup==group and '; fully-qualified' in line:required.append(''.join(chr(int(cp,16)) for cp in line.split(';')[0].split()))
 assert len(required)==count and set(required)<=set(manifest['sequences'])
 drawings=set()
 for text in required:
  result=shape(PATH,text,True);assert len(result)==1 and result[0][0]>0 and result[0][1]>0
  glyph=font['glyf'][font.getGlyphName(result[0][0])];assert glyph.numberOfContours>0;drawings.add(tuple(glyph.coordinates))
 assert len(drawings)==count


@pytest.mark.parametrize('heart',['❤‍🩹','❤️‍🩹'])
def test_visible_bandage_preserves_mending_heart(heart,font):
 a=shape(PATH,'🩹',True);b=shape(PATH,heart,True)
 assert len(a)==len(b)==1 and a!=b
 assert font.getGlyphName(b[0][0])=='expression.2764_200d_1fa79'
 for path in [PATH,ROOT/'assets/fonts/dad-emoji-ink.woff2']:
  assert shape(path,'🩹'+heart+'🩹',True)==a+b+a
 manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
 assert 0x1FA79 not in manifest['componentOnly']

def test_suit_colours_and_full_diamond_shape(font):
 cmap=font.getBestCmap()
 for cp in [0x2665,0x2666]:
  name=cmap[cp];colours=font['COLR'].ColorLayers[name];assert len(colours)==3
  colour=font['CPAL'].palettes[0][colours[1].colorID]
  assert colour.red>colour.green*1.5 and colour.red>colour.blue*1.5
  glyph=font['glyf'][name]
  # Optical fitting uses the longest dimension; the heart is wider than tall.
  assert max(glyph.xMax-glyph.xMin,glyph.yMax-glyph.yMin)>740
 diamond=font['glyf'][cmap[0x2666]];coords=list(diamond.coordinates)
 mid=(diamond.yMin+diamond.yMax)/2
 upper=[x for x,y in coords if y>mid+250];lower=[x for x,y in coords if y<mid-250]
 middle=[x for x,y in coords if abs(y-mid)<100]
 assert max(upper)-min(upper)<(max(middle)-min(middle))*.6
 assert max(lower)-min(lower)<(max(middle)-min(middle))*.6

def test_bandage_keeps_all_twenty_perforations(monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_game_medical_svg import prepare
 _,report=prepare('1fa79')
 assert report['sourceHoles']==21  # Twenty vents plus the central pad.
