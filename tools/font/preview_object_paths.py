"""Inspect visible native SVG paths without losing their original indices.

Keep definition geometry during isolation: a clipped stripe needs its donor
clip path even when all other painted shapes are hidden. The JSON separates
definition indices from individually rendered shapes.
"""
import argparse
import copy
import hashlib
import io
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
SHAPES={'path','polygon','circle','ellipse','rect','polyline','line'}


def shapes(root):
    return [e for e in root.iter() if e.tag.split('}')[-1] in SHAPES]


def render(root):
    png=subprocess.run(['rsvg-convert','-w','100','-h','100'],input=ET.tostring(root),
                       stdout=subprocess.PIPE,check=True).stdout
    return Image.open(io.BytesIO(png)).convert('RGBA')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keys',nargs='+')
    parser.add_argument('--out',type=Path,default=ROOT/'output/font-review/pen-translation')
    args=parser.parse_args()
    files=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
    sources={Path(e['path']).stem.removeprefix('emoji_u'):e for e in files}
    args.out.mkdir(parents=True,exist_ok=True)
    for key in args.keys:
        source=sources[key]
        raw=(ROOT/source['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==source['sha256']
        root=ET.fromstring(raw)
        native=shapes(root)
        ancestry={child:parent for parent in root.iter() for child in parent}
        definitions=[]
        for index,element in enumerate(native):
            parent=element
            while parent in ancestry:
                parent=ancestry[parent]
                if parent.tag.split('}')[-1] in {'defs','clipPath','mask','pattern'}:
                    definitions.append(index);break
        tiles=[('complete',render(root))]
        visible=[]
        for index in range(len(native)):
            isolated=copy.deepcopy(root)
            parents={child:parent for parent in isolated.iter() for child in parent}
            for i,element in enumerate(shapes(isolated)):
                if i!=index and i not in definitions:parents[element].remove(element)
            image=render(isolated)
            if image.getchannel('A').getbbox() is not None:
                visible.append(index)
                tiles.append((str(index),image))
        sheet=Image.new('RGB',(600,125*((len(tiles)+4)//5)),'#eee')
        draw=ImageDraw.Draw(sheet)
        for i,(label,image) in enumerate(tiles):
            x=i%5*120;y=i//5*125
            sheet.paste(image,(x,y),image)
            draw.text((x+4,y+104),label,fill='black',font=ImageFont.load_default(size=12))
        prefix=args.out/f'native-paths-{key}'
        sheet.save(prefix.with_suffix('.png'))
        prefix.with_suffix('.json').write_text(json.dumps(dict(source=source,
            sourceShapeCount=len(native),definitionIndices=definitions,visibleIndices=visible),indent=2)+'\n')
        print(key,len(native),'native shapes; visible indices:',visible,flush=True)


if __name__=='__main__':main()
