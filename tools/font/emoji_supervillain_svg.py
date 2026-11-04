"""Reviewed supervillain source experiment."""
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
RECIPES={'1f9b9': (44, {0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13, 15, 19, 22, 23, 26, 27, 29, 30, 34, 36, 38, 40, 42, 43}, {36, 7, 9, 11, 13, 22, 23, 26, 27, 29, 30}, {19, 15}), '1f9b9_200d_2642': (42, {0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13, 17, 20, 21, 22, 23, 25, 26, 32, 34, 36, 38, 40, 41}, {34, 7, 9, 11, 20, 21, 22, 23, 25, 26}, {17, 13}), '1f9b9_200d_2640': (41, {0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13, 15, 17, 20, 21, 22, 24, 25, 29, 31, 33, 35, 37, 38, 40}, {7, 40, 9, 11, 13, 20, 21, 22, 24, 25, 31}, {17, 15})}

def prepare(key):
 expected,keep,solid,skin_paths=RECIPES[key]
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-fantasy-beings-svg.json').read_text())
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
   merged={'1f9b9':{19:(17,19)},'1f9b9_200d_2642':{17:(15,17)},'1f9b9_200d_2640':{}}[key]
   if i in merged:e.set('d',leg_union(raw,merged[i]))
   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   e.set('stroke','none')
   black=i in (skin_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in skin_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
   head={'1f9b9':{13,15,19,22,23,26,27,29,30},'1f9b9_200d_2642':{13,17,20,21,22,23,25,26},'1f9b9_200d_2640':{7,15,17,20,21,22,24,25,40}}[key]
   transform='translate(64 22) scale(1.4) translate(-64 -17)'
   eyes={'1f9b9':{27,30},'1f9b9_200d_2642':{23,26},'1f9b9_200d_2640':{22,25}}[key]
   if i in eyes:transform+=' translate(64 18) scale(.55 .5) translate(-64 -17)'
   mouth={'1f9b9':22,'1f9b9_200d_2642':20,'1f9b9_200d_2640':20}[key]
   if i==mouth:transform+=' translate(64 24) scale(.65 .35) translate(-64 -22)'
   brows={'1f9b9':{26,29},'1f9b9_200d_2642':{22,25},'1f9b9_200d_2640':{21,24}}[key]
   if i in brows:transform+=' translate(64 14) scale(1 .5) translate(-64 -15)'
   jewel={'1f9b9':34,'1f9b9_200d_2642':32,'1f9b9_200d_2640':29}[key]
   if i==jewel:e.set('transform','translate(66 49) scale(1.5 1) translate(-66 -37)')
   if i in head:e.set('transform',transform+' '+e.get('transform',''))
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
 # Reviewed face/ears and neck only; no glove or costume regions.
 expected_skin={'1f9b9': (18, [4, 10]), '1f9b9_200d_2642': (18, [4, 10]), '1f9b9_200d_2640': (18, [2, 11])}[key]
 assert (n,selected)==expected_skin,(key,n,selected)
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 report['opticalHeadTransform']=dict(scale=1.4,sourceAnchor=[64,17],targetAnchor=[64,22])
 report['opticalFaceDetails']=dict(eyeScale=[.55,.5],mouthScale=[.65,.35],browScaleY=.5,browShiftY=-1,noseRemoved=True)
 report['jewelOpticalTransform']=dict(scaleX=1.5,shiftY=12,anchor=[66,37])
 report['mergedSourcePaths']=[list(group) for group in merged.values()]
 return (white,skin,ink),report

