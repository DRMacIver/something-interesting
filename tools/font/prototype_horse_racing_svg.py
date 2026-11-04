"""Independent horse-racing source experiment; not production coverage."""
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
RECIPES={'1f3c7':(32,set(range(32))-{7,8,29},{0,3,4,5,9,10,12,14,15,16,17,18,21,22,23,24,26,27,28,31},{19,20})}
def prepare(key):
 expected,keep,solid,skin_paths=RECIPES[key]
 spec=json.loads((ROOT/'docs/sport-emoji-svg-source-probe.json').read_text())
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
   if i==19:e.set('d',leg_union(raw,(19,29)))
   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   black=i in (skin_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in skin_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
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
 # Candidate skin regions require anatomical review.
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 assert selected and skin.sum()>5000 and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 return (white,skin,ink),report


def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--keys',nargs='*');parser.add_argument('--strict',action='store_true');args=parser.parse_args()
 active={k:v for k,v in RECIPES.items() if not args.keys or k in args.keys}
 from build_emoji import outline
 out=ROOT/'output/font-review/pen-translation';record_path=out/'horse-racing-svg-prototype.json'
 records=[r for r in json.loads(record_path.read_text()) if r['key'] not in active] if record_path.exists() else []
 for base in sorted({key.split('_')[0] for key in active}):
  keys=[k for k in active if k.split('_')[0]==base];sheet=Image.new('RGB',(350*len(keys),430),'#f5f2eb');draw=ImageDraw.Draw(sheet)
  for j,key in enumerate(keys):
   (white,skin,ink),r=prepare(key);ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1);glyph=outline(ink,(xs.min(),ys.min(),factor))
   r.update(key=key,compiledContours=glyph.numberOfContours,topologyAccepted=glyph.numberOfContours==r['sourceComponents']+r['sourceHoles'],treatmentAccepted=r['appliedStrength']>0 and not r['fallback'])
   rgb=np.full((*ink.shape,3),255,dtype='uint8');rgb[skin]=(171,129,90);rgb[ink]=17
   tile=Image.fromarray(rgb);tile.thumbnail((330,330));sheet.paste(tile,(j*350,0))
   draw.text((j*350+4,335),key,fill='black',font=ImageFont.load_default(size=15))
   draw.text((j*350+4,360),f'{r["appliedStrength"]:.3f}; contours {glyph.numberOfContours}/{r["sourceComponents"]+r["sourceHoles"]}',fill='black',font=ImageFont.load_default(size=15))
   draw.text((j*350+4,385),f'Skin regions {len(r["skinRegions"])}/{r["enclosedRegions"]}',fill='black',font=ImageFont.load_default(size=14))
   records.append(r)
  sheet.save(out/f'horse-racing-svg-{base}-prototype.png')
 (out/'horse-racing-svg-prototype.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
 failures=[r['key'] for r in records if not (r['topologyAccepted'] and r['treatmentAccepted'])]
 print(f'{len(records)-len(failures)} / {len(records)} drawings preserve treatment and compiled contours')
 if args.strict:assert not failures,failures
if __name__=='__main__':main()
