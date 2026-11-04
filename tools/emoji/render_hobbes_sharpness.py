"""Compare old/new compiled Hobbes glyphs at large and inline sizes."""
import sys
import argparse,json
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/font'))
from render_specimen import Font


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',default='output/font-review/hobbes-sharpness/before.woff2')
    parser.add_argument('--output',default='output/font-review/hobbes-sharpness/comparison')
    args=parser.parse_args()
    before=Font(args.before)
    after=Font('assets/fonts/dad-emoji.woff2')
    dad=Font('assets/fonts/dad-lettering-unicode.woff2')
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    parts=['<rect width="1200" height="980" fill="white"/>']
    def place(shape,x,y):parts.append(f'<g transform="translate({x} {y})">'+''.join(shape['paths'])+'</g>')
    for row,text in enumerate(['🐅','🐯']):
        for col,(label,font) in enumerate([('BEFORE',before),('AFTER',after)]):
            x=600*col;y=490*row
            place(dad.shape(label,18),x+24,y+32)
            big=font.shape(text,380)
            place(big,x+300-big['advance']/2,y+365)
            start=x+120
            for size in [20,28,40]:
                scale=manifest.get('customOptics',{}).get(text,{}).get('scale',1.4) if label=='AFTER' else 1.4
                letter=dad.shape('HI ',size);emoji=font.shape(text,size*scale)
                ratio=manifest.get('customOptics',{}).get(text,{}).get('strokeRatio',.018) if label=='AFTER' else (.006 if text=='🐅' else .018)
                if emoji['paths']:
                    emoji['paths'].append(emoji['paths'][-1].replace('<path ',f'<path stroke="#111" stroke-width="{ratio*font.upem}" stroke-linejoin="round" ',1))
                cap=dad.shape('H',size)['bounds'];b=emoji['bounds']
                offset=(cap[1]+cap[3]-b[1]-b[3])/2
                place(letter,start,y+445);place(emoji,start+letter['advance'],y+445+offset)
                start+=140
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="980">'+''.join(parts)+'</svg>'
    out=(ROOT/args.output).with_suffix('.svg');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(svg)
    with pymupdf.open(stream=svg.encode(),filetype='svg') as doc:doc[0].get_pixmap(alpha=False).save(out.with_suffix('.png'))
    print(out.with_suffix('.png'))


if __name__=='__main__':main()
