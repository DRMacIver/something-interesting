"""Find large scan components for visual review; never assigns Seal identities.

A box can contain only part of a glyph or adjacent commentary. Review the full
source before recording a final crop. Missing boxes do not establish absence.
"""
import argparse,hashlib,io,json
from pathlib import Path
import numpy as np
import pymupdf
from PIL import Image,ImageDraw,ImageFont,ImageOps
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('pages',type=int,nargs='+')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--holes',type=int)
    parser.add_argument('--invert',action='store_true')
    args=parser.parse_args()
    path=args.source.resolve();relative=path.relative_to(ROOT).as_posix()
    spec=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())
    source=next(e for e in spec['files'] if e['path']==relative)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256']
    assert len(args.pages)==len(set(args.pages)) and all(p>0 for p in args.pages)
    entries=[];tiles=[];pages=[]
    with pymupdf.open(path) as doc:
        for page in args.pages:
            assert page<=len(doc)
            native=doc[page-1]
            xref=max(native.get_images(),key=lambda item:item[2]*item[3])[0]
            image=Image.open(io.BytesIO(doc.extract_image(xref)['image'])).convert('L')
            if args.invert:image=ImageOps.invert(image)
            pages.append(dict(page=page,xref=xref,size=list(image.size),invert=args.invert,pixelSha256=hashlib.sha256(image.tobytes()).hexdigest()))
            ink=np.asarray(image)<160;labels,_=ndi.label(ink,np.ones((3,3)))
            for index,box in enumerate(ndi.find_objects(labels),1):
                if box is None:continue
                sy,sx=box;height=sy.stop-sy.start;width=sx.stop-sx.start
                if not (48<=height<=86 and 12<=width<=100):continue
                part=labels[box]==index
                holes=ndi.label(ndi.binary_fill_holes(part)&~part)[1]
                if args.holes is not None and holes!=args.holes:continue
                crop=(max(0,sx.start-28),max(0,sy.start-8),min(image.width,sx.stop+28),min(image.height,sy.stop+8))
                entries.append(dict(page=page,componentBounds=[sx.start,sy.start,sx.stop,sy.stop],contextBounds=list(crop),holes=holes))
                tile=image.crop(crop);tile=tile.resize((tile.width*2,tile.height*2));tile.thumbnail((180,155));tiles.append(tile)
    sheet=Image.new('RGB',(1000,max(1,(len(tiles)+4)//5)*200),'#eee');draw=ImageDraw.Draw(sheet)
    for index,(entry,tile) in enumerate(zip(entries,tiles)):
        x=index%5*200;y=index//5*200
        draw.text((x,y),f"p{entry['page']} {entry['contextBounds'][:2]} h{entry['holes']}",fill='black',font=ImageFont.load_default(size=12))
        sheet.paste(tile,(x,y+30))
    args.output.parent.mkdir(parents=True,exist_ok=True);sheet.save(args.output)
    args.output.with_suffix('.json').write_text(json.dumps(dict(candidateOnly=True,source=source,pages=pages,threshold=160,foregroundConnectivity=8,holesFilter=args.holes,candidates=entries),ensure_ascii=False,indent=2)+'\n')
    print(len(entries),'inspection candidates; no identities assigned')


if __name__=='__main__':main()
