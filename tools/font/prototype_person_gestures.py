"""Review source geometry and numbered skin regions; no production coverage."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
from emoji_licensed import raster
from emoji_sequences import source_ligature
from pen_translate import Settings,translate
from build_emoji import outline
ROOT=Path(__file__).resolve().parents[2]
BASES='🙍🙎🙅🙆💁🙋🧏🙇🤦🤷'

def main():
    spec=json.loads((ROOT/'data/font-sources/noto-emoji.json').read_text())['files'][0]
    source=ROOT/spec['path'];raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==spec['sha256']
    font=TTFont(source);shaping=hb.Font(hb.Face(raw));shaping.set_variations({'wght':400})
    out=ROOT/'output/font-review/pen-translation';records=[]
    for base in BASES:
        sheet=Image.new('RGB',(1050,420),'#f5f2eb');draw=ImageDraw.Draw(sheet)
        for j,suffix in enumerate(['','\u200d♂️','\u200d♀️']):
            text=base+suffix;name=source_ligature(font,shaping,text);key=text.replace('\ufe0f','')
            seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
            mask=raster(font.getGlyphSet(location={'wght':400}),name,pixels=384)
            image,r=translate(mask,Settings(strength=1.7,seed=seed));ink=np.asarray(image)<128
            white=ndimage.binary_fill_holes(ink);labels,n=ndimage.label(white&~ink)
            y,x=np.nonzero(white);factor=760/max(np.ptp(x)+1,np.ptp(y)+1)
            glyph=outline(ink,(x.min(),y.min(),factor))
            r.update(sequence=text,sourceGlyph=name,enclosedRegions=n,compiledContours=glyph.numberOfContours,source=spec['path'],sourceSha256=spec['sha256'])
            rgb=np.full((*ink.shape,3),255,dtype='uint8');rgb[ink]=17
            palette=[(238,180,150),(160,210,245),(195,230,150),(235,190,235),(255,220,100),(180,180,240)]
            for i in range(1,n+1):rgb[labels==i]=palette[(i-1)%len(palette)]
            tile=Image.fromarray(rgb);td=ImageDraw.Draw(tile)
            for i in range(1,n+1):
                yy,xx=ndimage.center_of_mass(labels==i);td.text((xx,yy),str(i),fill='black',font=ImageFont.load_default(size=18),anchor='mm')
            tile.thumbnail((330,330));sheet.paste(tile,(j*350,0))
            draw.text((j*350+5,335),' '.join(f'{ord(c):X}' for c in text),fill='black',font=ImageFont.load_default(size=14))
            draw.text((j*350+5,360),f'{r["appliedStrength"]:.3f}; {n} regions; {glyph.numberOfContours}/{r["sourceComponents"]+r["sourceHoles"]} contours',fill='black',font=ImageFont.load_default(size=14))
            records.append(r)
        sheet.save(out/f'person-gestures-{ord(base):x}.png')
    (out/'person-gestures-prototype.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
