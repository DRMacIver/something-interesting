"""Compile the original facial-expression atlas without borrowing system emoji."""
import hashlib
import numpy as np
from PIL import Image
from scipy import ndimage
from pen_translate import Settings, translate

POINTS = [0x1F60A, 0x1F606, 0x1F610, 0x1F634]


EXPANSION = [0x1F601, 0x1F603, 0x1F604, 0x1F605, 0x1F609, 0x1F60B,
             0x1F60E, 0x1F611, 0x1F642, 0x1F641, 0x1F62E, 0x1F62F]


PLAYFUL = [0x1F61B, 0x1F61C, 0x1F61D, 0x1F92A, 0x1F928, 0x1F9D0,
           0x1F913, 0x1F910, 0x1F644, 0x1F60F, 0x1F612, 0x1F62C]


STRAINED = [0x1F615, 0x1F61F, 0x1F61E, 0x1F614, 0x1F616, 0x1F623,
            0x1F629, 0x1F62B, 0x1F624, 0x1F620, 0x1F643, 0x1F636]


AILING = [0x1F637, 0x1F912, 0x1F915, 0x1F927, 0x1F971, 0x1F62A,
          0x1F924, 0x1F635, 0x1F632, 0x1F626, 0x1F627, 0x1F622]


def add_faces(root, glyphs, metrics, cmap, layers, review, outline):
    records = []
    for filename, points, columns, rows in [
        ('faces-reference-study-v2.png', POINTS, 2, None),
        ('faces-expansion-v1.png', EXPANSION, 4, [0, 365, 660, 1024]),
        ('faces-playful-v1.png', PLAYFUL, 4, [0, 350, 650, 1024]),
        ('faces-strained-v1.png', STRAINED, 4, [0, 345, 650, 1024]),
        ('faces-ailing-v1.png', AILING, [0, 410, 770, 1120, 1536], [0, 366, 672, 1024]),
    ]:
        records.append(add_sheet(root, glyphs, metrics, cmap, layers, review,
                                 outline, filename, points, columns, rows))
    return records


def add_sheet(root, glyphs, metrics, cmap, layers, review, outline,
              filename, points, columns, rows):
    source = root/'output/imagegen/emoji-production'/filename
    atlas = np.asarray(Image.open(source).convert('RGBA'))
    height, width = atlas.shape[:2]
    if isinstance(columns, int):
        assert width % columns == 0
        edges = [i*width//columns for i in range(columns+1)]
    else:
        edges = columns
        columns = len(edges)-1
        assert edges[0] == 0 and edges[-1] == width
        assert all(a < b for a, b in zip(edges, edges[1:]))
    if rows is None:
        assert height % 2 == 0
        rows = [0, height//2, height]
    assert rows[-1] == height and len(points) == columns*(len(rows)-1)
    for index, cp in enumerate(points):
        row, col = divmod(index, columns)
        top = rows[row]
        left, right = edges[col:col+2]
        cellw = right-left
        cell = atlas[top:rows[row+1], left:right]
        # Compile the approved white-background study into ink and enclosed
        # white interiors. This is glyph tracing, not a raster-image edit.
        ink = (cell[:, :, :3].max(axis=2) < 128) & (cell[:, :, 3] >= 128)
        labels, _ = ndimage.label(ink)
        areas = np.bincount(labels.ravel())
        ink &= areas[labels] >= 12
        sy, sx = np.nonzero(ink)
        source_bounds = [int(sx.min()), int(sy.min()), int(sx.max()), int(sy.max())]
        assert min(source_bounds[0], source_bounds[1], cellw-1-source_bounds[2],
                   cell.shape[0]-1-source_bounds[3]) > 2, f'Clipped source {cp:X}'
        # Preserve the phase choices in the user's comparison for those four
        # samples; other faces get a stable codepoint-derived phase.
        seed = {0x1F601:17, 0x1F913:18, 0x1F624:19, 0x1F636:20}.get(cp, cp)
        treated, treatment = translate(ink, Settings(strength=1.7, seed=seed))
        ink = np.asarray(treated) < 128
        opaque = ndimage.binary_fill_holes(ink)
        yy, xx = np.nonzero(opaque)
        x0, y0, x1, y1 = map(int, (xx.min(), yy.min(), xx.max(), yy.max()))
        assert min(x0, y0, ink.shape[1]-1-x1, ink.shape[0]-1-y1) > 2, f'Clipped face {cp:X}'
        factor = 760/max(x1-x0+1, y1-y0+1)
        transform = x0, y0, factor
        name = f'u{cp:X}'
        assert cp not in cmap
        advance = round((x1-x0+1)*factor)+100
        glyphs[name] = outline(ink, transform)
        metrics[name] = advance, 50
        cmap[cp] = name
        layers[name] = []
        for i, mask in enumerate((opaque, ink)):
            layer = f'{name}.layer{i}'
            glyphs[layer] = outline(mask, transform)
            metrics[layer] = advance, 50
            layers[name].append((layer, i))
        review.append(dict(codepoint=f'U+{cp:04X}', source=str(source.relative_to(root)),
                           cell=index, sourceTop=top, sourceLeft=left, sourceBounds=source_bounds,
                           bounds=[x0, y0, x1, y1], advance=advance, penTreatment=treatment))
    return dict(source=str(source.relative_to(root)), sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                codepoints=points, penRecipeSha256=hashlib.sha256((root/'tools/font/pen_translate.py').read_bytes()).hexdigest(),
                design='expressive procedural ink at requested strength 1.7; guarded per-glyph reductions; white interior and black details')
