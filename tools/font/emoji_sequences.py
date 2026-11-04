"""Compile reviewed donor ligatures, preserving exact Unicode qualification forms."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
import numpy as np
import uharfbuzz as hb
from scipy import ndimage
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from emoji_licensed import raster
from pen_translate import Settings, translate
from emoji_sequence_colour import COLOURS, colour_masks, read_colour

COMPOUNDS = [
    ('🍋\u200d🟩', 'Lime'),
    ('🍄\u200d🟫', 'Brown mushroom'),
    ('😶\u200d🌫️', 'Face in clouds'),
    ('😮\u200d💨', 'Face exhaling'),
    ('😵\u200d💫', 'Spiral eyes'),
    ('🙂\u200d↔️', 'Head shaking sideways'),
    ('🙂\u200d↕️', 'Head nodding'),
    ('🐈\u200d⬛', 'Black cat'),
    ('🐕\u200d🦺', 'Service dog'),
    ('🐻\u200d❄️', 'Polar bear'),
    ('⛓️\u200d💥', 'Broken chain'),
    ('🐦\u200d⬛', 'Black bird'),
]


@lru_cache(maxsize=8)
def _qualification_input(path, identity):
    """Read immutable source bytes once per filesystem generation."""
    source=Path(path)
    raw=source.read_bytes()
    stat=source.stat()
    current=(stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)
    if current!=identity:
        raise RuntimeError('Emoji qualification source changed while being read')
    return hashlib.sha256(raw).hexdigest(),raw


@lru_cache(maxsize=8)
def _qualification_index(digest, raw):
    """Decode source text only; never cache prepared artwork or build products."""
    assert hashlib.sha256(raw).hexdigest()==digest
    result={}
    for line in raw.decode().splitlines():
        fields=line.split('#')[0].strip().split(';')
        if len(fields)<2:
            continue
        text=''.join(chr(int(cp,16)) for cp in fields[0].split())
        result.setdefault(text.replace('\ufe0f',''),[]).append(text)
    return MappingProxyType({key:tuple(forms) for key,forms in result.items()})


def qualified_forms(root, canonical):
    source=(root/'data/unicode/18.0.0/emoji/emoji-test.txt').resolve()
    stat=source.stat()
    identity=(stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)
    digest,raw=_qualification_input(str(source),identity)
    result=list(_qualification_index(digest,raw).get(canonical.replace('\ufe0f',''),()))
    stat=source.stat()
    current=(stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)
    if current!=identity:
        raise RuntimeError('Emoji qualification source changed during lookup')
    assert canonical in result
    return result


def source_ligature(font, shaping_font, text):
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    buffer.flags = hb.BufferFlags.REMOVE_DEFAULT_IGNORABLES
    hb.shape(shaping_font, buffer)
    infos, positions = buffer.glyph_infos, buffer.glyph_positions
    assert len(infos) == 1 and infos[0].codepoint and positions[0].x_advance > 0, repr(text)
    return font.getGlyphName(infos[0].codepoint)


def add_sequences(root, glyphs, metrics, cmap, layers, palette, review, outline):
    manifest = json.loads((root/'data/font-sources/noto-emoji.json').read_text())
    source = root/manifest['files'][0]['path']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['files'][0]['sha256']
    assert {s for s,_ in COMPOUNDS} <= set(manifest['files'][0]['include_sequences'])
    font = TTFont(source)
    shaping_font = hb.Font(hb.Face(source.read_bytes()))
    shaping_font.set_variations({'wght':400})
    sequences, components, rules, variations = [], [], [], set()
    for canonical, label in COMPOUNDS:
        forms = qualified_forms(root, canonical)
        source_name = source_ligature(font, shaping_font, canonical)
        assert all(source_ligature(font, shaping_font, s) == source_name for s in forms)
        key = canonical.replace('\ufe0f', '')
        name = 'seq.'+'.'.join(f'{ord(c):X}' for c in key)
        seed = int.from_bytes(hashlib.sha256(key.encode()).digest()[:4], 'big')
        pixels = 384
        ink = raster(font.getGlyphSet(location={'wght':400}), source_name, pixels)
        treated, treatment = translate(ink, Settings(strength=1.7, seed=seed))
        ink = np.asarray(treated) < 128
        white = ndimage.binary_fill_holes(ink)
        yy, xx = np.nonzero(white)
        x0,y0,x1,y1 = map(int, (xx.min(),yy.min(),xx.max(),yy.max()))
        factor = 760/max(x1-x0+1,y1-y0+1)
        transform = x0,y0,factor
        advance = round((x1-x0+1)*factor)+100
        glyphs[name] = outline(ink,transform)
        assert glyphs[name].numberOfContours >= treatment['sourceComponents'] + treatment['sourceHoles'], f'Tracing lost a detail in {canonical!r}'
        metrics[name] = advance,50
        layers[name] = []
        colour_info = {}
        masks, colour_ids = (white,ink), (0,1)
        if canonical in COLOURS:
            colour=COLOURS[canonical]
            masks, colour_info = colour_masks(ink, canonical)
            rgb, provenance = read_colour(root, colour)
            if rgb not in palette: palette.append(rgb)
            colour_ids = (0,palette.index(rgb),1)
            colour_info.update(colour=colour,rgb=rgb,**provenance)
        for i,(mask,colour_id) in enumerate(zip(masks,colour_ids)):
            layer = name+f'.layer{i}'
            glyphs[layer] = outline(mask,transform)
            metrics[layer] = advance,50
            layers[name].append((layer,colour_id))
        for c in key:
            cp = ord(c)
            if cp not in cmap:
                component = f'component.{cp:X}'
                cmap[cp] = component
                glyphs[component] = TTGlyphPen(None).glyph()
                metrics[component] = 0,0
                components.append(cp)
        rules.append('sub '+' '.join(cmap[ord(c)] for c in key)+' by '+name+';')
        for form in forms:
            for before, after in zip(form,form[1:]):
                if after == '\ufe0f': variations.add((ord(before),0xFE0F))
        sequences.extend(forms)
        review.append(dict(sequence=canonical, qualificationForms=forms, glyphName=name,
                           label=label, category='compounds', source=str(source.relative_to(root)),
                           sourceGlyph=source_name, sourceWeight=400, sourcePixels=pixels,
                           bounds=[x0,y0,x1,y1], advance=advance, penTreatment=treatment,
                           license='NotoEmoji-OFL.txt', **colour_info))
    return sequences, components, '\n'.join(rules), sorted(variations)
