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
SYMBOLS={'2695':(13,list(range(13))),'267b':(9,list(range(6))),'269c':(12,[0,1,3,4,5,6,7,9]),'1f531':(16,[0,3])}
WORDS={}
NEGATIVE=set()
TILES=set()

REVIEWED_TOPOLOGY={'2695': (1, 5), '267b': (3, 0), '269c': (1, 0), '1f531': (1, 0)}

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
