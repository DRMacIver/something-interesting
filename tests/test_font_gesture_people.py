"""Person gesture identities, skin regions and gender/tone sequence boundaries."""
import hashlib,json
from pathlib import Path
import numpy as np
import pytest
from scipy import ndimage
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'
CASES=[('1f481', 7, 9, 9, [1, 3, 4, 8]), ('1f481_200d_2642', 7, 7, 7, [1, 2, 3, 4, 6]), ('1f481_200d_2640', 7, 5, 5, [1, 2, 4]), ('1f645', 7, 9, 9, [1, 2, 3, 4, 5]), ('1f645_200d_2642', 7, 9, 9, [1, 2, 3, 4, 5]), ('1f645_200d_2640', 7, 7, 7, [1, 2, 3]), ('1f646', 7, 13, 13, [1, 2, 5, 6, 7, 12]), ('1f646_200d_2642', 7, 11, 11, [1, 2, 5, 6, 7, 10]), ('1f646_200d_2640', 7, 7, 7, [1, 2, 5, 6]), ('1f64b', 7, 9, 9, [1, 2, 4, 9]), ('1f64b_200d_2642', 7, 8, 8, [1, 2, 4, 5, 8]), ('1f64b_200d_2640', 7, 5, 7, [1, 4, 7]), ('1f64d', 7, 5, 5, [1, 2, 3, 5]), ('1f64d_200d_2642', 7, 5, 5, [1, 2, 3, 5]), ('1f64d_200d_2640', 7, 3, 3, [1, 3]), ('1f64e', 9, 7, 7, [1, 2, 3, 5, 6, 7]), ('1f64e_200d_2642', 9, 7, 7, [1, 2, 3, 5, 6, 7]), ('1f64e_200d_2640', 9, 5, 5, [1, 3, 4, 5])]

CASES.extend([('1f647', 10, 8, 8, [1, 2, 3, 5, 6, 7]), ('1f647_200d_2642', 10, 8, 8, [1, 2, 3, 5, 6, 7]), ('1f647_200d_2640', 10, 6, 6, [1, 3, 4, 5, 6]), ('1f926', 1, 10, 10, [1, 2, 3, 4, 5, 6, 8]), ('1f926_200d_2642', 1, 11, 11, [1, 2, 3, 4, 6, 7, 9]), ('1f926_200d_2640', 1, 10, 10, [1, 2, 3, 4, 5, 6, 8]), ('1f937', 9, 10, 10, [1, 2, 3, 4, 5, 9]), ('1f937_200d_2642', 9, 10, 10, [1, 2, 3, 4, 5, 8]), ('1f937_200d_2640', 9, 8, 8, [1, 2, 3, 6]), ('1f9cf', 4, 8, 8, [1, 2, 3, 5, 6]), ('1f9cf_200d_2642', 4, 8, 8, [1, 2, 3, 5, 7]), ('1f9cf_200d_2640', 4, 7, 7, [1, 2, 3, 4, 6])])

@pytest.mark.parametrize('key,components,counters,count,selected',CASES)
def test_gesture_skin_and_sequence_identity(key,components,counters,count,selected,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_gesture_svg import prepare
 from emoji_sequences import qualified_forms
 (white,skin,ink),r=prepare(key)
 assert r['appliedStrength']>0 and not r['fallback']
 assert (r['sourceComponents'],r['sourceHoles'])==(components,counters)
 labels,n=ndimage.label(white&~ink)
 assert n==count and r['skinRegions']==selected
 for i in range(1,n+1):
  if i in selected:assert np.all(skin[labels==i])
  else:assert not np.any(skin[labels==i])
 masks2,r2=prepare(key)
 assert all(np.array_equal(a,b) for a,b in zip((white,skin,ink),masks2)) and r==r2
 source=r['source'];raw=(ROOT/source['path']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==source['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==source['git_blob_sha1']
 canonical=''.join(chr(int(c,16)) for c in key.split('_'));font=TTFont(PATH)
 name='gestureperson.'+key.replace('_','.')
 assert font['glyf'][name].numberOfContours==components+counters
 forms=[]
 for i in range(6):
  text=canonical[:1]+(chr(0x1f3fa+i) if i else '')+canonical[1:]
  alternatives=qualified_forms(ROOT,text);forms.extend(alternatives)
  result=shape(PATH,text,True);assert len(result)==1 and result[0][0]>0 and result[0][1]>0
  glyph=font.getGlyphName(result[0][0]);assert glyph==name+(f'.tone{i}' if i else '')
  expected=[(name+'.white',0)]+([(name+'.skin',5+i)] if i else [])+[(name+'.ink',1)]
  assert [(l.name,l.colorID) for l in font['COLR'].ColorLayers[glyph]]==expected
  for form in alternatives:assert shape(PATH,form,True)==result
  assert shape(PATH,text+text,True)==result+result
  assert shape(PATH,'😀'+text+'😀',True)==shape(PATH,'😀',True)+result+shape(PATH,'😀',True)
  assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==result
 assert set(forms)==set(source['include_sequences'])

@pytest.mark.parametrize('base',['1f481','1f645','1f646','1f64b','1f64d','1f64e','1f647','1f926','1f937','1f9cf'])
def test_gesture_gender_drawings_remain_distinct(base):
 font=TTFont(PATH)
 drawings=[]
 for suffix in ['', '.200d.2642','.200d.2640']:
  glyph=font['glyf']['gestureperson.'+base+suffix]
  drawings.append(tuple(glyph.coordinates))
 assert len(set(drawings))==3
