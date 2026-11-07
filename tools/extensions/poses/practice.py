"""Helpers for drawing Dad into a practice task (see tasks.py).

A drawer's script does:

    import sys; sys.path[:0] = [TOOLS + '/reconstruction-v2', TOOLS + '/poses']
    import practice, ink
    task = practice.Task(TASKS_DIR, 'walking')
    pen = ink.Ink(task.size, seed=1)
    ... draw with pen.fill / pen.stroke / pen.paint, task.kit(kind), task.part(...) ...
    task.save(pen.mask(), OUT_DIR)

`save` puts the drawing's ink inside the task's erased region (outside it,
Watterson's panel stays) and writes OUT_DIR/drawing.png plus
OUT_DIR/sheet.png: the drawing beside the guide, for looking at.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
REF = ROOT / 'docs' / 'dad-reference'


class Task:
    def __init__(self, tasks_dir, name):
        self.dir = Path(tasks_dir) / name
        self.name = name
        info = json.loads((Path(tasks_dir) / 'tasks.json').read_text())[name]
        self.__dict__.update(info)
        self.size = tuple(self.size)
        self.erased = Image.open(self.dir / 'erased.png').convert('L')
        self.region = np.asarray(Image.open(self.dir / 'region.png')) > 0

    def kit(self, kind):
        """Parts-kit cut-outs of one kind, excluding this task's own drawing."""
        return [p for p in json.loads((REF / 'parts.json').read_text())
                if p['kind'] == kind and self.crop not in p['source']]

    def part(self, entry, at, angle=0.0, flip=False, scale=1.0):
        """A parts-kit cut-out as an ink mask on this task's canvas.

        It is scaled to this task's head width (times `scale`), mirrored if
        `flip`, turned `angle` degrees anticlockwise about its centre, and
        centred at `at`.
        """
        im = Image.open(REF / entry['file']).convert('L')
        im = ImageOps.invert(im)
        if flip:
            im = ImageOps.mirror(im)
        k = scale * self.head_width / entry['head_width']
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))),
                       Image.Resampling.LANCZOS)
        im = im.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        canvas = Image.new('L', self.size, 0)
        canvas.paste(im, (round(at[0] - im.width / 2), round(at[1] - im.height / 2)))
        return np.asarray(canvas) > 128

    def compose(self, ink_mask, white=None):
        """The finished panel: Watterson outside the region, the drawing inside.

        `white` (optional boolean mask) is paper painted over Watterson's ink
        outside the region, e.g. to hide what an overlapping limb covers.
        """
        a = np.asarray(self.erased).copy()
        if white is not None:
            a[white] = 255
        a[self.region] = 255
        a[ink_mask] = 0
        return Image.fromarray(a)

    def save(self, ink_mask, out_dir, white=None):
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        drawing = self.compose(ink_mask, white)
        drawing.save(out / 'drawing.png')
        guide = Image.open(self.dir / 'guide.png').convert('RGB')
        sheet = Image.new('RGB', (guide.width * 2 + 20, guide.height), 'white')
        sheet.paste(drawing.convert('RGB'), (0, 0))
        sheet.paste(guide, (guide.width + 20, 0))
        sheet.save(out / 'sheet.png')
        return drawing


def comparison(tasks_dir, name, drawings, out):
    """Watterson's drawing beside one or more attempts, labelled, for a critic."""
    from PIL import ImageDraw, ImageFont
    key = Image.open(Path(tasks_dir) / 'keys' / f'{name}.png').convert('L')
    panels = [('WATTERSON', key)] + [(label, Image.open(p).convert('L')) for label, p in drawings]
    h = 900
    panels = [(l, im.resize((round(im.width * h / im.height), h))) for l, im in panels]
    font = ImageFont.load_default(size=40)
    sheet = Image.new('L', (sum(im.width + 30 for _, im in panels), h + 60), 255)
    x = 0
    pen = ImageDraw.Draw(sheet)
    for label, im in panels:
        pen.text((x + 10, 5), label, fill=0, font=font)
        sheet.paste(im, (x, 60))
        x += im.width + 30
    sheet.save(out)
