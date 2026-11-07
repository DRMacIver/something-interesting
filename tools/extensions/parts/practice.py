"""Practise drawing one kind of part (shoe, hand, sleeve, leg) against Watterson.

A part module defines `draw(pen, hw, **params)`, inking one part onto an
`ink.Ink` canvas at a head width of `hw` pixels. A fits file (JSON) maps
each reference's id to the params that reproduce it. `render` draws every
reference's fit on a canvas the size of the reference and lays the pairs
out side by side, Watterson on the left, for looking at and for critics.

A reference set (JSON) lists references: id, file (an image under
docs/dad-reference), head_width, view, note and split ('dev' or 'held').

    python practice.py render SET MODULE FITS OUT [--split dev|held|all]
    python practice.py sheet POOLKIND OUT        # contact sheet of the parts kit
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
REF = ROOT / 'docs' / 'dad-reference'
sys.path.insert(0, str(ROOT / 'tools' / 'extensions' / 'reconstruction-v2'))
import ink  # noqa: E402


def load(module_path):
    spec = importlib.util.spec_from_file_location(Path(module_path).stem + '_part', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def render_one(module, ref, params, seed=0):
    image = Image.open(REF / ref['file']).convert('L')
    pen = ink.Ink(image.size, seed=seed)
    module.draw(pen, ref['head_width'], **params)
    drawing = Image.fromarray(np.where(pen.mask(), 0, 255).astype(np.uint8))
    return image, drawing


def render(set_path, module_path, fits_path, out, split='dev', height=320):
    refs = [r for r in json.loads(Path(set_path).read_text())
            if split == 'all' or r['split'] == split]
    fits = json.loads(Path(fits_path).read_text()) if Path(fits_path).exists() else {}
    module = load(module_path)
    font = ImageFont.load_default(size=22)
    rows = []
    for ref in refs:
        params = fits.get(str(ref['id']))
        image = Image.open(REF / ref['file']).convert('L')
        if params is None:
            drawing = Image.new('L', image.size, 255)
            ImageDraw.Draw(drawing).text((5, 5), 'NO FIT', fill=0, font=font)
        else:
            try:
                image, drawing = render_one(module, ref, params)
            except Exception as e:  # show the failure in the sheet
                drawing = Image.new('L', image.size, 255)
                ImageDraw.Draw(drawing).text((5, 5), f'ERROR {e}'[:60], fill=0, font=font)
        k = height / image.height
        size = (max(1, round(image.width * k)), height)
        row = Image.new('L', (size[0] * 2 + 30, height + 34), 255)
        row.paste(image.resize(size), (0, 34))
        row.paste(drawing.resize(size), (size[0] + 30, 34))
        ImageDraw.Draw(row).text((4, 4), f"{ref['id']}  {ref['view']}  (left Watterson, right drawn)",
                                 fill=0, font=font)
        rows.append(row)
    if not rows:
        raise SystemExit('no references in that split')
    cols = 2 if len(rows) > 3 else 1
    w = max(r.width for r in rows) + 40
    h = max(r.height for r in rows) + 30
    sheet = Image.new('L', (cols * w, math.ceil(len(rows) / cols) * h), 255)
    for i, row in enumerate(rows):
        sheet.paste(row, ((i % cols) * w, (i // cols) * h))
    sheet.save(out)
    return out


def sheet(kinds, out, cell=220, cols=10):
    parts = json.loads((REF / 'parts.json').read_text())
    items = [(i, p) for i, p in enumerate(parts) if p['kind'] in kinds.split(',')]
    font = ImageFont.load_default(size=16)
    image = Image.new('L', (cols * cell, math.ceil(len(items) / cols) * (cell + 20)), 255)
    pen = ImageDraw.Draw(image)
    for k, (i, p) in enumerate(items):
        im = Image.open(REF / p['file']).convert('L')
        im.thumbnail((cell - 10, cell - 10))
        x, y = (k % cols) * cell, (k // cols) * (cell + 20)
        image.paste(im, (x + 5, y + 20))
        pen.text((x + 5, y), f"{i} {Path(p['source']).stem}", fill=0, font=font)
    image.save(out)


if __name__ == '__main__':
    if sys.argv[1] == 'render':
        split = sys.argv[sys.argv.index('--split') + 1] if '--split' in sys.argv else 'dev'
        render(*sys.argv[2:6], split=split)
    elif sys.argv[1] == 'sheet':
        sheet(sys.argv[2], sys.argv[3])
