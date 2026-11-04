"""Reviewed award and event symbols with meaningful medal colours."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from pen_translate import Settings,translate
from emoji_activity_svg import leg_union
from emoji_tile_lettering import replace_letters
ROOT=Path(__file__).resolve().parents[2]
# Rank numerals use the existing comic lettering; colours distinguish the metals.
RECIPES={
 '1f9e7':(12,{0:'red',1:'red',2:'yellow'},[]),
 '2728':(7,{0:'yellow',3:'yellow',6:'yellow'},[]),
 '1f397':(3,{0:'yellow',1:'yellow',2:'yellow'},[]),
 '1f396':(14,{0:'blue',2:'red',3:'yellow',4:'yellow'},[1]),
 '1f3c6':(13,{0:'yellow',11:'brown',12:'yellow'},[]),
 '1f3c5':(8,{0:'blue',1:'yellow',3:'yellow',5:'blue'},[]),
 '1f947':(9,{0:'blue',1:'yellow',3:'yellow',8:'blue'},[]),
 '1f948':(9,{0:'blue',1:'grey',3:'grey',7:'blue'},[]),
 '1f949':(9,{0:'blue',1:'orange',3:'orange',7:'blue'},[])}
INK={'1f3c6':{7},'1f3c5':{7},'1f947':{7},'1f948':{8},'1f949':{8}}
DIGITS={'1f947':(7,'1'),'1f948':(8,'2'),'1f949':(8,'3')}

def raster(root):
 root.set('width','1536');root.set('height','1536')
 doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128

REVIEWED_TOPOLOGY={'2728': (3, 3), '1f397': (1, 5), '1f396': (1, 7), '1f3c6': (4, 6), '1f3c5': (2, 5), '1f947': (2, 5), '1f948': (2, 5), '1f949': (2, 5), '1f9e7': (3, 4)}
REVIEWED_REGIONS={'2728': (3, [[1, 2, 3]]), '1f397': (5, [[1, 2, 3, 5]]), '1f396': (7, [[4, 5], [2], [6, 7]]), '1f3c6': (6, [[1, 4, 6], [5]]), '1f3c5': (5, [[1, 2], [3, 5]]), '1f947': (6, [[1, 2], [3, 6]]), '1f948': (6, [[1, 2], [3, 6]]), '1f949': (5, [[1, 2], [3, 5]]), '1f9e7': (4, [[1, 2, 4], [3]])}

def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-awards-events-svg.json').read_text());source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 masks=[];count,paths,paper=RECIPES[key];colour_names=list(dict.fromkeys(paths.values()))
 for mode in [None,*colour_names]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p};shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==count
  lettering=replace_letters(ROOT,key,shapes,[DIGITS[key][0]],DIGITS[key][1]) if key in DIGITS else None
  for i,e in enumerate(shapes):
   if i not in paths and i not in paper and i not in INK.get(key,set()):parents[e].remove(e);continue
   e.attrib.pop('style',None);e.attrib.pop('opacity',None)
   e.set('fill','#111111' if mode is not None and paths.get(i)==mode else '#ffffff');e.set('stroke','none')
   if i in INK.get(key,set()):e.set('fill','#111111' if mode is None else '#ffffff')
   elif mode is None:
    e.set('stroke','#111111');e.set('stroke-width','.4' if key=='1f9e7' and i in {2,3} else '1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  masks.append(raster(root))
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 im,r=translate(masks[0],Settings(strength=1.7,seed=seed,pressure=.04,taper=0,bend=.001));ink=np.asarray(im)<128
 assert r['appliedStrength']>0 and not r['fallback'],key
 if key in REVIEWED_TOPOLOGY:assert (r['sourceComponents'],r['sourceHoles'])==REVIEWED_TOPOLOGY[key],key
 white=ndimage.binary_fill_holes(ink);labels,n=ndimage.label(white&~ink);sizes=np.bincount(labels.ravel());colours=[];selected_regions=[]
 for mask in masks[1:]:
  material=np.pad(mask,r['padding']);overlaps=np.bincount(labels[material],minlength=n+1)
  selected=[i for i in range(1,n+1) if sizes[i]>=32 and overlaps[i]/sizes[i]>.5]
  assert selected,(key,n)
  colour=np.isin(labels,selected);colour=ndimage.binary_dilation(colour,iterations=3)&white&~((labels>0)&~np.isin(labels,selected));colours.append(colour);selected_regions.append(selected)
 if key in REVIEWED_REGIONS:assert (n,selected_regions)==REVIEWED_REGIONS[key],(key,n,selected_regions)
 assert len({i for region in selected_regions for i in region})==sum(map(len,selected_regions))
 character_report=None
 if key=='1f9e7':
  # Gold calligraphy is ink in its own right, without a black border that would
  # swallow its fine strokes when the renderer adds the black ink companion.
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
  shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  for i,e in enumerate(shapes):
   if i<3:parents[e].remove(e);continue
   e.attrib.pop('style',None);e.set('fill','#111111');e.set('stroke','none')
  character,character_report=translate(raster(root),Settings(strength=1.7,seed=seed,pressure=.04,taper=0,bend=.001))
  assert character_report['appliedStrength']>0 and not character_report['fallback']
  assert (character_report['sourceComponents'],character_report['sourceHoles'])==(4,5)
  padding=character_report['padding'];character=np.asarray(character)<128
  if padding:character=character[padding:-padding,padding:-padding]
  character=np.pad(character,r['padding']);assert character.shape==white.shape
  assert not np.any(character&~white)
  colours[colour_names.index('red')] &= ~character
  colours[colour_names.index('yellow')] |= character
  character_report['sourcePaths']=list(range(3,12))
 palette_path=ROOT/'output/imagegen/emoji-production/heart-palette-source.json';palette_raw=palette_path.read_bytes();palette=json.loads(palette_raw)
 assert hashlib.sha256((ROOT/palette['pdf']).read_bytes()).hexdigest()==palette['pdfSha256']
 rgbs=[next(s['rgb'] for s in palette['samples'] if s['colour']==name) for name in colour_names]
 r['goldCharacter']=character_report
 r.update(inkPaths=sorted(INK.get(key,set())),comicLettering=lettering,unionPaths=[],unionProgramSha256=hashlib.sha256((ROOT/'tools/font/emoji_activity_svg.py').read_bytes()).hexdigest(),key=key,source=source,sourcePixels=1536,colourPaths=paths,paperPaths=paper,colourRegions=selected_regions,regionCount=n,colourNames=colour_names,rgbs=rgbs,svgStrokeWidth=1.3,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest(),paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest())
 return (white,*colours,ink),r
