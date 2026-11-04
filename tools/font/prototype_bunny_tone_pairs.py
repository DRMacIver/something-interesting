"""Review independent skin colours on the paired bunny-ear drawings."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from emoji_activity_svg import ROOT,prepare
from emoji_paired_skin import split_paired_skin


def main():
    palette=json.loads((ROOT/'output/imagegen/emoji-production/skin-palette-source.json').read_text())['skinTones']
    sheet=Image.new('RGB',(1050,760),'#f5f2eb');draw=ImageDraw.Draw(sheet);records=[]
    for column,key in enumerate(['1f46f','1f46f_200d_2642','1f46f_200d_2640']):
        (white,skin,ink),source=prepare(key)
        left,right,report=split_paired_skin(skin,ink)
        for row,(a,b) in enumerate([(0,4),(4,0)]):
            rgb=np.full((*ink.shape,3),255,dtype='uint8')
            rgb[left]=palette[a];rgb[right]=palette[b];rgb[ink]=17
            tile=Image.fromarray(rgb);tile.thumbnail((330,330));sheet.paste(tile,(column*350,row*380))
            draw.text((column*350+4,row*380+335),f'{key}: {a+1} / {b+1}',fill='black',font=ImageFont.load_default(size=15))
        records.append(dict(key=key,split=report,source=source,
                            splitProgramSha256=hashlib.sha256((ROOT/'tools/font/emoji_paired_skin.py').read_bytes()).hexdigest()))
    out=ROOT/'output/font-review/pen-translation'
    sheet.save(out/'bunny-tone-pairs-prototype.png')
    (out/'bunny-tone-pairs-prototype.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
    print('3 paired masks partition exactly; six visual colour-order examples')


if __name__=='__main__':main()
