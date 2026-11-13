"""A ranked contact sheet of grafted candidates.

    uv run tools/extensions/graft/sheet.py GRAFT_DIR OUT.png [--columns N] [--only a,b,c]

Candidates are ordered by how well they fitted the scan (see `score`),
best first, and labelled with their numbers.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def score(report):
    """Lower is better: the chamfer fit inside the crop (scan px), plus a
    charge for ink cut off along the crop's edge and for every line that
    stops or starts there."""
    return report['fit_warped'] + report['seam'] / 300 \
        + 0.03 * (report['edges_lost'] + report['edges_extra']) + (1.0 if report['clipped'] else 0.0)


def trimmed(image, pad=60):
    ys, xs = np.nonzero(np.asarray(image.convert('L')) < 128)
    return image.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0),
                       min(xs.max() + pad, image.width), min(ys.max() + pad, image.height)))


def font(size):
    for name in ('/System/Library/Fonts/Helvetica.ttc', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory', type=Path)
    ap.add_argument('out', type=Path)
    ap.add_argument('--columns', type=int, default=3)
    ap.add_argument('--only', default='')
    ap.add_argument('--tile', type=int, default=900)
    ap.add_argument('--reject', type=float, default=5.0, help='leave out candidates fitting worse than this')
    ap.add_argument('--aspect', type=float, default=0.7, help='tile height / width')
    args = ap.parse_args()

    reports = {p.stem: json.loads(p.read_text()) for p in args.directory.glob('*.json')}
    names = sorted(reports, key=lambda n: score(reports[n]))
    if args.only:
        names = [n for n in names if n in args.only.split(',')]
    for name in [n for n in names if reports[n]['fit_warped'] > args.reject]:
        print(f"left out {name}: fit {reports[name]['fit_warped']:.1f}px, not a drawing of this scene")
        names.remove(name)
    tiles = []
    high = round(args.tile * args.aspect)
    for rank, name in enumerate(names, 1):
        r = reports[name]
        art = trimmed(Image.open(args.directory / f'{name}.png').convert('RGB'))
        art.thumbnail((args.tile, high))
        tile = Image.new('RGB', (args.tile, high + 70), 'white')
        tile.paste(art, ((args.tile - art.width) // 2, 70 + (high - art.height) // 2))
        draw = ImageDraw.Draw(tile)
        draw.text((12, 8), f'{rank}. {name}', fill=(180, 0, 0), font=font(30))
        draw.text((12, 42), f"fit {r['fit_warped']:.2f}px   cut along crop {r['seam']}px   "
                  f"loose line ends {r['edges_lost'] + r['edges_extra']}   enlarged {r['scale']:.2f}x"
                  + ('   CLIPPED' if r['clipped'] else ''),
                  fill=(90, 90, 90), font=font(20))
        tiles.append(tile)
    rows = -(-len(tiles) // args.columns)
    gap = 16
    sheet = Image.new('RGB', (args.columns * (args.tile + gap) + gap, rows * (high + 70 + gap) + gap), (225, 225, 225))
    for i, tile in enumerate(tiles):
        sheet.paste(tile, (gap + (i % args.columns) * (args.tile + gap), gap + (i // args.columns) * (high + 70 + gap)))
    sheet.save(args.out)
    for rank, name in enumerate(names, 1):
        print(rank, name, f'{score(reports[name]):.2f}')


if __name__ == '__main__':
    main()
