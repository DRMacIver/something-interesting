"""Reviewed handball source experiment."""
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
RECIPES={'1f93e': (36, {0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 14, 16, 18, 20, 21, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35}, {0, 1, 32, 33, 4, 34, 35, 9, 14, 20, 21, 29, 30, 31}, {3, 5, 11, 16, 28}), '1f93e_200d_2642': (36, {0, 1, 2, 3, 4, 5, 6, 8, 10, 11, 13, 15, 17, 19, 20, 23, 24, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35}, {0, 33, 32, 3, 34, 35, 8, 13, 19, 20, 26, 29, 30, 31}, {2, 4, 10, 15, 28}), '1f93e_200d_2640': (37, {0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 13, 15, 17, 19, 21, 22, 24, 26, 27, 28, 30, 31, 32, 33, 34, 35, 36}, {0, 32, 2, 35, 34, 5, 36, 33, 1, 10, 15, 21, 22, 24, 31}, {4, 6, 12, 17, 30})}

def prepare(key):
 expected,keep,solid,skin_paths=RECIPES[key]
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-five-sports-svg.json').read_text())
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
   if i not in keep:parents[e].remove(e);continue
   merged={'1f93e': {7: (7, 8, 23), 11: (10, 11), 16: (15, 16, 22), 18: (17, 18), 28: (19, 27, 28)}, '1f93e_200d_2642': {6: (6, 7, 22), 10: (9, 10), 15: (14, 15, 21), 17: (16, 17), 28: (18, 27, 28)}, '1f93e_200d_2640': {8: (8, 9, 25), 12: (11, 12), 17: (16, 17, 23), 19: (18, 19), 30: (20, 29, 30)}}[key]
   if i in merged:e.set('d',leg_union(raw,merged[i]))
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
 # Reviewed face/neck/ear, hands/arms separated by wristbands, and knees.
 expected_regions={'1f93e':(15,[2,3,4,6,8,9,12]),'1f93e_200d_2642':(15,[2,3,4,6,7,10,12]),'1f93e_200d_2640':(16,[2,3,4,5,7,9,10,13])}[key]
 assert (n,selected)==expected_regions,(key,n,selected)
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 report["mergedSourcePaths"]=[list(group) for group in merged.values()]
 return (white,skin,ink),report

