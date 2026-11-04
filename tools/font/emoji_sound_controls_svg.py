"""Reviewed sound controls preserving slider scales and knob pointers."""
import copy,hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from pen_translate import Settings,translate
from emoji_activity_svg import leg_union
ROOT=Path(__file__).resolve().parents[2]
# Explicit native geometry; black knobs retain white direction indicators.
RECIPES={'1f39a':(29,{},[1]),'1f39b':(61,{},[0])}
INK={'1f39a':{2,27},'1f39b':{2,16,32,47,*range(4,15),*range(18,29),*range(35,46),*range(50,61)}}
WHITE={'1f39a':set(),'1f39b':{3,17,33,48}}
STROKES={'1f39a':set(range(4,26)),'1f39b':set()}

RECIPES.update({
 '1f507':(14,{13:'red'},[0,8,9]),'1f508':(13,{},[0,8,9]),
 '1f509':(14,{},[0,8,9]),'1f50a':(15,{},[0,8,9]),
 '1f514':(9,{},[0,2,6]),'1f515':(18,{1:'red',15:'red'},[4,5,7,11]),
 '1f399':(38,{},[0]),'1f4e2':(19,{},[0,5,7,10,13]),
 '1f4e3':(13,{},[0,3,5,8]),'1f4ef':(15,{},[0,1,10])})
INK.update({key:{5} for key in ['1f507','1f508','1f509','1f50a']})
INK.update({'1f514':{3},'1f515':{8},'1f399':{2,*range(3,24),*range(25,30),*range(33,38)},'1f4e2':{8,14},'1f4e3':{9},'1f4ef':{3,5,11,13}})
STROKES.update({'1f509':{13},'1f50a':{13,14},'1f4ef':{2,4}})
UNIONS={key:{0:(0,1,3,6),5:(4,5,7)} for key in ['1f507','1f508','1f509','1f50a']}
UNIONS['1f4ef']={0:(0,)}

def raster(root):
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128

REVIEWED_TOPOLOGY={'1f39a': (22, 1), '1f39b': (49, 1), '1f507': (1, 5), '1f508': (2, 3), '1f514': (2, 4), '1f515': (1, 10), '1f399': (8, 2), '1f4e2': (2, 5), '1f4e3': (2, 5), '1f4ef': (2, 3), '1f509': (5, 3), '1f50a': (7, 3)}
REVIEWED_REGIONS={'1f39a': (1, []), '1f39b': (1, []), '1f507': (5, [[1]]), '1f508': (3, []), '1f514': (4, []), '1f515': (10, [[1, 3, 4]]), '1f399': (3, []), '1f4e2': (5, []), '1f4e3': (5, []), '1f4ef': (3, []), '1f509': (3, []), '1f50a': (3, [])}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-sound-controls-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 masks=[];count,paths,paper=RECIPES[key];colour_names=list(dict.fromkeys(paths.values()))
 for mode in [None,*colour_names]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==count
  if key in {'1f509','1f50a'}:
   root.set('viewBox','0 -8 144 144')
   for index in STROKES[key]:shapes[index].set('transform','translate(12 -8)')
  for index,parts in UNIONS.get(key,{}).items():
   shapes[index].tag='{http://www.w3.org/2000/svg}path';shapes[index].set('d',leg_union(raw,parts))
  for i,e in enumerate(shapes):
   if i not in paths and i not in paper and i not in INK.get(key,set()) and i not in WHITE.get(key,set()) and i not in STROKES.get(key,set()):parents[e].remove(e);continue
   e.attrib.pop('style',None);e.attrib.pop('opacity',None)
   e.set('fill','#111111' if mode is not None and paths.get(i)==mode else '#ffffff');e.set('stroke','none')
   if i in STROKES.get(key,set()):
    if key in {'1f509','1f50a'} and mode is None:
     halo=copy.deepcopy(e);halo.set('fill','none');halo.set('stroke','#ffffff');halo.set('stroke-width','7');halo.set('stroke-linecap','round')
     parent=parents[e];parent.insert(list(parent).index(e),halo)
    e.set('fill','none');e.set('stroke','#111111' if mode is None else '#ffffff');e.set('stroke-width','1.3' if key=='1f39a' else '2');e.set('stroke-linecap','round')
   elif i in INK.get(key,set()):e.set('fill','#111111' if mode is None else '#ffffff')
   elif i in WHITE.get(key,set()):
    e.set('stroke','#ffffff');e.set('stroke-width','1.8');e.set('stroke-linecap','round');e.set('stroke-linejoin','round')
   elif (i in paper or i in paths) and mode is None:
    e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  masks.append(raster(root))
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 removed_pixels=0
 if key in {'1f509','1f50a'}:
  # Halo intersections can leave isolated raster crumbs, far below a visible feature.
  labels,n=ndimage.label(masks[0]);sizes=np.bincount(labels.ravel())
  crumbs=np.isin(labels,np.flatnonzero((sizes>0)&(sizes<4)))
  removed_pixels=int(crumbs.sum());assert removed_pixels<=8
  masks[0]=masks[0]&~crumbs
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
 palette_path=ROOT/'output/imagegen/emoji-production/heart-palette-source.json';palette_raw=palette_path.read_bytes();palette=json.loads(palette_raw)
 assert hashlib.sha256((ROOT/palette['pdf']).read_bytes()).hexdigest()==palette['pdfSha256']
 rgbs=[next(s['rgb'] for s in palette['samples'] if s['colour']==name) for name in colour_names]
 r.update(removedHaloCrumbPixels=removed_pixels,whitePaths=sorted(WHITE.get(key,set())),whitePointerStroke=1.8,
          strokedPaths=sorted(STROKES.get(key,set())),lineWidth=1.3 if key=='1f39a' else 2,
          waveHaloWidth=7 if key in {'1f509','1f50a'} else 0,
          waveTranslation=[12,-8] if key in {'1f509','1f50a'} else None)
 r.update(inkPaths=sorted(INK.get(key,set())),unionPaths=UNIONS.get(key,{}),unionProgramSha256=hashlib.sha256((ROOT/'tools/font/emoji_activity_svg.py').read_bytes()).hexdigest(),key=key,source=source,sourcePixels=1536,colourPaths=paths,paperPaths=paper,colourRegions=selected_regions,regionCount=n,colourNames=colour_names,rgbs=rgbs,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest(),paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest())
 return (white,*colours,ink),r
