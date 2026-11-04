"""Compiled sign identities, semantic colours and medical-component shaping."""
from pathlib import Path
import hashlib,importlib,json
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
SOURCES=json.loads((ROOT/'data/font-sources/noto-emoji-signs-svg.json').read_text())['files']
FAMILIES={
 'transport_signs':{'1f3e7','1f6ae','267f','1f6b9','1f6ba','1f6bb','1f6bc','1f6be','1f6c2','1f6c3','1f6c4','1f6c5'},
 'other_mono_symbols':{'2705','2611','2714','274e','27b0','27bf','303d','2733','2734','2747','00a9','00ae','2122'},
 'warning_signs':{'26a0','1f6b8','26d4','1f6ab','1f6b3','1f6ad','1f6af','1f6b1','1f6b7','1f4f5','1f51e','2622','2623'},
 'colour_symbols':{'1f530','2b55','274c','1f4db'},
 'emblem_symbols':{'2695','267b','269c','1f531'},
 'potable_water':{'1f6b0'},
}
CASES=[(key,'emoji_'+family+'_svg') for family,keys in FAMILIES.items() for key in sorted(keys)]
assert len(CASES)==len(SOURCES)==47
assert {key for key,_ in CASES}=={Path(e['path']).stem.removeprefix('emoji_u') for e in SOURCES}

@pytest.fixture(scope='module')
def font():return TTFont(PATH)

@pytest.mark.parametrize('key,module_name',CASES)
def test_compiled_sign_matches_reviewed_source(key,module_name,font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from build_emoji import outline
 from emoji_sequences import qualified_forms
 module=importlib.import_module(module_name);(white,*colours,ink),r=module.prepare(key)
 cp=int(key,16);name=font.getBestCmap()[cp]
 assert name==('component.2695' if cp==0x2695 else 'sign.'+key)
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

@pytest.mark.parametrize('group,count',[('transport-sign',13),('warning',13),('other-symbol',22)])
def test_complete_sign_subgroups_are_distinct_drawings(group,count,font):
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

@pytest.mark.parametrize('person',['🧑','👨','👩'])
@pytest.mark.parametrize('tone',['',*'🏻🏼🏽🏾🏿'])
def test_visible_medical_symbol_preserves_doctor_ligatures(person,tone,font):
 symbol='⚕️';sequence=person+tone+'‍⚕️';a=shape(PATH,symbol,True);joined=shape(PATH,sequence,True)
 assert len(a)==len(joined)==1 and a!=joined
 assert font['glyf'][font.getGlyphName(joined[0][0])].numberOfContours>0
 for text,want in [(symbol+sequence+symbol,a+joined+a),(sequence+symbol+sequence,joined+a+joined)]:
  assert shape(PATH,text,True)==want
  assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==want
 manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
 assert 0x2695 not in manifest['componentOnly']

def test_beginner_mark_keeps_ordered_two_colour_halves(monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_colour_symbols_svg import prepare
 (white,yellow,green,ink),r=prepare('1f530')
 assert r['colourNames']==['yellow','green'] and r['rgbs'][0]!=r['rgbs'][1]
 assert not (yellow&green&~ink).any()
 assert np.nonzero(yellow)[1].mean()<np.nonzero(green)[1].mean()
 assert yellow.sum()>white.sum()*.3 and green.sum()>white.sum()*.3
