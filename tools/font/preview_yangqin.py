"""Show compiled Yangqin signs beside their native Suzhou baseline form."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import pymupdf

ROOT = Path(__file__).resolve().parents[2]


def main():
    manifest = json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    image = Image.new('RGB',(800,220),'#f5f2eb'); draw = ImageDraw.Draw(image)
    for i,cp in enumerate([0x3026,0x16FF4,0x16FF5,0x16FF6]):
        entry = next(e for e in manifest['fonts'] if 'LXGWWenKai' in e['source'] and any(a<=cp<=b for a,b in e['ranges']))
        font = TTFont(ROOT/entry['file']); glyphs = font.getGlyphSet()
        pen = SVGPathPen(glyphs); glyphs[font.getBestCmap()[cp]].draw(pen)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000"><rect width="100%" height="100%" fill="white"/><path transform="translate(0 850) scale(1 -1)" d="{pen.getCommands()}"/></svg>'
        doc = pymupdf.open(stream=svg.encode(),filetype='svg'); pdf = pymupdf.open('pdf',doc.convert_to_pdf())
        for size,dx,dy in [(140,0,0),(24,160,75)]:
            pix = pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000),alpha=False)
            image.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(i*200+dx,dy))
        draw.text((i*200+10,150),f'U+{cp:04X}',fill='black',font=ImageFont.load_default(size=18))
        draw.text((i*200+10,178),['1/2 beat','1 beat','3/2 beats','2 beats'][i],fill='black',font=ImageFont.load_default(size=16))
    out = ROOT/'output/font-review/yangqin-signs.png'; image.save(out); print(out)


if __name__ == '__main__': main()
