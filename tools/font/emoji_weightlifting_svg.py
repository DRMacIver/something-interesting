"""Reviewed weightlifting source experiment."""
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
RECIPES={'1f3cb': (59, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30, 31, 32, 33, 35, 36, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 54, 55, 56, 57, 58}, {2, 3, 4, 6, 7, 9, 19, 20, 24, 25, 26, 30, 31, 32, 33, 35, 36, 40, 41, 42, 43, 44, 45, 47, 54, 55, 57, 58}, {0, 1, 10, 11, 12, 13, 14, 15, 17, 18, 23, 29, 34, 37, 38, 39, 48, 49, 50, 51, 52, 53}), '1f3cb_200d_2642': (55, {0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 26, 27, 28, 29, 30, 31, 32, 25, 34, 35, 36, 37, 38, 39, 41, 46, 47, 48, 49, 50, 51, 52, 53, 54}, {0, 1, 3, 4, 6, 17, 18, 22, 26, 27, 29, 30, 34, 35, 36, 37, 41, 46, 47, 48, 49, 50, 51, 53, 54}, {7, 8, 9, 10, 11, 12, 14, 15, 16, 21, 23, 24, 25, 33, 38, 39, 40, 42, 43, 44, 45}), '1f3cb_200d_2640': (56, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 31, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 30, 32, 33, 34, 35, 36, 37, 38, 40, 41, 43, 48, 49, 50, 51, 52, 53, 54, 55}, {0, 1, 3, 4, 5, 12, 14, 22, 23, 27, 30, 32, 33, 35, 36, 40, 41, 43, 48, 49, 50, 51, 52, 54, 55}, {6, 7, 8, 9, 10, 11, 15, 16, 17, 19, 20, 21, 26, 28, 29, 31, 39, 42, 44, 45, 46, 47})}
def prepare(key):
 expected,keep,solid,skin_paths=RECIPES[key]
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-swim-ball-weights-svg.json').read_text())
 entry=next(e for e in spec['files'] if e['path'].endswith(f'emoji_u{key}.svg'))
 raw=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
 masks=[];pixels=1536;stroke=1.3
 for material in [False,True]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
  shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==expected,(key,len(shapes),expected)
  for i,e in enumerate(shapes):
   parent=parents.get(e);definition=False
   while parent is not None:
    if parent.tag.split('}')[-1] in {'defs','clipPath'}:definition=True
    parent=parents.get(parent)
   if definition:continue
   plate_detail={'1f3cb':{32,33},'1f3cb_200d_2642':{36,37},'1f3cb_200d_2640':{5,41}}[key]
   if i not in keep or i in plate_detail:parents[e].remove(e);continue
   merged={'1f3cb': {11: (11, 13), 12: (12, 14), 39: (37, 38, 39), 48: (48, 34, 50, 53), 49: (49, 10, 29, 51, 52)}, '1f3cb_200d_2642': {7: (7, 9), 8: (8, 10), 25: (23, 24, 25), 38: (38, 33, 42, 43), 39: (39, 40, 44, 45)}, '1f3cb_200d_2640': {8: (8, 16), 9: (9, 17), 31: (28, 29, 31), 6: (6, 42, 44, 47), 7: (7, 15, 39, 45, 46)}}[key]
   if i in merged:e.set('d',leg_union(raw,merged[i]))
   head={'1f3cb':{2,35,36,39,40,41,42,43,44,45,46,47},'1f3cb_200d_2642':{25,26,27,28,46,47,48,49,50},'1f3cb_200d_2640':{30,31,32,33,34,48,49,50,51}}[key]
   if i in head:e.set('transform','translate(64,49) scale(1.1) translate(-64,-47)')
   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   black=i in (skin_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in skin_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
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
 # Reviewed exposed face/neck, hands, arms and leg regions only.
 expected_regions={'1f3cb': (24, [3, 4, 6, 7, 8, 11, 13, 15, 17, 18, 19, 20, 21, 22]), '1f3cb_200d_2642': (25, [3, 4, 6, 7, 8, 11, 13, 15, 18, 19, 20, 21, 22, 23]), '1f3cb_200d_2640': (24, [3, 4, 6, 7, 8, 11, 13, 16, 17, 18, 19, 20, 21, 22])}
 assert (n,selected)==expected_regions[key],(key,n,selected)
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 report["opticalHeadTransform"]={"scale":1.1,"sourceAnchor":[64,47],"targetAnchor":[64,49]}
 report["removedInnerPlateRims"]=sorted(plate_detail)
 report["mergedSourcePaths"]=[list(group) for group in merged.values()]
 return (white,skin,ink),report

