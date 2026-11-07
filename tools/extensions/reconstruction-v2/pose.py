"""Pose skeletons for Dad in the completed panels, measured from Watterson.

Every length is in Dad's head widths (the widest ink across his head at the
eyes, back of the head to the glasses), measured on Watterson's own
full-length drawing of him in panel 1, where his head is about 290px wide.
In the close-ups his head is 493px (panel 2) and 562px (panel 3) wide.

The joints of each pose are anchored to what the scan shows and placed
from these lengths; `check` reports how each bone compares with panel 1,
allowing for foreshortening where a limb points towards or away from us.
`overlay` draws a pose over its panel for review before anything is inked.
"""
import math

from PIL import Image, ImageDraw, ImageFont

HEAD = {1: 290, 2: 493, 3: 562}

# Panel 1, Dad walking (full-panel export coordinates), joint by joint.
PANEL1 = {
    'shoulder': (560, 470), 'elbow': (725, 905), 'wrist': (765, 1150),
    'fingertips': (770, 1230), 'hip': (500, 1050),
    'knee': (480, 1470), 'ankle': (400, 1850), 'toe': (580, 1960),
    'far knee': (720, 1480), 'far ankle': (900, 1820), 'far toe': (1060, 1680),
}

BONES = [('shoulder', 'elbow'), ('elbow', 'wrist'), ('wrist', 'fingertips'),
         ('shoulder', 'hip'), ('hip', 'knee'), ('knee', 'ankle'), ('ankle', 'toe'),
         ('hip', 'far knee'), ('far knee', 'far ankle'), ('far ankle', 'far toe')]


def length(pose, a, b):
    (x0, y0), (x1, y1) = pose[a], pose[b]
    return math.hypot(x1 - x0, y1 - y0)


# Bone lengths in head widths, from panel 1.
PROPORTIONS = {bone: length(PANEL1, *bone) / HEAD[1] for bone in BONES}

# What each limb of the close-ups does, and how much its drawn length may
# shrink because it points towards or away from us (1 = flat on the page).
POSES = {
    2: dict(
        description='Sitting back on his heels, leaning far forward to the '
                    'record player. With panel 1\'s lengths, the thigh lying '
                    'on the shin makes the knee about 0.9 head widths tall, '
                    'which is where the top of his knee is in the scan (it '
                    'turns down at the crop\'s foot, x=1051). A full-length '
                    'torso then puts his seat well behind, over his heels, '
                    'with his feet lying behind it, soles up. The earlier '
                    'extension of his back is too short and will be redrawn.',
        # Shoulder lowered into the sleeve cap after critique, the rest moved
        # with it. The elbow and wrist are where the scan shows them.
        joints={'shoulder': (784, 1280), 'elbow': (850, 1885), 'wrist': (1180, 1890),
                'hip': (314, 2150), 'knee': (1025, 2250), 'ankle': (357, 2309),
                'toe': (16, 2370)},
        floor=2382,
        flat={('shoulder', 'elbow'): 1.0, ('elbow', 'wrist'): 1.0, ('shoulder', 'hip'): 1.0,
              ('hip', 'knee'): 1.0, ('knee', 'ankle'): 1.0, ('ankle', 'toe'): 1.0},
    ),
    3: dict(
        description='Kneeling, turned three-quarters towards us, gesturing '
                    'with his far hand and resting the near one on his near '
                    'knee. His near upper arm hangs to an elbow just above his '
                    'waist; the forearm reaches forward and down to the knee. '
                    'He is nearer us than Calvin, so his knees meet the floor '
                    'lower in the panel than Calvin\'s feet do.',
        # Elbow, wrist and fingertips as revised after critique: a shorter
        # forearm, the hand resting on top of the knee, not at its joint.
        joints={'shoulder': (860, 1890), 'elbow': (816, 2707), 'wrist': (1134, 2968),
                'fingertips': (1270, 3104), 'hip': (640, 2860), 'knee': (1250, 3200),
                'ankle': (660, 3230), 'toe': (430, 3268)},
        floor=3320,
        flat={('shoulder', 'elbow'): 0.92, ('elbow', 'wrist'): 1.0, ('shoulder', 'hip'): 0.9,
              ('wrist', 'fingertips'): 0.8, ('hip', 'knee'): 0.85,
              ('knee', 'ankle'): 0.75, ('ankle', 'toe'): 0.5},
    ),
}


def check(panel):
    """Each bone's drawn length against panel 1's, foreshortening allowed."""
    pose = POSES[panel]
    rows = []
    for bone, flat in pose['flat'].items():
        drawn = length(pose['joints'], *bone) / HEAD[panel]
        expected = PROPORTIONS[bone]
        rows.append((bone, round(drawn, 2), round(expected * flat, 2), round(expected, 2),
                     round(drawn / (expected * flat), 2)))
    return rows


COLOURS = {'arm': (220, 40, 40), 'leg': (30, 90, 220), 'foot': (20, 150, 60),
           'torso': (150, 60, 190)}


def kind(bone):
    names = ' '.join(bone)
    if 'toe' in names:
        return 'foot'
    if 'knee' in names or 'ankle' in names:
        return 'leg'
    if 'shoulder' in names and 'hip' in names:
        return 'torso'
    return 'arm'


def overlay(panel_image, joints, head, scan_box=None, floor=None, title=''):
    """The panel faded, with the skeleton drawn over it in colour."""
    base = panel_image.convert('L').point(lambda v: 150 + v * 105 // 255).convert('RGB')
    pen = ImageDraw.Draw(base)
    width = max(8, head // 28)
    if scan_box:
        pen.rectangle(scan_box, outline=(255, 140, 0), width=width // 2)
    if floor:
        pen.line((0, floor, base.width, floor), fill=(120, 120, 120), width=width // 3)
    for bone in BONES:
        if all(j in joints for j in bone):
            pen.line(joints[bone[0]] + joints[bone[1]], fill=COLOURS[kind(bone)], width=width)
    font = ImageFont.load_default(size=head // 7)
    for name, (x, y) in joints.items():
        r = width * 1.4
        pen.ellipse((x - r, y - r, x + r, y + r), fill=(0, 0, 0))
        pen.text((x + r * 1.5, y - r), name, fill=(0, 0, 0), font=font)
    if title:
        pen.text((20, 20), title, fill=(0, 0, 0), font=ImageFont.load_default(size=head // 5))
    return base
