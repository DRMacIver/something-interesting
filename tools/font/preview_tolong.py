"""Render compiled Tolong glyphs and shaped marks at review and dialogue sizes."""
from pathlib import Path
import argparse
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import pymupdf
from build_tolong import ROOT, ABOVE, BELOW


def preview(path, output):
    font=TTFont(path); glyphset=font.getGlyphSet(); hfont=hb.Font(hb.Face(path.read_bytes()))
    rows=[('All letters and signs', ''.join(chr(cp) for cp in range(0x11DB0,0x11DDC))),
          ('Digits', ''.join(chr(cp) for cp in range(0x11DE0,0x11DEA))),
          ('Nine marks on I', ' '.join(chr(0x11DB0)+chr(cp) for cp in sorted(ABOVE|BELOW))),
          ('Unicode table 13-11', ' '.join(chr(cp)+'\u0324' for cp in
              (0x11DCA,0x11DCC,0x11DC5,0x11DC7,0x11DB7,0x11DD2,0x11DD4))+' '+chr(0x11DD4)+'\u0308'),
          ('Nasalized vowels and spacing SELA', ' '.join(chr(cp)+'\u0303'+chr(0x11DD9)
               for cp in (0x11DB0,0x11DB1,0x11DB2,0x11DB3,0x11DB4,0x11DB5))),
          ('Above, below and repeated marks', ' '.join(chr(0x11DB0)+marks
               for marks in ('\u0324\u0303','\u0303\u0303','\u0324\u0324')))]
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1250"><rect width="1200" height="1250" fill="#f5f2eb"/>']
    y=30
    for label,text in rows:
        svg.append(f'<text x="25" y="{y}" font-size="16">{label}</text>')
        for size in (40,24):
            buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(hfont,buf)
            cursor=0;baseline=y+size*1.5
            for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
                if cursor*size/1000>1130:
                    cursor=0;baseline+=size*1.6
                pen=SVGPathPen(glyphset);glyphset[font.getGlyphName(info.codepoint)].draw(pen)
                svg.append(f'<path fill="#111" transform="translate({25+(cursor+pos.x_offset)*size/1000} {baseline-pos.y_offset*size/1000}) scale({size/1000} {-size/1000})" d="{pen.getCommands()}"/>')
                cursor+=pos.x_advance
            y=baseline+size*.5
        y+=40
    svg.append('</svg>')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.with_suffix('.svg').write_text(''.join(svg))
    doc=pymupdf.open(stream=''.join(svg).encode(),filetype='svg')
    pdf=pymupdf.open('pdf',doc.convert_to_pdf());pdf[0].get_pixmap().save(output)
    print(output)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font',type=Path,default=ROOT/'output/font-review/tolong/DadTolongReview.ttf')
    parser.add_argument('--output',type=Path,default=ROOT/'output/font-review/tolong/compiled.png')
    args=parser.parse_args();preview(args.font,args.output)
