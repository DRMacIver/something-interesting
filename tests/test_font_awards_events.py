"""Award/event identities, metal distinctions and preserved gold calligraphy."""
from pathlib import Path
import hashlib,importlib,json
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
SOURCES=json.loads((ROOT/'data/font-sources/noto-emoji-awards-events-svg.json').read_text())['files']
FAMILIES={'awards_events':{'2728','1f9e7','1f397','1f396','1f3c6','1f3c5','1f947','1f948','1f949'}}
CASES=[(key,'emoji_'+family+'_svg') for family,keys in FAMILIES.items() for key in sorted(keys)]
assert len(CASES)==len(SOURCES)==9
assert {key for key,_ in CASES}=={Path(e['path']).stem.removeprefix('emoji_u') for e in SOURCES}

@pytest.fixture(scope='module')
def font():return TTFont(PATH)

@pytest.mark.parametrize('key,module_name',CASES)
def test_compiled_awards_events_matches_reviewed_source(key,module_name,font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from build_emoji import outline
 from emoji_sequences import qualified_forms
 module=importlib.import_module(module_name);(white,*colours,ink),r=module.prepare(key)
 cp=int(key,16);name=font.getBestCmap()[cp]
 assert name=='awards-events.'+key
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

@pytest.mark.parametrize('group,count',[('event', 21), ('award-medal', 6)])
def test_complete_awards_events_subgroups_are_distinct_drawings(group,count,font):
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


def test_ranked_medals_have_distinct_metals_and_comic_numerals(font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_awards_events_svg import prepare
 palettes=[]
 for key,digit in [('1f947','1'),('1f948','2'),('1f949','3')]:
  _,r=prepare(key);assert [x['character'] for x in r['comicLettering']['letters']]==[digit]
  layers=font['COLR'].ColorLayers[font.getBestCmap()[int(key,16)]]
  colour=font['CPAL'].palettes[0][layers[2].colorID]
  palettes.append((colour.red,colour.green,colour.blue))
 assert len(set(palettes))==3
 gold,silver,bronze=palettes
 assert max(silver)-min(silver)<5
 assert gold[1]>bronze[1] and gold[2]>bronze[2]


def test_red_envelope_retains_gold_character_counters(font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_awards_events_svg import prepare
 from scipy import ndimage
 (white,red,gold,ink),report=prepare('1f9e7')
 letter=report['goldCharacter'];assert letter['sourcePaths']==list(range(3,12))
 assert (letter['sourceComponents'],letter['sourceHoles'])==(4,5)
 assert letter['appliedStrength']>0 and not letter['fallback']
 assert ndimage.label(gold)[1]==5  # Four character components plus the surrounding ring.
 assert ndimage.label(ndimage.binary_fill_holes(gold)&~gold)[1]==6
 layers=font['COLR'].ColorLayers[font.getBestCmap()[0x1F9E7]]
 assert font['glyf'][layers[2].name].numberOfContours==11
 # Adjacent fills overlap beneath the black border to prevent pale seams.
 # The gold character and red field must remain disjoint wherever visible.
 assert not np.any(red&gold&~ink)
