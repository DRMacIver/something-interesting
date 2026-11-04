"""Reviewed alphanumeric emoji ink translation."""
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
# Unicode's negative squared letters retain white letters on a black tile.
NEGATIVE={'1f170','1f171','1f17e','1f17f','1f18e'}
# Reviewed source letter paths, excluding gloss, shadow and duplicate backgrounds.
LETTERS={'1f520':(7,[3,4,5,6]),'1f521':(8,[4,5,6,7]),'1f522':(7,[3,4,5,6]),'1f523':(8,[3,4,5,6,7]),'1f524':(6,[3,4,5]),'1f170':(4,[3]),'1f18e':(5,[3,4]),'1f171':(4,[3]),'1f191':(5,[3,4]),'1f192':(7,[3,4,5,6]),'1f193':(7,[3,4,5,6]),'2139':(5,[2,3]),'1f194':(5,[3,4]),'24c2':(5,[3]),'1f195':(6,[3,4,5]),'1f196':(5,[3,4]),'1f17e':(4,[3]),'1f197':(5,[3,4]),'1f17f':(4,[2]),'1f198':(6,[3,4,5]),'1f199':(6,[3,4,5]),'1f19a':(5,[3,4]),'1f201':(4,[2]),'1f202':(4,[2]),'1f237':(4,[2]),'1f236':(4,[2]),'1f22f':(4,[2]),'1f250':(5,[3]),'1f239':(4,[2]),'1f21a':(4,[2]),'1f232':(4,[2]),'1f251':(5,[3]),'1f238':(4,[2]),'1f234':(4,[2]),'1f233':(4,[2]),'3297':(5,[3]),'3299':(5,[3]),'1f23a':(5,[2,3]),'1f235':(4,[2])}

REVIEWED_TOPOLOGY={'1f520': (5, 5), '1f521': (5, 4), '1f522': (5, 2), '1f523': (8, 5), '1f524': (4, 3), '1f170': (2, 1), '1f18e': (4, 2), '1f171': (3, 1), '1f191': (3, 1), '1f192': (5, 3), '1f193': (5, 2), '2139': (3, 1), '1f194': (3, 2), '24c2': (2, 1), '1f195': (4, 1), '1f196': (3, 1), '1f17e': (2, 1), '1f197': (3, 2), '1f17f': (2, 1), '1f198': (4, 2), '1f199': (5, 2), '1f19a': (3, 1), '1f201': (3, 1), '1f202': (2, 1), '1f237': (2, 3), '1f236': (2, 3), '1f22f': (4, 3), '1f250': (6, 3), '1f239': (6, 2), '1f21a': (6, 7), '1f232': (7, 1), '1f251': (3, 2), '1f238': (2, 5), '1f234': (4, 2), '1f233': (3, 1), '3297': (3, 2), '3299': (5, 1), '1f23a': (3, 3), '1f235': (5, 2)}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-symbol-tiles-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
 count,letters=LETTERS[key];assert len(shapes)==count
 lettering=replace_letters(ROOT,key,shapes,letters)
 for i,e in enumerate(shapes):
  if i not in [0,*letters]:parents[e].remove(e);continue
  e.attrib.pop('style',None)
  dark=(i!=0) if key not in NEGATIVE else (i==0)
  e.set('fill','#111111' if dark else '#ffffff');e.set('stroke','#111111' if i==0 else 'none')
  if i==0:e.set('stroke-width','1.3');e.set('stroke-linecap','round');e.set('stroke-linejoin','round')
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 # A solid tile has a much larger medial radius than a pen stroke: cap its
 # pressure variation so the enclosure stays square rather than swelling.
 im,r=translate(mask,Settings(strength=1.7,seed=seed,pressure=.04 if key in NEGATIVE else .25,taper=.1,bend=.004));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink)
 r.update(key=key,source=source,sourcePixels=1536,letterPaths=letters,enclosurePath=0,negative=key in NEGATIVE,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 r['comicLettering']=lettering
 return (white,ink),r

RECIPES=LETTERS
