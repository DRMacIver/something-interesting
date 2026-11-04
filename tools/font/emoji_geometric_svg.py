"""Reviewed geometric symbols with PDF-sampled colour."""
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
# Source path colours preserve semantic red and the beginner mark's two halves.
RECIPES={
 '1f536':(4,{0:'orange'},[]),'1f537':(4,{0:'blue'},[]),
 '1f538':(4,{0:'orange'},[]),'1f539':(4,{0:'blue'},[]),
 '1f53a':(3,{0:'red'},[]),'1f53b':(3,{0:'red'},[]),
 '1f4a0':(10,{0:'blue',2:'blue',3:'blue',4:'blue',5:'blue'},[1]),
 '1f518':(6,{},[2]),'1f533':(5,{},[0]),'1f532':(5,{},[2]),
 '1f51f':(5,{},[2,3])}
INK={'1f4a0':{6,7,8,9},'1f518':{0},'1f533':{2},'1f532':{0},'1f51f':{0}}
# Preserve Unicode size distinctions instead of normalising every silhouette.
OPTICAL_HEIGHT={'1f538':300,'1f539':300,'1f53a':450,'1f53b':450}

def raster(root):
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128

REVIEWED_TOPOLOGY={'1f536': (1, 1), '1f537': (1, 1), '1f538': (1, 1), '1f539': (1, 1), '1f53a': (1, 1), '1f53b': (1, 1), '1f4a0': (2, 6), '1f518': (1, 1), '1f533': (2, 1), '1f532': (1, 1), '1f51f': (2, 2)}
REVIEWED_REGIONS={'1f536': (1, [[1]]), '1f537': (1, [[1]]), '1f538': (1, [[1]]), '1f539': (1, [[1]]), '1f53a': (1, [[1]]), '1f53b': (1, [[1]]), '1f4a0': (6, [[1, 2, 3, 4, 6]]), '1f518': (1, []), '1f533': (1, []), '1f532': (1, []), '1f51f': (2, [])}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-geometric-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 masks=[];count,paths,paper=RECIPES[key];colour_names=list(dict.fromkeys(paths.values()))
 for mode in [None,*colour_names]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==count
  lettering=replace_letters(ROOT,key,shapes,[2,3],"10") if key=="1f51f" else None
  for i,e in enumerate(shapes):
   if i not in paths and i not in paper and i not in INK.get(key,set()):parents[e].remove(e);continue
   e.attrib.pop('style',None);e.attrib.pop('opacity',None)
   e.set('fill','#111111' if mode is not None and paths.get(i)==mode else '#ffffff');e.set('stroke','none')
   if i in INK.get(key,set()):
    e.set('fill','#111111' if mode is None else '#ffffff')
   elif mode is None and key!='1f51f':
    e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  masks.append(raster(root))
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 im,r=translate(masks[0],Settings(strength=1.7,seed=seed,pressure=.04 if key in {'1f518','1f532','1f51f'} else .25,taper=.1,bend=.004));ink=np.asarray(im)<128
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
 rgbs=[next(s['rgb'] for s in palette['samples'] if s['colour']==name) for name in colour_names]
 r.update(opticalHeight=OPTICAL_HEIGHT.get(key,760),comicLettering=lettering,inkPaths=sorted(INK.get(key,set())),key=key,source=source,sourcePixels=1536,colourPaths=paths,paperPaths=paper,colourRegions=selected_regions,regionCount=n,colourNames=colour_names,rgbs=rgbs,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest(),paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest())
 return (white,*colours,ink),r
