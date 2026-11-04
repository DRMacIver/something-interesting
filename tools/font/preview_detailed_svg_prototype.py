"""Compile and preview the four detailed SVG experiments without publishing them."""
import sys,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from scipy import ndimage
from fontTools.pens.svgPathPen import SVGPathPen
ROOT=Path(__file__).resolve().parents[2]
from build_emoji import outline
out=ROOT/'output/font-review/pen-translation';sheet=Image.new('RGB',(960,240),'#f5f2eb');draw=ImageDraw.Draw(sheet);records=[]
for i,cp in enumerate(['1f930','1fac3','1fac4','1f468_200d_1f37c']):
 p=out/f'detailed-svg-{cp}-768-1.3.png';r=json.loads(p.with_suffix('.json').read_text());ink=np.asarray(Image.open(p))<128;white=ndimage.binary_fill_holes(ink);ys,xs=np.nonzero(white);scale=760/max(np.ptp(xs)+1,np.ptp(ys)+1);g=outline(ink,(xs.min(),ys.min(),scale));advance=round((np.ptp(xs)+1)*scale)+100;pen=SVGPathPen(None);g.draw(pen,None)
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{advance}" height="1000"><rect width="100%" height="100%" fill="white"/><path transform="translate(0 850) scale(1 -1)" fill="#111111" d="{pen.getCommands()}"/></svg>'
 doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf())
 for size,dx,dy in [(160,5,0),(24,185,65)]:
  pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000));sheet.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(i*240+dx,dy))
 draw.text((i*240+5,165),cp,fill='black',font=ImageFont.load_default(size=12));draw.text((i*240+5,185),f"Applied {r['appliedStrength']:.2f}; experiment",fill='black',font=ImageFont.load_default(size=12))
 expected=r['sourceComponents']+r['sourceHoles'];records.append(dict(source=p.name,expectedContours=expected,compiledContours=g.numberOfContours,contoursPreserved=g.numberOfContours>=expected,status='prototype; not production'))
sheet.save(out/'detailed-svg-compiled-probe.png');(out/'detailed-svg-compiled-probe.json').write_text(json.dumps(records,indent=2)+'\n');print(records)
