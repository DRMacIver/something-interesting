"""Reviewed vampire source experiment."""
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
RECIPES={'1f9db': (33, {0, 1, 2, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26}, {0, 2, 9, 17, 18, 22, 23, 24, 25, 26}, {16}), '1f9db_200d_2642': (21, {0, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20}, {0, 3, 8, 9, 10, 11, 12, 17, 19, 20}, {4, 7}), '1f9db_200d_2640': (19, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18}, {0, 2, 5, 6, 7, 8, 9, 10, 11, 16, 18}, {3, 4})}

def prepare(key):
 expected,keep,solid,skin_paths=RECIPES[key]
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-vampire-elf-svg.json').read_text())
 entry=next(e for e in spec['files'] if e['path'].endswith(f'emoji_u{key}.svg'))
 raw=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
 masks=[];pixels=1536;stroke=1.3
 for material in [False,True]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
  # Enlarge the identifying smile and fangs together for the production ink stroke.
  for element in root.iter():
   if element.get('id') in {'mouth','teeth'}:
    element.set('transform','translate(64 78) scale(1.6 1.8) translate(-64 -78)')
  shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==expected,(key,len(shapes),expected)
  for i,e in enumerate(shapes):
   parent=parents.get(e);definition=False
   while parent is not None:
    if parent.tag.split('}')[-1] in {'defs','clipPath'}:definition=True
    parent=parents.get(parent)
   if definition:continue
   if i not in keep:parents[e].remove(e);continue
   merged={'1f9db': {16: (15, 16)}, '1f9db_200d_2642': {7: (6, 7)}, '1f9db_200d_2640': {}}[key]
   if i in merged:e.set('d',leg_union(raw,merged[i]))
   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   black=i in (skin_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in skin_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
   fangs={'1f9db':{20,21},'1f9db_200d_2642':{15,16},'1f9db_200d_2640':{14,15}}[key]
   if i in fangs:
    points=[tuple(map(float,p.split(','))) for p in e.get('points').split()]
    centre=sum(x for x,y in points)/len(points)
    e.set('points',' '.join(f'{centre+(x-centre)*2.2},{75.66+(y-75.66)*1.35}' for x,y in points))
    e.set('stroke','#ffffff' if material else '#111111');e.set('stroke-width','0.65')
   if key=='1f9db_200d_2640' and i==17:e.set('stroke','none')
   if key=='1f9db' and i in {11,12}:
    e.set('fill','none');e.set('stroke','#ffffff' if material else '#111111');e.set('stroke-width','2')
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
 # These regions were checked against the native light/dark source drawings.
 expected_skin={'1f9db':(10,[1]),'1f9db_200d_2642':(7,[1,6]),'1f9db_200d_2640':(8,[2,7,8])}[key]
 assert (n,selected)==expected_skin,(key,n,selected)
 fang_regions=[5,6] if key.endswith('2640') else [4,5]
 for region in fang_regions:
  assert region not in selected
  tooth=labels==region
  y,x=np.nonzero(tooth)
  box=[(float(v)-report['padding'])/12 for v in [x.min(),y.min(),x.max(),y.max()]]
  assert 43<box[0]<81 and 70<box[1]<88 and box[2]<83 and box[3]<90,(key,region,box)
  assert ndimage.distance_transform_edt(tooth).max()>32,(key,region)
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 report["fangRegions"]=fang_regions
 report["mouthOpticalScale"]=[1.6,1.8]
 report["fangWidthScale"]=2.2
 report["fangHeightScale"]=1.35
 report["mergedSourcePaths"]=[list(group) for group in merged.values()]
 return (white,skin,ink),report

