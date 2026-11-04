"""Reviewed person-gesture SVG geometry and exposed-skin masks."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import pymupdf
from pen_translate import Settings,translate,same_features
ROOT=Path(__file__).resolve().parents[2]
# expected shape count, retained paint, solid ink, exposed skin
RECIPES={
 '1f9cf':(25,{0}|set(range(4,13))|set(range(16,25)),{0,8,9,10,11,12,18,19,20,22,24},{5,6,7,17,21}),
 '1f9cf_200d_2642':(21,{0}|set(range(2,9))|set(range(10,18))|{19,20},{5,6,7,8,12,13,14,16,17,20},{2,3,4,11,15}),
 '1f9cf_200d_2640':(22,{0}|set(range(2,11))|set(range(13,22)),{0,6,7,8,9,10,15,16,17,19,21},{3,4,5,14,18}),
 '1f937':(29,{0,1,2,4,7,9}|set(range(10,20))|set(range(22,29)),{0}|set(range(14,20))|set(range(22,28)),{7,9,10,11,12,13}),
 '1f937_200d_2642':(29,{0,1,3,6,8,9}|set(range(12,29)),set(range(12,18))|{21}|set(range(23,29)),{6,8,9,19,20,22}),
 '1f937_200d_2640':(29,{0,1,3,4,6,9,11,12}|set(range(15,29)),{0,1}|set(range(15,21))|set(range(23,29)),{9,11,12,22}),
 '1f926':(27,{0}|set(range(7,18))|{25,26},{0}|set(range(11,18)),{8,9,10,25}),
 '1f926_200d_2642':(15,set(range(11))|{13,14},set(range(4,11)),{1,2,3,13}),
 '1f926_200d_2640':(16,{0}|set(range(2,12))|{14,15},{0}|set(range(5,12)),{3,4,14}),
 '1f647':(30,{0,7,8}|set(range(10,24)),{0}|set(range(14,24)),{7,10,11,12,13}),
 '1f647_200d_2642':(18,{0,1}|set(range(3,17)),set(range(5,9))|set(range(11,17)),{1,3,4,9,10}),
 '1f647_200d_2640':(19,{0,2}|set(range(4,14))|set(range(15,19)),{0}|set(range(8,14))|set(range(15,19)),{4,5,6,7}),
 '1f64b':(27,{0}|set(range(7,18))|{24,25,26},{0}|set(range(11,18))|{26},{8,9,10,24}),
 '1f64b_200d_2642':(15,set(range(11))|{12,13,14},set(range(4,11))|{14},{1,2,3,12}),
 '1f64b_200d_2640':(16,{0,2,3,4,5,6}|set(range(8,16)),{0,5,6,8,9,10,11,12,15},{3,4,13}),
 '1f481':(27,{0}|set(range(7,17))|{18,19,20},{0}|set(range(11,17))|{20},{8,9,10,18}),
 '1f481_200d_2642':(15,set(range(10))|{11,12,13},set(range(4,10))|{13},{1,2,3,11}),
 '1f481_200d_2640':(16,{0}|set(range(2,10))|{12,13,14,15},{0}|set(range(5,10))|{14,15},{3,4,12}),
 '1f645':(21,{0,1,2,3,4,6,11,12,13,14,15,16,17,18,20},{0,13,14,15,16,17,20},{1,2,3,6,11}),
 '1f645_200d_2642':(21,set(range(10))|{11,12,18,19,20},{2,4,5,6,7,8,9},{0,1,3,11,18}),
 '1f645_200d_2640':(19,set(range(9))|{10,15,16,17},{0,2,3,4,5,6,7},{1,10,15}),
 '1f646':(27,{0,1}|set(range(8,18))|{23,24,25,26},{1}|set(range(11,18)),{8,9,10,23,25}),
 '1f646_200d_2642':(16,set(range(11))|{12,13,14,15},set(range(4,11)),{1,2,3,12,14}),
 '1f646_200d_2640':(17,{0}|set(range(2,12))|{13,14,15,16},{0}|set(range(5,12)),{3,4,13,15}),
 '1f64d':(24,{0,1}|set(range(8,18)),{1}|set(range(11,18)),{8,9,10}),
 '1f64d_200d_2642':(12,set(range(11)),set(range(4,11)),{1,2,3}),
 '1f64d_200d_2640':(13,{0}|set(range(2,12)),{0}|set(range(5,12)),{3,4}),
 '1f64e':(31,{0}|set(range(7,25)),{0,9,11,12,13}|set(range(17,25)),{8,10,14,15,16}),
 '1f64e_200d_2642':(19,set(range(16))|{17,18},{2,4,5,6}|set(range(10,16))|{17,18},{1,3,7,8,9}),
 '1f64e_200d_2640':(20,{0}|set(range(2,19)),{0,4,6,7,8}|set(range(11,19)),{3,5,9,10}),
}

EXPECTED_REGIONS={'1f481': [9, [1, 3, 4, 8]], '1f481_200d_2642': [7, [1, 2, 3, 4, 6]], '1f481_200d_2640': [5, [1, 2, 4]], '1f645': [9, [1, 2, 3, 4, 5]], '1f645_200d_2642': [9, [1, 2, 3, 4, 5]], '1f645_200d_2640': [7, [1, 2, 3]], '1f646': [13, [1, 2, 5, 6, 7, 12]], '1f646_200d_2642': [11, [1, 2, 5, 6, 7, 10]], '1f646_200d_2640': [7, [1, 2, 5, 6]], '1f64b': [9, [1, 2, 4, 9]], '1f64b_200d_2642': [8, [1, 2, 4, 5, 8]], '1f64b_200d_2640': [7, [1, 4, 7]], '1f64d': [5, [1, 2, 3, 5]], '1f64d_200d_2642': [5, [1, 2, 3, 5]], '1f64d_200d_2640': [3, [1, 3]], '1f64e': [7, [1, 2, 3, 5, 6, 7]], '1f64e_200d_2642': [7, [1, 2, 3, 5, 6, 7]], '1f64e_200d_2640': [5, [1, 3, 4, 5]]}

EXPECTED_REGIONS.update({'1f647': [8, [1, 2, 3, 5, 6, 7]], '1f647_200d_2642': [8, [1, 2, 3, 5, 6, 7]], '1f647_200d_2640': [6, [1, 3, 4, 5, 6]], '1f926': [10, [1, 2, 3, 4, 5, 6, 8]], '1f926_200d_2642': [11, [1, 2, 3, 4, 6, 7, 9]], '1f926_200d_2640': [10, [1, 2, 3, 4, 5, 6, 8]], '1f937': [10, [1, 2, 3, 4, 5, 9]], '1f937_200d_2642': [10, [1, 2, 3, 4, 5, 8]], '1f937_200d_2640': [8, [1, 2, 3, 6]], '1f9cf': [8, [1, 2, 3, 5, 6]], '1f9cf_200d_2642': [8, [1, 2, 3, 5, 7]], '1f9cf_200d_2640': [7, [1, 2, 3, 4, 6]]})

def prepare(key):
 expected,keep,solid,skin_paths=RECIPES[key]
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-gesture-svg.json').read_text())
 entry=next(e for e in spec['files'] if e['path'].endswith(f'emoji_u{key}.svg'))
 raw=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
 masks=[];pixels=768;stroke=1.8 if key.startswith('1f645') else 1.3
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
   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   black=i in (skin_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in skin_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  for e in shapes:
   if e.tag.split('}')[-1]=='line':
    e.set('fill','none');e.set('stroke','#ffffff' if material else '#111111');e.set('stroke-width','2')
  if key.startswith('1f9cf'):
   arrow=shapes[{'1f9cf':23,'1f9cf_200d_2642':19,'1f9cf_200d_2640':20}[key]]
   arrow.set('fill','none');arrow.set('stroke','#ffffff' if material else '#111111');arrow.set('stroke-width','2')
  if key.startswith('1f645'):
   for i in {'1f645':{6,11},'1f645_200d_2642':{11,18},'1f645_200d_2640':{10,15}}[key]:shapes[i].set('stroke-width','.9')
  root.set('width',str(pixels));root.set('height',str(pixels))
  doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
  masks.append(np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128)
 removed=0
 if key.split('_')[0] in {'1f645','1f647','1f926','1f937','1f9cf'}:
  holes,n=ndimage.label(ndimage.binary_fill_holes(masks[0])&~masks[0]);sizes=np.bincount(holes.ravel())
  tiny=np.isin(holes,[i for i in range(1,n+1) if sizes[i]<4]);clean=masks[0]|tiny
  assert same_features(masks[0],clean);removed=int(tiny.sum());masks[0]=clean
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 settings=Settings(strength=1.7,seed=seed,pressure=.1,taper=0) if key=='1f647' else Settings(strength=1.7,seed=seed)
 image,report=translate(masks[0],settings)
 assert report['appliedStrength']>0 and not report['fallback'],key
 ink=np.asarray(image)<128
 removed_after=0
 if key.split('_')[0] in {'1f645','1f647','1f926','1f937','1f9cf'}:
  holes,n=ndimage.label(ndimage.binary_fill_holes(ink)&~ink);sizes=np.bincount(holes.ravel())
  tiny=np.isin(holes,[i for i in range(1,n+1) if sizes[i]<4]);clean=ink|tiny
  assert same_features(ink,clean);removed_after=int(tiny.sum());ink=clean
 white=ndimage.binary_fill_holes(ink)
 material=np.pad(masks[1],report['padding']);labels,n=ndimage.label(white&~ink);sizes=np.bincount(labels.ravel());overlaps=np.bincount(labels[material],minlength=n+1)
 selected=[i for i in range(1,n+1) if sizes[i]>=32 and overlaps[i]/sizes[i]>.5]
 assert [n,selected]==EXPECTED_REGIONS[key],(key,n,selected)
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 return (white,skin,ink),report
