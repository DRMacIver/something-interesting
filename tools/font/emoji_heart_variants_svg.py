"""Reviewed heart variants with PDF-sampled colour."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from pen_translate import Settings,translate
ROOT=Path(__file__).resolve().parents[2]
# Source colours retain meaningful red/pink heart distinctions.
RECIPES={'2763':(7,{0:'red',2:'red'},[]),'1f494':(6,{0:'red',1:'red'},[]),'1f495':(10,{0:'pink',5:'pink'},[]),'1f493':(13,{0:'pink'},[]),'1f497':(14,{2:'pink'},[1,9]),'1f496':(13,{0:'pink',4:'yellow',5:'yellow',6:'yellow',7:'yellow',10:'yellow'},[]),'1f49e':(12,{2:'pink',7:'pink'},[])}
INK={'1f493':set(range(5,13)),'1f49e':{0,1}}

RECIPES.update({'1f498':(14,{1:'yellow',4:'pink',10:'yellow',11:'yellow'},[]),'1f49d':(19,{0:'pink',5:'yellow',7:'yellow',8:'yellow',10:'yellow',12:'yellow',17:'yellow'},[]),'2764_200d_1f525':(8,{0:'orange',1:'yellow',2:'red',5:'yellow',6:'orange',7:'yellow'},[]),'2764_200d_1fa79':(11,{0:'red'},[4,6])})
INK.update({'1f498':{0,9,12},'1f49d':{11,13}})

def raster(root):
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128

REVIEWED_TOPOLOGY={'2763': (2, 2), '1f494': (2, 2), '1f495': (2, 2), '1f493': (9, 1), '1f497': (3, 3), '1f496': (4, 6), '1f49e': (2, 2), '1f498': (1, 4), '1f49d': (1, 9), '2764_200d_1f525': (1, 7), '2764_200d_1fa79': (1, 6)}
REVIEWED_REGIONS={'2763': (2, [[1, 2]]), '1f494': (2, [[1, 2]]), '1f495': (2, [[1, 2]]), '1f493': (1, [[1]]), '1f497': (3, [[3]]), '1f496': (6, [[2], [1, 3, 4, 5, 6]]), '1f49e': (2, [[1, 2]]), '1f498': (4, [[1, 3, 4], [2]]), '1f49d': (9, [[1, 8, 9], [2, 3, 4, 5, 6, 7]]), '2764_200d_1f525': (7, [[1, 2, 4], [3, 6, 7], [5]]), '2764_200d_1fa79': (6, [[1, 2, 6]])}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-expressions-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 masks=[];count,paths,paper=RECIPES[key];colour_names=list(dict.fromkeys(paths.values()))
 for mode in [None,*colour_names]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==count
  for i,e in enumerate(shapes):
   if i not in paths and i not in paper and i not in INK.get(key,set()):parents[e].remove(e);continue
   e.attrib.pop('style',None);e.attrib.pop('opacity',None)
   e.set('fill','#111111' if mode is not None and paths.get(i)==mode else '#ffffff');e.set('stroke','none')
   if i in INK.get(key,set()):
    e.set('fill','#111111' if mode is None else '#ffffff')
   elif mode is None:
    e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  if key=='1f497':
   # Paint nested silhouettes outside-in; the source's translucent layers
   # are otherwise ordered for shading and obscure the innermost heart.
   for i,factor in [(9,.9),(2,.78)]:shapes[i].set('transform',f'translate(64 64) scale({factor}) translate(-64 -64)')
   for i in [1,9,2]:parents[shapes[i]].remove(shapes[i]);root.append(shapes[i])
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
 rgbs=[next(s['rgb'] for s in palette['samples'] if s['colour']==name) for name in colour_names]
 r.update(key=key,source=source,sourcePixels=1536,colourPaths=paths,inkPaths=sorted(INK.get(key,set())),paperPaths=paper,nestedScales={9:.9,2:.78} if key=='1f497' else {},colourRegions=selected_regions,regionCount=n,colourNames=colour_names,rgbs=rgbs,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest(),paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest())
 return (white,*colours,ink),r
