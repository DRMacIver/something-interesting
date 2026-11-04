"""Fully covered sport drawings and exact presentation forms."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'

@pytest.mark.parametrize('key,components,holes,specks,forms',[
 ('1f93a',1,20,0,['🤺']),('26f7',1,29,2,['⛷','⛷︎','⛷️']),
 ('1f3c2',4,20,0,['🏂'+tone for tone in ['',*'🏻🏼🏽🏾🏿']]),
])
def test_clothed_sport_geometry_and_presentation(key,components,holes,specks,forms,monkeypatch):
 monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
 from emoji_clothed_sport import prepare
 from build_emoji import outline
 (white,ink),report=prepare(key)
 assert report['appliedStrength']>0 and not report['fallback']
 assert (report['sourceComponents'],report['sourceHoles'])==(components,holes)
 assert report['removedRasterSpeckPixels']==specks
 assert np.all(white[ink]) and np.any(white&~ink)
 masks2,report2=prepare(key)
 assert all(np.array_equal(a,b) for a,b in zip((white,ink),masks2)) and report==report2
 source=report['source'];raw=(ROOT/source['path']).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==source['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==source['git_blob_sha1']
 assert set(source['include_sequences'])==set(forms)
 assert source['skin_modifiers'] is (key=='1f3c2')
 if key=='1f3c2':
  refs=json.loads((ROOT/'data/font-sources/noto-emoji-snowboarding-tone-references.json').read_text())['files']
  assert len(refs)==5 and {e['sequence'] for e in refs}==set(forms[1:])
  assert set(source['equivalent_tone_sources'])=={e['path'] for e in refs}
  for e in refs:
   variant=(ROOT/e['path']).read_bytes()
   assert variant==raw
   assert hashlib.sha256(variant).hexdigest()==e['sha256']
   assert hashlib.sha1(b'blob '+str(len(variant)).encode()+b'\0'+variant).hexdigest()==e['git_blob_sha1']
 ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1);transform=xs.min(),ys.min(),factor
 font=TTFont(PATH);name='clothedsport.'+key;glyph=font['glyf'][name]
 rebuilt=outline(ink,transform)
 assert glyph.numberOfContours==rebuilt.numberOfContours==holes+components
 assert tuple(glyph.coordinates)==tuple(rebuilt.coordinates)
 assert [(l.name,l.colorID) for l in font['COLR'].ColorLayers[name]]==[(name+'.white',0),(name+'.ink',1)]
 for suffix,mask in [('white',white),('ink',ink)]:
  assert tuple(font['glyf'][name+'.'+suffix].coordinates)==tuple(outline(mask,transform).coordinates)
 expected=shape(PATH,forms[0],True)
 assert len(expected)==1 and expected[0][0]>0 and expected[0][1]>0
 assert font.getGlyphName(expected[0][0])==name
 for form in forms:
  assert shape(PATH,form,True)==expected
  assert shape(PATH,form+form,True)==expected+expected
  assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',form,True)==expected
  assert shape(PATH,'🤹'+form+'🤹',True)==shape(PATH,'🤹',True)+expected+shape(PATH,'🤹',True)
 if key=='26f7':
  for filename in ['dad-emoji.woff2','dad-emoji-ink.woff2']:
   variations=next(t.uvsDict for t in TTFont(ROOT/'assets/fonts'/filename)['cmap'].tables if t.format==14)
   assert all(any(cp==0x26f7 for cp,_ in variations[selector]) for selector in [0xfe0e,0xfe0f])
 manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ')[1].rstrip(';\n'))
 assert set(forms)<=set(manifest['sequences'])
 if key!='1f3c2':assert not any(forms[0]+tone in manifest['sequences'] for tone in '🏻🏼🏽🏾🏿')
