"""Reviewed mathematical, gender, currency and punctuation symbols."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import pymupdf
from pen_translate import Settings,translate,same_features
from emoji_tile_lettering import replace_letters
ROOT=Path(__file__).resolve().parents[2]
SYMBOLS={'2640': (5, [1]), '2642': (5, [1]), '26a7': (9, [1]), '2716': (7, [3]), '2795': (6, [3]), '2796': (3, [1]), '2797': (9, [3, 4, 5]), '1f7f0': (26, [18, 21]), '203c': (14, [0, 4, 7, 11]), '2049': (14, [0, 2, 6, 11]), '2753': (7, [1, 5]), '2754': (7, [1, 5]), '2755': (7, [0, 4]), '2757': (7, [0, 4]), '3030': (5, [1]), '1f4b1': (19, [4, 7, 12, 13, 14, 17, 18]), '1f4b2': (9, [4, 7])}

REVIEWED_TOPOLOGY={'2640': (1, 1), '2642': (1, 1), '26a7': (1, 1), '2716': (1, 0), '2795': (1, 0), '2796': (1, 0), '2797': (3, 0), '1f7f0': (2, 0), '203c': (4, 0), '2049': (4, 0), '2753': (2, 0), '2754': (2, 2), '2755': (2, 2), '2757': (2, 0), '3030': (1, 0), '1f4b1': (4, 2), '1f4b2': (1, 2)}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-symbol-marks-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
 count,letters=SYMBOLS[key];assert len(shapes)==count
 lettering=None
 enclosure=None
 for i,e in enumerate(shapes):
  if i not in [enclosure,*letters]:parents[e].remove(e);continue
  e.attrib.pop('style',None)
  dark=(i!=enclosure)
  e.set('fill','#111111' if dark else '#ffffff');e.set('stroke','#111111' if i==enclosure else 'none')
  if i==enclosure:e.set('stroke-width','1.3');e.set('stroke-linecap','round');e.set('stroke-linejoin','round')
  if key in {'2754','2755'}:e.set('fill','#ffffff');e.set('stroke','#111111');e.set('stroke-width','1.8');e.set('stroke-linejoin','round')
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 # Moderate correlated variation retains the conventional symbol anatomy.
 im,r=translate(mask,Settings(strength=1.7,seed=seed,pressure=.25,taper=.1,bend=.004));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink)
 r.update(key=key,source=source,sourcePixels=1536,symbolPaths=letters,enclosurePath=enclosure,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 r['comicLettering']=lettering
 return (white,ink),r

RECIPES=SYMBOLS
