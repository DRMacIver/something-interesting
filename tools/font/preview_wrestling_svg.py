"""Review independent wrestling anatomy and mixed-tone drawings at dialogue size."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import pymupdf
from fontTools.pens.svgPathPen import SVGPathPen
from build_emoji import outline
from prototype_wrestling_svg import ROOT,prepare,RECIPES

palette=json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())['palette']
sheet=Image.new('RGB',(1100,780),'#f5f2eb');d=ImageDraw.Draw(sheet);records=[]
for row,key in enumerate(RECIPES):
 (white,skin,ink),report=prepare(key);labels,n=ndimage.label(white&~ink)
 sides=[ndimage.binary_dilation(np.isin(labels,report['pairedSkinRegions'][side]),iterations=3)&skin for side in ['left','right']]
 assert not (sides[0]&sides[1]).any() and np.array_equal(sides[0]|sides[1],skin)
 anatomy=np.full((*ink.shape,3),255,dtype='uint8');anatomy[sides[0]]=(45,163,216);anatomy[sides[1]]=(216,92,162);anatomy[ink]=17
 labelled=Image.fromarray(anatomy).resize((700,700));ld=ImageDraw.Draw(labelled);regions=[]
 for side in ['left','right']:
  for index in report['pairedSkinRegions'][side]:
   yy,xx=np.nonzero(labels==index);ld.text((xx.mean()/ink.shape[1]*700,yy.mean()/ink.shape[0]*700),str(index),fill='red',font=ImageFont.load_default(size=17))
   regions.append(dict(region=index,owner=side,pixels=int(len(xx)),sourceBox=[round((float(v)-report['padding'])/12,2) for v in [xx.min(),yy.min(),xx.max(),yy.max()]]))
 labelled.save(ROOT/f'output/font-review/pen-translation/wrestling-{key}-paired-regions.png')
 ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1);transform=xs.min(),ys.min(),factor;advance=round((np.ptp(xs)+1)*factor)+100;paths=[]
 for mask in [white,*sides,ink]:
  glyph=outline(mask,transform);pen=SVGPathPen(None);glyph.draw(pen,None);paths.append(pen.getCommands())
 for col,(a,b) in enumerate([(1,5),(5,1),(2,4),(4,2),(3,3)]):
  colours=['#fff']+['#%02x%02x%02x'%tuple(palette[5+i]) for i in [a,b]]+['#111']
  parts=[f'<path fill="{c}" d="{p}"/>' for c,p in zip(colours,paths)]
  parts.append(f'<path fill="none" stroke="#111" stroke-width="18" stroke-linejoin="round" d="{paths[-1]}"/>')
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{advance}" height="1000"><rect width="100%" height="100%" fill="white"/><g transform="translate(0 850) scale(1 -1)">{"".join(parts)}</g></svg>'
  doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf())
  for size,xoff,yoff in [(160,10,35),(33.6,165,105)]:
   pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000));sheet.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(col*220+xoff,row*260+yoff))
 d.text((8,row*260+8),key+' - paired tones; stronger ink; 160px and 33.6px',fill='black',font=ImageFont.load_default(size=16))
 records.append(dict(key=key,regions=regions,pairedSkinRegions=report['pairedSkinRegions']))
sheet.save(ROOT/'output/font-review/pen-translation/wrestling-optics-comparison.png')
(ROOT/'output/font-review/pen-translation/wrestling-paired-skin-review.json').write_text(json.dumps(records,indent=2)+'\n')
