"""Reviewed hair/gender person ligatures, with independent skin and hair layers."""
import hashlib
import json
import numpy as np
import uharfbuzz as hb
from scipy import ndimage
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from emoji_licensed import raster
from emoji_sequences import source_ligature, qualified_forms
from emoji_sequence_colour import read_colour
from pen_translate import Settings, translate

# Canonical neutral form: enclosed-region count, skin-region IDs, hair colour.
FORMS = {
    '👱': (2, [2], 'yellow'),
    '🧔‍♂️': (3, [1,3], None),
    '🧔‍♀️': (3, [1,3], None),
    '👨‍🦰': (1, [1], 'orange'),
    '👨‍🦱': (1, [1], None),
    '👨‍🦳': (2, [2], None),
    '👨‍🦲': (1, [1], None),
    '👩‍🦰': (1, [1], 'orange'),
    '🧑‍🦰': (1, [1], 'orange'),
    '👩‍🦱': (1, [1], None),
    '🧑‍🦱': (1, [1], None),
    '👩‍🦳': (2, [2], None),
    '🧑‍🦳': (3, [2], None),
    '👩‍🦲': (1, [1], None),
    '🧑‍🦲': (1, [1], None),
    '👱‍♀️': (2, [2], 'yellow'),
    '👱‍♂️': (2, [2], 'yellow'),
}


def prepare(font, shaping_font, canonical):
    name = source_ligature(font, shaping_font, canonical)
    key = canonical.replace('\ufe0f', '')
    seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], 'big')
    source = raster(font.getGlyphSet(location={'wght':400}), name)
    treated, report = translate(source, Settings(strength=1.7, seed=seed))
    assert report['appliedStrength'] > 0 and not report['fallback']
    ink = np.asarray(treated) < 128
    white = ndimage.binary_fill_holes(ink)
    labels, count = ndimage.label(white & ~ink)
    expected, selected, colour = FORMS[canonical]
    assert count == expected, canonical
    interior = np.isin(labels, selected)
    excluded = (labels != 0) & ~interior
    skin = ndimage.binary_dilation(interior, iterations=3) & white & ~excluded
    hair = np.zeros_like(ink)
    display_ink = ink.copy()
    if colour == 'yellow':
        hair = ndimage.binary_dilation(labels == 1, iterations=3) & white & ~interior
    elif colour == 'orange':
        # Red hair is solid in the monochrome donor. Open only the inset of
        # the largest thick ink component; eyes, mouth and thin face borders
        # stay black. Preserve the original complete ink for monochrome fallback.
        cores, n = ndimage.label(ndimage.distance_transform_edt(ink) > 9)
        sizes = np.bincount(cores.ravel()); sizes[0] = 0
        core = cores == sizes.argmax()
        assert n > 1 and core.sum() > 5000
        assert sorted(sizes[1:])[-1] > 5*sorted(sizes[1:])[-2]
        assert not (core & skin).any()
        hair = ndimage.binary_dilation(core, iterations=2) & ink
        display_ink &= ~core
        report.update(hairBorderPixels=9, hairCorePixels=int(core.sum()),
                      monochromeFallback='original solid hair')
    assert skin.sum() > 5000 and not (skin & excluded).any()
    assert not (hair & interior).any()
    report.update(skinRegions=selected, enclosedRegions=count,
                  skinPixels=int(skin.sum()), hairPixels=int(hair.sum()))
    return (white, skin, hair, display_ink, ink), report, name


def add_person_forms(root, glyphs, metrics, cmap, layers, palette, review, outline):
    spec = json.loads((root/'data/font-sources/noto-emoji.json').read_text())['files'][0]
    source = root/spec['path']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == spec['sha256']
    font = TTFont(source); shaping_font = hb.Font(hb.Face(source.read_bytes()))
    shaping_font.set_variations({'wght':400})
    sequences, components, rules, variations, tones = [], [], [], set(), []
    for canonical, (_, _, colour) in FORMS.items():
        masks, treatment, source_name = prepare(font, shaping_font, canonical)
        white, skin, hair, display_ink, fallback = masks
        ys, xs = np.nonzero(white)
        x0,y0,x1,y1 = map(int,(xs.min(),ys.min(),xs.max(),ys.max()))
        factor = 760/max(x1-x0+1,y1-y0+1); transform = x0,y0,factor
        advance = round((x1-x0+1)*factor)+100
        key = canonical.replace('\ufe0f','')
        name = 'personform.'+'.'.join(f'{ord(c):X}' for c in key)
        glyphs[name] = outline(fallback,transform);metrics[name] = advance,50
        assert glyphs[name].numberOfContours >= treatment['sourceComponents']+treatment['sourceHoles']
        if len(canonical)==1:
            assert ord(canonical) not in cmap
            cmap[ord(canonical)] = name
        colour_info = {}
        colour_id = None
        if colour:
            rgb, provenance = read_colour(root,colour)
            if rgb not in palette: palette.append(rgb)
            colour_id = palette.index(rgb)
            colour_info = dict(hairColour=colour,hairRGB=rgb,**provenance)
        for suffix, mask in [('white',white),('skin',skin),('ink',display_ink),*([('hair',hair)] if colour else [])]:
            layer = name+'.'+suffix;glyphs[layer] = outline(mask,transform);metrics[layer] = advance,50
        for i in range(6):
            variant = name+(f'.tone{i}' if i else '')
            glyphs[variant] = glyphs[name];metrics[variant] = advance,50
            layers[variant] = [(name+'.white',0)]
            if i: layers[variant].append((name+'.skin',5+i))
            if colour: layers[variant].append((name+'.hair',colour_id))
            layers[variant].append((name+'.ink',1))
            text = canonical[:1]+(chr(0x1F3FA+i) if i else '')+canonical[1:]
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
                sequences.extend(forms)
            if i: tones.extend(forms)
            for form in forms:
                for before,after in zip(form,form[1:]):
                    if after=='\ufe0f':variations.add((ord(before),0xFE0F))
        identity = dict(codepoint=f'U+{ord(canonical):04X}') if len(canonical)==1 else dict(sequence=canonical)
        review.append(dict(**identity,label=source_name,glyphName=name,category='person-forms',
                           source=spec['path'],sourceGlyph=source_name,sourceWeight=400,sourcePixels=384,
                           bounds=[x0,y0,x1,y1],advance=advance,penTreatment=treatment,
                           license='NotoEmoji-OFL.txt',**colour_info))
    return sequences, components, '\n'.join(rule for _,rule in sorted(rules,key=lambda item:-item[0])), sorted(variations), tones
