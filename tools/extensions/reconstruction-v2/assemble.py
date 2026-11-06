"""Build four full panels, preserving the scanned art at its original resolution."""
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as b
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
PLAYER_AT = (1500, 2714)


def drawing(filename, size):
    return Image.open(HERE / filename).convert('L').resize(size, RESAMPLE)


def register_bottom(image, seam, target_x, donor_x, donor_y, depth):
    """Match the widths and positions of cut contours, fading to native geometry."""
    a = np.asarray(image)
    yy, xx = np.mgrid[seam:seam + depth, :image.width]
    fade = (1 - (yy - seam) / depth) ** 2
    dx = np.interp(xx, target_x, donor_x) - xx
    aligned = ndimage.map_coordinates(a, [yy + (donor_y - seam) * fade, xx + dx * fade],
                                       order=1, mode='nearest')
    image.paste(Image.fromarray(aligned), (0, seam))


def panel_two():
    canvas = Image.new('L', (1591, 1830), 255)
    upper = Image.open(HERE / 'upper-2.png').convert('L')
    canvas.paste(upper.resize((1391, 1030), RESAMPLE), (200, 0))
    # Dad's legs below the last scan row are drawn by drawn_legs.panel_two.
    lower = drawing('panel2-player-and-shirt.png', (735, 608))
    player = lower.crop((0, 0, 438, 608))
    register_bottom(player, 400, [0, 138, 141, 401, 405, 438],
                    [0, 125, 157, 390, 420, 438], 400, 22)
    # Only the record and its case use this warp. The left shoe overlaps its
    # right wall and stays attached to the rest of the child at native scale.
    canvas.paste(player.crop((0, 400, 438, 608)), (635, 1030))
    child = lower.crop((438, 0, 735, 608))
    register_bottom(child, 400, [0, 36, 49, 80, 86, 118, 154, 208, 214, 297],
                    [0, 39, 50, 72, 81, 116, 143, 191, 202, 297], 380, 62)
    canvas.paste(child.crop((0, 400, 297, 608)), (1073, 1030))
    # Restore the actual grille and the irregular pair of knobs from panel 1.
    # The record in the locked strip has a different perspective, so retain
    # the fitted case and use the original controls on its front face.
    canvas.paste(255, (790, 1051, 864, 1124))
    canvas.paste(255, (889, 1056, 934, 1134))
    controls = Image.open(HERE / 'calvin-player-source.png').crop((240, 268, 345, 332))
    controls.paste(255, (55, 0, 105, 4))
    controls.paste(255, (0, 59, 25, 64))
    controls = controls.resize((132, 81), RESAMPLE)
    face = canvas.crop((793, 1053, 925, 1134))
    canvas.paste(ImageChops.darker(face, controls), (793, 1053))
    result = b.smooth(np.asarray(canvas) < 128)
    result.paste(255, (0, 0, result.width, 2060))
    result.paste(upper, (400, 0))
    return result


def scaled_inserts():
    """Separate the original child and player at the small shoe-to-case contact."""
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
    player = source.crop((218, 226, 415, 349))
    ImageDraw.Draw(player).polygon([(0, 84), (5, 84), (7, 101), (0, 101)], fill=255)
    # Anchor the face to the original seated figure's box even when the toes move.
    child = child.crop((margin + 3 - CALVIN_SHIFT, 8, margin + 226, 365))
    player = player.crop(ImageChops.invert(player).getbbox())
    result = []
    for art in (child, player):
        art = b.smooth(np.asarray(art) < 128)
        result.append(art.resize(tuple(round(s * CALVIN_SCALE) for s in art.size), RESAMPLE))
    return result


def panel_three(original):
    # Everything of Dad outside the scan is drawn by drawn_legs.panel_three.
    staged = Image.new('L', (1587, 1830), 255)
    staged.paste(Image.open(HERE / 'original-3.png'), (400, 0))
    result = b.smooth(np.asarray(staged) < 128)
    result.paste(original, (800, 0))
    child, player = scaled_inserts()
    # Ink them over the panel, so their white surround leaves the scan alone.
    for art, at in ((child, CALVIN_AT), (player, PLAYER_AT)):
        box = (*at, at[0] + art.width, at[1] + art.height)
        result.paste(ImageChops.darker(result.crop(box), art), box)
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
            image = drawn_legs.panel_two(panel_two())
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
    # Normalize by Dad's head width so the proof does not hide scale errors.
    comparison = Image.new('L', (1536, 606), 255)
    pen = ImageDraw.Draw(comparison)
    for column, (number, head_width) in enumerate(((2, 493), (3, 562))):
        panel = Image.open(OUT / f'panel{number}.png')
        art = panel.crop(ImageChops.invert(panel).getbbox())
        art = art.resize(tuple(round(s * 136 / head_width) for s in art.size), RESAMPLE)
        left = column*768 + (768-art.width)//2
        comparison.paste(art, (left, 575-art.height))
        pen.text((column*768+26, 21), f'Panel {number}', font=ImageFont.load_default(size=22), fill=30)
    pen.line((767, 20, 767, 585), fill=218)
    comparison.save(OUT / 'kneeling-comparison.png')
    (OUT / 'verification.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    build()
