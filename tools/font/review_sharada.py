"""Render a deterministic HarfBuzz-positioned specimen of the Sharada prototype."""
from pathlib import Path
import pymupdf
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from sharada_vowels import add_marks

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/font-review'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    font=TTFont(ROOT/'build/unicode-sources/noto/NotoSansSharada-Regular.ttf')
    add_marks(font,TTFont(ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf'))
    path=OUT/'sharada-vowels-prototype.ttf';font.save(path)
    shaping=hb.Font(hb.Face(path.read_bytes()));glyphs=font.getGlyphSet()
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="850"><rect width="100%" height="100%" fill="white"/>']
    for col,cp in enumerate(range(0x11b60,0x11b68)):
        parts.append(f'<text x="{col*160+20}" y="30" font-size="16">{cp:X}</text>')
    for row,base in enumerate(['𑆑','𑆘','𑆨𑇀𑆘','𑆰𑇀𑆟']):
        for col,cp in enumerate(range(0x11b60,0x11b68)):
            x=20+col*160;y=170+row*200;advance=0
            buf=hb.Buffer();buf.add_str(base+chr(cp));buf.guess_segment_properties();hb.shape(shaping,buf)
            for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
                pen=SVGPathPen(glyphs);glyphs[font.getGlyphName(info.codepoint)].draw(pen)
                parts.append(f'<path d="{pen.getCommands()}" transform="translate({x+(advance+pos.x_offset)*.09} {y-pos.y_offset*.09}) scale(.09 -.09)"/>')
                advance+=pos.x_advance
    parts.append('</svg>')
    document=pymupdf.open(stream=''.join(parts).encode(),filetype='svg')
    target=OUT/'sharada-vowels-prototype.png';document[0].get_pixmap().save(target)
    print(target)


if __name__=='__main__':main()
