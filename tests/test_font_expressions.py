"""Compiled expression identities, semantic colours and joined sequences."""
from pathlib import Path
import hashlib,importlib,json
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
SOURCES=json.loads((ROOT/'data/font-sources/noto-emoji-expressions-svg.json').read_text())['files']
FAMILIES={'balloon_symbols': {'1f4ad', '1f5e8', '1f5ef', '1f4ac', '1f573'}, 'expression_faces': {'263a', '1f47d', '2620', '1f4a9', '1f47f', '2639'}, 'pixel_alien': {'1f47e'}, 'heart_variants': {'1f493', '1f49d', '1f498', '1f497', '1f49e', '1f495', '2763', '1f494', '2764_200d_1fa79', '2764_200d_1f525', '1f496'}, 'heart_decoration': {'1f49f'}, 'ghost': {'1f47b'}, 'motion_symbols': {'1f4a4', '1f4a8', '1f4af', '1f4a2'}, 'coloured_expression': {'1f633', '1f4a5', '1f92e', '1f479', '1f48b', '1f48c', '1f4ab', '1f921', '1f47a', '1f4a6', '1f916'}, 'eye_balloon': {'1f441_200d_1f5e8'}, 'swearing_face': {'1f92c'}}
CASES=[(key,'emoji_'+family+'_svg') for family,keys in FAMILIES.items() for key in sorted(keys)]
assert len(CASES)==len(SOURCES)==42
assert {key for key,_ in CASES}=={Path(e['path']).stem.removeprefix('emoji_u') for e in SOURCES}

@pytest.fixture(scope='module')
def font():return TTFont(PATH)

@pytest.mark.parametrize('key,module_name',CASES)
def test_compiled_expression_matches_reviewed_source(key,module_name,font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from build_emoji import outline
 from emoji_sequences import qualified_forms
 module=importlib.import_module(module_name);(white,*colours,ink),r=module.prepare(key)
 canonical=''.join(chr(int(cp,16)) for cp in key.split('_'))
 name=('component.'+key.upper() if key in {'1f4a5','1f4ab','1f4a8'} else 'expression.'+key)
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


@pytest.mark.parametrize('symbol,compound',[('💨','😮‍💨'),('💫','😵‍💫'),('💥','⛓️‍💥')])
def test_visible_expression_preserves_existing_compound(symbol,compound,font):
 a=shape(PATH,symbol,True);b=shape(PATH,compound,True)
 assert len(a)==len(b)==1 and a!=b
 assert font['glyf'][font.getGlyphName(b[0][0])].numberOfContours>0
 for path in [PATH,ROOT/'assets/fonts/dad-emoji-ink.woff2']:
  assert shape(path,symbol+compound+symbol,True)==a+b+a
 manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
 assert ord(symbol) not in manifest['componentOnly']
