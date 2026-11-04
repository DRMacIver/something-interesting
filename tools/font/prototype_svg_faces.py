"""Experimental newer face recipes; production recipe review."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from pen_translate import Settings,translate
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[2]
RECIPES={
    '1fae9':(10,{2,4,5,6,7,9},{4,5,7,9},1.8),
    '1faea':(9,{0,2,3,4,6,7},{2,4,7},1.8),
    '1faeb':(31,set(range(21))|{24,26,28,30},{26,28,30},1.8),
}


from emoji_new_svg import prepare


def main():
    from build_emoji import outline
    from fontTools.pens.svgPathPen import SVGPathPen
    sheet=Image.new('RGB',(900,300),'#f5f2eb');draw=ImageDraw.Draw(sheet);records=[]
    for i,key in enumerate(RECIPES):
        (white,ink),r=prepare(key);ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1)
        glyph=outline(ink,(xs.min(),ys.min(),factor));advance=round((np.ptp(xs)+1)*factor)+100
        pen=SVGPathPen(None);glyph.draw(pen,None)
        r.update(codepoint=key,compiledContours=glyph.numberOfContours,status='Production recipe review')
        records.append(r)
        for size,x,y,optical in [(180,5,5,False),(33.6,235,80,True)]:
            stroke=' stroke="#111111" stroke-width="18" stroke-linejoin="round"' if optical else ''
            svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{advance}" height="1000"><rect width="100%" height="100%" fill="white"/><path transform="translate(0 850) scale(1 -1)" d="{pen.getCommands()}" fill="#111111"{stroke}/></svg>'
            doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000))
            sheet.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(i*300+x,y))
        draw.text((i*300+5,210),f'U+{key.upper()} applied {r["appliedStrength"]:.3f}',fill='black',font=ImageFont.load_default(size=16))
        draw.text((i*300+5,240),f'Contours {glyph.numberOfContours}/{r["sourceComponents"]+r["sourceHoles"]}',fill='black',font=ImageFont.load_default(size=14))
    out=ROOT/'output/font-review/pen-translation/svg-faces-prototype'
    sheet.save(out.with_suffix('.png'));out.with_suffix('.json').write_text(json.dumps(records,indent=2)+'\n')
    print(out)

if __name__=='__main__':main()
