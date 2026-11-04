"""Source-specific general flag ink recipes, pending optical review."""
import hashlib,json,io,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
from pen_translate import Settings,translate
ROOT=Path(__file__).resolve().parents[2]
# (native shape count, outlined paper paths, solid ink paths, unoutlined
# white cutouts, colour paths). Shading/highlight paths are omitted.
RECIPES={
 '1f3c1':(17,[0,9],[10],list(range(11,17)),{}),
 '1f6a9':(6,[0,2,3],[],[],{2:'red',3:'red'}),
 '1f38c':(12,[0,2,4,5,6,7,8,9],[],[],{10:'red',11:'red'}),
 '1f3f4':(7,[0],[2,3,4],[],{}),
 '1f3f3':(7,[0,2,3,4],[],[],{}),
 '1f3f3_200d_1f308':(9,[],[],[],{1:'red',2:'orange',3:'yellow',4:'green',5:'blue',6:'purple'}),
 '1f3f3_200d_26a7':(7,[],[],[],{0:'blue',1:'pink',2:'white',4:'pink',5:'blue'}),
 '1f3f4_200d_2620':(8,[],[0],[4,5,6,7],{}),
}


def raster(root):
 raw=subprocess.run(['rsvg-convert','-w','1536','-h','1536'],input=ET.tostring(root),stdout=subprocess.PIPE,check=True).stdout
 rgba=Image.open(io.BytesIO(raw)).convert('RGBA');canvas=Image.new('RGBA',rgba.size,'white');canvas.alpha_composite(rgba)
 return np.asarray(canvas.convert('RGB')).max(axis=2)<128


def prepare(key):
 spec=json.loads((ROOT/'data/font-sources/noto-emoji-general-flags-svg.json').read_text())
 source=next(e for e in spec['files'] if e['path'].endswith('emoji_u'+key+'.svg'))
 raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
 count,paper_paths,ink_paths,cutouts,colour_paths=RECIPES[key]
 names=list(dict.fromkeys(colour_paths.values()));masks=[]
 for mode in [None,*names]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
  shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
  assert len(shapes)==count
  for i,e in enumerate(shapes):
   if i not in paper_paths and i not in ink_paths and i not in cutouts and i not in colour_paths:
    parents[e].remove(e);continue
   e.attrib.pop('style',None);e.attrib.pop('opacity',None)
   e.set('stroke','none');e.set('fill','#ffffff')
   if mode is not None:
    if colour_paths.get(i)==mode:e.set('fill','#111111')
   elif i in ink_paths:e.set('fill','#111111')
   elif i not in cutouts:
    e.set('stroke','#111111');e.set('stroke-width','1.3');e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
  masks.append(raster(root))
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 image,report=translate(masks[0],Settings(strength=1.7,seed=seed,pressure=.04,taper=0,bend=.001))
 assert report['appliedStrength']>0 and not report['fallback'],key
 ink=np.asarray(image)<128;paper=ndi.binary_fill_holes(ink)
 labels,n=ndi.label(paper&~ink);sizes=np.bincount(labels.ravel());colours=[]
 for mask in masks[1:]:
  material=np.pad(mask,report['padding']);overlaps=np.bincount(labels[material],minlength=n+1)
  selected=[i for i in range(1,n+1) if sizes[i]>=32 and overlaps[i]/sizes[i]>.5]
  assert selected,(key,names,n)
  colours.append(ndi.binary_dilation(np.isin(labels,selected),iterations=3)&paper&~((labels>0)&~np.isin(labels,selected)))
 palette_path=ROOT/'output/imagegen/emoji-production/heart-palette-source.json';palette_raw=palette_path.read_bytes();palette=json.loads(palette_raw)
 assert hashlib.sha256((ROOT/palette['pdf']).read_bytes()).hexdigest()==palette['pdfSha256']
 samples={e['colour']:e['rgb'] for e in palette['samples']}
 rgbs=[(255,255,255) if name=='white' else tuple(samples[name]) for name in names]
 report.update(key=key,source=source,rgbs=rgbs,colourNames=names,paletteSha256=hashlib.sha256(palette_raw).hexdigest(),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 return (paper,*colours,ink),report

