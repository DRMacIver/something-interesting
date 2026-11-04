"""Expressive people with reviewed skin regions and exact tone sequences."""
import hashlib
import json
import numpy as np
from scipy import ndimage
from fontTools.ttLib import TTFont
from emoji_licensed import raster
from pen_translate import Settings, translate

SYMBOLS = '👶🧒👦👧🧑👨👩🧓👴👵🧔'
POINTS = list(map(ord, SYMBOLS))
# Region IDs are connected white interiors in the deterministic treated ink.
# The reviewed sheet distinguishes skin from caps, bows, hair, teeth and wraps.
REGIONS = {
    0x1F476: (4, [1]),       # Baby: face, excluding pacifier and blanket.
    0x1F9D2: (1, [1]),
    0x1F466: (4, [4]),       # Boy: keep all three cap panels white.
    0x1F467: (3, [3]),       # Girl: both hair bows remain white.
    0x1F9D1: (1, [1]),
    0x1F468: (1, [1]),
    0x1F469: (1, [1]),
    0x1F9D3: (2, [2]),       # Older people: white hair is not skin.
    0x1F474: (2, [2]),
    0x1F475: (2, [2]),
    0x1F9D4: (3, [1, 3]),    # Beard: face and neck, excluding teeth.
}


def prepare(font, cp):
    name = font.getBestCmap()[cp]
    source = raster(font.getGlyphSet(location={'wght': 400}), name)
    treated, report = translate(source, Settings(strength=1.7, seed=cp))
    assert report['appliedStrength'] > 0 and not report['fallback']
    ink = np.asarray(treated) < 128
    white = ndimage.binary_fill_holes(ink)
    labels, count = ndimage.label(white & ~ink)
    expected, selected = REGIONS[cp]
    assert count == expected, f'Unexpected people regions in U+{cp:04X}'
    interior = np.isin(labels, selected)
    excluded = (labels != 0) & ~interior
    # Underpaint the black edge, retaining the exact source ink on top.
    skin = ndimage.binary_dilation(interior, iterations=3) & white & ~excluded
    assert interior.sum() > 5000 and not (skin & excluded).any()
    report.update(skinPixels=int(skin.sum()), whiteDetailPixels=int(excluded.sum()),
                  skinRegions=selected, enclosedRegions=count)
    return (white, skin, ink), report, name


def add_people(root, glyphs, metrics, cmap, layers, review, outline):
    spec = json.loads((root/'data/font-sources/noto-emoji.json').read_text())['files'][0]
    path = root/spec['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == spec['sha256']
    forms = {chr(cp)+chr(t) for cp in POINTS for t in range(0x1F3FB, 0x1F400)}
    assert forms <= set(spec['include_sequences'])
    font = TTFont(path)
    sequences, rules = [], []
    for cp in POINTS:
        # U+1F9D1 was a blank input for the original astronaut ligature. Keep
        # that glyph name so existing longer substitutions retain their input.
        if cp in cmap:
            assert cp == 0x1F9D1 and glyphs[cmap[cp]].numberOfContours == 0
        name = cmap.get(cp, f'u{cp:X}')
        (white, skin, ink), treatment, source_name = prepare(font, cp)
        ys, xs = np.nonzero(white)
        x0, y0, x1, y1 = map(int, (xs.min(), ys.min(), xs.max(), ys.max()))
        factor = 760/max(x1-x0+1, y1-y0+1)
        transform = x0, y0, factor
        advance = round((x1-x0+1)*factor)+100
        glyphs[name] = outline(ink, transform)
        assert glyphs[name].numberOfContours >= treatment['sourceComponents']+treatment['sourceHoles']
        metrics[name] = advance, 50
        cmap[cp] = name
        for suffix, mask in [('white', white), ('skin', skin), ('ink', ink)]:
            layer = name+'.'+suffix
            glyphs[layer] = outline(mask, transform)
            metrics[layer] = advance, 50
        layers[name] = [(name+'.white', 0), (name+'.ink', 1)]
        for i in range(5):
            variant = name+f'.tone{i+1}'
            glyphs[variant] = glyphs[name]
            metrics[variant] = advance, 50
            layers[variant] = [(name+'.white', 0), (name+'.skin', 6+i), (name+'.ink', 1)]
            sequences.append(chr(cp)+chr(0x1F3FB+i))
            rules.append(f'sub {name} tone{i+1} by {variant};')
        review.append(dict(codepoint=f'U+{cp:04X}', glyphName=name, category='people',
                           source=spec['path'], sourceGlyph=source_name,
                           sourceWeight=400, sourcePixels=384, advance=advance,
                           bounds=[x0,y0,x1,y1], penTreatment=treatment,
                           license='NotoEmoji-OFL.txt',
                           fill='reviewed face/neck regions; hair, hats, bows, teeth, pacifier and blanket remain unchanged'))
    return sequences, '\n'.join(rules)
