"""Person activity identities, skin regions and gender/tone sequence boundaries."""
import hashlib,json
from pathlib import Path
import numpy as np
import pytest
from scipy import ndimage
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'

@pytest.mark.parametrize('subgroup_name,required_count',[('person-activity',408),('person-resting',30),('body-parts',48),('person-fantasy',158)])
def test_activity_subgroup_is_fully_covered_by_real_shaped_drawings(subgroup_name,required_count):
 manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
 custom=set(manifest['sequences']);required=set();subgroup=None
 for line in (ROOT/'data/unicode/18.0.0/emoji/emoji-test.txt').read_text().splitlines():
  if line.startswith('# subgroup: '):subgroup=line.partition(': ')[2]
  fields=line.partition('#')[0].strip().split(';')
  if subgroup==subgroup_name and len(fields)==2 and fields[1].strip()=='fully-qualified':
   required.add(''.join(chr(int(cp,16)) for cp in fields[0].split()))
 assert len(required)==required_count and required<=custom
 font=TTFont(PATH)
 for text in required:
  result=shape(PATH,text,True)
  assert len(result)==1 and result[0][0]>0 and result[0][1]>0,text
  assert font['glyf'][font.getGlyphName(result[0][0])].numberOfContours>0,text

CASES=[('1f3c3', 3, 15, 15, [1, 3, 5, 6, 7, 9, 10, 11, 13]), ('1f3c3_200d_2642', 3, 16, 16, [1, 3, 5, 6, 7, 9, 10, 11, 12, 14]), ('1f3c3_200d_2640', 3, 16, 16, [1, 4, 5, 6, 7, 9, 10, 11, 12, 14]), ('1f3c3_200d_27a1', 3, 16, 16, [1, 3, 4, 6, 7, 8, 10, 11, 12, 13, 14]), ('1f3c3_200d_2642_200d_27a1', 3, 16, 16, [1, 4, 5, 6, 7, 9, 10, 11, 12, 14]), ('1f3c3_200d_2640_200d_27a1', 3, 16, 16, [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14]), ('1f6b6', 3, 9, 9, [1, 6, 9]), ('1f6b6_200d_2642', 3, 9, 9, [1, 5, 8]), ('1f6b6_200d_2640', 3, 9, 9, [1, 5, 8]), ('1f6b6_200d_27a1', 3, 9, 9, [1, 4, 5, 9]), ('1f6b6_200d_2642_200d_27a1', 3, 9, 9, [1, 5, 8]), ('1f6b6_200d_2640_200d_27a1', 3, 9, 9, [1, 5, 7, 9]), ('1f9cd', 9, 9, 9, [1, 2, 3, 4, 6, 7]), ('1f9cd_200d_2642', 9, 9, 9, [1, 2, 3, 4, 6, 7]), ('1f9cd_200d_2640', 9, 7, 7, [1, 2, 4, 5]), ('1f9ce', 3, 6, 6, [1, 4]), ('1f9ce_200d_2642', 3, 6, 6, [1, 4]), ('1f9ce_200d_2640', 3, 6, 6, [1, 4]), ('1f9ce_200d_27a1', 3, 6, 6, [1, 4]), ('1f9ce_200d_2642_200d_27a1', 3, 6, 6, [1, 4]), ('1f9ce_200d_2640_200d_27a1', 3, 6, 6, [1, 4])]

CASES.extend([('1f483', 4, 27, 27, [1, 2, 6, 9, 11, 22, 26]), ('1f57a', 7, 16, 16, [1, 2, 3, 5, 6, 9, 11, 16])])

CASES.extend([('1f9d6',9,9,9,[1,3,6,8]),('1f9d6_200d_2642',9,9,9,[1,2,3,6,8]),('1f9d6_200d_2640',9,7,7,[1,4,6]),('1f9d7',2,26,26,[3,5,8,9,11,14,16,18,21,24]),('1f9d7_200d_2642',2,26,26,[3,6,8,9,10,13,16,18,21,24]),('1f9d7_200d_2640',2,26,26,[3,6,8,9,10,13,16,18,21,24])])

CASES.extend([('1f46f', 14, 28, 28, [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 25, 26, 27, 28]), ('1f46f_200d_2642', 14, 28, 28, [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 25, 26, 27, 28]), ('1f46f_200d_2640', 14, 24, 24, [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 21, 22, 23, 24])])

CASES.extend([('1f9d1_200d_1f9af', 3, 9, 9, [1, 4, 5, 6]), ('1f468_200d_1f9af', 3, 9, 9, [1, 4, 5]), ('1f469_200d_1f9af', 3, 9, 9, [1, 4, 5, 6]), ('1f9d1_200d_1f9af_200d_27a1', 3, 9, 9, [1, 4, 5]), ('1f468_200d_1f9af_200d_27a1', 3, 9, 9, [1, 4, 5, 6]), ('1f469_200d_1f9af_200d_27a1', 3, 9, 9, [1, 4, 5, 6]), ('1f9d1_200d_1f9bd', 3, 42, 42, [1, 4, 7, 11]), ('1f468_200d_1f9bd', 3, 42, 42, [1, 4, 7, 11]), ('1f469_200d_1f9bd', 3, 42, 42, [1, 4, 7, 11]), ('1f9d1_200d_1f9bd_200d_27a1', 3, 42, 42, [1, 4, 6, 7, 11]), ('1f468_200d_1f9bd_200d_27a1', 3, 42, 42, [1, 4, 6, 7, 11]), ('1f469_200d_1f9bd_200d_27a1', 3, 42, 42, [1, 4, 7, 11]), ('1f9d1_200d_1f9bc', 4, 19, 19, [1, 5]), ('1f468_200d_1f9bc', 4, 19, 19, [1, 5, 6]), ('1f469_200d_1f9bc', 4, 20, 20, [1, 6]), ('1f9d1_200d_1f9bc_200d_27a1', 4, 19, 19, [1, 5, 6]), ('1f468_200d_1f9bc_200d_27a1', 4, 19, 19, [1, 5]), ('1f469_200d_1f9bc_200d_27a1', 4, 20, 20, [1, 2, 6])])

CASES.extend([('1f486', 7, 7, 7, [1, 2, 3, 4, 5, 6]), ('1f486_200d_2642', 7, 7, 7, [1, 2, 3, 4, 5, 6]), ('1f486_200d_2640', 7, 5, 5, [1, 2, 3, 4]), ('1f487', 3, 7, 7, [3, 4, 5, 6]), ('1f487_200d_2642', 6, 8, 8, [3, 5, 6, 7]), ('1f487_200d_2640', 4, 6, 6, [3, 5]), ('1f574', 4, 19, 19, [1, 3, 4, 9, 16, 17]), ('1f9d1_200d_1fa70', 7, 14, 14, [1, 2, 3, 5, 7, 9, 10, 11, 12, 14])])

CASES.extend([('1f6c0', 4, 19, 19, [7]), ('1f6cc', 1, 7, 7, [1]), ('1f9d8', 8, 14, 14, [1, 2, 3, 4, 6, 7, 11, 13, 14]), ('1f9d8_200d_2642', 8, 15, 15, [1, 2, 3, 4, 6, 7, 13, 14, 15]), ('1f9d8_200d_2640', 8, 12, 12, [1, 2, 4, 5, 10, 11, 12])])

CASES.extend([('1f442', 3, 1, 1, [1]), ('1f443', 1, 1, 1, [1]), ('1f4aa', 2, 1, 1, [1]), ('1f9b5', 2, 1, 1, [1]), ('1f9b6', 2, 1, 1, [1]), ('1f9bb', 2, 5, 5, [3])])

CASES.extend([('1f939',9,14,14,[3,4,6,9]),('1f939_200d_2642',9,14,14,[3,4,5,9]),('1f939_200d_2640',9,12,12,[3,7])])

CASES.extend([('1f3c7',5,21,21,[1,2,9,10]),('1f3cc',1,13,13,[3,5]),('1f3cc_200d_2642',1,14,14,[3,4]),('1f3cc_200d_2640',1,14,14,[3,4,6,9])])

CASES.extend([('1f3ca', 7, 14, 14, [1, 6, 8, 12]), ('1f3ca_200d_2642', 7, 14, 14, [1, 4, 5, 8, 12]), ('1f3ca_200d_2640', 7, 15, 15, [1, 4, 6, 9, 13]), ('26f9', 4, 18, 18, [1, 4, 6, 11, 14]), ('26f9_200d_2642', 4, 18, 18, [1, 4, 6, 10, 11]), ('26f9_200d_2640', 4, 18, 18, [1, 4, 6, 10, 12]), ('1f3cb', 7, 24, 24, [3, 4, 6, 7, 8, 11, 13, 15, 17, 18, 19, 20, 21, 22]), ('1f3cb_200d_2642', 7, 25, 25, [3, 4, 6, 7, 8, 11, 13, 15, 18, 19, 20, 21, 22, 23]), ('1f3cb_200d_2640', 7, 24, 24, [3, 4, 6, 7, 8, 11, 13, 16, 17, 18, 19, 20, 21, 22])])

CASES.extend([('1f6a3', 6, 27, 27, [1, 5]), ('1f6a3_200d_2642', 6, 27, 27, [1, 5]), ('1f6a3_200d_2640', 6, 27, 27, [1, 5]), ('1f3c4', 9, 17, 17, [1, 3, 7, 14, 17]), ('1f3c4_200d_2642', 9, 17, 17, [1, 3, 7, 14, 17]), ('1f3c4_200d_2640', 7, 18, 18, [1, 2, 4, 8, 15, 18])])

CASES.extend([('1f6b4', 15, 22, 22, [2, 3, 5, 7, 8, 10, 13, 14]), ('1f6b4_200d_2642', 15, 22, 22, [2, 3, 5, 7, 8, 10, 13, 14]), ('1f6b4_200d_2640', 15, 23, 23, [2, 4, 6, 8, 9, 11, 14, 15]), ('1f6b5', 5, 27, 27, [4, 5, 7, 14, 18, 21]), ('1f6b5_200d_2642', 5, 27, 27, [4, 5, 7, 14, 18, 21]), ('1f6b5_200d_2640', 5, 29, 29, [4, 5, 9, 16, 20, 23]), ('1f938', 6, 10, 10, [1, 2, 3, 5, 8, 10]), ('1f938_200d_2642', 6, 8, 8, [1, 2, 3, 5, 7, 8]), ('1f938_200d_2640', 7, 9, 9, [1, 2, 3, 5, 7, 8, 9]), ('1f93e', 7, 15, 15, [2, 3, 4, 6, 8, 9, 12]), ('1f93e_200d_2642', 7, 15, 15, [2, 3, 4, 6, 7, 10, 12]), ('1f93e_200d_2640', 6, 16, 16, [2, 3, 4, 5, 7, 9, 10, 13]), ('1f93d', 9, 23, 23, [8, 10, 15, 17, 19]), ('1f93d_200d_2642', 11, 18, 18, [8, 10]), ('1f93d_200d_2640', 10, 26, 26, [8, 10, 15, 16, 18, 19, 20, 21, 22])])

CASES.extend([('1f93c', 5, 18, 18, [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]), ('1f93c_200d_2642', 5, 18, 18, [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]), ('1f93c_200d_2640', 5, 18, 18, [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]), ('1f385', 6, 8, 8, [2, 6, 7]), ('1f936', 11, 12, 12, [3, 6, 7, 8, 11]), ('1f9d1_200d_1f384', 12, 9, 9, [2]), ('1f9d9', 7, 11, 11, [4, 9]), ('1f9d9_200d_2642', 6, 14, 14, [4, 6, 7, 10, 12]), ('1f9d9_200d_2640', 6, 16, 16, [6])])

CASES.extend([('1f9db', 7, 10, 10, [1]), ('1f9db_200d_2642', 7, 7, 7, [1, 6]), ('1f9db_200d_2640', 7, 8, 8, [2, 7, 8]), ('1f9dd', 8, 19, 19, [2, 5, 8, 13]), ('1f9dd_200d_2642', 8, 19, 19, [6, 7, 13]), ('1f9dd_200d_2640', 7, 21, 21, [5, 9, 10, 11, 15])])

CASES.extend([('1f9da', 7, 19, 19, [1, 6, 7, 8, 17, 18]), ('1f9da_200d_2642', 7, 19, 19, [1, 6, 7, 8, 17, 18]), ('1f9da_200d_2640', 8, 21, 21, [1, 6, 8, 9, 10, 19, 20]), ('1f9dc', 7, 12, 12, [1, 2, 3, 4, 6, 9, 10]), ('1f9dc_200d_2642', 7, 11, 11, [1, 2, 3, 5, 11]), ('1f9dc_200d_2640', 8, 12, 12, [2, 3, 4, 10]), ('1f9b8', 6, 7, 7, [2, 4]), ('1f9b8_200d_2642', 7, 7, 7, [2, 4]), ('1f9b8_200d_2640', 6, 7, 7, [2, 4])])

CASES.extend([('1f9b9', 6, 18, 18, [4, 10]), ('1f9b9_200d_2642', 6, 18, 18, [4, 10]), ('1f9b9_200d_2640', 5, 18, 18, [2, 11])])

CASES.append(('1f47c',8,11,11,[3]))

@pytest.mark.parametrize('key,components,counters,count,selected',CASES)
def test_activity_skin_and_sequence_identity(key,components,counters,count,selected,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_activity_svg import prepare
 from emoji_sequences import qualified_forms
 (white,skin,ink),r=prepare(key)
 assert r['appliedStrength']>0 and not r['fallback']
 assert (r['sourceComponents'],r['sourceHoles'])==(components,counters)
 if key.startswith('1f939'):
  assert r['opticalDetailAdjustment']==dict(eyeRadii=[1.7,1.9],eyeShiftY=2,removedMiddleGloveCreases=True)
 if key=='1f3c7':
  assert r['opticalHeadTransform']==dict(scale=1.25,anchor=[44,12])
  assert r['opticalHandTransform']==dict(scale=1.25,anchor=[42,46])
  assert r['mergedHandPaths']==[19,29]
 if key.startswith('26f9'):
  assert r['opticalBallTransform']==dict(scale=1.25,sourceAnchor=[23.52,80.96],targetAnchor=[23.52,83.83])
 if key.startswith('1f3cb'):
  assert r['opticalHeadTransform']==dict(scale=1.1,sourceAnchor=[64,47],targetAnchor=[64,49])
  assert len(r['removedInnerPlateRims'])==2
 if key.startswith('1f3cc'):

  assert r['opticalCapSeams']['strokeWidth']==.65
 if key=='1f6cc':
  assert r['opticalHeadTransform']==dict(scale=1.8,anchor=[40,85])
  assert skin.sum()>14000
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
 name='activityperson.'+key.replace('_','.')
 assert font['glyf'][name].numberOfContours==components+counters
 if key.split('_')[0] in {'1f3ca','26f9','1f3cb','1f6a3','1f3c4','1f6b4','1f6b5','1f938','1f93e','1f93d','1f93c','1f385','1f936','1f9d1','1f9d9','1f9db','1f9dd','1f9da','1f9dc','1f9b8','1f9b9','1f47c'}:
  from build_emoji import outline
  yy,xx=np.nonzero(white);transform=(xx.min(),yy.min(),760/max(np.ptp(xx)+1,np.ptp(yy)+1))
  for suffix,mask in [('white',white),('skin',skin),('ink',ink)]:
   rebuilt=outline(mask,transform)
   assert tuple(font['glyf'][name+'.'+suffix].coordinates)==tuple(rebuilt.coordinates)

 forms=[]
 for i in range(6):
  text=canonical[:1]+(chr(0x1f3fa+i) if i else '')+canonical[1:]
  alternatives=qualified_forms(ROOT,text)
  if key in {'1f3cc','1f3ca','26f9','1f3cb','1f3c4'} and i==0:
   for selector in ['\ufe0e','\ufe0f']:
    if text+selector not in alternatives:alternatives.append(text+selector)
  forms.extend(alternatives)
  result=shape(PATH,text,True);assert len(result)==1 and result[0][0]>0 and result[0][1]>0
  glyph=font.getGlyphName(result[0][0]);assert glyph==name+(f'.tone{i}' if i else '')
  expected=[(name+'.white',0)]+([(name+'.skin',5+i)] if i else [])+[(name+'.ink',1)]
  assert [(l.name,l.colorID) for l in font['COLR'].ColorLayers[glyph]]==expected
  for form in alternatives:assert shape(PATH,form,True)==result
  assert shape(PATH,text+text,True)==result+result
  assert shape(PATH,'😀'+text+'😀',True)==shape(PATH,'😀',True)+result+shape(PATH,'😀',True)
  assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==result
 assert set(forms)==set(source['include_sequences'])-set(source.get('paired_sequences',[]))

@pytest.mark.parametrize('base',['1f3c3','1f6b6','1f9cd','1f9ce','1f9d6','1f9d7','1f46f','1f486','1f487','1f9d8','1f939','1f3cc','1f3ca','26f9','1f3cb','1f6a3','1f3c4','1f6b4','1f6b5','1f938','1f93e','1f93d','1f93c','1f9d9','1f9db','1f9dd','1f9da','1f9dc','1f9b8','1f9b9'])
def test_activity_gender_drawings_remain_distinct(base):
 font=TTFont(PATH)
 drawings=[]
 for suffix in ['', '.200d.2642','.200d.2640']:
  glyph=font['glyf']['activityperson.'+base+suffix]
  drawings.append(tuple(glyph.coordinates))
 assert len(set(drawings))==3

@pytest.mark.parametrize('base',['1f3c3','1f6b6','1f9ce'])
@pytest.mark.parametrize('gender',['','\u200d♂','\u200d♀'])
def test_activity_direction_boundaries(base,gender):
 font=TTFont(PATH)
 for tone in ['',*'🏻🏼🏽🏾🏿']:
  left=chr(int(base,16))+tone+gender;right=left+'\u200d➡️'
  l=shape(PATH,left,True);r=shape(PATH,right,True)
  assert len(l)==len(r)==1 and l[0][0]!=r[0][0]
  assert tuple(font['glyf'][font.getGlyphName(l[0][0])].coordinates)!=tuple(font['glyf'][font.getGlyphName(r[0][0])].coordinates)
  assert shape(PATH,left+right+left,True)==l+r+l
  assert shape(PATH,right+left+right,True)==r+l+r

@pytest.mark.parametrize('filename',['dad-emoji.woff2','dad-emoji-ink.woff2'])
def test_activity_variation_selectors_are_declared_for_browser_font_selection(filename):
 font=TTFont(ROOT/'assets/fonts'/filename)
 variations={}
 for table in font['cmap'].tables:
  if table.format==14:
   for selector,pairs in table.uvsDict.items():variations.setdefault(selector,set()).update(cp for cp,_ in pairs)
 manifest_text=(ROOT/'js/emoji-manifest.js').read_text()
 manifest=json.loads(manifest_text.split('export default ',1)[1].rstrip(';\n'))
 for text in manifest['sequences']:
  for base,selector in zip(text,text[1:]):
   if ord(selector) in (0xFE0E,0xFE0F):assert ord(base) in variations.get(ord(selector),set()),text

@pytest.mark.parametrize('aid',['🦯','🦼','🦽'])
def test_activity_mobility_gender_direction_and_component_boundaries(aid):
 font=TTFont(PATH)
 for tone in ['',*'🏻🏼🏽🏾🏿']:
  drawings=[]
  for person in '🧑👨👩':
   left=person+tone+'\u200d'+aid;right=left+'\u200d➡️'
   l=shape(PATH,left,True);r=shape(PATH,right,True)
   assert len(l)==len(r)==1 and l[0][0]!=r[0][0]
   for result in [l,r]:drawings.append(tuple(font['glyf'][font.getGlyphName(result[0][0])].coordinates))
   assert shape(PATH,left+right+left,True)==l+r+l
   assert shape(PATH,right+left+right,True)==r+l+r
   surrounding=shape(PATH,person+tone,True)
   assert shape(PATH,person+tone+left+person+tone,True)==surrounding+l+surrounding
  assert len(set(drawings))==6

@pytest.mark.parametrize('key,person',[('1f46f','🧑'),('1f46f_200d_2642','👨'),('1f46f_200d_2640','👩')])
def test_activity_bunny_pairs_keep_independent_skin_and_sequence_order(key,person,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_activity_svg import prepare
 from emoji_paired_skin import split_paired_skin
 (white,skin,ink),report=prepare(key)
 left,right,split=split_paired_skin(skin,ink)
 assert not (left&right).any() and np.array_equal(left|right,skin)
 assert np.nonzero(left)[1].max()<np.nonzero(right)[1].min()
 font=TTFont(PATH);name='activityperson.'+key.replace('_','.')
 assert font['glyf'][name+'.skin.left'].xMax<font['glyf'][name+'.skin.right'].xMin
 expected=[]
 for a in range(1,6):
  for b in range(1,6):
   if a==b:continue
   text=person+chr(0x1f3fa+a)+'\u200d🐰\u200d'+person+chr(0x1f3fa+b)
   expected.append(text);result=shape(PATH,text,True)
   assert len(result)==1 and result[0][0]>0 and result[0][1]>0
   glyph=font.getGlyphName(result[0][0]);assert glyph==name+f'.tones{a}.{b}'
   assert [(l.name,l.colorID) for l in font['COLR'].ColorLayers[glyph]]==[(name+'.white',0),(name+'.skin.left',5+a),(name+'.skin.right',5+b),(name+'.ink',1)]
   reverse=person+chr(0x1f3fa+b)+'\u200d🐰\u200d'+person+chr(0x1f3fa+a)
   other=shape(PATH,reverse,True);assert other[0][0]!=result[0][0]
   assert shape(PATH,text+reverse+text,True)==result+other+result
   prefix=person+chr(0x1f3fa+a);suffix='🐰'+person+chr(0x1f3fa+b)
   assert shape(PATH,prefix+text+suffix,True)==shape(PATH,prefix,True)+result+shape(PATH,suffix,True)
   assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==result
   assert tuple(font['glyf'][glyph].coordinates)==tuple(font['glyf'][name].coordinates)
 assert set(expected)==set(report['source']['paired_sequences'])


@pytest.mark.parametrize('key,person,left_ids,right_ids',[
 ('1f93c','🧑',[2,5,6,7,11,14],[1,3,4,8,10,12,13]),
 ('1f93c_200d_2642','👨',[1,3,6,7,10,11,13],[2,4,5,8,12,14]),
 ('1f93c_200d_2640','👩',[2,3,6,7,10,11,13],[1,4,5,8,12,14]),
])
def test_activity_wrestling_pairs_keep_source_owned_skin(key,person,left_ids,right_ids,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_activity_svg import prepare
 from emoji_wrestling_svg import split_skin
 from build_emoji import outline
 (white,skin,ink),report=prepare(key)
 left,right,review=split_skin(white,skin,ink,report)
 assert review['leftRegions']==left_ids and review['rightRegions']==right_ids
 assert not (left&right).any() and np.array_equal(left|right,skin)
 # Both people's limbs cross the gap; a midpoint split cannot represent them.
 assert np.nonzero(left)[1].max()>np.nonzero(right)[1].min()
 labels,_=ndimage.label(white&~ink)
 for ids,mask in [(left_ids,left),(right_ids,right)]:
  for index in report['skinRegions']:
   assert np.all(mask[labels==index]) if index in ids else not np.any(mask[labels==index])
 yy,xx=np.nonzero(white);transform=(xx.min(),yy.min(),760/max(np.ptp(xx)+1,np.ptp(yy)+1))
 font=TTFont(PATH);name='activityperson.'+key.replace('_','.')
 for side,mask in [('left',left),('right',right)]:
  rebuilt=outline(mask,transform)
  assert tuple(font['glyf'][name+'.skin.'+side].coordinates)==tuple(rebuilt.coordinates)
 expected=[]
 for a in range(1,6):
  for b in range(1,6):
   if a==b:continue
   text=person+chr(0x1f3fa+a)+'\u200d🫯\u200d'+person+chr(0x1f3fa+b)
   expected.append(text);result=shape(PATH,text,True)
   assert len(result)==1 and result[0][0]>0 and result[0][1]>0
   glyph=font.getGlyphName(result[0][0]);assert glyph==name+f'.tones{a}.{b}'
   assert [(l.name,l.colorID) for l in font['COLR'].ColorLayers[glyph]]==[(name+'.white',0),(name+'.skin.left',5+a),(name+'.skin.right',5+b),(name+'.ink',1)]
   reverse=person+chr(0x1f3fa+b)+'\u200d🫯\u200d'+person+chr(0x1f3fa+a)
   other=shape(PATH,reverse,True);assert other[0][0]!=result[0][0]
   assert shape(PATH,text+reverse+text,True)==result+other+result
   prefix=person+chr(0x1f3fa+a);suffix='🫯'+person+chr(0x1f3fa+b)
   assert shape(PATH,prefix+text+suffix,True)==shape(PATH,prefix,True)+result+shape(PATH,suffix,True)
   assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==result
   assert tuple(font['glyf'][glyph].coordinates)==tuple(font['glyf'][name].coordinates)
 assert set(expected)==set(report['source']['paired_sequences'])
