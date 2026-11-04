"""Preview prototype horse racing at production ink weight and dialogue size."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from fontTools.pens.svgPathPen import SVGPathPen
from build_emoji import outline
from prototype_horse_racing_svg import ROOT,prepare
palette=json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())['palette']
sheet=Image.new('RGB',(1100,260),'#f5f2eb');d=ImageDraw.Draw(sheet)
for row,key in enumerate(['1f3c7']):
 (white,skin,ink),r=prepare(key);ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1);transform=xs.min(),ys.min(),factor;advance=round((np.ptp(xs)+1)*factor)+100
 paths=[]
 for mask in [white,skin,ink]:
  g=outline(mask,transform);pen=SVGPathPen(None);g.draw(pen,None);paths.append(pen.getCommands())
 for i in range(5):
  colour='#%02x%02x%02x'%tuple(palette[6+i]);parts=[]
  for path,fill in zip(paths,['#fff',colour,'#111']):parts.append(f'<path fill="{fill}" d="{path}"/>')
  parts.append(f'<path fill="none" stroke="#111" stroke-width="18" stroke-linejoin="round" d="{paths[2]}"/>')
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{advance}" height="1000"><rect width="100%" height="100%" fill="white"/><g transform="translate(0 850) scale(1 -1)">{"".join(parts)}</g></svg>'
  doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf())
  for size,xoff,yoff in [(160,10,35),(33.6,165,105)]:
   pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000));sheet.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(i*220+xoff,row*260+yoff))
 d.text((8,row*260+8),key+' - stronger ink; 160px and 33.6px',fill='black',font=ImageFont.load_default(size=17))
sheet.save(ROOT/'output/font-review/pen-translation/horse-racing-optics-comparison.png')
