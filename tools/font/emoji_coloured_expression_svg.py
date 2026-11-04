"""Reviewed coloured expression details with PDF-sampled colour."""
import hashlib,json,re
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from pen_translate import Settings,translate,same_features
from emoji_activity_svg import leg_union
ROOT=Path(__file__).resolve().parents[2]
# Source colours retain meaningful red/pink heart distinctions.
RECIPES={'1f633':(13,{2:'pink',3:'pink'},[0,7,9]),'1f4a6':(6,{0:'light blue',1:'light blue',2:'light blue'},[]),'1f48c':(5,{3:'red'},[0]),'1f4ab':(5,{2:'yellow'},[]),'1f916':(15,{3:'red',10:'red'},[0,1,2,4,11,13]),'1f48b':(2,{0:'red',1:'red'},[]),'1f4a5':(2,{0:'orange',1:'yellow'},[])}
INK={'1f633':{4,5,6,8,10},'1f48c':{1},'1f4ab':{0},'1f916':set(range(5,10))}

RECIPES.update({'1f92e':(22,{6:'green',14:'green',15:'green',16:'green',17:'green'},[1,11]),'1f921':(22,{4:'red',13:'red',17:'red',19:'red'},[0,5,6])})
INK.update({'1f92e':{3,4,5,7,8,9,10,12,13},'1f921':{7,9,16,21}})

RECIPES.update({'1f479':(34,{7:'red',25:'red',30:'yellow',32:'yellow'},[9,12,*range(15,23)]),'1f47a':(21,{0:'red',11:'red'},[1,3,5])})
INK.update({'1f479':{0,3,5,8,10,11,13,14,26,27},'1f47a':{4,6,7,8,15,17}})

def raster(root):
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128

REVIEWED_TOPOLOGY={'1f633': (8, 5), '1f4a6': (3, 3), '1f48c': (1, 3), '1f4ab': (1, 1), '1f916': (6, 13), '1f48b': (2, 2), '1f4a5': (2, 2)}
REVIEWED_REGIONS={'1f633': (5, [[4, 5]]), '1f4a6': (3, [[1, 2, 3]]), '1f48c': (3, [[3]]), '1f4ab': (1, [[1]]), '1f916': (13, [[2, 7]]), '1f48b': (2, [[1, 2]]), '1f4a5': (2, [[1], [2]])}

REVIEWED_TOPOLOGY.update({'1f92e': (13, 8), '1f921': (8, 8), '1f479': (7, 14), '1f47a': (7, 5)})
REVIEWED_REGIONS.update({'1f92e': (8, [[3, 4, 5, 7, 8]]), '1f921': (8, [[1, 2, 6, 7]]), '1f479': (14, [[3, 6], [1, 2]]), '1f47a': (5, [[1, 4]])})

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-expressions-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 masks=[];count,paths,paper=RECIPES[key];colour_names=list(dict.fromkeys(paths.values()))
 for mode in [None,*colour_names]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==count
  if key=='1f4a5':
   for element in shapes:
    points=re.findall(r'-?\d+(?:\.\d+)?',element.attrib.pop('points'));element.tag=element.tag.replace('polygon','path')
    element.set('d','M'+' L'.join(','.join(points[i:i+2]) for i in range(0,len(points),2))+' Z')
  if key=='1f4ab':shapes[0].set('d',leg_union(raw,(0,1)))
  if key=='1f633':
   for i in [2,3]:
    shapes[i].tag=shapes[i].tag.replace('circle','ellipse');shapes[i].attrib.pop('r')
    shapes[i].set('rx','10');shapes[i].set('ry','5');shapes[i].set('cy','83')
  for i,e in enumerate(shapes):
   if i not in paths and i not in paper and i not in INK.get(key,set()):parents[e].remove(e);continue
   e.attrib.pop('style',None);e.attrib.pop('opacity',None)
   e.set('fill','#111111' if mode is not None and paths.get(i)==mode else '#ffffff');e.set('stroke','none')
   if i in INK.get(key,set()):
    e.set('fill','#111111' if mode is None else '#ffffff')
   elif mode is None and not (key=='1f479' and i in range(15,23)):
    e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  mask=raster(root)
  if key=='1f47a' and mode is None:
   # Raster intersections can enclose subpixel specks; they are not features.
   labels,n=ndimage.label(ndimage.binary_fill_holes(mask)&~mask)
   sizes=np.bincount(labels.ravel());mask|=np.isin(labels,[i for i in range(1,n+1) if sizes[i]<4])
  masks.append(mask)
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 im,r=translate(masks[0],Settings(strength=1.7,seed=seed,pressure=.04 if key=='1f47a' else .25,taper=0 if key=='1f47a' else .1,bend=.001 if key=='1f47a' else .004));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 if key=='1f47a':
  labels,n=ndimage.label(ndimage.binary_fill_holes(ink)&~ink);sizes=np.bincount(labels.ravel())
  specks=[i for i in range(1,n+1) if sizes[i]<4]
  r['rasterPinholesFilled']=int(sum(sizes[i] for i in specks))
  cleaned=ink|np.isin(labels,specks);assert same_features(ink,cleaned);ink=cleaned
 if key in REVIEWED_TOPOLOGY:assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink);labels,n=ndimage.label(white&~ink);sizes=np.bincount(labels.ravel());colours=[];selected_regions=[]
 for mask in masks[1:]:
  material=np.pad(mask,r['padding']);overlaps=np.bincount(labels[material],minlength=n+1)
  selected=[i for i in range(1,n+1) if sizes[i]>=32 and overlaps[i]/sizes[i]>.5]
  assert selected,(key,n)
  colour=np.isin(labels,selected);colour=ndimage.binary_dilation(colour,iterations=3)&white&~((labels>0)&~np.isin(labels,selected));colours.append(colour);selected_regions.append(selected)
 if key in REVIEWED_REGIONS:assert (n,selected_regions)==REVIEWED_REGIONS[key],(key,n,selected_regions)
 assert len({i for region in selected_regions for i in region})==sum(map(len,selected_regions))
 palette_path=ROOT/'output/imagegen/emoji-production/heart-palette-source.json';palette_raw=palette_path.read_bytes();palette=json.loads(palette_raw)
 assert hashlib.sha256((ROOT/palette['pdf']).read_bytes()).hexdigest()==palette['pdfSha256']
 rgbs=[next(s['rgb'] for s in palette['samples'] if s['colour']==name) for name in colour_names]
 r.update(key=key,source=source,sourcePixels=1536,colourPaths=paths,inkPaths=sorted(INK.get(key,set())),paperPaths=paper,unionPaths=[0,1] if key=='1f4ab' else [],unionProgramSha256=hashlib.sha256((ROOT/'tools/font/emoji_activity_svg.py').read_bytes()).hexdigest(),blushEllipse={'rx':10,'ry':5,'cy':83} if key=='1f633' else None,colourRegions=selected_regions,regionCount=n,colourNames=colour_names,rgbs=rgbs,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest(),paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest())
 return (white,*colours,ink),r
