"""Review the pinned native sources for the last non-flag emoji batch."""
import collections,hashlib,io,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]


def main():
    entries=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
    assert len(entries)==113
    reports=[];out=ROOT/'output/font-review/pen-translation'
    for start in range(0,len(entries),30):
        batch=entries[start:start+30];sheet=Image.new('RGB',(1000,150*((len(batch)+5)//6)),'#f5f2eb');draw=ImageDraw.Draw(sheet)
        for i,entry in enumerate(batch):
            path=ROOT/entry['path'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
            png=subprocess.run(['rsvg-convert','-w','120','-h','120',str(path)],stdout=subprocess.PIPE,check=True).stdout
            im=Image.open(io.BytesIO(png)).convert('RGBA');paper=Image.new('RGBA',im.size,'white');paper.alpha_composite(im)
            x=i%6*166;y=i//6*150;sheet.paste(paper.convert('RGB'),(x+22,y+2))
            key=path.stem.removeprefix('emoji_u');draw.text((x+5,y+123),key,fill='black',font=ImageFont.load_default(size=12));draw.text((x+5,y+137),entry['subgroup'],fill='black',font=ImageFont.load_default(size=10))
            root=ET.fromstring(raw);shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
            reports.append(dict(key=key,sequence=entry['sequence'],subgroup=entry['subgroup'],source=entry,viewBox=root.get('viewBox'),elements=dict(collections.Counter(e.tag.split('}')[-1] for e in root.iter())),shapes=[dict(index=i,tag=e.tag.split('}')[-1],attributes=dict(e.attrib)) for i,e in enumerate(shapes)]))
        sheet.save(out/f'remaining-objects-native-{start//30+1}.png')
    (out/'remaining-objects-source-structure.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    print('113 sources verified and rendered in four sheets')


if __name__=='__main__':main()
