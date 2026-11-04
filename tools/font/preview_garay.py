"""Render compiled Garay glyphs and shaped marks at review and dialogue sizes."""
from pathlib import Path
import argparse
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import pymupdf
from build_garay import ROOT, MARKS


def preview(path, output):
    font=TTFont(path); glyphset=font.getGlyphSet(); hfont=hb.Font(hb.Face(path.read_bytes()))
    rows=[('Uppercase consonants', ''.join(chr(cp) for cp in range(0x10D50,0x10D66))),
          ('Lowercase consonants', ''.join(chr(cp) for cp in range(0x10D70,0x10D86))),
          ('Spacing signs and symbols', ' '.join(chr(cp) for cp in list(range(0x10D4A,0x10D50))+[0x10D6E,0x10D6F,0x10D8E,0x10D8F])),
          ('All marks on both cases', ' '.join(chr(base)+chr(mark) for base in (0x10D53,0x10D73) for mark in sorted(MARKS))),
          ('Unicode figure 19-5', ' '.join(''.join(map(chr,seq)) for seq in
            [(0x10D73,),(0x10D73,0x10D69),(0x10D73,0x10D69,0x10D4D),
             (0x10D74,0x10D69),(0x10D74,0x10D69,0x10D4D),(0x10D74,0x10D69,0x10D4D,0x10D4D),
             (0x10D74,),(0x10D74,0x10D4D),(0x10D74,0x10D4D,0x10D4D)])),
          ('Mark stacks and adjacent bases', chr(0x10D73)+chr(0x10D69)*2+chr(0x10D74)+chr(0x10D6A)),
          ('Digits (LTR number run)', ''.join(chr(cp) for cp in range(0x10D40,0x10D4A)))]
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1250"><rect width="1200" height="1250" fill="#f5f2eb"/>']
    y=30
    for label,text in rows:
        svg.append(f'<text x="25" y="{y}" font-size="16">{label}</text>')
        for size in (40,24):
            buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties()
            if label.startswith('Digits'):buf.direction='ltr'
            hb.shape(hfont,buf)
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
    parser.add_argument('--font',type=Path,default=ROOT/'output/font-review/garay/DadGaray.ttf')
    parser.add_argument('--output',type=Path,default=ROOT/'output/font-review/garay/compiled.png')
    args=parser.parse_args();preview(args.font,args.output)
