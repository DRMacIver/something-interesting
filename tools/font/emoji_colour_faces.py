"""Selective PDF-derived face colours over guarded expressive donor outlines."""
import hashlib
import json
import numpy as np
from scipy import ndimage
from fontTools.ttLib import TTFont
from emoji_licensed import raster
from pen_translate import Settings, translate

COLOURS = {0x1F621:'red', 0x1F922:'green', 0x1F975:'orange', 0x1F976:'light blue'}


def prepare_face(font, cp):
    source_name = font.getBestCmap()[cp]
    ink = raster(font.getGlyphSet(location={'wght':400}), source_name)
    treated, treatment = translate(ink, Settings(strength=1.7, seed=cp))
    ink = np.asarray(treated) < 128
    white = ndimage.binary_fill_holes(ink)
    interiors, _ = ndimage.label(white & ~ink)
    sizes = np.bincount(interiors.ravel()); sizes[0] = 0
    face = interiors == sizes.argmax()
    # Only the main face region receives semantic colour. Enclosed teeth,
    # eyes, tongue and sweat droplets remain on the white underlayer.
    assert face.sum() > white.sum()*.25, f'Review face fill U+{cp:04X}'
    treatment['faceFillPixels'] = int(face.sum())
    treatment['whiteDetailPixels'] = int((white & ~ink & ~face).sum())
    # Fill beneath the final ink layer as well. Independently traced, abutting
    # boundaries expose pale antialiasing seams around features and the rim.
    # Enclosed white details remain excluded; the ink paints over the overlap.
    face = face | ink
    return (white, face, ink), treatment, source_name


def add_colour_faces(root, glyphs, metrics, cmap, layers, palette, review, outline):
    source_record = json.loads((root/'data/font-sources/noto-emoji.json').read_text())
    source = root/source_record['files'][0]['path']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_record['files'][0]['sha256']
    palette_path = root/'output/imagegen/emoji-production/colour-face-palette-source.json'
    palette_record = json.loads(palette_path.read_text())
    assert hashlib.sha256((root/palette_record['pdf']).read_bytes()).hexdigest() == palette_record['pdfSha256']
    reused = palette_record['reusedPalette']
    assert hashlib.sha256((root/reused['path']).read_bytes()).hexdigest() == reused['sha256']
    colours = {s['colour']:tuple(s['rgb']) for s in palette_record['samples']}
    font = TTFont(source)
    for cp, colour in COLOURS.items():
        assert cp not in cmap
        masks, treatment, source_name = prepare_face(font, cp)
        white, face, ink = masks
        yy, xx = np.nonzero(white)
        x0,y0,x1,y1 = map(int,(xx.min(),yy.min(),xx.max(),yy.max()))
        factor = 760/max(x1-x0+1,y1-y0+1)
        transform = x0,y0,factor
        name = f'u{cp:X}'
        advance = round((x1-x0+1)*factor)+100
        glyphs[name] = outline(ink,transform)
        assert glyphs[name].numberOfContours >= treatment['sourceComponents']+treatment['sourceHoles'], f'Tracing lost a detail in U+{cp:04X}'
        metrics[name] = advance,50
        cmap[cp] = name
        rgb = colours[colour]
        if rgb not in palette: palette.append(rgb)
        layers[name] = []
        for i,(mask,colour_id) in enumerate(zip(masks,[0,palette.index(rgb),1])):
            layer = name+f'.layer{i}'
            glyphs[layer] = outline(mask,transform)
            metrics[layer] = advance,50
            layers[name].append((layer,colour_id))
        review.append(dict(codepoint=f'U+{cp:04X}',category='colour-faces',source=str(source.relative_to(root)),
                           sourceGlyph=source_name,sourceWeight=400,sourcePixels=384,advance=advance,
                           bounds=[x0,y0,x1,y1],penTreatment=treatment,colour=colour,rgb=rgb,
                           paletteSource=str(palette_path.relative_to(root)),
                           paletteSha256=hashlib.sha256(palette_path.read_bytes()).hexdigest(),
                           fill='largest enclosed face region plus ink underpaint; other enclosed details stay white',
                           license='NotoEmoji-OFL.txt'))
