"""Trace and review the new SVG prototypes without modifying production assets."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from fontTools.pens.svgPathPen import SVGPathPen
from build_emoji import outline

ROOT=Path(__file__).resolve().parents[2]


def main():
    out=ROOT/'output/font-review/pen-translation'
    reports=json.loads((out/'new-svg-ink-prototype.json').read_text())
    sheet=Image.new('RGB',(300*len(reports),300),'#f5f2eb');draw=ImageDraw.Draw(sheet)
    for i,r in enumerate(reports):
        ink=np.asarray(Image.open(out/f'new-svg-ink-{r["codepoint"]}.png'))<128
        ys,xs=np.nonzero(ink);scale=760/max(np.ptp(xs)+1,np.ptp(ys)+1)
        glyph=outline(ink,(xs.min(),ys.min(),scale));advance=round((np.ptp(xs)+1)*scale)+100
        assert glyph.numberOfContours>=r['sourceComponents']+r['sourceHoles']
        pen=SVGPathPen(None);glyph.draw(pen,None)
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{advance}" height="1000"><rect width="100%" height="100%" fill="white"/><path transform="translate(0 850) scale(1 -1)" fill="#111111" d="{pen.getCommands()}"/></svg>'
        doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf())
        for size,dx,dy in [(210,5,5),(24,245,90)]:
            pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000))
            sheet.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(i*300+dx,dy))
        draw.text((i*300+5,225),f'U+{r["codepoint"].upper()} traced prototype',fill='black',font=ImageFont.load_default(size=15))
        draw.text((i*300+5,251),f'{glyph.numberOfContours} contours preserved',fill='black',font=ImageFont.load_default(size=14))
    sheet.save(out/'new-svg-compiled-prototype.png')
    print(out/'new-svg-compiled-prototype.png')


if __name__=='__main__':main()
