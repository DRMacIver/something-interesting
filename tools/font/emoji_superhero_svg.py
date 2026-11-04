"""Reviewed superhero source experiment."""
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
RECIPES={'1f9b8': (44, {0, 3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 17, 19, 21, 28, 30, 31, 32, 33, 34, 35, 36, 37}, {0, 5, 7, 10, 12, 15, 16, 17, 19, 21, 31, 32, 33, 34, 35, 36, 37}, {28, 30}), '1f9b8_200d_2642': (32, {0, 3, 5, 7, 8, 10, 11, 12, 13, 15, 16, 17, 19, 21, 23, 24, 25, 26, 27, 28, 29, 30}, {0, 5, 7, 10, 12, 15, 16, 17, 19, 24, 25, 26, 27, 28, 29, 30}, {21, 23}), '1f9b8_200d_2640': (32, {0, 2, 5, 7, 9, 10, 12, 13, 14, 15, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30}, {0, 2, 7, 9, 12, 14, 17, 18, 19, 23, 24, 25, 26, 27, 28, 29, 30}, {21, 22})}

# At dialogue size the nose fills the gap between eyes and smile.
for key,nose in [('1f9b8',34),('1f9b8_200d_2642',26),('1f9b8_200d_2640',26)]:
 RECIPES[key][1].discard(nose)

# A solid triangle keeps the badge legible under production stroke; its narrow
# source-colour rim otherwise closes and joins the neck or belt.
for key in RECIPES:RECIPES[key][1].discard(15 if key.endswith('2640') else 13)

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
   merged={'1f9b8':{30:(29,30)},'1f9b8_200d_2642':{23:(22,23)},'1f9b8_200d_2640':{}}[key]
   if i in merged:e.set('d',leg_union(raw,merged[i]))
   rear_boot=9 if key.endswith('2640') else 7
   if i==rear_boot:
    # Separate the bent boot from the cape; the leg paints over the upper gap.
    halo=ET.Element(e.tag,{'d':e.get('d'),'fill':'#ffffff','stroke':'#ffffff','stroke-width':'8','stroke-linejoin':'round','stroke-linecap':'round'})
    parent=parents[e];parent.insert(list(parent).index(e),halo)
   badge={14,15} if key.endswith('2640') else {12,13}
   if i in badge:e.set('transform','translate(0 51) scale(1 .7) translate(0 -47) '+e.get('transform',''))
   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   black=i in (skin_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in skin_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
   head={'1f9b8':{21,28,30,31,32,33,34,35,36,37},'1f9b8_200d_2642':{21,23,24,25,26,27,28,29,30},'1f9b8_200d_2640':{0,21,22,23,24,25,26,27,28,29}}[key]
   transform='translate(75 26) scale(1.3) translate(-75 -24)'
   eyes={'1f9b8':{31,32},'1f9b8_200d_2642':{24,25},'1f9b8_200d_2640':{23,24}}[key]
   if i in eyes:
    e.set('rx','.6');e.set('ry','.6');e.set('cy',str(float(e.get('cy'))+.7))
   nose={'1f9b8':34,'1f9b8_200d_2642':26,'1f9b8_200d_2640':26}[key]
   mouth={'1f9b8':33,'1f9b8_200d_2642':27,'1f9b8_200d_2640':25}[key]
   brows={'1f9b8':{35,36},'1f9b8_200d_2642':{28,29},'1f9b8_200d_2640':{27,28}}[key]
   if i==nose:transform+=' translate(75 28) scale(.45) translate(-75 -28)'
   if i==mouth:transform+=' translate(75 32) scale(.7 .4) translate(-75 -32)'
   if i in brows:transform+=' translate(75 19.5) scale(1 .5) translate(-75 -21)'
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
 # Reviewed face and neck; gloves, costume, badge and boot clearance stay white.
 assert (n,selected)==(7,[2,4]),(key,n,selected)
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 report['opticalHeadTransform']=dict(scale=1.3,sourceAnchor=[75,24],targetAnchor=[75,26])
 report['opticalFaceDetails']=dict(eyeRadii=[.6,.6],eyeShiftY=.7,noseRemoved=True,mouthScale=[.7,.4],browScaleY=.5,browShiftY=-1.5)
 report['badgeOpticalTransform']=dict(shiftY=4,scaleY=.7,anchorY=47,solidTriangle=True)
 report['rearBootWhiteUnderstroke']=8
 report['mergedSourcePaths']=[list(group) for group in merged.values()]
 return (white,skin,ink),report

