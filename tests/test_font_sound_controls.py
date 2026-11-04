"""Compiled sound identities, mute colours, volume waves and control pointers."""
from pathlib import Path
import hashlib,importlib,json
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
SOURCES=json.loads((ROOT/'data/font-sources/noto-emoji-sound-controls-svg.json').read_text())['files']
FAMILIES={'sound_controls':{'1f39a','1f39b','1f399','1f507','1f508','1f509','1f50a','1f514','1f515','1f4e2','1f4e3','1f4ef'}}
CASES=[(key,'emoji_'+family+'_svg') for family,keys in FAMILIES.items() for key in sorted(keys)]
assert len(CASES)==len(SOURCES)==12
assert {key for key,_ in CASES}=={Path(e['path']).stem.removeprefix('emoji_u') for e in SOURCES}

@pytest.fixture(scope='module')
def font():return TTFont(PATH)

@pytest.mark.parametrize('key,module_name',CASES)
def test_compiled_sound_controls_matches_reviewed_source(key,module_name,font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from build_emoji import outline
 from emoji_sequences import qualified_forms
 module=importlib.import_module(module_name);(white,*colours,ink),r=module.prepare(key)
 cp=int(key,16);name=font.getBestCmap()[cp]
 assert name=='sound-controls.'+key
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

@pytest.mark.parametrize('group,count',[('sound',9),('music',9)])
def test_complete_sound_controls_subgroups_are_distinct_drawings(group,count,font):
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


def test_mute_marks_have_semantic_red_but_volume_levels_are_monochrome(font):
 for cp in [0x1F507,0x1F515]:
  layers=font['COLR'].ColorLayers[font.getBestCmap()[cp]];assert len(layers)==3
  c=font['CPAL'].palettes[0][layers[1].colorID]
  assert c.red>c.green*1.5 and c.red>c.blue*1.5
 for cp in [0x1F508,0x1F509,0x1F50A]:
  assert len(font['COLR'].ColorLayers[font.getBestCmap()[cp]])==2


def test_volume_levels_have_distinct_wave_geometry(font):
 drawings=[]
 for cp in [0x1F508,0x1F509,0x1F50A]:
  g=font['glyf'][font.getBestCmap()[cp]];drawings.append(tuple(g.coordinates))
 assert len(set(drawings))==3
 # The waves extend beyond the cone instead of disappearing into its black fill.
 for cp in [0x1F509,0x1F50A]:
  g=font['glyf'][font.getBestCmap()[cp]]
  upper=[x for x,y in g.coordinates if y>g.yMax-150]
  assert max(upper)-min(upper)>150


def test_control_knobs_retain_four_white_pointers(monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_sound_controls_svg import prepare
 from scipy import ndimage
 (white,ink),r=prepare('1f39b')
 # Four solid circular knobs with a white radial pointer, separate from the dots.
 labels,n=ndimage.label(ink);sizes=np.bincount(labels.ravel())
 knobs=[i for i in range(1,n+1) if 40000<sizes[i]<150000 and np.ptp(np.nonzero(labels==i)[1])<500]
 assert len(knobs)==4
 for i in knobs:
  yy,xx=np.nonzero(labels==i);cx=(xx.min()+xx.max())/2;cy=(yy.min()+yy.max())/2
  y,x=np.indices(ink.shape);core=(x-cx)**2+(y-cy)**2<((xx.max()-xx.min())*.35)**2
  assert np.count_nonzero(core&~ink)>100
