"""Shared source-specific SVG-to-ink recipe engine.

Recipes choose semantic paths explicitly. Every raster cleanup is bounded per
source; topology-preserving pen backoff never accepts an unchanged fallback.
"""
import copy,hashlib,json,io,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from pen_translate import Settings,translate
from emoji_tile_lettering import replace_letters
from svg_recipe_checks import selected_strokes


def raster(root):
 raw=subprocess.run(['rsvg-convert','-w','1536','-h','1536'],input=ET.tostring(root),stdout=subprocess.PIPE,check=True).stdout
 rgba=Image.open(io.BytesIO(raw)).convert('RGBA');canvas=Image.new('RGBA',rgba.size,'white');canvas.alpha_composite(rgba)
 return np.asarray(canvas.convert('RGB')).max(axis=2)<128


def prepare_recipe(ROOT,key,source_manifest,RECIPES,STROKE_PATHS,LETTER_PATHS,
                   pinhole_limits,crumb_limits,program_path,stroke_styles=None,boundary_blur=.45):
 stroke_styles=stroke_styles or {}
 spec=json.loads((ROOT/source_manifest).read_text())
 source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 count,paper_paths,ink_paths,cutouts,colour_paths=RECIPES[key]
 names=list(dict.fromkeys(colour_paths.values()));masks=[];lettering=None
 for mode in [None,*names]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
  shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
  assert len(shapes)==count,(key,len(shapes),count)
  if key in LETTER_PATHS:
   indices,text=LETTER_PATHS[key];lettering=replace_letters(ROOT,key,shapes,indices,text)
  if mode is None:
   selected_strokes(root,RECIPES[key],STROKE_PATHS.get(key,set()),LETTER_PATHS.get(key,([],''))[0])
  for i,e in enumerate(shapes):
   if i not in paper_paths and i not in ink_paths and i not in cutouts and i not in colour_paths and i not in STROKE_PATHS.get(key,set()):
    parents[e].remove(e);continue
   e.attrib.pop('style',None);e.attrib.pop('opacity',None)
   e.set('stroke','none');e.set('fill','#ffffff')
   if i in STROKE_PATHS.get(key,set()):
    e.set('fill','none');e.set('stroke','#111111' if mode is None else '#ffffff');e.set('stroke-width','1.3');e.set('stroke-linecap','round');e.set('stroke-linejoin','round')
    if i in stroke_styles:
     style=stroke_styles[i];width=float(style['width']);colour=style['colour']
     assert width>0 and colour_paths.get(i)==colour
     if mode is None:
      # Preserve a coloured stroke as a hollow ink outline, rather than
      # closing its open centreline into a filled polygon.
      e.set('stroke-width',str(width+1.3))
      inner=copy.deepcopy(e);inner.set('stroke','#ffffff');inner.set('stroke-width',str(width))
      parent=parents[e];parent.insert(list(parent).index(e)+1,inner)
     else:
      e.set('stroke','#111111' if mode==colour else '#ffffff')
      e.set('stroke-width',str(width))
   elif mode is not None:
    if colour_paths.get(i)==mode:e.set('fill','#111111')
   elif i in ink_paths:e.set('fill','#111111')
   elif i not in cutouts:
    e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  # Selected ink marks must stay opaque even when the donor groups use
  # faded print. Preserve display/transform/clip properties and remove only
  # opacity; otherwise the parcel handling marks fall below raster threshold.
  for group in root.iter():
   if group.tag.split('}')[-1]!='g':continue
   for attr in ['opacity','fill-opacity','stroke-opacity']:group.attrib.pop(attr,None)
   if 'style' in group.attrib:
    group.set('style',';'.join(rule for rule in group.get('style','').split(';') if rule.split(':',1)[0].strip() not in {'opacity','fill-opacity','stroke-opacity'}))
  masks.append(raster(root))
 # Sub-four-pixel pinholes at 1536px arise at overlapping antialiased
 # borders; no visible source counter occupies so little area. Bound cleanup.
 removed_crumbs=0
 if key in crumb_limits:
  component_labels,n=ndi.label(masks[0]);component_sizes=np.bincount(component_labels.ravel())
  crumbs=np.isin(component_labels,np.flatnonzero((component_sizes>0)&(component_sizes<4)))
  removed_crumbs=int(crumbs.sum());assert removed_crumbs<=crumb_limits[key]
  masks[0] &= ~crumbs
 holes=ndi.binary_fill_holes(masks[0])&~masks[0]
 hole_labels,n=ndi.label(holes);hole_sizes=np.bincount(hole_labels.ravel())
 cutoff,limit=pinhole_limits.get(key,(4,16))
 pinholes=np.isin(hole_labels,np.flatnonzero((hole_sizes>0)&(hole_sizes<cutoff)))
 filled=int(pinholes.sum());assert filled<=limit,(key,filled)
 masks[0] |= pinholes
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 image,report=translate(masks[0],Settings(strength=1.7,seed=seed,pressure=.04,taper=0,bend=.001,boundary_blur=boundary_blur))
 assert report['appliedStrength']>0 and not report['fallback'],key
 ink=np.asarray(image)<128;paper=ndi.binary_fill_holes(ink)
 labels,n=ndi.label(paper&~ink);sizes=np.bincount(labels.ravel());colours=[]
 for mask in masks[1:]:
  material=np.pad(mask,report['padding']);overlaps=np.bincount(labels[material],minlength=n+1)
  selected=[i for i in range(1,n+1) if sizes[i]>=32 and overlaps[i]/sizes[i]>.5]
  assert selected,(key,names,n)
  colours.append(ndi.binary_dilation(np.isin(labels,selected),iterations=3)&paper&~((labels>0)&~np.isin(labels,selected)))
 palette_path=ROOT/'output/imagegen/emoji-production/heart-palette-source.json';palette_raw=palette_path.read_bytes();palette=json.loads(palette_raw)
 assert hashlib.sha256((ROOT/palette['pdf']).read_bytes()).hexdigest()==palette['pdfSha256']
 samples={e['colour']:e['rgb'] for e in palette['samples']}
 rgbs=[(255,255,255) if name=='white' else tuple(samples[name]) for name in names]
 report.update(strokeStyles=stroke_styles,removedRasterCrumbPixels=removed_crumbs,lettering=lettering,filledRasterPinholePixels=filled,key=key,source=source,rgbs=rgbs,colourNames=names,paletteSha256=hashlib.sha256(palette_raw).hexdigest(),programSha256=hashlib.sha256(program_path.read_bytes()).hexdigest(),recipeEngineSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 return (paper,*colours,ink),report


