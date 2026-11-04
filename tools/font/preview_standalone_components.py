"""Contact sheet of prepared component masks; font optical review is separate."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from emoji_standalone_components import ROOT, POINTS, prepare


if __name__ == '__main__':
    sheet = Image.new('RGB',(1000,1260),'#f5f2eb')
    draw = ImageDraw.Draw(sheet)
    for i,cp in enumerate(POINTS):
        (paper,*colours,ink), report = prepare(f'{cp:x}')
        rgb = np.full((*paper.shape,3),255,dtype=np.uint8)
        for mask,colour in zip(colours,report['rgbs']):
            rgb[mask] = colour
        rgb[ink] = 17
        im = Image.fromarray(rgb)
        large = im.resize((132,132),Image.Resampling.LANCZOS)
        small = im.resize((34,34),Image.Resampling.LANCZOS)
        x,y = (i%5)*200,(i//5)*180
        sheet.paste(large,(x,y))
        sheet.paste(small,(x+145,y+80))
        draw.text((x+5,y+140),f'U+{cp:X}',font=ImageFont.load_default(size=13),fill='black')
    path = ROOT/'output/font-review/pen-translation/standalone-components-prototype.png'
    sheet.save(path)
    print(path)
