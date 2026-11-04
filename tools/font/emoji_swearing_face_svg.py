"""Reviewed swearing face with comic grawlix lettering; not yet approved for production."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import pymupdf
from pen_translate import Settings,translate
from emoji_tile_lettering import replace_letters
ROOT=Path(__file__).resolve().parents[2]
SYMBOLS={'1f92c':(11,[0,2,3,4,5,6,7,8])}
OUTLINED={'1f92c':{0}}
REVIEWED_TOPOLOGY={'1f92c': (7, 7)}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-expressions-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
 count,letters=SYMBOLS[key];assert len(shapes)==count
 points=shapes[2].attrib.pop('points').split();shapes[2].tag=shapes[2].tag.replace('polyline','path')
 shapes[2].set('d','M'+' L'.join(','.join(points[i:i+2]) for i in range(0,len(points),2))+' Z')
 lettering=replace_letters(ROOT,key,shapes,[3,4,5,6],'#$!@')
 for i,e in enumerate(shapes):
  if i not in letters:parents[e].remove(e);continue
  e.attrib.pop('style',None)
  outlined=i in OUTLINED[key]
  e.set('fill','#ffffff' if outlined or i in {3,4,5,6} else '#111111')
  e.set('stroke','#111111' if outlined else 'none')
  if i in {3,4,5,6}:
   e.set('stroke','#ffffff');e.set('stroke-width','2.4');e.set('stroke-linejoin','round')
  if outlined:
   e.set('stroke-width','1.3');e.set('stroke-linecap','round');e.set('stroke-linejoin','round')
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 # Moderate correlated variation preserves conventional symbol anatomy.
 im,r=translate(mask,Settings(strength=1.7,seed=seed,pressure=.01,taper=0,bend=.001));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 if key in REVIEWED_TOPOLOGY:assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink)
 r.update(key=key,source=source,sourcePixels=1536,symbolPaths=letters,comicLettering=lettering,negativeLetterStroke=2.4,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 return (white,ink),r

RECIPES=SYMBOLS
