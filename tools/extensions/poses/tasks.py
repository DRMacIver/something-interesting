"""Practice tasks for drawing Dad: Watterson's own drawings with the body erased.

Each task takes a reference drawing from docs/dad-reference, erases Dad's
body below the head (the bones from the annotations, thickened, and the
marked part boxes) and keeps everything else. A drawer gets the erased
panel, the region to fill and a skeleton; Watterson's drawing is the answer
key a critic compares against.

    uv run --no-project --with pillow,numpy,scipy python tools/extensions/poses/tasks.py OUT
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[3]
REF = ROOT / 'docs' / 'dad-reference'

TASKS = {
    'standing': ('p245-13', 'Standing upright, facing left, hands in his trouser pockets, '
                            'elbows out; long straight legs, feet together.'),
    'walking': ('p186-07', 'Walking to the right in profile, torso upright, near arm '
                           'hanging with the hand curled; front foot lifted heel-first, '
                           'back foot trailing flat.'),
    'armchair': ('p054-01', 'Sitting in an armchair facing left, leaning forward slightly, '
                            'near arm reaching down to the chair arm; knees up, feet flat '
                            'on the floor.'),
    'crouching': ('p108-05', 'Crouching facing right, leaning forward, one elbow on his '
                             'knee and that hand held up at his chin; other arm hanging '
                             'forward; feet flat, knees high.'),
    'kneeling': ('p008-01', 'Kneeling bent far forward facing left, head low, back arched; '
                            'seat on his heels, soles of both shoes turned up towards us. '
                            'He wears light trousers here, not black.'),
    'floor': ('p110-11', 'Sitting on the floor facing left, leaning slightly forward, '
                         'legs crossed with knees out to the right, arms forward '
                         'holding something in his lap.'),
}

BONES = [('shoulder', 'elbow'), ('elbow', 'wrist'), ('wrist', 'fingertips'),
         ('shoulder', 'hip'), ('hip', 'knee'), ('knee', 'ankle'), ('ankle', 'toe')]
BONES += [('far_' + a if a != 'hip' and a != 'shoulder' else a, 'far_' + b) for a, b in BONES
          if a != 'shoulder' or b != 'hip']


def joints(note):
    return {k: tuple(v) for k, v in note['joints'].items() if len(v) == 2}


def body_region(note, size):
    """Where Dad's body is: thick bones and part boxes, without his head."""
    hw = math.dist(note['head_back'], note['head_front'])
    region = Image.new('L', size, 0)
    pen = ImageDraw.Draw(region)
    j = joints(note)
    for a, b in BONES:
        if a in j and b in j:
            pen.line(j[a] + j[b], fill=255, width=int(0.75 * hw))
            for p in (j[a], j[b]):
                r = 0.375 * hw
                pen.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=255)
    for part in note['parts']:
        pen.rectangle(part['box'], fill=255)
    mask = np.asarray(region) > 0
    # The torso between shoulders, hips and the sleeve: fill its hull.
    mask = ndimage.binary_closing(mask, iterations=int(0.2 * hw))
    mask = ndimage.binary_fill_holes(mask)
    mask = ndimage.binary_dilation(mask, iterations=int(0.06 * hw))
    # Keep the head: a disc around it, reaching down to the chin.
    (bx, by), (fx, fy) = note['head_back'], note['head_front']
    cx, cy = (bx + fx) / 2, (by + fy) / 2
    yy, xx = np.mgrid[:size[1], :size[0]]
    head = ((xx - cx) / (0.62 * hw)) ** 2 + ((yy - cy - 0.1 * hw) / (0.75 * hw)) ** 2 < 1
    return mask & ~head, hw


def build(out):
    notes = {a['name']: a for a in json.loads((REF / 'annotations.json').read_text())}
    out.mkdir(parents=True, exist_ok=True)
    keys = out / 'keys'
    keys.mkdir(exist_ok=True)
    manifest = {}
    for name, (crop, description) in TASKS.items():
        note = notes[crop + '.png']
        key = Image.open(REF / 'crops' / f'{crop}.png').convert('L')
        mask, hw = body_region(note, key.size)
        erased = np.asarray(key).copy()
        erased[mask] = 255
        task = out / name
        task.mkdir(exist_ok=True)
        Image.fromarray(erased).save(task / 'erased.png')
        Image.fromarray((mask * 255).astype(np.uint8)).save(task / 'region.png')
        key.save(keys / f'{name}.png')
        # A guide: erased panel, region tinted, skeleton in colour.
        guide = Image.fromarray(erased).convert('RGB')
        tint = Image.new('RGB', key.size, (255, 225, 190))
        guide = Image.composite(Image.blend(guide, tint, 0.5), guide,
                                Image.fromarray((mask * 255).astype(np.uint8)))
        pen = ImageDraw.Draw(guide)
        j = joints(note)
        for a, b in BONES:
            if a in j and b in j:
                colour = (40, 90, 220) if ('knee' in a + b or 'ankle' in a + b or 'toe' in b) \
                    else (220, 40, 40)
                if a.startswith('far') or b.startswith('far'):
                    colour = tuple(c // 2 + 100 for c in colour)
                pen.line(j[a] + j[b], fill=colour, width=max(3, int(hw / 30)))
        guide.save(task / 'guide.png')
        manifest[name] = dict(crop=crop, description=description, head_width=round(hw, 1),
                              facing=note['facing'], size=key.size, joints=j,
                              parts=[{k: p[k] for k in ('kind', 'box', 'near', 'note')}
                                     for p in note['parts']])
    (out / 'tasks.json').write_text(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    build(Path(sys.argv[1]))
