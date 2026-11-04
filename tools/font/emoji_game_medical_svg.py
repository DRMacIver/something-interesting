"""Reviewed game symbols and medical objects with semantic colours."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from pen_translate import Settings,translate
from emoji_activity_svg import leg_union
ROOT=Path(__file__).resolve().parents[2]
# Source path colours preserve semantic red and the beginner mark's two halves.
RECIPES={
 '2660':(4,{},[]),'2663':(3,{},[]),
 '2665':(2,{0:'red'},[]),'2666':(2,{0:'red'},[]),
 '1fa78':(2,{0:'red'},[]),'1fa79':(4,{},[1]),
 '265f':(13,{},[]),
 '1f004':(9,{5:'red'},[0,2]),
 '1f52b':(14,{0:'green',1:'green',2:'yellow',4:'red',5:'orange',6:'orange',7:'red',8:'yellow',9:'yellow',10:'red',11:'red',12:'red',13:'red'},[])}
INK={'2660':set(range(4)),'2663':set(range(3)),'1fa79':{2,3},'265f':{0,1,2,4,5,6,7,8,9,10,11}}

def raster(root):
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128

REVIEWED_TOPOLOGY={'2660': (1, 0), '2663': (1, 0), '1fa78': (1, 1), '1fa79': (23, 21), '1f004': (5, 5), '1f52b': (2, 20), '2665': (1, 1), '2666': (1, 1), '265f': (1, 0)}
REVIEWED_REGIONS={'2660': (0, []), '2663': (0, []), '1fa78': (1, [[1]]), '1fa79': (21, []), '1f004': (5, [[3]]), '1f52b': (20, [[8, 9], [1, 4, 5], [10, 14, 15, 17, 19, 20], [2, 6, 7, 11, 18]]), '2665': (1, [[1]]), '2666': (1, [[1]]), '265f': (0, [])}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-game-medical-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 masks=[];count,paths,paper=RECIPES[key];colour_names=list(dict.fromkeys(paths.values()))
 for mode in [None,*colour_names]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==count
  if key=='1f004':shapes[5].set('d',leg_union(raw,(5,6,7,8)))
  if key in {'2665','2666'}:shapes[0].set('d',leg_union(raw,(0,1)))
  for i,e in enumerate(shapes):
   if i not in paths and i not in paper and i not in INK.get(key,set()):parents[e].remove(e);continue
   e.attrib.pop('style',None);e.attrib.pop('opacity',None)
   e.set('fill','#111111' if mode is not None and paths.get(i)==mode else '#ffffff');e.set('stroke','none')
   if i in INK.get(key,set()):e.set('fill','#111111' if mode is None else '#ffffff')
   elif mode is None:
    e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  masks.append(raster(root))
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 im,r=translate(masks[0],Settings(strength=1.7,seed=seed,pressure=.04 if key in {'265f','2660','2663'} else .25,taper=.1,bend=.004));ink=np.asarray(im)<128
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
 r.update(inkPaths=sorted(INK.get(key,set())),unionPaths=[5,6,7,8] if key=='1f004' else [0,1] if key in {'2665','2666'} else [],unionProgramSha256=hashlib.sha256((ROOT/'tools/font/emoji_activity_svg.py').read_bytes()).hexdigest(),key=key,source=source,sourcePixels=1536,colourPaths=paths,paperPaths=paper,colourRegions=selected_regions,regionCount=n,colourNames=colour_names,rgbs=rgbs,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest(),paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest())
 return (white,*colours,ink),r
