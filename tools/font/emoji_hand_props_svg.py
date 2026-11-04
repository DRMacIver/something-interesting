"""Reviewed hand props with separate exposed-skin and object masks."""
import hashlib,json,io,subprocess
from functools import lru_cache
from skimage.measure import find_contours,approximate_polygon
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from pen_translate import Settings,translate
from emoji_tile_lettering import replace_letters
ROOT=Path(__file__).resolve().parents[2]
# Source path colours preserve semantic red and the beginner mark's two halves.
RECIPES={'270d':(11,{0:'skin'},[9]),'1f485':(30,{0:'skin',13:'red',14:'red',15:'red',27:'red'},[22,24]),'1f933':(13,{8:'skin'},[0,4])}
INK={'270d':{7},'1f485':{1,2,3,23},'1f933':{2,5,7,12}}

def raster(root):
 # These sources use clipping to put the pen behind the thumb. librsvg keeps
 # those clips; the generic PDF conversion loses this important overlap.
 root.set('width','1536');root.set('height','1536')
 raw=subprocess.run(['rsvg-convert','-w','1536','-h','1536'],input=ET.tostring(root),stdout=subprocess.PIPE,check=True).stdout
 rgba=Image.open(io.BytesIO(raw)).convert('RGBA');canvas=Image.new('RGBA',rgba.size,'white');canvas.alpha_composite(rgba)
 return np.asarray(canvas.convert('RGB')).max(axis=2)<128

@lru_cache(maxsize=8)
def clipped_pen_path(raw):
 root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
 shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
 for i,e in enumerate(shapes):
  parent=parents.get(e);definition=False
  while parent is not None:
   if parent.tag.split('}')[-1] in {'defs','clipPath'}:definition=True
   parent=parents.get(parent)
  if definition:continue
  if i!=9:parents[e].remove(e)
  else:e.attrib.pop('style',None);e.set('fill','#000');e.set('stroke','none')
 mask=raster(root);paths=[]
 for contour in find_contours(np.pad(mask.astype(float),1),.5):
  contour=approximate_polygon(contour,tolerance=.65)
  if len(contour)<4:continue
  paths.append('M'+' L'.join(f'{(x-1)/12:.4f},{(y-1)/12:.4f}' for y,x in contour)+' Z')
 return ' '.join(paths)

REVIEWED_TOPOLOGY={'270d': (1, 8), '1f485': (1, 9), '1f933': (2, 5)}
REVIEWED_REGIONS={'270d': (8, [[2, 3, 4, 6, 7, 8]]), '1f485': (10, [[4, 6, 10], [2, 5, 7, 8]]), '1f933': (5, [[2]])}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-hand-props-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 masks=[];count,paths,paper=RECIPES[key];colour_names=list(dict.fromkeys(paths.values()))
 for mode in [None,*colour_names]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==count
  if key=='270d':
   # Flatten the clipped pen silhouette before outlining it, so the thumb
   # occlusion creates a closed boundary between the skin and the pen.
   parents[shapes[9]].remove(shapes[9]);root.append(shapes[9]);parents[shapes[9]]=root
   shapes[9].set('d',clipped_pen_path(raw))
  for i,e in enumerate(shapes):
   ancestor=parents.get(e);definition=False
   while ancestor is not None:
    if ancestor.tag.split('}')[-1] in {'defs','clipPath'}:definition=True
    ancestor=parents.get(ancestor)
   if definition:continue
   if i not in paths and i not in paper and i not in INK.get(key,set()):parents[e].remove(e);continue
   style=e.attrib.pop('style','');e.attrib.pop('opacity',None)
   retained=';'.join(part for part in style.split(';') if part.strip().startswith('clip-path:'))
   if retained:e.set('style',retained)
   e.set('fill','#111111' if mode is not None and paths.get(i)==mode else '#ffffff');e.set('stroke','none')
   if i in INK.get(key,set()):e.set('fill','#111111' if mode is None else '#ffffff')
   elif mode is None:
    e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  masks.append(raster(root))
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 im,r=translate(masks[0],Settings(strength=1.7,seed=seed,pressure=.25,taper=.1,bend=.004));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 if key in REVIEWED_TOPOLOGY:assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink);labels,n=ndimage.label(white&~ink);sizes=np.bincount(labels.ravel());colours=[];selected_regions=[]
 for mask in masks[1:]:
  material=np.pad(mask,r['padding']);overlaps=np.bincount(labels[material],minlength=n+1)
  selected=[i for i in range(1,n+1) if sizes[i]>=32 and overlaps[i]/sizes[i]>.5]
  assert selected,(key,n)
  colour=np.isin(labels,selected);colour=ndimage.binary_dilation(colour,iterations=3)&white&~((labels>0)&~np.isin(labels,selected));colours.append(colour);selected_regions.append(selected)
 if key in REVIEWED_REGIONS:assert (n,selected_regions)==REVIEWED_REGIONS[key],(key,n,selected_regions)
 assert len({i for region in selected_regions for i in region})==sum(map(len,selected_regions))
 palette_path=ROOT/'output/imagegen/emoji-production/heart-palette-source.json';palette_raw=palette_path.read_bytes();palette=json.loads(palette_raw)
 assert hashlib.sha256((ROOT/palette['pdf']).read_bytes()).hexdigest()==palette['pdfSha256']
 skin_path=ROOT/'output/imagegen/emoji-production/skin-palette-source.json';skin_raw=skin_path.read_bytes();skin_palette=json.loads(skin_raw)
 assert hashlib.sha256((ROOT/skin_palette['pdf']).read_bytes()).hexdigest()==skin_palette['pdfSha256']
 rgbs=[skin_palette['skinTones'][2] if name=='skin' else next(s['rgb'] for s in palette['samples'] if s['colour']==name) for name in colour_names]
 r.update(rasterizer=subprocess.check_output(['rsvg-convert','--version'],text=True).strip(),clippedPenFlattened=key=='270d',skinPaletteSha256=hashlib.sha256(skin_raw).hexdigest(),inkPaths=sorted(INK[key]),key=key,source=source,sourcePixels=1536,colourPaths=paths,paperPaths=paper,colourRegions=selected_regions,regionCount=n,colourNames=colour_names,rgbs=rgbs,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest(),paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest())
 return (white,*colours,ink),r
