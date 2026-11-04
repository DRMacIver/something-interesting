"""Compiled expression identities, semantic colours and joined sequences."""
from pathlib import Path
import hashlib,importlib,json
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
SOURCES=json.loads((ROOT/'data/font-sources/noto-emoji-person-symbols-svg.json').read_text())['files']
FAMILIES={'person_symbols':{'1f5e3', '1f9d1_200d_1f9d2_200d_1f9d2', '1f464', '1f463', '1f46a', '1f9d1_200d_1f9d1_200d_1f9d2', '1f465', '1fac2', '1f9d1_200d_1f9d2', '1f9d1_200d_1f9d1_200d_1f9d2_200d_1f9d2'}}
CASES=[(key,'emoji_'+family+'_svg') for family,keys in FAMILIES.items() for key in sorted(keys)]
assert len(CASES)==len(SOURCES)==10
assert {key for key,_ in CASES}=={Path(e['path']).stem.removeprefix('emoji_u') for e in SOURCES}

@pytest.fixture(scope='module')
def font():return TTFont(PATH)

@pytest.mark.parametrize('key,module_name',CASES)
def test_compiled_person_symbol_matches_reviewed_source(key,module_name,font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from build_emoji import outline
 from emoji_sequences import qualified_forms
 module=importlib.import_module(module_name);(white,*colours,ink),r=module.prepare(key)
 canonical=''.join(chr(int(cp,16)) for cp in key.split('_'))
 name='personsymbol.'+key
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



FAMILIES_TEXT=['🧑‍🧑‍🧒','🧑‍🧑‍🧒‍🧒','🧑‍🧒','🧑‍🧒‍🧒']
@pytest.mark.parametrize('first',FAMILIES_TEXT)
@pytest.mark.parametrize('second',FAMILIES_TEXT)
def test_family_prefixes_and_adjacent_sequences_keep_all_children(first,second,font):
 a=shape(PATH,first,True);b=shape(PATH,second,True)
 assert len(a)==len(b)==1
 assert font.getGlyphName(a[0][0])=='personsymbol.'+'_'.join(f'{ord(c):x}' for c in first)
 assert font.getGlyphName(b[0][0])=='personsymbol.'+'_'.join(f'{ord(c):x}' for c in second)
 for path in [PATH,ROOT/'assets/fonts/dad-emoji-ink.woff2']:
  assert shape(path,first+second,True)==a+b
  assert shape(path,'🧑'+first+'🧒',True)==shape(path,'🧑',True)+a+shape(path,'🧒',True)

def test_neutral_families_retain_source_adult_and_child_counts():
 import xml.etree.ElementTree as ET
 expected={'1f46a':(2,1),'1f9d1_200d_1f9d1_200d_1f9d2':(2,1),'1f9d1_200d_1f9d1_200d_1f9d2_200d_1f9d2':(2,2),'1f9d1_200d_1f9d2':(1,1),'1f9d1_200d_1f9d2_200d_1f9d2':(1,2)}
 for source in SOURCES:
  key=Path(source['path']).stem.removeprefix('emoji_u')
  if key not in expected:continue
  circles=[e for e in ET.fromstring((ROOT/source['path']).read_bytes()).iter() if e.tag.split('}')[-1]=='circle']
  assert (sum(float(e.attrib['r'])>14 for e in circles),sum(float(e.attrib['r'])<14 for e in circles))==expected[key]
