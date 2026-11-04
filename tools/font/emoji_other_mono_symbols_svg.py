"""Reviewed other monochrome symbols."""
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
SYMBOLS={'2705': (4, [3]), '2611': (4, [3]), '2714': (4, [0]), '274e': (5, [3]), '27b0': (8, [2]), '27bf': (11, [3]), '303d': (5, [1]), '2733': (5, [4]), '2734': (12, [11]), '2747': (5, [4]), '00a9': (8, [1, 5]), '00ae': (10, [5, 6]), '2122': (10, [5, 6])}
WORDS={'00a9':('C',[5]),'00ae':('R',[6]),'2122':('TM',[5,6])}
NEGATIVE={'2705','274e'}
TILES={'2705','2611','274e','2733','2734','2747'}

REVIEWED_TOPOLOGY={'2705': (1, 1), '2611': (2, 1), '2714': (1, 0), '274e': (1, 1), '27b0': (1, 1), '27bf': (1, 2), '303d': (1, 0), '2733': (2, 1), '2734': (2, 1), '2747': (2, 1), '00a9': (2, 1), '00ae': (2, 2), '2122': (2, 0)}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-signs-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
 count,letters=SYMBOLS[key];assert len(shapes)==count
 lettering=replace_letters(ROOT,key,shapes,WORDS[key][1],WORDS[key][0]) if key in WORDS else None
 enclosure=0 if key in TILES else None
 for i,e in enumerate(shapes):
  if i not in [enclosure,*letters]:parents[e].remove(e);continue
  e.attrib.pop('style',None)
  dark=(i==enclosure) if key in NEGATIVE else (i!=enclosure)
  e.set('fill','#111111' if dark else '#ffffff');e.set('stroke','#111111' if i==enclosure else 'none')
  if i==enclosure:e.set('stroke-width','1.3');e.set('stroke-linecap','round');e.set('stroke-linejoin','round')
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 # Moderate correlated variation preserves conventional symbol anatomy.
 im,r=translate(mask,Settings(strength=1.7,seed=seed,pressure=.04 if key in NEGATIVE else .25,taper=.1,bend=.004));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink)
 r.update(key=key,source=source,sourcePixels=1536,symbolPaths=letters,enclosurePath=enclosure,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 r['comicLettering']=lettering
 return (white,ink),r

RECIPES=SYMBOLS
