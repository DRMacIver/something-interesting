"""Reviewed holding-hands families with independent left/right skin masks."""
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
# Skin assignments are verified against opposite light/dark native references.
RECIPES={
 '1f9d1_200d_1f91d_200d_1f9d1':(61,{**dict.fromkeys([33,34,43,44,45],'left'),**dict.fromkeys([0,5,14,15,16,59],'right')},[2,6,30,35]),
 '1f46d':(39,{**dict.fromkeys([22,23,27,28],'left'),**dict.fromkeys([3,4,8,9,37],'right')},[0,7,19,26]),
 '1f46b':(38,{**dict.fromkeys([21,22,26,27],'left'),**dict.fromkeys([0,4,7,8,9,36],'right')},[1,6,18,25]),
 '1f46c':(37,{**dict.fromkeys([18,22,24,25,26],'left'),**dict.fromkeys([0,4,7,8,9,35],'right')},[1,6,19,23])}
INK={
 '1f9d1_200d_1f91d_200d_1f9d1':{3,4,7,17,24,25,26,27,28,29,31,32,36,46,47,54,55,56,57,58,60},
 '1f46d':{1,2,5,10,11,12,13,14,15,17,20,21,24,29,30,31,32,33,34,35,38},
 '1f46b':{2,3,10,11,12,13,14,15,16,19,20,23,28,29,30,31,32,33,34,37},
 '1f46c':{2,3,10,11,12,13,14,15,16,20,21,27,28,29,30,31,32,33,36}}

def raster(root):
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128

REVIEWED_TOPOLOGY={'1f9d1_200d_1f91d_200d_1f9d1': (13, 17), '1f46d': (13, 13), '1f46b': (13, 15), '1f46c': (13, 17)}
REVIEWED_REGIONS={'1f9d1_200d_1f91d_200d_1f9d1': (18, [[1, 3, 5, 9, 12, 15], [2, 4, 6, 8, 13, 14, 18]]), '1f46d': (13, [[1, 4, 7, 10], [2, 3, 8, 9, 13]]), '1f46b': (15, [[1, 6, 9, 12], [2, 3, 4, 5, 10, 11, 15]]), '1f46c': (18, [[2, 3, 6, 9, 12, 15], [1, 4, 5, 8, 13, 14, 18]])}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-holding-hands-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 masks=[];count,paths,paper=RECIPES[key];colour_names=list(dict.fromkeys(paths.values()))
 for mode in [None,*colour_names]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==count
  for i,e in enumerate(shapes):
   if i not in paths and i not in paper and i not in INK.get(key,set()):parents[e].remove(e);continue
   e.attrib.pop('style',None);e.attrib.pop('opacity',None)
   e.set('fill','#111111' if mode is not None and paths.get(i)==mode else '#ffffff');e.set('stroke','none')
   if i in INK.get(key,set()):e.set('fill','#111111' if mode is None else '#ffffff')
   elif mode is None:
    e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  masks.append(raster(root))
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 labels,n=ndimage.label(masks[0]);sizes=np.bincount(labels.ravel())
 crumbs=np.isin(labels,np.flatnonzero((sizes>0)&(sizes<4)))
 removed=int(crumbs.sum());assert removed<=12
 masks[0] &= ~crumbs
 holes=ndimage.binary_fill_holes(masks[0])&~masks[0]
 labels,n=ndimage.label(holes);sizes=np.bincount(labels.ravel())
 pinholes=np.isin(labels,np.flatnonzero((sizes>0)&(sizes<4)))
 filled=int(pinholes.sum());assert filled<=12
 masks[0] |= pinholes
 im,r=translate(masks[0],Settings(strength=1.7,seed=seed,pressure=.04,taper=0,bend=.001));ink=np.asarray(im)<128
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
 palette_path=ROOT/'output/imagegen/emoji-production/skin-palette-source.json';palette_raw=palette_path.read_bytes();palette=json.loads(palette_raw)
 assert hashlib.sha256((ROOT/palette['pdf']).read_bytes()).hexdigest()==palette['pdfSha256']
 rgbs=[palette['skinTones'][0 if name=='left' else 4] for name in colour_names]
 r.update(removedRasterCrumbPixels=removed,filledRasterPinholePixels=filled)
 r.update(inkPaths=sorted(INK.get(key,set())),unionPaths=[],unionProgramSha256=hashlib.sha256((ROOT/'tools/font/emoji_activity_svg.py').read_bytes()).hexdigest(),key=key,source=source,sourcePixels=1536,colourPaths=paths,paperPaths=paper,colourRegions=selected_regions,regionCount=n,colourNames=colour_names,rgbs=rgbs,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest(),paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest())
 return (white,*colours,ink),r
