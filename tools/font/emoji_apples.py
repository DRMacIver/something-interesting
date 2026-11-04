"""Red/green apples share reviewed pen geometry and distinct PDF-derived fills."""
import hashlib
import json
import numpy as np
from fontTools.ttLib import TTFont
from emoji_colour_faces import prepare_face

APPLES = {0x1F34E: 'red', 0x1F34F: 'green'}
OUTLINE_SOURCE = 0x1F34F


def prepare_apple(font):
    # The donor's red apple is a solid silhouette. Use its outlined green apple
    # for both identities; colour, rather than unrelated geometry, carries the
    # distinction. The shared helper fills the largest enclosed region beneath
    # the final ink while leaving other enclosed white details unpainted.
    masks, treatment, source_name = prepare_face(font, OUTLINE_SOURCE)
    treatment['fruitFillPixels'] = treatment.pop('faceFillPixels')
    return masks, treatment, source_name


def add_apples(root, glyphs, metrics, cmap, layers, palette, review, outline):
    source_record = json.loads((root/'data/font-sources/noto-emoji.json').read_text())
    source = root/source_record['files'][0]['path']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_record['files'][0]['sha256']
    palette_path = root/'output/imagegen/emoji-production/apple-palette-source.json'
    palette_record = json.loads(palette_path.read_text())
    assert hashlib.sha256((root/palette_record['pdf']).read_bytes()).hexdigest() == palette_record['pdfSha256']
    reused = palette_record['reusedPalette']
    assert hashlib.sha256((root/reused['path']).read_bytes()).hexdigest() == reused['sha256']
    colours = {s['colour']:tuple(s['rgb']) for s in palette_record['samples']}
    masks, treatment, source_name = prepare_apple(TTFont(source))
    white, _, ink = masks
    yy, xx = np.nonzero(white)
    x0,y0,x1,y1 = map(int,(xx.min(),yy.min(),xx.max(),yy.max()))
    factor = 760/max(x1-x0+1,y1-y0+1)
    transform = x0,y0,factor
    advance = round((x1-x0+1)*factor)+100
    for cp,colour in APPLES.items():
        assert cp not in cmap
        name = f'u{cp:X}'
        glyphs[name] = outline(ink,transform)
        assert glyphs[name].numberOfContours >= treatment['sourceComponents']+treatment['sourceHoles']
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
        review.append(dict(codepoint=f'U+{cp:04X}',category='apples',source=str(source.relative_to(root)),
                           sourceGlyph=source_name,sourceCodepoint=f'U+{OUTLINE_SOURCE:X}',
                           sourceWeight=400,sourcePixels=384,advance=advance,
                           bounds=[x0,y0,x1,y1],penTreatment=treatment,colour=colour,rgb=rgb,
                           paletteSource=str(palette_path.relative_to(root)),
                           paletteSha256=hashlib.sha256(palette_path.read_bytes()).hexdigest(),
                           fill='shared outlined apple; largest enclosed fruit region plus ink underpaint',
                           license='NotoEmoji-OFL.txt'))
