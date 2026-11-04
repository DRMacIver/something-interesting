"""Preview reviewed clothed-sport production geometry."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from fontTools.pens.svgPathPen import SVGPathPen
from build_emoji import outline
from emoji_clothed_sport import ROOT,RECIPES as ALL_RECIPES,prepare
RECIPES={k:v for k,v in ALL_RECIPES.items() if k=='1f3c2'}

def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--keys',nargs='*');args=parser.parse_args()
 active={k:v for k,v in RECIPES.items() if not args.keys or k in args.keys}
 records=[];sheet=Image.new('RGB',(350*len(active),450),'#f5f2eb');draw=ImageDraw.Draw(sheet)
 for i,key in enumerate(active):
  (white,ink),r=prepare(key);ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1);glyph=outline(ink,(xs.min(),ys.min(),factor));advance=round((np.ptp(xs)+1)*factor)+100
  assert glyph.numberOfContours==r['sourceComponents']+r['sourceHoles']
  r['compiledContours']=glyph.numberOfContours;records.append(r);pen=SVGPathPen(None);glyph.draw(pen,None)
  for size,x,y,stroke in [(280,0,0,0),(33.6,280,100,18)]:
   svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{advance}" height="1000"><rect width="100%" height="100%" fill="white"/><path transform="translate(0 850) scale(1 -1)" fill="#111" stroke="#111" stroke-width="{stroke}" stroke-linejoin="round" d="{pen.getCommands()}"/></svg>'
   doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000))
   sheet.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(i*350+x,y))
  draw.text((i*350+5,300),f'{key}: {r["appliedStrength"]:.3f}; {glyph.numberOfContours} contours',fill='black',font=ImageFont.load_default(size=16))
 out=ROOT/('output/font-review/pen-translation/snowboarding-svg-'+('-'.join(active))+'-prototype');sheet.save(out.with_suffix('.png'));out.with_suffix('.json').write_text(json.dumps(records,indent=2)+'\n');print(out)
if __name__=='__main__':main()
