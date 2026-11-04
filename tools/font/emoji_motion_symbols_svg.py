"""Reviewed motion/emotion symbols; not yet approved for production."""
import hashlib,json,copy
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import pymupdf
from pen_translate import Settings,translate
from emoji_tile_lettering import replace_letters
ROOT=Path(__file__).resolve().parents[2]
SYMBOLS={'1f4a8':(11,[1,2,6,7,9,10]),'1f4a2':(4,[0,1,2,3]),'1f4a4':(3,[0,1,2]),'1f4af':(4,[0,1,2,3,4])}
OUTLINED={'1f4a8':{1},'1f4a2':set(),'1f4a4':set(),'1f4af':set()}
REVIEWED_TOPOLOGY={'1f4a8': (5, 1), '1f4a2': (4, 0), '1f4a4': (3, 0), '1f4af': (5, 2)}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-expressions-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
 count,letters=SYMBOLS[key];assert len(shapes)==count
 lettering=None
 if key=='1f4a4':lettering=replace_letters(ROOT,key,shapes,[0,1,2],'ZZZ')
 if key=='1f4af':
  # The source draws its two zeroes in one path; split its placement cell
  # into two equal digit cells before fitting the existing comic lettering.
  pen=BoundsPen(None);parse_path(shapes[3].attrib['d'],pen);x0,y0,x1,y1=pen.bounds;mid=(x0+x1)/2
  extra=copy.deepcopy(shapes[3]);parents[shapes[3]].append(extra);parents[extra]=parents[shapes[3]];shapes.append(extra)
  for i,a,b in [(3,x0,mid),(4,mid,x1)]:shapes[i].set('d',f'M{a},{y0} H{b} V{y1} H{a} Z')
  lettering=replace_letters(ROOT,key,shapes,[2,3,4],'100')
 for i,e in enumerate(shapes):
  if i not in letters:parents[e].remove(e);continue
  e.attrib.pop('style',None)
  outlined=i in OUTLINED[key]
  e.set('fill','#ffffff' if outlined else '#111111')
  e.set('stroke','#111111' if outlined else 'none')
  if outlined:
   e.set('stroke-width','1.3');e.set('stroke-linecap','round');e.set('stroke-linejoin','round')
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 # Moderate correlated variation preserves conventional symbol anatomy.
 im,r=translate(mask,Settings(strength=1.7,seed=seed,pressure=.25,taper=.1,bend=.004));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 if key in REVIEWED_TOPOLOGY:assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink)
 r.update(key=key,source=source,sourcePixels=1536,symbolPaths=letters,comicLettering=lettering,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 return (white,ink),r

RECIPES=SYMBOLS
