"""Reviewed occupation ligatures, with skin kept separate from clothing and tools."""
import hashlib
import json
import numpy as np
import uharfbuzz as hb
from scipy import ndimage
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from emoji_licensed import raster
from emoji_sequences import source_ligature, qualified_forms
from pen_translate import Settings, translate

# Canonical form: reviewed enclosed-region count and exposed-skin region IDs.
# Spectacle lenses are transparent; protective science goggles remain white.
# The neutral firefighter needs 768px to preserve the small helmet emblem.
FORMS = {
    '🧑\u200d⚕️': (8, [1]),
    '👨\u200d⚕️': (8, [1]),
    '👩\u200d⚕️': (8, [1]),
    '🧑\u200d🎓': (3, [3]),
    '👨\u200d🎓': (3, [3]),
    '👩\u200d🎓': (3, [3]),
    '🧑\u200d🏫': (10, [1, 3, 5, 6]),
    '👨\u200d🏫': (10, [1, 4, 5, 6]),
    '👩\u200d🏫': (10, [1, 4, 5, 6]),
    '🧑\u200d⚖️': (5, [1]),
    '👨\u200d⚖️': (5, [1]),
    '👩\u200d⚖️': (5, [1]),
    '🧑\u200d🌾': (5, [5]),
    '👨\u200d🌾': (5, [5]),
    '👩\u200d🌾': (5, [5]),
    '🧑\u200d🍳': (5, [2]),
    '👨\u200d🍳': (5, [2]),
    '👩\u200d🍳': (5, [2]),
    '🧑\u200d🔧': (3, [3]),
    '👨\u200d🔧': (3, [3]),
    '👩\u200d🔧': (3, [3]),
    '🧑\u200d🏭': (5, [3]),
    '👨\u200d🏭': (5, [3]),
    '👩\u200d🏭': (5, [3]),
    '🧑\u200d💼': (6, [1]),
    '👨\u200d💼': (6, [1]),
    '👩\u200d💼': (6, [1]),
    '🧑\u200d🔬': (7, [1, 7]),
    '👨\u200d🔬': (7, [1, 7]),
    '👩\u200d🔬': (8, [1, 7]),
    '🧑\u200d💻': (4, [2]),
    '👨\u200d💻': (4, [2]),
    '👩\u200d💻': (4, [2]),
    '🧑\u200d🎤': (5, [1]),
    '👨\u200d🎤': (6, [1]),
    '👩\u200d🎤': (6, [1]),
    '🧑\u200d🎨': (11, [5]),
    '👨\u200d🎨': (11, [5]),
    '👩\u200d🎨': (11, [5]),
    '🧑\u200d✈️': (7, [7]),
    '👨\u200d✈️': (7, [7]),
    '👩\u200d✈️': (7, [7]),
    '👨\u200d🚀': (7, [6]),
    '👩\u200d🚀': (7, [6]),
    '🧑\u200d🚒': (9, [7]),
    '👨\u200d🚒': (9, [7]),
    '👩\u200d🚒': (9, [7]),
}


def prepare(font, shaping_font, canonical):
    pixels = 768 if canonical in {'🧑‍🚒', '👩‍🍳'} else 384
    return prepare_regions(font, shaping_font, canonical, *FORMS[canonical], pixels=pixels)


def prepare_regions(font, shaping_font, canonical, expected, selected, pixels=384):
    name = source_ligature(font, shaping_font, canonical)
    key = canonical.replace('\ufe0f', '')
    seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], 'big')
    source = raster(font.getGlyphSet(location={'wght':400}), name, pixels=pixels)
    treated, report = translate(source, Settings(strength=1.7, seed=seed))
    assert report['appliedStrength'] > 0 and not report['fallback']
    ink = np.asarray(treated) < 128
    white = ndimage.binary_fill_holes(ink)
    labels, count = ndimage.label(white & ~ink)
    assert count == expected, canonical
    interior = np.isin(labels, selected)
    excluded = (labels != 0) & ~interior
    skin = ndimage.binary_dilation(interior, iterations=3) & white & ~excluded
    assert skin.sum() > 5000 and not (skin & excluded).any()
    report.update(sourcePixels=pixels, skinRegions=selected, enclosedRegions=count,
                  skinPixels=int(skin.sum()))
    return (white, skin, ink), report, name


def add_professions(root, glyphs, metrics, cmap, layers, palette, review, outline):
    return add_reviewed_roles(root, glyphs, metrics, cmap, layers, review, outline,
                              FORMS, prepare, 'professions', 'profession')


def add_reviewed_roles(root, glyphs, metrics, cmap, layers, review, outline,
                       forms_by_name, prepare_fn, category, prefix):
    spec = json.loads((root/'data/font-sources/noto-emoji.json').read_text())['files'][0]
    source = root/spec['path']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == spec['sha256']
    font = TTFont(source); shaping_font = hb.Font(hb.Face(source.read_bytes()))
    shaping_font.set_variations({'wght':400})
    sequences, components, rules, variations, tones = [], [], [], set(), []
    for canonical in forms_by_name:
        masks, treatment, source_name = prepare_fn(font, shaping_font, canonical)
        white, skin, ink = masks
        ys, xs = np.nonzero(white)
        x0,y0,x1,y1 = map(int,(xs.min(),ys.min(),xs.max(),ys.max()))
        factor = 760/max(x1-x0+1,y1-y0+1); transform = x0,y0,factor
        advance = round((x1-x0+1)*factor)+100
        key = canonical.replace('\ufe0f','')
        name = prefix+'.'+'.'.join(f'{ord(c):X}' for c in key)
        glyphs[name] = outline(ink,transform);metrics[name] = advance,50
        assert glyphs[name].numberOfContours >= treatment['sourceComponents']+treatment['sourceHoles'], (canonical, glyphs[name].numberOfContours, treatment)
        if len(key)==1:
            assert ord(key) not in cmap
            cmap[ord(key)] = name
        for suffix, mask in [('white',white),('skin',skin),('ink',ink)]:
            layer = name+'.'+suffix;glyphs[layer] = outline(mask,transform);metrics[layer] = advance,50
        for i in range(6):
            variant = name+(f'.tone{i}' if i else '')
            glyphs[variant] = glyphs[name];metrics[variant] = advance,50
            layers[variant] = [(name+'.white',0)]
            if i: layers[variant].append((name+'.skin',5+i))
            layers[variant].append((name+'.ink',1))
            text = canonical[:1]+chr(0x1F3FA+i)+canonical[1:].removeprefix('\ufe0f') if i else canonical
            forms = qualified_forms(root,text)
            assert set(forms) <= set(spec['include_sequences'])
            assert all(source_ligature(font,shaping_font,s)==source_name for s in forms)
            input_key = text.replace('\ufe0f','')
            for char in input_key:
                cp = ord(char)
                if cp not in cmap:
                    component = f'component.{cp:X}'
                    cmap[cp] = component;glyphs[component] = TTGlyphPen(None).glyph()
                    metrics[component] = 0,0;components.append(cp)
            if len(input_key)>1:
                rules.append((len(input_key),'sub '+' '.join(cmap[ord(c)] for c in input_key)+' by '+variant+';'))
            sequences.extend(form for form in forms if i or form != key or len(key)>1)
            if i: tones.extend(forms)
            for form in forms:
                for before,after in zip(form,form[1:]):
                    if after=='\ufe0f':variations.add((ord(before),0xFE0F))
        identity = dict(codepoint=f'U+{ord(key):04X}') if len(key)==1 else dict(sequence=canonical)
        review.append(dict(**identity,label=source_name,glyphName=name,category=category,
                           source=spec['path'],sourceGlyph=source_name,sourceWeight=400,sourcePixels=treatment['sourcePixels'],
                           bounds=[x0,y0,x1,y1],advance=advance,penTreatment=treatment,
                           license='NotoEmoji-OFL.txt'))
    return sequences, components, '\n'.join(rule for _,rule in sorted(rules,key=lambda item:-item[0])), sorted(variations), tones
