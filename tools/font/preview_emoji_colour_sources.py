"""Review pinned original SVG colours with librsvg (requires rsvg-convert).

This is a review tool, not a production font builder. Unlike the ink conversion,
it retains source gradients and opacity so anatomical paint can be inspected.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifests', nargs='+', type=Path, required=True)
    parser.add_argument('--prefix', required=True)
    args = parser.parse_args()
    renderer = shutil.which('rsvg-convert')
    if not renderer:
        raise SystemExit('Install librsvg to provide rsvg-convert for colour-source review.')
    entries = [entry for manifest in args.manifests
               for entry in json.loads(manifest.read_text())['files']]
    out = ROOT / 'output/font-review/pen-translation'
    out.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(size=12)
    with tempfile.TemporaryDirectory(prefix='emoji-source-review-') as temporary:
        for start in range(0, len(entries), 12):
            batch = entries[start:start+12]
            sheet = Image.new('RGB', (1040, ((len(batch)+3)//4)*300), 'white')
            draw = ImageDraw.Draw(sheet)
            for i, entry in enumerate(batch):
                path = ROOT / entry['path']
                raw = path.read_bytes()
                assert hashlib.sha256(raw).hexdigest() == entry['sha256'], path
                assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == entry['git_blob_sha1'], path
                png = Path(temporary) / f'{i}.png'
                subprocess.run([renderer, '-w', '240', '-h', '240', '-o', str(png), str(path)], check=True)
                tile = Image.open(png).convert('RGBA')
                x, y = (i % 4)*260, (i // 4)*300
                sheet.paste(tile, (x+10, y), tile)
                label = path.stem.removeprefix('emoji_u')
                draw.text((x+5, y+245), '\n'.join(textwrap.wrap(label, 32)), fill='black', font=font)
            destination = out / f'{args.prefix}-{start//12+1}.png'
            sheet.save(destination)
            print(destination)


if __name__ == '__main__':
    main()
