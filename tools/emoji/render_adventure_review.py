"""Review compiled colour font outlines locally at large and dialogue sizes."""
import json
import sys
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/font'))
from render_specimen import Font


def main():
    font=Font('assets/fonts/dad-emoji.woff2')
    dad=Font('assets/fonts/dad-lettering-unicode.woff2')
    review=json.loads((ROOT/'assets/emoji-concepts/production-review.json').read_text())
    parts=['<rect width="1200" height="1040" fill="white"/>']
    def place(shape,x,y):
        parts.append(f'<g transform="translate({x} {y})">'+''.join(shape['paths'])+'</g>')
    for i,row in enumerate(review['drawings']):
        x=i%4*300;y=i//4*260
        place(dad.shape(row['codepoint'],12),x+20,y+28)
        big=font.shape(row['emoji'],160)
        place(big,x+150-big['advance']/2,y+178)
        left=dad.shape('HI ',20);right=dad.shape('!',20)
        scale=review['font'].get('customOptics',{}).get(row['emoji'],{}).get('scale',1.4)
        small=font.shape(row['emoji'],20*scale)
        cap=dad.shape('H',20)['bounds'];box=small['bounds']
        offset=(cap[1]+cap[3]-box[1]-box[3])/2
        start=x+150-(left['advance']+small['advance']+right['advance'])/2
        place(left,start,y+223)
        place(small,start+left['advance'],y+223+offset)
        place(right,start+left['advance']+small['advance'],y+223)
        parts.append(f'<path d="M{x+15} {y+246} H{x+285}" stroke="#ddd"/>')
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1040">'+''.join(parts)+'</svg>'
    out=ROOT/'assets/emoji-concepts/production-review.svg';out.write_text(svg)
    with pymupdf.open(stream=svg.encode(),filetype='svg') as doc:
        doc[0].get_pixmap(alpha=False).save(out.with_suffix('.png'))
    print(out.with_suffix('.png'))


if __name__=='__main__':main()
