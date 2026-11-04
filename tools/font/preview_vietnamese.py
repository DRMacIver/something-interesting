"""Inspect provisional Vietnamese side marks in compiled font shards."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import pymupdf

ROOT = Path(__file__).resolve().parents[2]


def main():
    manifest = json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    samples = ['日𖿰','日𖿱','量𖿰','外𖿱']
    image = Image.new('RGB',(960,260),'#f5f2eb'); draw = ImageDraw.Draw(image)
    for i,text in enumerate(samples):
        paths = []; x = 0
        for char in text:
            cp = ord(char)
            entry = next(e for e in manifest['fonts'] if 'LXGWWenKai' in e['source'] and any(a<=cp<=b for a,b in e['ranges']))
            font = TTFont(ROOT/entry['file']); glyphs = font.getGlyphSet()
            name = font.getBestCmap()[cp]; pen = SVGPathPen(glyphs); glyphs[name].draw(pen)
            paths.append(f'<path transform="translate({x} 850) scale(1 -1)" d="{pen.getCommands()}"/>')
            x += font['hmtx'][name][0]
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{x}" height="1000"><rect width="100%" height="100%" fill="white"/>{"".join(paths)}</svg>'
        doc = pymupdf.open(stream=svg.encode(),filetype='svg'); pdf = pymupdf.open('pdf',doc.convert_to_pdf())
        for size,dy in [(140,0),(24,160)]:
            pix = pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000),alpha=False)
            image.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(i*240+10,dy))
        draw.text((i*240+10,202),' + '.join(f'{ord(c):04X}' for c in text),fill='black',font=ImageFont.load_default(size=16))
    draw.text((10,235),'Provisional side forms; historical merged forms still need review.',fill='black',font=ImageFont.load_default(size=15))
    out = ROOT/'output/font-review/vietnamese-marks.png'; image.save(out); print(out)


if __name__ == '__main__': main()
