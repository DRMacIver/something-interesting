"""Reviewed wrestling source experiment."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import pymupdf
from pen_translate import Settings,translate,same_features
ROOT=Path(__file__).resolve().parents[2]
from emoji_activity_svg import leg_union
RECIPES={'1f93c': (46, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 41}, {1, 4, 5, 6, 8, 9, 10, 19, 21, 22, 25, 26, 27, 29, 31, 33, 35, 36, 41}, {0, 2, 3, 7, 11, 12, 13, 16, 17, 18, 20, 23, 24}), '1f93c_200d_2642': (40, {0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 16, 17, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39}, {1, 5, 6, 7, 8, 11, 12, 13, 14, 23, 25, 26, 29, 30, 31, 33, 35, 37, 39}, {0, 2, 3, 4, 10, 16, 17, 20, 21, 22, 24, 27, 28}), '1f93c_200d_2640': (48, {0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 14, 15, 16, 17, 18, 22, 24, 25, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47}, {1, 5, 6, 7, 8, 12, 15, 16, 17, 18, 22, 31, 33, 34, 37, 38, 39, 41, 43, 45, 47}, {0, 32, 2, 3, 4, 35, 36, 14, 24, 25, 28, 29, 30})}
OWNERS={'1f93c': {'left': {0, 2, 3, 11, 13, 17, 23}, 'right': {7, 12, 16, 18, 20, 24}}, '1f93c_200d_2642': {'left': {0, 2, 3, 10, 17, 21, 27}, 'right': {4, 16, 20, 22, 24, 28}}, '1f93c_200d_2640': {'left': {0, 2, 35, 4, 3, 25, 29}, 'right': {32, 36, 14, 24, 28, 30}}}

def prepare(key):
 expected,keep,solid,skin_paths=RECIPES[key]
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-wrestling-fantasy-svg.json').read_text())
 entry=next(e for e in spec['files'] if e['path'].endswith(f'emoji_u{key}.svg'))
 raw=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
 masks=[];pixels=1536;stroke=1.3
 for material in [None,'all','left','right']:
  material_paths=skin_paths if material=='all' else OWNERS[key].get(material,set())
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
  shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==expected,(key,len(shapes),expected)
  for i,e in enumerate(shapes):
   parent=parents.get(e);definition=False
   while parent is not None:
    if parent.tag.split('}')[-1] in {'defs','clipPath'}:definition=True
    parent=parents.get(parent)
   if definition:continue
   if i not in keep:parents[e].remove(e);continue
   merged={}

   if i in merged:e.set('d',leg_union(raw,merged[i]))
   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   black=i in (material_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in material_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  root.set('width',str(pixels));root.set('height',str(pixels))
  doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
  masks.append(np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128)
 removed_specks=0
 removed=0
 if True:
  holes,n=ndimage.label(ndimage.binary_fill_holes(masks[0])&~masks[0]);sizes=np.bincount(holes.ravel())
  tiny=np.isin(holes,[i for i in range(1,n+1) if sizes[i]<4]);clean=masks[0]|tiny
  if same_features(masks[0],clean):removed=int(tiny.sum());masks[0]=clean
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 settings=Settings(strength=1.7,seed=seed,pressure=.025 if key.endswith('2640') else .1,taper=0,bend=.001 if key.endswith('2640') else .012)
 image,report=translate(masks[0],settings)
 assert report["appliedStrength"]>0 and not report["fallback"],key
 ink=np.asarray(image)<128
 removed_after=0
 if True:
  holes,n=ndimage.label(ndimage.binary_fill_holes(ink)&~ink);sizes=np.bincount(holes.ravel())
  tiny=np.isin(holes,[i for i in range(1,n+1) if sizes[i]<4]);clean=ink|tiny
  if same_features(ink,clean):removed_after=int(tiny.sum());ink=clean
 white=ndimage.binary_fill_holes(ink)
 material=np.pad(masks[1],report['padding']);labels,n=ndimage.label(white&~ink);sizes=np.bincount(labels.ravel());overlaps=np.bincount(labels[material],minlength=n+1)
 selected=[i for i in range(1,n+1) if sizes[i]>=32 and overlaps[i]/sizes[i]>.5]
 # Anatomical masks require visual review.
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 # Assign complete enclosed skin regions by source-painted anatomical ownership.
 side_regions={};side_scores={}
 for side,source_mask in zip(['left','right'],masks[2:]):
  source_mask=np.pad(source_mask,report['padding'])
  overlap=np.bincount(labels[source_mask],minlength=n+1)
  side_regions[side]=[i for i in selected if overlap[i]/sizes[i]>.5]
  side_scores[side]={int(i):float(overlap[i]/sizes[i]) for i in range(1,n+1)}
 assert set(side_regions['left']).isdisjoint(side_regions['right']),side_regions
 assert set(side_regions['left'])|set(side_regions['right'])==set(selected),(selected,side_regions,side_scores)
 # Reviewed against source-painted overlays, including crossed hand fragments.
 expected_owners={'1f93c':{'left':[2,5,6,7,11,14],'right':[1,3,4,8,10,12,13]},'1f93c_200d_2642':{'left':[1,3,6,7,10,11,13],'right':[2,4,5,8,12,14]},'1f93c_200d_2640':{'left':[2,3,6,7,10,11,13],'right':[1,4,5,8,12,14]}}
 assert n==18 and side_regions==expected_owners[key],(key,n,side_regions)
 report.update(enclosedRegionSizes=[int(v) for v in sizes],skinSourceOverlap={i:float(overlaps[i]/sizes[i]) for i in range(1,n+1)},pairedSkinRegions=side_regions,pairedSkinOverlap=side_scores,sourceOwnerPaths={k:sorted(v) for k,v in OWNERS[key].items()})
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 report["mergedSourcePaths"]=[list(group) for group in merged.values()]
 return (white,skin,ink),report



def split_skin(white,skin,ink,report):
 """Use reviewed source ownership for interlocking limbs, preserving occlusion."""
 labels,_=ndimage.label(white&~ink)
 sides=[ndimage.binary_dilation(np.isin(labels,report['pairedSkinRegions'][side]),iterations=3)&skin for side in ['left','right']]
 left,right=sides
 assert not (left&right).any() and np.array_equal(left|right,skin)
 return left,right,dict(method='reviewed source-painted ownership',leftRegions=report['pairedSkinRegions']['left'],rightRegions=report['pairedSkinRegions']['right'],leftPixels=int(left.sum()),rightPixels=int(right.sum()))
