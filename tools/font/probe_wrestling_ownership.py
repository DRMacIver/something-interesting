"""Compare wrestling skin ownership with opposite-tone licensed source drawings.

Geometric correspondence is review evidence, not a production skin assignment.
Run from the repository root; inspect the emitted source-colour overlay.
"""
from pathlib import Path
import xml.etree.ElementTree as E,json,re,hashlib,copy
import numpy as np
import pymupdf
ROOT=Path.cwd();tags={'path','polygon','circle','ellipse','rect','polyline','line'}
probe=json.loads(Path('docs/wrestling-tone-reference-emoji-svg-source-probe.json').read_text())
light={'#FFD29C','#F9DDBD','#EDBD82','#DBA689'};dark={'#5C4037','#70534A','#4A2F27','#33251F'}
def load(path):
 raw=Path(path).read_bytes();r=E.fromstring(raw);ss=[e for e in r.iter() if e.tag.split('}')[-1] in tags];return raw,r,ss
def colours(e,r):
 v=e.get('fill','')+e.get('style','')
 if 'url(#' in v:
  ident=v.split('url(#')[1].split(')')[0];v=' '.join(E.tostring(x,encoding='unicode') for g in r.iter() if g.get('id')==ident for x in g if x.tag.endswith('stop'))
 return set(c.upper() for c in re.findall(r'#[0-9a-fA-F]{6}',v))
def mask(raw,index):
 r=E.fromstring(raw);ss=[e for e in r.iter() if e.tag.split('}')[-1] in tags];parents={c:p for p in r.iter() for c in p}
 for i,e in enumerate(ss):
  if i!=index:parents[e].remove(e)
  else:
   e.attrib.pop('style',None);e.set('fill','#000000');e.set('stroke','none')
 r.set('width','256');r.set('height','256')
 d=pymupdf.open(stream=E.tostring(r),filetype='svg');pdf=pymupdf.open('pdf',d.convert_to_pdf());p=pdf[0].get_pixmap(alpha=False)
 return np.frombuffer(p.samples,dtype=np.uint8).reshape(p.height,p.width,3).max(axis=2)<128
refs=[]
for n,e in enumerate(probe['files']):
 raw,r,ss=load(e['path']);assert hashlib.sha256(raw).hexdigest()==e['sha256'];pieces=[]
 for i,s in enumerate(ss):
  cs=colours(s,r)
  tone='light' if cs and cs<=light else 'dark' if cs and cs<=dark else None
  if tone:pieces.append((i,('left' if (tone=='light')==(n==0) else 'right'),mask(raw,i)))
 refs.append(pieces)
records=[]
for key in ['1f93c','1f93c_200d_2642','1f93c_200d_2640']:
 path=f'build/unicode-sources/noto-emoji-sport-svg/emoji_u{key}.svg';raw,r,ss=load(path);rows=[]
 for i,s in enumerate(ss):
  a=mask(raw,i);matches=[]
  for pieces in refs:
   scores=[(float((a&b).sum()/max(1,(a|b).sum())),j,owner) for j,owner,b in pieces];score,j,owner=max(scores);matches.append(dict(referencePathIndex=j,owner=owner,iou=score))
  if min(m['iou'] for m in matches)>.8 and len({m['owner'] for m in matches})==1:rows.append(dict(pathIndex=i,owner=matches[0]['owner'],matches=matches))
 records.append(dict(key=key,source=path,sourceSha256=hashlib.sha256(raw).hexdigest(),matches=rows))
 print(key,[(r['pathIndex'],r['owner'],round(min(m['iou'] for m in r['matches']),3)) for r in rows])
Path('docs/wrestling-source-ownership-probe.json').write_text(json.dumps(dict(status='Geometric correspondence candidates; requires anatomical review before production',referenceProbe='docs/wrestling-tone-reference-emoji-svg-source-probe.json',rasterPixels=256,minimumIoU=.8,drawings=records),indent=2)+'\n')

# Review source-painted ownership with occlusion preserved, not a midpoint split.
from PIL import Image,ImageDraw,ImageFont
sheet=Image.new('RGB',(1536,560),'white');draw=ImageDraw.Draw(sheet)
for column,record in enumerate(records):
 raw,r,ss=load(record['source'])
 for row in record['matches']:
  shape=ss[row['pathIndex']];shape.attrib.pop('style',None)
  shape.set('fill','#2DA3D8' if row['owner']=='left' else '#D85CA2')
 r.set('width','512');r.set('height','512')
 d=pymupdf.open(stream=E.tostring(r),filetype='svg');pdf=pymupdf.open('pdf',d.convert_to_pdf());p=pdf[0].get_pixmap(alpha=False)
 sheet.paste(Image.frombytes('RGB',(p.width,p.height),p.samples),(512*column,0))
 draw.text((512*column+10,515),record['key'],fill='black',font=ImageFont.load_default(size=18))
 draw.text((512*column+10,538),'Blue: first person; pink: second',fill='black',font=ImageFont.load_default(size=16))
sheet.save('output/font-review/pen-translation/wrestling-source-ownership-probe.png')
