"""Build four full panels, preserving the scanned art at its original resolution."""
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as b
import dad2_refine
import drawn_legs

HERE = Path(__file__).resolve().parent
OUT = b.ROOT / 'assets/full-panels'
RESAMPLE = Image.Resampling.LANCZOS
CALVIN_SCALE = 1.56
# Turning Calvin's body about his torso needs room on the left for his legs.
CALVIN_TURN_MARGIN = 100
CALVIN_TORSO_MIDDLE = 67
# Where panel 3's Calvin and player go: his head where it was, the crop now
# starting CALVIN_SHIFT source pixels further left for his turned legs (100
# source pixels are exactly 312 export pixels), the player beyond his toes.
CALVIN_SHIFT = 100
CALVIN_AT = (2422 - round(CALVIN_SHIFT * 2 * CALVIN_SCALE), 2024)
# Panel 3 ends just above Dad's trousers, so his legs are never drawn.
PANEL3_HEIGHT = 2690


def panel_two():
    """Watterson's crop already reaches Dad's knee at its foot, so panel 2 is
    not extended below it: only to the left, for his back and sleeve (drawn
    by dad2_refine), and to the right, for the rest of Calvin's head (the
    earlier repaired upper artwork)."""
    upper = Image.open(HERE / 'upper-2.png').convert('L')
    result = Image.new('L', (400 + upper.width, upper.height), 255)
    result.paste(upper, (400, 0))
    return dad2_refine.panel_two(result)


def calvin_insert():
    """Panel 1's seated Calvin, turned to face the player, at close-up scale."""
    source = Image.open(HERE / 'calvin-player-source.png').convert('L')
    child = source.crop((0, 0, 228, 380))
    ImageDraw.Draw(child).polygon([(231, 219), (217, 242), (216, 291),
                                   (214, 316), (210, 337), (216, 379),
                                   (432, 379), (432, 219)], fill=255)
    # In panel 2 Calvin sits facing left, his feet towards the player, so turn
    # his seated body about the middle of his torso (x=67) to face left too,
    # keeping it under his head, which still looks up towards Dad. The neck
    # line divides head from body.
    neck = [(0, 213), (56, 213), (62, 212), (71, 216), (78, 219), (86, 217),
            (99, 214), (116, 215), (123, 221), (210, 225), (228, 225)]
    head = child.copy()
    ImageDraw.Draw(head).polygon(neck + [(228, 380), (0, 380)], fill=255)
    body = child.copy()
    ImageDraw.Draw(body).polygon([(0, 0), (228, 0)] + neck[::-1], fill=255)
    margin, axis = CALVIN_TURN_MARGIN, CALVIN_TORSO_MIDDLE
    child = Image.new('L', (228 + margin, 380), 255)
    child.paste(head, (margin, 0))
    turned = Image.new('L', child.size, 255)
    turned.paste(ImageOps.mirror(body), (margin + 2 * axis - 227, 0))
    child = ImageChops.darker(child, turned)
    # Anchor the face to the original seated figure's box even when the toes move.
    child = child.crop((margin + 3 - CALVIN_SHIFT, 8, margin + 226, 365))
    art = b.smooth(np.asarray(child) < 128)
    return art.resize(tuple(round(s * CALVIN_SCALE) for s in art.size), RESAMPLE)


def panel_three(original):
    # Everything of Dad outside the scan is drawn by drawn_legs.panel_three.
    staged = Image.new('L', (1587, PANEL3_HEIGHT // 2), 255)
    staged.paste(Image.open(HERE / 'original-3.png'), (400, 0))
    result = b.smooth(np.asarray(staged) < 128)
    result.paste(original, (800, 0))
    # Calvin as far down as the panel goes (the player sits below its foot).
    child = calvin_insert()
    child = child.crop((0, 0, child.width, PANEL3_HEIGHT - CALVIN_AT[1]))
    # Ink him over the panel, so his white surround leaves the scan alone.
    box = (*CALVIN_AT, CALVIN_AT[0] + child.width, CALVIN_AT[1] + child.height)
    result.paste(ImageChops.darker(result.crop(box), child), box)
    return result


def build():
    OUT.mkdir(exist_ok=True)
    source_pair = Image.open(HERE / 'calvin-player-source.png')
    b.smooth(np.asarray(source_pair) < 128).save(OUT / 'reused-calvin-player.png')
    records = []
    overview = Image.new('L', (1600, 2100), 235)
    for number in range(1, 5):
        original = Image.open(HERE / f'locked-{number}.png').convert('L')
        x = 800 if number in (2, 3) else 400
        if number == 2:
            image = panel_two()
        elif number == 3:
            image = drawn_legs.panel_three(panel_three(original))
        else:
            ink = np.asarray(Image.open(HERE / f'original-{number}.png')) < 128
            extended, _ = b.extended(ink, b.PANELS[number - 1])
            image = b.smooth(extended)
            image.paste(original, (x, 0))
        original.save(OUT / f'original{number}.png', optimize=True)
        image.save(OUT / f'panel{number}.png', optimize=True)
        preview = image.copy()
        preview.thumbnail((950, 1100))
        preview.save(OUT / f'preview{number}.png')
        source = np.asarray(original)
        difference = np.asarray(image.crop((x, 0, x + original.width, original.height))) != source
        records.append(dict(panel=number, size=image.size, originalOffset=[x, 0],
                            originalSize=original.size, changedOriginalPixels=int(difference.sum()),
                            originalMatchFraction=1 - float(difference.mean()),
                            changedOriginalInkPixels=int(difference[source < 255].sum())))
        ink = ImageChops.invert(image) if number < 4 else image
        l, t, r, bottom = ink.getbbox()
        crop = image.crop((max(0, l-30), max(0, t-30), min(image.width, r+30), min(image.height, bottom+30)))
        crop.thumbnail((770, 970))
        col, row = (number - 1) % 2, (number - 1) // 2
        overview.paste(crop, (col*800+(800-crop.width)//2, row*1050+50))
        ImageDraw.Draw(overview).text((col*800+20, row*1050+20), f'Panel {number}', fill=0)
    overview.save(OUT / 'overview.png')
    (OUT / 'verification.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    build()
