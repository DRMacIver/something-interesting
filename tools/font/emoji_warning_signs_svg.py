"""Reviewed warning signs with source anatomy and PDF-sampled colour."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from pen_translate import Settings,translate
from emoji_tile_lettering import replace_letters
ROOT=Path(__file__).resolve().parents[2]
# Total source shapes, pictogram paths; enclosure is always source shape zero.
RECIPES={'26a0':(8,[2,3]),'1f6b8':(12,[2,3,4,5]),'26d4':(4,[3]),'1f6ab':(4,[]),'1f6b3':(10,[5]),'1f6ad':(13,[5,6,7]),'1f6af':(14,[5,6,7,8,9]),'1f6b1':(11,[5,6]),'1f6b7':(11,[5,6]),'1f4f5':(10,[5]),'1f51e':(16,[5,6,7,8,9,10,11]),'2622':(8,[2,3,4,6]),'2623':(5,[3])}
YELLOW={'26a0','1f6b8','2622','2623'}

REVIEWED_TOPOLOGY={'26a0': (3, 1), '1f6b8': (4, 2), '26d4': (2, 2), '1f6ab': (3, 3), '1f6b3': (3, 8), '1f6ad': (4, 3), '1f6af': (7, 3), '1f6b1': (4, 4), '1f6b7': (4, 3), '1f4f5': (3, 8), '1f51e': (7, 7), '2622': (5, 1), '2623': (7, 1)}
REVIEWED_REGIONS={'26a0': (1, [1]), '1f6b8': (2, [1, 2]), '26d4': (2, [1]), '1f6ab': (3, [1]), '1f6b3': (8, [1]), '1f6ad': (3, [1]), '1f6af': (3, [1]), '1f6b1': (4, [1]), '1f6b7': (3, [1]), '1f4f5': (8, [1]), '1f51e': (7, [1]), '2622': (1, [1]), '2623': (1, [1])}

def raster(root):
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-signs-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 masks=[];lettering=None;count,icons=RECIPES[key]
 for material in [False,True]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==count
  if key=='1f51e':
   lettering=[replace_letters(ROOT,key,shapes,[6,5],'18'),replace_letters(ROOT,key,shapes,[10,11,9,8,7],'UNDER')]
  for i,e in enumerate(shapes):
   if i not in [0,*icons]:parents[e].remove(e);continue
   e.attrib.pop('style',None);e.attrib.pop('opacity',None)
   dark=(i==0) if material else (i!=0 and key!='26d4')
   e.set('fill','#111111' if dark else '#ffffff');e.set('stroke','none')
   if not material and (i==0 or key=='26d4'):
    e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  # The combined prohibition ring/slash must occlude the central pictogram.
  if key not in YELLOW and key!='26d4':
   parents[shapes[0]].remove(shapes[0]);root.append(shapes[0])
  masks.append(raster(root))
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 im,r=translate(masks[0],Settings(strength=1.7,seed=seed,pressure=.25,taper=.1,bend=.004));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink);material=np.pad(masks[1],r['padding']);labels,n=ndimage.label(white&~ink)
 sizes=np.bincount(labels.ravel());overlaps=np.bincount(labels[material],minlength=n+1)
 selected=[i for i in range(1,n+1) if sizes[i]>=32 and overlaps[i]/sizes[i]>.5]
 assert (n,selected)==REVIEWED_REGIONS[key],(key,n,selected)
 colour=np.isin(labels,selected);colour=ndimage.binary_dilation(colour,iterations=3)&white&~((labels>0)&~np.isin(labels,selected))
 palette_path=ROOT/'output/imagegen/emoji-production/heart-palette-source.json';palette_raw=palette_path.read_bytes();palette=json.loads(palette_raw)
 assert hashlib.sha256((ROOT/palette['pdf']).read_bytes()).hexdigest()==palette['pdfSha256']
 colour_name='yellow' if key in YELLOW else 'red';rgb=next(s['rgb'] for s in palette['samples'] if s['colour']==colour_name)
 r.update(key=key,source=source,sourcePixels=1536,symbolPaths=icons,enclosurePath=0,colourRegions=selected,regionCount=n,colourName=colour_name,rgb=rgb,comicLettering=lettering,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest(),paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest())
 return (white,colour,ink),r
