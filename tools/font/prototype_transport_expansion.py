"""Review remaining transport drawings; does not modify production assets."""
import hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import pymupdf
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from emoji_licensed import raster
from pen_translate import Settings,translate
from build_emoji import outline
ROOT=Path(__file__).resolve().parents[2]
POINTS=[ord(c) for c in '🚀🚁🚉🚊🚋🚏🚒🚓🚖🚞🚟🚠🚡🛴🛵🛫🛬🛝🛞🛟🛢']


def main():
    spec=json.loads((ROOT/'data/font-sources/noto-emoji.json').read_text());entry=spec['files'][0]
    raw=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
    font=TTFont(ROOT/entry['path']);glyphs=font.getGlyphSet(location={'wght':400})
    names={int(line.split(';')[0],16):line.split(';')[1] for line in (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines()}
    sheet=Image.new('RGB',(1500,math.ceil(len(POINTS)/5)*250),'#f5f2eb');draw=ImageDraw.Draw(sheet);records=[]
    for i,cp in enumerate(POINTS):
        weight=350 if cp==0x1F696 else 400
        selected=font.getGlyphSet(location={'wght':weight}) if weight!=400 else glyphs
        for pixels in [384,512,768]:
            mask=raster(selected,font.getBestCmap()[cp],pixels)
            image,r=translate(mask,Settings(strength=1.7,seed=cp));ink=np.asarray(image)<128;white=ndimage.binary_fill_holes(ink)
            ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1)
            g=outline(ink,(xs.min(),ys.min(),factor));advance=round((np.ptp(xs)+1)*factor)+100
            if r['appliedStrength']>0 and not r['fallback'] and g.numberOfContours>=r['sourceComponents']+r['sourceHoles']:break
        pen=SVGPathPen(None);g.draw(pen,None)
        r.update(codepoint=f'U+{cp:04X}',unicodeName=names[cp],sourcePixels=pixels,sourceWeight=weight,compiledContours=g.numberOfContours,sourceSha256=entry['sha256'],status='Prototype only')
        records.append(r)
        for size,dx,dy,optical in [(160,5,0,False),(33.6,240,70,True)]:
            stroke=' stroke="#111111" stroke-width="18" stroke-linejoin="round"' if optical else ''
            svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{advance}" height="1000"><rect width="100%" height="100%" fill="white"/><path transform="translate(0 850) scale(1 -1)" fill="#111111" d="{pen.getCommands()}"{stroke}/></svg>'
            doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000))
            sheet.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(i%5*300+dx,i//5*250+dy))
        for j,text in enumerate([f'U+{cp:04X} {names[cp]}',f'{pixels}px; applied {r["appliedStrength"]:.3f}',f'Contours {g.numberOfContours}/{r["sourceComponents"]+r["sourceHoles"]}']):draw.text((i%5*300+5,i//5*250+165+j*23),text,fill='black',font=ImageFont.load_default(size=11 if j==0 else 14))
    out=ROOT/'output/font-review/pen-translation/transport-expansion-prototype'
    sheet.save(out.with_suffix('.png'));out.with_suffix('.json').write_text(json.dumps(records,indent=2)+'\n');print(out)


if __name__=='__main__':main()
