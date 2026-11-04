"""Audit native couple head positions and modifier paints against independent references."""
import copy
import hashlib
import json
import xml.etree.ElementTree as E
import numpy as np
from emoji_holding_hands_svg import raster


def validate_couple_sources(root):
    spec=json.loads((root/'docs/family-pairs-emoji-svg-source-probe.json').read_text())['files']
    # Authoritative source colours for each modifier, read from independent existing
    # holding-hands references, rather than inferred from the candidate sequence.
    reference=json.loads((root/'docs/holding-hands-emoji-svg-source-probe.json').read_text())['files'];paints={}
    for tone in range(1,6):
     text='👭'+chr(0x1f3fa+tone);e=next(e for e in reference if e['sequence']==text);r=E.fromstring((root/e['path']).read_bytes());shapes=[s for s in r.iter() if s.tag.split('}')[-1] in {'path','circle','ellipse','polygon','polyline','rect','line'}]
     paints[tone]=shapes[28].get('style',shapes[28].get('fill',''))
    reports=[]
    for e in spec:
     text=e['sequence']
     if '❤' not in text and text[0] not in '💏💑':continue
     raw=(root/e['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256']
     assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['git_blob_sha1']
     r=E.fromstring(raw);parents={c:p for p in r.iter() for c in p};heads=[]
     for s in r.iter():
      if s.tag.split('}')[-1] not in {'path','circle','ellipse','polygon','polyline','rect','line'}:continue
      p=s;ids=[]
      while p is not None:
       ids.append(p.get('id',''));p=parents.get(p)
      if not any(i.startswith('head') for i in ids):continue
      one=E.Element(r.tag,{'viewBox':'0 0 128 128'});clone=copy.deepcopy(s);clone.attrib.pop('style',None);clone.set('fill','#000');one.append(clone)
      ys,xs=np.nonzero(raster(one));heads.append((float(xs.mean()),s.get('style',s.get('fill',''))))
     duplicateHeads=len(heads)-len(set(heads));heads=list(set(heads))
     assert len(heads)==2,(text,heads)
     heads.sort();assert heads[0][0]<768<heads[1][0]
     tones=[ord(c)-0x1f3fa for c in text if 0x1f3fb<=ord(c)<=0x1f3ff];tones=tones*2 if len(tones)==1 else tones
     if tones:
      assert [p for _,p in heads]==[paints[t] for t in tones],(text,heads,tones,paints)
     else:assert all('#FFCA28' in p for _,p in heads)
     reports.append(dict(sequence=text,duplicateHeads=duplicateHeads,leftHeadX=heads[0][0]/12,rightHeadX=heads[1][0]/12,tones=tones or [0,0],headPaints=[p for _,p in heads]))
    assert len(reports)==208
    return reports
