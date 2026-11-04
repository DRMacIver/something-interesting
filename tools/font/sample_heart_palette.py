"""Reproduce the heart palette from visually selected full-resolution PDF patches.

Requires Poppler pdftoppm. Reads recorded page/box selections; --check verifies
rather than rewriting the accepted RGB samples. Does not edit the source PDF.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
RECORD=ROOT/'output/imagegen/emoji-production/heart-palette-source.json'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true');args=parser.parse_args()
    record=json.loads(RECORD.read_text());pdf=ROOT/record['pdf']
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=record['pdfSha256']:
        raise ValueError('Source PDF changed; review palette selections')
    folder=ROOT/'tmp/pdfs/heart-palette';folder.mkdir(parents=True,exist_ok=True)
    images={}
    for page in sorted({s['page'] for s in record['samples']}):
        stem=folder/f'page{page}'
        subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','4644','-png','-singlefile',str(pdf),str(stem)],check=True)
        path=stem.with_suffix('.png');images[page]=(Image.open(path).convert('RGB'),hashlib.sha256(path.read_bytes()).hexdigest())
    for sample in record['samples']:
        im,digest=images[sample['page']]
        a=np.asarray(im.crop(sample['box'])).reshape(-1,3).astype(int)
        chromatic=sample['colour'] in ('red','yellow')
        keep=(a.max(axis=1)>65)&(a.max(axis=1)<(256 if chromatic else 230))
        if chromatic: keep &= a.max(axis=1)-a.min(axis=1)>40
        a=a[keep]
        if not len(a): raise ValueError(f'Empty sample: {sample["colour"]}')
        rgb=np.median(a,axis=0).astype(int).tolist()
        if args.check:
            if rgb!=sample['rgb']: raise ValueError(f'Palette changed: {sample["colour"]}: {rgb}')
        else: sample.update(rgb=rgb,acceptedPixels=len(a),renderSha256=digest)
    if not args.check: RECORD.write_text(json.dumps(record,indent=2)+'\n')
    print(f'{len(record["samples"])} full-resolution colour samples verified')


if __name__=='__main__': main()
