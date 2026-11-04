"""Reviewed merperson source experiment."""
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
RECIPES={'1f9dc': (52, {0, 4, 5, 6, 9, 11, 17, 18, 19, 23, 29, 31, 33, 34, 35, 36, 38, 39, 40, 46, 47, 48, 49, 50, 51}, {33, 4, 38, 39, 40, 11, 46, 47, 48, 49, 18, 19, 50, 51, 23}, {5, 6, 9, 29, 31}), '1f9dc_200d_2642': (47, {0, 1, 2, 9, 10, 12, 16, 17, 18, 26, 27, 28, 29, 30, 31, 32, 33, 39, 40, 43, 44, 45, 46}, {2, 39, 40, 10, 43, 45, 46, 17, 18, 27, 28, 29, 30, 31}, {9, 26, 12}), '1f9dc_200d_2640': (49, {0, 1, 4, 9, 10, 11, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 40, 41, 42, 43, 44, 45, 46, 47, 48}, {1, 4, 10, 11, 25, 26, 27, 28, 29, 30, 31, 41, 42, 43, 44, 45, 46, 48}, {21, 22, 23})}

# The waist paint is a tail-edge highlight, not an open white belt.
for key,rim in [('1f9dc',34),('1f9dc_200d_2642',44),('1f9dc_200d_2640',32)]:
 RECIPES[key][1].discard(rim)

# Use the central fin vein; edge-highlight shapes create accidental hairline
# counters against the outer fin outline at raster size.
for key,edges,vein in [('1f9dc',{18,19},20),('1f9dc_200d_2642',{17,18},19),('1f9dc_200d_2640',{10,11},12)]:
 RECIPES[key][1].difference_update(edges);RECIPES[key][2].difference_update(edges)
 RECIPES[key][1].add(vein);RECIPES[key][2].add(vein)

# Keep one central rib per shell; crowded decorative lines close under final ink.
RECIPES['1f9dc_200d_2640'][1].difference_update({41,43,44,46})
RECIPES['1f9dc_200d_2642'][1].discard(43)

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
   merged={'1f9dc': {33:(33,34),4: (4, 8, 10, 15, 16), 5: (2, 5), 6: (1, 6), 9: (3, 7, 9), 31: (30, 31)}, '1f9dc_200d_2642': {31:(31,44),9: (7, 9), 10: (10, 11, 13, 14, 15), 26: (8, 26)}, '1f9dc_200d_2640': {31:(31,32),4: (4, 5, 6, 7, 8), 21: (3, 20, 21), 23: (19, 23)}}[key]
   if i in merged:e.set('d',leg_union(raw,merged[i]))
   if key=='1f9dc_200d_2640' and i==4:
    # Keep the black trident separate where it crosses black hair. A white
    # under-stroke leaves clearance for the stronger production ink stroke.
    halo=ET.Element(e.tag,{'d':e.get('d'),'fill':'#ffffff','stroke':'#ffffff','stroke-width':'8','stroke-linejoin':'round','stroke-linecap':'round'})
    parent=parents[e];parent.insert(list(parent).index(e),halo)

   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   black=i in (skin_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in skin_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
   highlights={'1f9dc':{34,35,36},'1f9dc_200d_2642':{32,33,44},'1f9dc_200d_2640':{32,33,34}}[key]
   if i in highlights:e.set('stroke','none')
   head={'1f9dc':{11,31,46,47,48,49,50,51},'1f9dc_200d_2642':{2,26,27,28,29,30,45,46},'1f9dc_200d_2640':{1,23,25,26,27,28,29,30,47,48}}[key]
   transform='translate(104 40) scale(1.15) translate(-104 -40)'
   eyes={'1f9dc':{50:(110.3,41.2),51:(101.7,40)},'1f9dc_200d_2642':{45:(110.1,41),46:(101.7,40)},'1f9dc_200d_2640':{29:(101.7,40),30:(110.3,41.2)}}[key]
   if i in eyes:
    cx,cy=eyes[i];transform+=f' translate({cx} {cy+.7}) scale(.65) translate({-cx} {-cy})'
   nose={'1f9dc':49,'1f9dc_200d_2642':30,'1f9dc_200d_2640':28}[key]
   mouth={'1f9dc':48,'1f9dc_200d_2642':29,'1f9dc_200d_2640':27}[key]
   if i==nose:transform+=' translate(105 45) scale(.65) translate(-105 -45)'
   if i==mouth:transform+=' translate(105 48.8) scale(1 .65) translate(-105 -48)'
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
 # Reviewed against native tone references and all three anatomical sheets.
 expected_skin={'1f9dc':(12,[1,2,3,4,6,9,10]),'1f9dc_200d_2642':(11,[1,2,3,5,11]),'1f9dc_200d_2640':(12,[2,3,4,10])}[key]
 assert (n,selected)==expected_skin,(key,n,selected)
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 report["opticalHeadTransform"]=dict(scale=1.15,anchor=[104,40])
 report["opticalFaceDetails"]=dict(eyeScale=.65,eyeShiftY=.7,noseScale=.65,mouthScaleY=.65,mouthShiftY=.8)
 report["tridentWhiteUnderstroke"]=8 if key.endswith('2640') else 0
 report["centralFinVeinPath"]={'1f9dc':20,'1f9dc_200d_2642':19,'1f9dc_200d_2640':12}[key]
 report["mergedSourcePaths"]=[list(group) for group in merged.values()]
 return (white,skin,ink),report

