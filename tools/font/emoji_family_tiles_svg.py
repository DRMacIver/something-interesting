"""Reviewed family tiles preserving every adult and child silhouette."""
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
RECIPES={'1f468_200d_1f469_200d_1f466': (10, [0], [3, 4, 5, 6, 7, 8, 9]), '1f468_200d_1f469_200d_1f467': (9, [0], [3, 4, 5, 6, 7, 8]), '1f468_200d_1f469_200d_1f467_200d_1f466': (12, [0], [3, 4, 5, 6, 7, 8, 9, 10, 11]), '1f468_200d_1f469_200d_1f466_200d_1f466': (12, [0], [3, 4, 5, 6, 7, 8, 9, 10, 11]), '1f468_200d_1f469_200d_1f467_200d_1f467': (12, [0], [3, 4, 5, 6, 7, 8, 9, 10, 11]), '1f468_200d_1f468_200d_1f466': (9, [0], [3, 4, 5, 6, 7, 8]), '1f468_200d_1f468_200d_1f467': (9, [0], [3, 4, 5, 6, 7, 8]), '1f468_200d_1f468_200d_1f467_200d_1f466': (12, [0], [3, 4, 5, 6, 7, 8, 9, 10, 11]), '1f468_200d_1f468_200d_1f466_200d_1f466': (12, [0], [3, 4, 5, 6, 7, 8, 9, 10, 11]), '1f468_200d_1f468_200d_1f467_200d_1f467': (12, [0], [3, 4, 5, 6, 7, 8, 9, 10, 11]), '1f469_200d_1f469_200d_1f466': (9, [0], [3, 4, 5, 6, 7, 8]), '1f469_200d_1f469_200d_1f467': (9, [0], [3, 4, 5, 6, 7, 8]), '1f469_200d_1f469_200d_1f467_200d_1f466': (12, [0], [3, 4, 5, 6, 7, 8, 9, 10, 11]), '1f469_200d_1f469_200d_1f466_200d_1f466': (12, [0], [3, 4, 5, 6, 7, 8, 9, 10, 11]), '1f469_200d_1f469_200d_1f467_200d_1f467': (12, [0], [3, 4, 5, 6, 7, 8, 9, 10, 11]), '1f468_200d_1f466': (7, [0], [3, 4, 5, 6]), '1f468_200d_1f466_200d_1f466': (10, [0], [3, 4, 5, 6, 7, 8, 9]), '1f468_200d_1f467': (7, [0], [3, 4, 5, 6]), '1f468_200d_1f467_200d_1f466': (10, [0], [3, 4, 5, 6, 7, 8, 9]), '1f468_200d_1f467_200d_1f467': (10, [0], [3, 4, 5, 6, 7, 8, 9]), '1f469_200d_1f466': (7, [0], [3, 4, 5, 6]), '1f469_200d_1f466_200d_1f466': (10, [0], [3, 4, 5, 6, 7, 8, 9]), '1f469_200d_1f467': (7, [0], [3, 4, 5, 6]), '1f469_200d_1f467_200d_1f466': (10, [0], [3, 4, 5, 6, 7, 8, 9]), '1f469_200d_1f467_200d_1f467': (10, [0], [3, 4, 5, 6, 7, 8, 9])}
REVIEWED_TOPOLOGY={'1f468_200d_1f469_200d_1f466': (7, 1), '1f468_200d_1f469_200d_1f467': (7, 1), '1f468_200d_1f469_200d_1f467_200d_1f466': (10, 1), '1f468_200d_1f469_200d_1f466_200d_1f466': (10, 1), '1f468_200d_1f469_200d_1f467_200d_1f467': (10, 1), '1f468_200d_1f468_200d_1f466': (7, 1), '1f468_200d_1f468_200d_1f467': (7, 1), '1f468_200d_1f468_200d_1f467_200d_1f466': (10, 1), '1f468_200d_1f468_200d_1f466_200d_1f466': (10, 1), '1f468_200d_1f468_200d_1f467_200d_1f467': (10, 1), '1f469_200d_1f469_200d_1f466': (7, 1), '1f469_200d_1f469_200d_1f467': (7, 1), '1f469_200d_1f469_200d_1f467_200d_1f466': (10, 1), '1f469_200d_1f469_200d_1f466_200d_1f466': (10, 1), '1f469_200d_1f469_200d_1f467_200d_1f467': (10, 1), '1f468_200d_1f466': (5, 1), '1f468_200d_1f466_200d_1f466': (8, 1), '1f468_200d_1f467': (5, 1), '1f468_200d_1f467_200d_1f466': (8, 1), '1f468_200d_1f467_200d_1f467': (8, 1), '1f469_200d_1f466': (5, 1), '1f469_200d_1f466_200d_1f466': (8, 1), '1f469_200d_1f467': (5, 1), '1f469_200d_1f467_200d_1f466': (8, 1), '1f469_200d_1f467_200d_1f467': (8, 1)}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-family-tiles-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
 count,paper,solid=RECIPES[key];assert len(shapes)==count
 for i,e in enumerate(shapes):
  if i not in paper and i not in solid:parents[e].remove(e);continue
  e.attrib.pop('style',None)
  e.set('fill','#111111' if i in solid else '#ffffff');e.set('stroke','none')
  if i in paper:
   e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linecap','round');e.set('stroke-linejoin','round')
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 # Moderate correlated variation preserves conventional symbol anatomy.
 im,r=translate(mask,Settings(strength=1.7,seed=seed,pressure=.04,taper=0,bend=.001));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 if key in REVIEWED_TOPOLOGY:assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink)
 r.update(key=key,source=source,sourcePixels=1536,solidPaths=solid,paperPaths=paper,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 return (white,ink),r

