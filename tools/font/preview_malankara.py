"""Compiled joining and vowel specimen for the eleven Malayalam Syriac letters."""
import io
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import uharfbuzz as hb
import pymupdf

ROOT=Path(__file__).resolve().parents[2]


def main():
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    entry=next(e for e in manifest['fonts'] if e['source'].endswith('/EastSyriacMalankara.ttf'))
    font=TTFont(ROOT/entry['file']);font.flavor=None
    stream=io.BytesIO();font.save(stream);face=hb.Face(stream.getvalue());glyphs=font.getGlyphSet()
    image=Image.new('RGB',(1000,720),'#f5f2eb');draw=ImageDraw.Draw(image)
    for i,cp in enumerate(range(0x860,0x86B)):
        # Render actual HarfBuzz output, including native RTL order and GPOS.
        text='ܒ'+chr(cp)+'ܒ '+chr(cp)+'ܲ '+chr(cp)+'ܼ'
        buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(hb.Font(face),buf)
        paths=[];x=0
        for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
            pen=SVGPathPen(glyphs);glyphs[font.getGlyphName(info.codepoint)].draw(pen)
            paths.append(f'<path transform="translate({x+pos.x_offset} {1900-pos.y_offset}) scale(1 -1)" d="{pen.getCommands()}"/>')
            x+=pos.x_advance
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{x+200}" height="3000"><rect width="100%" height="100%" fill="white"/>{"".join(paths)}</svg>'
        doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf())
        px=(i%2)*500+10;py=(i//2)*115+10
        draw.text((px,py),f'U+{cp:04X}',fill='black',font=ImageFont.load_default(size=16))
        for size,dx,dy in [(52,90,0),(24,90,72)]:
            scale=size/font['head'].unitsPerEm
            pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False)
            image.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(px+dx,py+dy))
    draw.text((10,700),'Native calligraphic source; fluent-reader and comic-style review still pending.',fill='black',font=ImageFont.load_default(size=15))
    out=ROOT/'output/font-review/malankara.png';image.save(out);print(out)


if __name__=='__main__':main()
