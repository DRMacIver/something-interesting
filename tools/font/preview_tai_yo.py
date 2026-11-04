"""Render compiled Tai Yo glyphs and shaped marks at review and dialogue sizes."""
from pathlib import Path
import argparse
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import pymupdf
from build_tai_yo import ROOT, MARKS


def preview(path, output):
    font=TTFont(path); glyphset=font.getGlyphSet(); hfont=hb.Font(hb.Face(path.read_bytes()))
    rows=[('Consonants', ''.join(chr(cp) for cp in range(0x1E6C0,0x1E6DF))),
          ('Spacing vowels, rhymes and symbols', ''.join(chr(cp) for cp in range(0x1E6E0,0x1E6F6) if cp not in MARKS)+chr(0x1E6FE)+chr(0x1E6FF)),
          ('Five marks on LOW KO', ' '.join(chr(0x1E6C0)+chr(cp) for cp in sorted(MARKS))),
          ('Wide consonant body attachment', ' '.join(chr(base)+chr(mark) for base in (0x1E6CD,0x1E6D5) for mark in sorted(MARKS))),
          ('Figure 16-9 adjacent marks', chr(0x1E6C5)+chr(0x1E6EE)*2+' '+chr(0x1E6DC)+chr(0x1E6EE)+chr(0x1E6EF)),
          ('Figure 16-6 UE spelling', ' '.join(''.join(map(chr,seq)) for seq in
            [(0x1E6D6,0x1E6E3),(0x1E6C6,0x1E6E3),(0x1E6D1,0x1E6E2,0x1E6CF),(0x1E6D4,0x1E6E2,0x1E6CF)])),
          ('Explicit KVO and ordinary KO + VO', chr(0x1E6DD)+' '+chr(0x1E6C0)+chr(0x1E6D9)+' '+chr(0x1E6DE)+' '+chr(0x1E6C1)+chr(0x1E6D9))]
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1500"><rect width="1200" height="1500" fill="#f5f2eb"/>']
    y=30
    for label,text in rows:
        svg.append(f'<text x="25" y="{y}" font-size="16">{label}</text>')
        for size in (40,24):
            buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties()
            if label.startswith('Digits'):buf.direction='ltr'
            hb.shape(hfont,buf)
            cursor=0;baseline=y+size*1.9
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
    parser.add_argument('--font',type=Path,default=ROOT/'output/font-review/tai-yo/DadTaiYo.ttf')
    parser.add_argument('--output',type=Path,default=ROOT/'output/font-review/tai-yo/compiled.png')
    args=parser.parse_args();preview(args.font,args.output)
