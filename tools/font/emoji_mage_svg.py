"""Reviewed mage source experiment."""
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
RECIPES={'1f9d9': (30, {0, 1, 2, 4, 5, 6, 10, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 27, 28}, {0, 1, 5, 14, 15, 16, 17, 18, 19, 22, 25, 27}, {13, 6}), '1f9d9_200d_2642': (26, {0, 1, 2, 3, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 22, 24, 25}, {0, 1, 2, 10, 11, 12, 13, 14, 16, 19, 21, 25}, {9}), '1f9d9_200d_2640': (33, {0, 1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 28, 29, 32}, {0, 3, 4, 7, 16, 17, 18, 19, 20, 21, 23, 26, 28}, {10, 14})}

# Keep the round orb distinct from its wooden holder and shaft.
for key,staff in [('1f9d9',25),('1f9d9_200d_2642',19),('1f9d9_200d_2640',26)]:
 RECIPES[key][2].discard(staff)

# Merge the two forehead skin paints, then restore side locks above the face.
RECIPES['1f9d9_200d_2640'][1].discard(10)
RECIPES['1f9d9_200d_2640'][3].discard(10)

def prepare(key):
 expected,keep,solid,skin_paths=RECIPES[key]
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-wrestling-fantasy-svg.json').read_text())
 entry=next(e for e in spec['files'] if e['path'].endswith(f'emoji_u{key}.svg'))
 raw=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
 masks=[];pixels=1536;stroke=1.3
 for material in [False,True]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
  shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==expected,(key,len(shapes),expected)
  if key=='1f9d9_200d_2640':
   parent=parents[shapes[14]]
   for index in [13,12]:
    assert parents[shapes[index]] is parent
    parent.remove(shapes[index]);parent.insert(list(parent).index(shapes[14])+1,shapes[index])
  for i,e in enumerate(shapes):
   parent=parents.get(e);definition=False
   while parent is not None:
    if parent.tag.split('}')[-1] in {'defs','clipPath'}:definition=True
    parent=parents.get(parent)
   if definition:continue
   if i not in keep:parents[e].remove(e);continue
   merged={'1f9d9': {10: (7, 8, 9, 10), 13: (11, 12, 13, 20), 25: (24, 25, 29), }, '1f9d9_200d_2642': {9: (4, 5, 8, 9), 19: (18, 19, 23), }, '1f9d9_200d_2640': {1: (1, 2), 14: (8, 9, 10, 14), 26: (25, 26, 30), }}[key]
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
 settings=Settings(strength=1.7,seed=seed,pressure=.025 if key.endswith('2640') else .1,taper=0,bend=.001 if key in {'1f9d9_200d_2640','1f9d9_200d_2642'} else .012)
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
 # Reviewed face, ears, exposed neck and skin surrounding the beard mouth.
 expected_regions={'1f9d9':(11,[4,9]),'1f9d9_200d_2642':(14,[4,6,7,10,12]),'1f9d9_200d_2640':(16,[6])}
 assert (n,selected)==expected_regions[key],(key,n,selected)
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 report["mergedSourcePaths"]=[list(group) for group in merged.values()]
 return (white,skin,ink),report

