"""Reviewed fairy source experiment."""
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
RECIPES={'1f9da': (52, {0, 1, 2, 4, 5, 6, 10, 11, 12, 14, 15, 16, 23, 24, 28, 29, 31, 32, 33, 35, 36, 37, 38, 39, 40, 41, 42, 50}, {32, 36, 37, 38, 39, 40, 41, 42, 28, 29, 31}, {33, 50, 35, 23, 24}), '1f9da_200d_2642': (51, {0, 1, 2, 4, 5, 6, 10, 11, 12, 14, 15, 16, 23, 24, 28, 29, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 49}, {35, 36, 37, 38, 39, 40, 41, 28, 29, 31}, {32, 49, 34, 23, 24}), '1f9da_200d_2640': (51, {0, 1, 2, 4, 5, 6, 10, 11, 12, 14, 15, 16, 23, 24, 27, 28, 30, 38, 40, 41, 43, 44, 45, 46, 47, 48, 49, 50}, {41, 44, 45, 46, 47, 48, 49, 50, 27, 28, 30}, {38, 23, 40, 24, 43})}

# Keep crossed legs separately outlined; merge only the rear toe with its leg.
for key,back_leg in [('1f9da',22),('1f9da_200d_2642',21),('1f9da_200d_2640',21)]:
 RECIPES[key][1].add(back_leg);RECIPES[key][3].add(back_leg)

def prepare(key):
 expected,keep,solid,skin_paths=RECIPES[key]
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-fairy-merperson-hero-svg.json').read_text())
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
   merged={'1f9da': {23: (20, 23), 35: (34, 35), 50: (25, 26, 43, 44, 45, 46, 50)}, '1f9da_200d_2642': {23: (20, 23), 34: (33, 34), 49: (25, 26, 42, 43, 44, 45, 49)}, '1f9da_200d_2640': {23: (20, 23), 38: (25, 31, 32, 33, 34, 38), 43: (42, 43)}}[key]
   if i in merged:e.set('d',leg_union(raw,merged[i]))
   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   black=i in (skin_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in skin_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
   if i in {1,2,5,6,11,12,15,16}:
    e.set('fill','none');e.set('stroke','#ffffff' if material else '#111111');e.set('stroke-width','0.8')
   wand=27 if key.endswith('2640') else 28
   if i==wand:e.set('stroke','#ffffff' if material else '#111111');e.set('stroke-width','1.3')
   head={'1f9da':{32,35,36,37,38,39,40,41,42},'1f9da_200d_2642':{34,35,36,37,38,39,40,41},'1f9da_200d_2640':{41,43,44,45,46,47,48,49,50}}[key]
   native_transform=e.get('transform','')
   transform='translate(64 26.5) scale(1.22) translate(-64 -24)'
   eyes={'1f9da':{38,39},'1f9da_200d_2642':{37,38},'1f9da_200d_2640':{46,47}}[key]
   if i in eyes:
    e.set('rx','1.1');e.set('ry','1.1');transform+=' translate(0 1)'
   nose={'1f9da':40,'1f9da_200d_2642':39,'1f9da_200d_2640':48}[key]
   mouth={'1f9da':41,'1f9da_200d_2642':40,'1f9da_200d_2640':49}[key]
   if i==nose:transform+=' translate(64 28.5) scale(0.65) translate(-64 -28.5)'
   if i==mouth:transform+=' translate(64 33.1) scale(1 0.65) translate(-64 -32.4)'
   if i in head:e.set('transform',transform+' '+native_transform)
  root.set('width',str(pixels));root.set('height',str(pixels))
  doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
  masks.append(np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128)
 removed_specks=0
 if key=='1f9da_200d_2640':
  # One isolated raster pixel at the tapered ponytail tip is not a hair strand.
  labels,n=ndimage.label(masks[0]);sizes=np.bincount(labels.ravel())
  tiny=np.isin(labels,[i for i in range(1,n+1) if sizes[i]<4])
  removed_specks=int(tiny.sum());assert removed_specks==1
  masks[0]&=~tiny
 removed=0
 if True:
  holes,n=ndimage.label(ndimage.binary_fill_holes(masks[0])&~masks[0]);sizes=np.bincount(holes.ravel())
  tiny=np.isin(holes,[i for i in range(1,n+1) if sizes[i]<4]);clean=masks[0]|tiny
  if same_features(masks[0],clean):removed=int(tiny.sum());masks[0]=clean
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 settings=Settings(strength=1.7,seed=seed,pressure=.025 if key.endswith('2640') else .1,taper=0,bend=.001)
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
 # Reviewed face/ears, collar opening, both arms and separately outlined legs.
 expected_skin={'1f9da':(19,[1,6,7,8,17,18]),'1f9da_200d_2642':(19,[1,6,7,8,17,18]),'1f9da_200d_2640':(21,[1,6,8,9,10,19,20])}[key]
 assert (n,selected)==expected_skin,(key,n,selected)
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 report["opticalHeadTransform"]=dict(scale=1.22,sourceAnchor=[64,24],targetAnchor=[64,26.5])
 report["opticalFaceDetails"]=dict(eyeRadii=[1.1,1.1],eyeShiftY=1,noseScale=.65,mouthScaleY=.65,mouthShiftY=.7,nativeTransformsPreserved=True)
 report["wingVeinPaths"]=[1,2,5,6,11,12,15,16]
 report["mergedSourcePaths"]=[list(group) for group in merged.values()]
 return (white,skin,ink),report

