"""Review individual painted paths before writing an SVG ink-conversion recipe."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
SHAPES = {'path','circle','ellipse','rect','polygon','polyline','line'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='docs/noto-svg-source-probe.json')
    parser.add_argument('--codepoints', nargs='*', help='Optional lowercase SVG filename keys')
    args = parser.parse_args()
    spec = json.loads((ROOT/args.manifest).read_text())
    for entry in spec['files']:
        path = ROOT/entry['path']
        if path.suffix != '.svg': continue
        if args.codepoints and path.stem.removeprefix('emoji_u') not in args.codepoints: continue
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry['sha256']
        root = ET.fromstring(raw)
        shapes = [x for x in root.iter() if x.tag.split('}')[-1] in SHAPES]
        sheet = Image.new('RGB',(1280,160*math.ceil(len(shapes)/8)),'#f5f2eb')
        draw = ImageDraw.Draw(sheet)
        for i, original in enumerate(shapes):
            single = copy.deepcopy(root)
            painted = [x for x in single.iter() if x.tag.split('}')[-1] in SHAPES]
            parents = {child:parent for parent in single.iter() for child in parent}
            for j, element in enumerate(painted):
                if i != j: parents[element].remove(element)
                else:
                    element.set('fill','#111111')
                    if element.get('stroke') not in (None,'none'): element.set('stroke','#111111')
            single.set('width','128'); single.set('height','128')
            doc = pymupdf.open(stream=ET.tostring(single),filetype='svg')
            pdf = pymupdf.open('pdf',doc.convert_to_pdf()); pix = pdf[0].get_pixmap(alpha=False)
            image = Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            x,y=i%8*160,i//8*160;sheet.paste(image,(x,y))
            draw.text((x+3,y+130),f'{i}: {original.tag.split("}")[-1]}',fill='black',font=ImageFont.load_default(size=12))
            draw.text((x+3,y+144),original.get('fill',original.get('style','inherited'))[:23],fill='black',font=ImageFont.load_default(size=10))
        output = ROOT/'output/font-review/pen-translation'/f'{path.stem}-path-probe.png'
        sheet.save(output);print(output)


if __name__ == '__main__':main()
