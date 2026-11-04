"""Reviewed expressive kissing and heart couples with independent skin masks."""
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
RECIPES={'1f48f': (30, {0: 'left', 12: 'right', 25: 'red'}, []), '1f469_200d_2764_200d_1f48b_200d_1f468': (25, {2: 'left', 11: 'right', 20: 'red'}, []), '1f468_200d_2764_200d_1f48b_200d_1f468': (23, {0: 'left', 9: 'right', 18: 'red'}, []), '1f469_200d_2764_200d_1f48b_200d_1f469': (27, {2: 'left', 13: 'right', 22: 'red'}, []), '1f491': (53, {8: 'right', 9: 'right', 10: 'right', 31: 'left', 33: 'left', 34: 'left', 48: 'red'}, [7, 32]), '1f469_200d_2764_200d_1f468': (29, {2: 'left', 3: 'left', 13: 'right', 14: 'right', 15: 'right', 24: 'red'}, [1, 12]), '1f468_200d_2764_200d_1f468': (29, {1: 'right', 2: 'right', 3: 'right', 13: 'left', 14: 'left', 15: 'left', 24: 'red'}, [0, 12]), '1f469_200d_2764_200d_1f469': (29, {2: 'left', 3: 'left', 14: 'right', 15: 'right', 24: 'red'}, [1, 13])}
INK={'1f48f': {1, 2, 3, 4, 5, 6, 7, 13, 14, 15, 16, 17, 18, 19}, '1f469_200d_2764_200d_1f48b_200d_1f468': {0, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18}, '1f468_200d_2764_200d_1f48b_200d_1f468': {1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16}, '1f469_200d_2764_200d_1f48b_200d_1f469': {0, 3, 4, 5, 6, 7, 8, 9, 11, 14, 15, 16, 17, 18, 19, 20}, '1f491': {0, 35, 36, 37, 38, 39, 40, 41, 11, 12, 13, 14, 15, 16, 17, 24}, '1f469_200d_2764_200d_1f468': {0, 4, 5, 6, 7, 8, 9, 10, 16, 17, 18, 19, 20, 21, 22}, '1f468_200d_2764_200d_1f468': {4, 5, 6, 7, 8, 9, 10, 16, 17, 18, 19, 20, 21, 22}, '1f469_200d_2764_200d_1f469': {0, 4, 5, 6, 7, 8, 9, 10, 12, 16, 17, 18, 19, 20, 21, 22}}

def raster(root):
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128

REVIEWED_TOPOLOGY={'1f48f': (13, 3), '1f469_200d_2764_200d_1f48b_200d_1f468': (13, 3), '1f468_200d_2764_200d_1f48b_200d_1f468': (13, 3), '1f469_200d_2764_200d_1f48b_200d_1f469': (13, 3), '1f491': (15, 11), '1f469_200d_2764_200d_1f468': (15, 9), '1f468_200d_2764_200d_1f468': (15, 11), '1f469_200d_2764_200d_1f469': (15, 7)}
REVIEWED_REGIONS={'1f48f': (3, [[3], [2], [1]]), '1f469_200d_2764_200d_1f48b_200d_1f468': (3, [[2], [3], [1]]), '1f468_200d_2764_200d_1f48b_200d_1f468': (3, [[2], [3], [1]]), '1f469_200d_2764_200d_1f48b_200d_1f469': (3, [[2], [3], [1]]), '1f491': (11, [[2, 5, 6, 10], [3, 4, 7, 11], [1]]), '1f469_200d_2764_200d_1f468': (9, [[2, 6], [3, 4, 5, 9], [1]]), '1f468_200d_2764_200d_1f468': (11, [[3, 5, 7, 10], [2, 4, 6, 11], [1]]), '1f469_200d_2764_200d_1f469': (7, [[2, 4], [3, 5], [1]])}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-couples-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
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
 heart_raw=(ROOT/'output/imagegen/emoji-production/heart-palette-source.json').read_bytes();heart=json.loads(heart_raw)
 assert heart['pdfSha256']==palette['pdfSha256']
 red=next(e['rgb'] for e in heart['samples'] if e['colour']=='red')
 rgbs=[red if name=='red' else palette['skinTones'][0 if name=='left' else 4] for name in colour_names]
 r.update(removedRasterCrumbPixels=removed,filledRasterPinholePixels=filled)
 r.update(heartPaletteSource='output/imagegen/emoji-production/heart-palette-source.json',heartPaletteSha256=hashlib.sha256(heart_raw).hexdigest())
 r.update(inkPaths=sorted(INK.get(key,set())),unionPaths=[],unionProgramSha256=hashlib.sha256((ROOT/'tools/font/emoji_activity_svg.py').read_bytes()).hexdigest(),key=key,source=source,sourcePixels=1536,colourPaths=paths,paperPaths=paper,colourRegions=selected_regions,regionCount=n,colourNames=colour_names,rgbs=rgbs,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest(),paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest())
 return (white,*colours,ink),r
