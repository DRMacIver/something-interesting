"""Compiled hand props preserve anatomy, object colour and exact modifiers."""
from pathlib import Path
import hashlib,json
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'

@pytest.fixture(scope='module')
def font():return TTFont(PATH)

@pytest.mark.parametrize('key',['270d','1f485','1f933'])
def test_hand_prop_compiled_layers_and_all_modifiers(key,font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_hand_props_svg import prepare
 from emoji_sequences import qualified_forms
 from build_emoji import outline
 (white,*materials,ink),record=prepare(key);name='handprop.'+key
 assert font.getBestCmap()[int(key,16)]==name
 assert record['appliedStrength']>0 and not record['fallback']
 assert font['glyf'][name].numberOfContours==record['sourceComponents']+record['sourceHoles']
 ys,xs=np.nonzero(white);scale=760/max(np.ptp(xs)+1,np.ptp(ys)+1);transform=xs.min(),ys.min(),scale
 specifications=[('white',white),('skin',materials[0]),*[(f'colour{i}',mask) for i,mask in enumerate(materials[1:])],('ink',ink)]
 for suffix,mask in specifications:
  expected=outline(mask,transform);actual=font['glyf'][name+'.'+suffix]
  assert tuple(actual.coordinates)==tuple(expected.coordinates)
  assert actual.endPtsOfContours==expected.endPtsOfContours
 expected=outline(ink,transform);assert tuple(font['glyf'][name].coordinates)==tuple(expected.coordinates)
 skin=json.loads((ROOT/'output/imagegen/emoji-production/skin-palette-source.json').read_text())['skinTones']
 all_forms=[]
 for tone in range(6):
  text=chr(int(key,16))+(chr(0x1F3FA+tone) if tone else '');variant=name+(f'.tone{tone}' if tone else '')
  forms=qualified_forms(ROOT,text);all_forms+=forms
  expected_layers=[(name+'.white',(255,255,255))]+([(name+'.skin',tuple(skin[tone-1]))] if tone else [])+[(name+f'.colour{i}',tuple(rgb)) for i,rgb in enumerate(record['rgbs'][1:])]+[(name+'.ink',(17,17,17))]
  layers=font['COLR'].ColorLayers[variant];assert len(layers)==len(expected_layers)
  for layer,(layername,rgb) in zip(layers,expected_layers):
   assert layer.name==layername
   colour=font['CPAL'].palettes[0][layer.colorID];assert (colour.red,colour.green,colour.blue)==rgb and colour.alpha==255
  assert tuple(font['glyf'][variant].coordinates)==tuple(expected.coordinates)
  result=shape(PATH,text,True)
  assert len(result)==1 and result[0][1]>0 and font.getGlyphName(result[0][0])==variant
  for form in forms:
   for path in [PATH,ROOT/'assets/fonts/dad-emoji-ink.woff2']:
    assert shape(path,form,True)==result
    assert shape(path,form+form,True)==result+result
    assert shape(path,'😀'+form+'😀',True)==shape(path,'😀',True)+result+shape(path,'😀',True)
 assert set(all_forms)==set(record['source']['include_sequences'])


def test_all_hand_prop_reference_sources_are_pinned():
 sources=json.loads((ROOT/'data/font-sources/noto-emoji-hand-props-svg.json').read_text())['files']
 assert len(sources)==18
 for entry in sources:
  raw=(ROOT/entry['path']).read_bytes()
  assert hashlib.sha256(raw).hexdigest()==entry['sha256']
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['git_blob_sha1']

@pytest.mark.parametrize('key,skin_points,paper_points',[
 ('270d',[(40,85),(110,95)],[(75,30),(17,110)]),
 ('1f485',[(20,80)],[(100,20)]),
 ('1f933',[(100,60)],[(90,20),(35,100)]),
])
def test_skin_does_not_spill_onto_objects_or_clothes(key,skin_points,paper_points,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_hand_props_svg import prepare
 (white,skin,*rest),record=prepare(key);pad=record['padding']
 for expected,points in [(True,skin_points),(False,paper_points)]:
  for x,y in points:
   cx,cy=round(x*12)+pad,round(y*12)+pad
   assert white[cy,cx]
   assert bool(skin[cy,cx]) is expected,(key,x,y)
 if key=='270d':assert record['clippedPenFlattened']

def test_nail_polish_stays_red_and_outside_skin(monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_hand_props_svg import prepare
 (white,skin,polish,ink),record=prepare('1f485');pad=record['padding']
 assert record['colourNames']==['skin','red']
 assert not (skin&polish&~ink).any()
 for x,y in [(30,40),(85,69)]:
  cx,cy=x*12+pad,y*12+pad
  assert polish[cy,cx] and not skin[cy,cx] and not ink[cy,cx]
