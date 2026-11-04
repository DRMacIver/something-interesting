"""Verify pinned native geometry and independent left/right skin paints."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET

def shapes(root):return [x for x in root.iter() if x.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
def geometry(root):return [(x.tag,{k:v for k,v in x.attrib.items() if k not in ['style','fill','stroke','id','opacity']}) for x in shapes(root)]
def paint(root,e):
 s=e.get('style',e.get('fill',''));m=re.search(r'url\(#([^)]*)\)',s)
 return '|'.join(x.get('style','') for x in next(g for g in root.iter() if g.get('id')==m[1]) if x.tag.endswith('stop')) if m else s

def validate_sources(root, spec, recipes):
    groups = {key: [] for key in recipes}
    aliases = {'👩‍🤝‍👩':'1f46d', '👩‍🤝‍👨':'1f46b', '👨‍🤝‍👨':'1f46c'}
    for e in spec:
     raw=(root/e['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256']
     assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==e['git_blob_sha1']
     text=e['sequence'];base=''.join(c for c in text if not 0x1f3fb<=ord(c)<=0x1f3ff and ord(c)!=0xfe0f)
     key=aliases.get(base,'_'.join(f'{ord(c):04x}' for c in base))
     tones=[ord(c)-0x1f3fa for c in text if 0x1f3fb<=ord(c)<=0x1f3ff]
     tones=tones*2 if len(tones)==1 else tones;tones=tones or [0,0];assert len(tones)==2
     groups[key].append((e,ET.fromstring(raw),tones))
    reports=[]
    for key,entries in groups.items():
     assert len(entries)==26
     base=next(r for _,r,t in entries if t==[0,0]);g=geometry(base)
     references={t[0]:r for _,r,t in entries if t[0]==t[1]};assert set(references)==set(range(6))
     for e,r,tones in entries:
      assert geometry(r)==g,e['sequence']
      for i,side in recipes[key][1].items():
       ref=references[tones[0 if side=='left' else 1]]
       assert paint(r,shapes(r)[i])==paint(ref,shapes(ref)[i]),(e['sequence'],i,side)
     reports.append(dict(key=key,variants=len(entries),geometrySha256=hashlib.sha256(json.dumps(g,sort_keys=True).encode()).hexdigest(),skinPaths=recipes[key][1],allTonePaintsIndependent=True,sourceFiles=[e['path'] for e,_,_ in entries]))
    return reports
