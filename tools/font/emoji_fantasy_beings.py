"""Compile reviewed non-human fantasy drawings without skin-tone ligatures."""
import hashlib
import importlib
import json

import numpy as np
from fontTools.pens.ttGlyphPen import TTGlyphPen
from emoji_sequences import qualified_forms

FAMILIES = {
    'genie': ('emoji_genie_svg', 'light blue'),
    'zombie': ('emoji_zombie_svg', 'green'),
    'troll': ('emoji_troll_svg', 'green'),
}


def add_fantasy_beings(root, glyphs, metrics, cmap, layers, palette, review, outline):
    palette_path = root/'output/imagegen/emoji-production/colour-face-palette-source.json'
    palette_raw = palette_path.read_bytes()
    palette_source = json.loads(palette_raw)
    assert hashlib.sha256((root/palette_source['pdf']).read_bytes()).hexdigest() == palette_source['pdfSha256']
    colours = {sample['colour']: tuple(sample['rgb']) for sample in palette_source['samples']}
    sequences, components, rules = [], [], []
    for family, (module_name, colour_name) in FAMILIES.items():
        module = importlib.import_module(module_name)
        rgb = colours[colour_name]
        if rgb not in palette:
            palette.append(rgb)
        colour_id = palette.index(rgb)
        for key in module.RECIPES:
            canonical = ''.join(chr(int(cp, 16)) for cp in key.split('_'))
            (white, body, ink), report = module.prepare(key)
            source = report['source']
            forms = qualified_forms(root, canonical)
            assert set(forms) == set(source['include_sequences'])
            assert not any(0x1F3FB <= ord(char) <= 0x1F3FF for text in forms for char in text)
            ys, xs = np.nonzero(white)
            bounds = list(map(int, (xs.min(), ys.min(), xs.max(), ys.max())))
            scale = 760/max(bounds[2]-bounds[0]+1, bounds[3]-bounds[1]+1)
            transform = bounds[0], bounds[1], scale
            advance = round((bounds[2]-bounds[0]+1)*scale)+100
            name = 'fantasybeing.'+key.replace('_', '.')
            glyphs[name] = outline(ink, transform)
            metrics[name] = advance, 50
            assert report['appliedStrength'] > 0 and not report['fallback']
            assert glyphs[name].numberOfContours == report['sourceComponents']+report['sourceHoles'], key
            layers[name] = []
            for suffix, mask, index in [('white', white, 0), ('body', body, colour_id), ('ink', ink, 1)]:
                layer = name+'.'+suffix
                glyphs[layer] = outline(mask, transform)
                metrics[layer] = advance, 50
                layers[name].append((layer, index))
            if len(canonical) == 1:
                assert ord(canonical) not in cmap
                cmap[ord(canonical)] = name
            for char in canonical:
                cp = ord(char)
                if cp not in cmap:
                    component = f'component.{cp:X}'
                    cmap[cp] = component
                    glyphs[component] = TTGlyphPen(None).glyph()
                    metrics[component] = 0, 0
                    components.append(cp)
            if len(canonical) > 1:
                rules.append((len(canonical), 'sub '+' '.join(cmap[ord(char)] for char in canonical)+' by '+name+';'))
                sequences.extend(forms)
            else:
                sequences.extend(form for form in forms if form != canonical)
            identity = dict(codepoint=f'U+{ord(canonical):04X}') if len(canonical) == 1 else dict(sequence=canonical)
            review.append(dict(
                **identity, label=key, glyphName=name, category='fantasy-beings',
                source=source['path'], sourceSha256=source['sha256'], sourceRecipe=key,
                sourcePixels=report['sourcePixels'], bounds=bounds, advance=advance,
                penTreatment=report, bodyColour=list(rgb),
                paletteSource=str(palette_path.relative_to(root)),
                paletteSourceSha256=hashlib.sha256(palette_raw).hexdigest(),
                license='NotoEmoji-SVG-Apache-2.0.txt', notice='NotoEmoji-SVG-NOTICE.txt',
            ))
    return sequences, components, '\n'.join(rule for _, rule in sorted(rules, key=lambda item: -item[0]))
