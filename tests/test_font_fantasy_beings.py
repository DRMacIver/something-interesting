"""Non-human fantasy material regions and exact, non-tone sequence shaping."""
import hashlib
import importlib
import json
from pathlib import Path
import numpy as np
import pytest
from scipy import ndimage
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
CASES=[
 ('genie','1f9de',8,12,[1,4,5,6,7,9]),
 ('genie','1f9de_200d_2642',8,13,[2,5,6,7,8,10]),
 ('genie','1f9de_200d_2640',8,12,[2,4,5,6,7,9]),
 ('zombie','1f9df',13,13,[1,4,5,13]),
 ('zombie','1f9df_200d_2642',13,11,[1,4,5,11]),
 ('zombie','1f9df_200d_2640',12,11,[1,4,6,11]),
 ('troll','1f9cc',6,24,[3,5,6,8,15,19,20,22,24]),
]

@pytest.mark.parametrize('family,key,components,counters,selected',CASES)
def test_fantasy_material_and_compiled_identity(family,key,components,counters,selected,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from build_emoji import outline
 from emoji_sequences import qualified_forms
 module=importlib.import_module('emoji_'+family+'_svg')
 (white,body,ink),r=module.prepare(key)
 assert r['appliedStrength']>0 and not r['fallback']
 assert (r['sourceComponents'],r['sourceHoles'])==(components,counters)
 labels,n=ndimage.label(white&~ink)
 assert n==counters and r['skinRegions']==selected
 for i in range(1,n+1):
  if i in selected:assert np.all(body[labels==i])
  else:assert not np.any(body[labels==i])
 if family=='troll':
  assert r['reviewedToothRegions']==[12,13] and min(r['toothInteriorRadii'])>32
 source=r['source'];raw=(ROOT/source['path']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==source['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==source['git_blob_sha1']
 font=TTFont(PATH);name='fantasybeing.'+key.replace('_','.')
 assert font['glyf'][name].numberOfContours==components+counters
 ys,xs=np.nonzero(white);transform=xs.min(),ys.min(),760/max(np.ptp(xs)+1,np.ptp(ys)+1)
 for suffix,mask in [('white',white),('body',body),('ink',ink)]:
  rebuilt=outline(mask,transform)
  assert tuple(font['glyf'][name+'.'+suffix].coordinates)==tuple(rebuilt.coordinates)
 layers=font['COLR'].ColorLayers[name]
 assert [l.name for l in layers]==[name+'.'+s for s in ['white','body','ink']]
 assert layers[0].colorID==0 and layers[2].colorID==1
 colour=font['CPAL'].palettes[0][layers[1].colorID]
 assert (colour.red,colour.green,colour.blue)==((119,161,189) if family=='genie' else (134,177,152))
 canonical=''.join(chr(int(c,16)) for c in key.split('_'));forms=qualified_forms(ROOT,canonical)
 assert set(forms)==set(source['include_sequences'])
 result=shape(PATH,canonical,True)
 assert len(result)==1 and result[0][1]>0 and font.getGlyphName(result[0][0])==name
 for text in forms:
  assert shape(PATH,text,True)==result
  assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==result
  assert shape(PATH,text+text,True)==result+result
  assert shape(PATH,'😀'+text+'😀',True)==shape(PATH,'😀',True)+result+shape(PATH,'😀',True)
 manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
 assert set(forms)<=set(manifest['sequences'])
 for tone in '🏻🏼🏽🏾🏿':
  unsupported=canonical[:1]+tone+canonical[1:]
  assert unsupported not in manifest['sequences']
  assert shape(PATH,unsupported,True)!=result

@pytest.mark.parametrize('base',['1f9de','1f9df'])
def test_nonhuman_fantasy_gender_drawings_remain_distinct(base):
 font=TTFont(PATH)
 assert len({tuple(font['glyf']['fantasybeing.'+base+suffix].coordinates) for suffix in ['', '.200d.2642','.200d.2640']})==3
