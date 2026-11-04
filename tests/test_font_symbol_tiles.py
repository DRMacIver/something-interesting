"""Reviewed tile identities, typography and promoted ZWJ-component regressions."""
from pathlib import Path
import hashlib
import importlib
import json
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
SOURCES=json.loads((ROOT/'data/font-sources/noto-emoji-symbol-tiles-svg.json').read_text())['files']
CASES=[(Path(e['path']).stem.removeprefix('emoji_u'),'emoji_alphanum_svg' if 'alphanum' in e['path'] else 'emoji_arrows_controls_svg') for e in SOURCES]

@pytest.fixture(scope='module')
def font():return TTFont(PATH)

@pytest.mark.parametrize('key,module_name',CASES)
def test_symbol_tile_compiled_identity(key,module_name,font,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from build_emoji import outline
 from emoji_sequences import qualified_forms
 module=importlib.import_module(module_name);(white,ink),r=module.prepare(key)
 cp=int(key,16);name=font.getBestCmap()[cp]
 expected=f'component.{cp:X}' if cp in {0x2194,0x2195,0x27A1} else 'symboltile.'+key
 assert name==expected
 assert r['appliedStrength']>0 and not r['fallback']
 assert font['glyf'][name].numberOfContours==sum(module.REVIEWED_TOPOLOGY[key])
 ys,xs=np.nonzero(white);transform=xs.min(),ys.min(),760/max(np.ptp(xs)+1,np.ptp(ys)+1)
 for suffix,mask in [('white',white),('ink',ink)]:
  rebuilt=outline(mask,transform);actual=font['glyf'][name+'.'+suffix]
  assert tuple(actual.coordinates)==tuple(rebuilt.coordinates)
  assert actual.endPtsOfContours==rebuilt.endPtsOfContours
 assert [(layer.name,layer.colorID) for layer in font['COLR'].ColorLayers[name]]==[(name+'.white',0),(name+'.ink',1)]
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

@pytest.mark.parametrize('group,count',[('alphanum',39),('arrow',21),('av-symbol',25)])
def test_complete_symbol_subgroups_are_real_distinct_drawings(group,count,font):
 manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
 required=[];subgroup=None
 for line in (ROOT/'data/unicode/18.0.0/emoji/emoji-test.txt').read_text().splitlines():
  if line.startswith('# subgroup: '):subgroup=line.split(': ',1)[1]
  if subgroup==group and '; fully-qualified' in line:
   required.append(''.join(chr(int(cp,16)) for cp in line.split(';')[0].split()))
 assert len(required)==count and set(required)<=set(manifest['sequences'])
 drawings=set()
 for text in required:
  result=shape(PATH,text,True);assert len(result)==1 and result[0][0]>0 and result[0][1]>0
  glyph=font['glyf'][font.getGlyphName(result[0][0])];assert glyph.numberOfContours>0
  drawings.add(tuple(glyph.coordinates))
 assert len(drawings)==count

@pytest.mark.parametrize('arrow,sequence,expected',[
 ('➡️','🚶‍➡️','activityperson.1f6b6.200d.27a1'),
 ('➡️','🚶🏿‍♀️‍➡️','activityperson.1f6b6.200d.2640.200d.27a1.tone5'),
 ('↔️','🙂‍↔️','seq.1F642.200D.2194'),
 ('↕️','🙂‍↕️','seq.1F642.200D.2195'),
])
def test_visible_arrows_do_not_break_existing_zwj_ligatures(arrow,sequence,expected,font):
 manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
 assert ord(arrow[0]) not in manifest['componentOnly']
 a=shape(PATH,arrow,True);joined=shape(PATH,sequence,True)
 assert len(a)==len(joined)==1 and a!=joined
 assert font.getGlyphName(joined[0][0])==expected
 for text,want in [(arrow+sequence+arrow,a+joined+a),(sequence+arrow+sequence,joined+a+joined)]:
  assert shape(PATH,text,True)==want
  assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==want
