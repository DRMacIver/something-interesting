"""Reviewed zombie source experiment."""
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
RECIPES={'1f9df': (39, {0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 17, 18, 19, 20, 25, 28, 30, 31, 32, 33, 38}, {0, 1, 5, 6, 7, 8, 9, 10, 12, 18, 19, 20, 25, 31, 32, 33, 38}, {17, 2, 4, 30}), '1f9df_200d_2642': (39, {0, 1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 15, 19, 21, 22, 23, 24, 29, 30, 31, 32, 33, 38}, {0, 5, 6, 7, 8, 9, 10, 11, 22, 23, 24, 29, 31, 32, 33, 38}, {1, 3, 21, 30}), '1f9df_200d_2640': (41, {0, 1, 2, 3, 4, 7, 9, 10, 11, 12, 13, 14, 15, 21, 23, 24, 25, 26, 31, 32, 33, 34, 35, 40}, {0, 1, 4, 9, 10, 11, 12, 13, 15, 24, 25, 26, 31, 33, 34, 35, 40}, {32, 2, 3, 23})}

# Enlarged finger openings supply this contour; the source shading across
# those openings would leave tiny detached ink fragments.
for key,paths in [('1f9df',{19,20,32,33}),('1f9df_200d_2642',{23,24,32,33}),('1f9df_200d_2640',{25,26,34,35})]:
 RECIPES[key][1].difference_update(paths)

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
   merged={'1f9df':{4:(3,4)},'1f9df_200d_2642':{3:(2,3)},'1f9df_200d_2640':{}}[key]
   if i in merged:e.set('d',leg_union(raw,merged[i]))
   hands={'1f9df':{17,30},'1f9df_200d_2642':{21,30},'1f9df_200d_2640':{23,32}}[key]
   if i in hands:
    # Enlarge the source's tiny enclosed finger gap for the final ink stroke.
    import re
    from fontTools.svgLib.path import parse_path
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    parts=re.split(r'\s+(?=M)',e.get('d'))
    assert len(parts)==2,(key,i,len(parts))
    bounds=BoundsPen(None);parse_path(parts[1],bounds);x0,y0,x1,y1=bounds.bounds;cx=(x0+x1)/2;cy=(y0+y1)/2
    pen=SVGPathPen(None);parse_path(parts[1],TransformPen(pen,(3,0,0,1.5,-2*cx,-.5*cy)))
    e.set('d',parts[0]+' '+pen.getCommands())
   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   e.set('stroke','none')
   black=i in (skin_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in skin_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  root.set('width',str(pixels));root.set('height',str(pixels))
  doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
  masks.append(np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128)
 removed_specks=0
 if key=='1f9df_200d_2642':
  # Two isolated raster pixels at the sharp right hair tip; neither is a
  # source feature. Pin their count instead of allowing general deletion.
  specks,n=ndimage.label(masks[0]);sizes=np.bincount(specks.ravel())
  tiny=np.isin(specks,[i for i in range(1,n+1) if sizes[i]<4])
  assert int(tiny.sum())==2,(key,int(tiny.sum()))
  removed_specks=2;masks[0]&=~tiny
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
 # Reviewed face, neck and both hands; blank eyes and tongue stay white.
 expected_material={'1f9df': (13, [1, 4, 5, 13]), '1f9df_200d_2642': (11, [1, 4, 5, 11]), '1f9df_200d_2640': (11, [1, 4, 6, 11])}[key]
 assert (n,selected)==expected_material,(key,n,selected)
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 report['opticalFingerGapScale']=[3,1.5]
 report['mergedSourcePaths']=[list(group) for group in merged.values()]
 return (white,skin,ink),report

