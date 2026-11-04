"""Reviewed religious and zodiac symbols."""
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
SYMBOLS={'1f6d0': (7, [3, 5, 6]), '269b': (5, [3, 4]), '1f549': (6, [3, 4, 5]), '2721': (4, [3]), '2638': (4, [3]), '262f': (5, [3, 4]), '271d': (4, [3]), '2626': (5, [4]), '262a': (7, [5, 6]), '262e': (6, [5]), '1f54e': (14, [2, 3, 4, 5, 6, 7, 8, 9, 10, 12]), '1f52f': (5, [3, 4]), '1faaf': (4, [3]), '2648': (5, [3]), '2649': (4, [3]), '264a': (5, [3]), '264b': (6, [3, 4]), '264c': (4, [3]), '264d': (5, [3]), '264e': (5, [3, 4]), '264f': (5, [4]), '2650': (4, [3]), '2651': (6, [4]), '2652': (5, [3, 4]), '2653': (5, [3]), '26ce': (4, [3]), '267e': (4, [3])}

REVIEWED_TOPOLOGY={'1f6d0': (4, 1), '269b': (3, 14), '1f549': (4, 1), '2721': (2, 8), '2638': (2, 10), '262f': (3, 3), '271d': (2, 1), '2626': (2, 1), '262a': (3, 1), '262e': (2, 5), '1f54e': (11, 1), '1f52f': (3, 8), '1faaf': (2, 3), '2648': (2, 1), '2649': (2, 2), '264a': (2, 2), '264b': (3, 3), '264c': (2, 2), '264d': (2, 2), '264e': (3, 1), '264f': (2, 1), '2650': (2, 1), '2651': (2, 2), '2652': (3, 1), '2653': (2, 1), '26ce': (2, 2), '267e': (2, 3)}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-symbol-marks-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
 count,letters=SYMBOLS[key];assert len(shapes)==count
 lettering=None
 enclosure=0
 for i,e in enumerate(shapes):
  if i not in [enclosure,*letters]:parents[e].remove(e);continue
  e.attrib.pop('style',None)
  dark=(i!=enclosure)
  e.set('fill','#111111' if dark else '#ffffff');e.set('stroke','#111111' if i==enclosure else 'none')
  if i==enclosure:e.set('stroke-width','1.3');e.set('stroke-linecap','round');e.set('stroke-linejoin','round')
  if key=='1f549' and i==3:e.set('stroke','#111111');e.set('stroke-width','2')
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 # Moderate correlated variation preserves conventional symbol anatomy.
 im,r=translate(mask,Settings(strength=1.7,seed=seed,pressure=.25,taper=.1,bend=.004));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink)
 r.update(key=key,source=source,sourcePixels=1536,symbolPaths=letters,enclosurePath=enclosure,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 r['comicLettering']=lettering
 return (white,ink),r

RECIPES=SYMBOLS
