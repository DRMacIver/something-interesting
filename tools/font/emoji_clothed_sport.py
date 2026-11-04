"""Reviewed detailed SVG sports figures with fully covered skin."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from fontTools.pens.svgPathPen import SVGPathPen
from pen_translate import Settings,translate,same_features
ROOT=Path(__file__).resolve().parents[2]
RECIPES={'1f93a':(35,{0,2,3,4,5,9,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,31,32,33,34},{0,3,5,9,14,15,16,17,18,20,21,22,23,24,25,28,29,31,32,34})}

RECIPES['1f93a'][1].update({7,8})
RECIPES['1f93a'][2].add(8)
RECIPES['26f7']=(68,{1,2,3,6,8,9,10,11,12,13,15,16,17,20,22,23,24,25,26,27,28,30,31,32,33,34,35,36,37,38,39,40,41,42,44,45,46,47,48,49,50,51,52,53,54,55,56,58,60,61,62,65,66,67},{1,2,8,9,10,11,12,15,16,22,23,24,25,26,27,30,31,33,35,36,37,38,39,40,44,45,47,48,49,51,52,53,54,56,58,66})

# A single black goggle rim avoids outlining both edges of a thin grey trim.
RECIPES['26f7'][2].add(65)
# Source32 is a narrow colour highlight crossing the bent sleeve, not a seam.
# Outline the complete sleeve silhouette31 and leave that paint highlight out.
RECIPES['26f7'][1].discard(32)
RECIPES['26f7'][2].discard(31)

RECIPES.update({'1f3c2': (46, {1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 35, 36, 38, 39, 40, 41, 42, 43, 44, 45}, {1, 3, 4, 6, 7, 9, 10, 11, 17, 18, 20, 22, 26, 28, 29, 30, 35, 36, 38, 39, 40, 43, 44, 45})})

def prepare(key):
 expected,keep,solid=RECIPES[key]
 entry=next(e for e in json.loads((ROOT/'data/font-sources/noto-emoji-clothed-sport-svg.json').read_text())['files'] if e['path'].endswith(f'emoji_u{key}.svg'))
 raw=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
 root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
 shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
 assert len(shapes)==expected
 for i,e in enumerate(shapes):
  if i not in keep:parents[e].remove(e);continue
  e.attrib.pop('style',None);e.set('fill','#111' if i in solid else 'white')
  if i not in solid:e.set('stroke','#111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
 labels,n=ndimage.label(mask);sizes=np.bincount(labels.ravel())
 specks=np.isin(labels,[i for i in range(1,n+1) if sizes[i]<4]);removed_specks=int(specks.sum());mask &= ~specks
 holes,n=ndimage.label(ndimage.binary_fill_holes(mask)&~mask);sizes=np.bincount(holes.ravel())
 tiny=np.isin(holes,[i for i in range(1,n+1) if sizes[i]<4]);clean=mask|tiny
 if same_features(mask,clean):mask=clean
 image,r=translate(mask,Settings(strength=1.7,seed=int(key,16),pressure=.025,bend=.001,taper=0))
 ink=np.asarray(image)<128;white=ndimage.binary_fill_holes(ink)
 assert r['appliedStrength']>0 and not r['fallback'],key
 assert (r['sourceComponents'],r['sourceHoles'])=={'1f93a':(1,20),'26f7':(1,29),'1f3c2':(4,20)}[key]
 r.update(removedRasterSpeckPixels=removed_specks,key=key,source=entry,sourcePixels=1536,keptPaths=sorted(keep),solidPaths=sorted(solid),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 return (white,ink),r


def add_clothed_sport(root,glyphs,metrics,cmap,layers,review,outline):
 sequences,rules=[],[]
 for key in RECIPES:
  (white,ink),report=prepare(key);source=report['source'];cp=int(key,16)
  assert cp not in cmap
  ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1)
  transform=xs.min(),ys.min(),factor;advance=round((np.ptp(xs)+1)*factor)+100
  name='clothedsport.'+key;cmap[cp]=name
  glyphs[name]=outline(ink,transform);metrics[name]=advance,50
  assert glyphs[name].numberOfContours==report['sourceComponents']+report['sourceHoles'],key
  for suffix,mask in [('white',white),('ink',ink)]:
   glyphs[name+'.'+suffix]=outline(mask,transform);metrics[name+'.'+suffix]=advance,50
  layers[name]=[(name+'.white',0),(name+'.ink',1)]
  for form in source['include_sequences']:
   canonical=form.replace('\ufe0e','').replace('\ufe0f','')
   assert canonical[0]==chr(cp)
   if len(canonical)>1:
    assert all(ord(c) in cmap for c in canonical)
    rules.append((len(canonical),'sub '+' '.join(cmap[ord(c)] for c in canonical)+' by '+name+';'))
   if form!=chr(cp):sequences.append(form)
  review.append(dict(codepoint=f'U+{cp:04X}',label=key,glyphName=name,category='clothed-sport',
   source=source['path'],sourceSha256=source['sha256'],sourcePixels=report['sourcePixels'],
   bounds=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],advance=advance,
   penTreatment=report,license='NotoEmoji-SVG-Apache-2.0.txt',notice='NotoEmoji-SVG-NOTICE.txt'))
 return sequences,'\n'.join(rule for _,rule in sorted(rules,reverse=True))
