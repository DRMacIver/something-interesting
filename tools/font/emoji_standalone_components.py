"""Candidate standalone forms for existing flag, tone and hair GSUB inputs."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from scipy import ndimage as ndi

from emoji_licensed import raster
from emoji_sequence_colour import read_colour
from pen_translate import Settings, translate

ROOT = Path(__file__).resolve().parents[2]
POINTS = [*range(0x1f1e6, 0x1f200), *range(0x1f3fb, 0x1f400), *range(0x1f9b0, 0x1f9b4)]


@lru_cache(maxsize=1)
def sources():
    spec = json.loads((ROOT/'data/font-sources/noto-emoji.json').read_text())['files'][0]
    path = ROOT/spec['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == spec['sha256']
    noto = TTFont(path)
    dad_path = ROOT/'assets/fonts/dad-lettering-unicode.woff2'
    dad = TTFont(dad_path)
    return noto, noto.getGlyphSet(location={'wght':400}), spec, dad, dad.getGlyphSet(), hashlib.sha256(dad_path.read_bytes()).hexdigest()


@lru_cache(maxsize=35)
def prepared(cp):
    assert cp in POINTS
    noto, glyphs, spec, dad, lettering, dad_sha = sources()
    source_name = noto.getBestCmap()[cp]
    if 0x1f1e6 <= cp <= 0x1f1ff:
        letter = chr(ord('A')+cp-0x1f1e6)
        name = dad.getBestCmap()[ord(letter)]
        ink = raster(lettering, name, 512)
        report = dict(requestedStrength=0, appliedStrength=0, fallback=False,
                      treatment='reuse existing hand-lettered capital without further distortion',
                      letter=letter, letteringSource='assets/fonts/dad-lettering-unicode.woff2',
                      letteringSha256=dad_sha, letteringGlyph=name)
    else:
        original = raster(glyphs, source_name, 512)
        treated, report = translate(original, Settings(strength=1.7, seed=cp))
        assert report['appliedStrength'] > 0 and not report['fallback'], hex(cp)
        ink = np.asarray(treated) < 128
    paper = ndi.binary_fill_holes(ink)
    fallback_ink = ink.copy()
    colours, rgbs = [], []
    if 0x1f3fb <= cp <= 0x1f3ff:
        path = ROOT/'output/imagegen/emoji-production/skin-palette-source.json'
        record = json.loads(path.read_text())
        assert hashlib.sha256((ROOT/record['pdf']).read_bytes()).hexdigest() == record['pdfSha256']
        colours.append(paper.copy())
        rgbs.append(record['skinTones'][cp-0x1f3fb])
        report.update(colourRegion='native framed tone swatch; original hatching retained',
                      paletteSource=path.relative_to(ROOT).as_posix(),
                      paletteSha256=hashlib.sha256(path.read_bytes()).hexdigest())
    elif cp == 0x1f9b0:
        # Recolour only the broad solid hair mass. The fine dashed component
        # frame cannot enter this inset; retain it and the black hair border.
        labels, count = ndi.label(ndi.distance_transform_edt(ink) > 9)
        sizes = np.bincount(labels.ravel())
        sizes[0] = 0
        core = labels == sizes.argmax()
        assert count >= 1 and core.sum() > 1000
        assert count == 1 or sorted(sizes[1:])[-1] > 5*sorted(sizes[1:])[-2]
        fill = ndi.binary_dilation(core, iterations=2) & ink
        ink = ink & ~fill
        rgb, provenance = read_colour(ROOT, 'orange')
        colours.append(fill)
        rgbs.append(list(rgb))
        report.update(colourRegion='inset native solid red-hair mass; dashed frame unchanged',
                      hairInsetPixels=9, hairCorePixels=int(core.sum()),
                      monochromeFallback='original solid hair', **provenance)
    report.update(source=spec['path'], sourceSha256=spec['sha256'], sourceGlyph=source_name,
                  sourceWeight=400, sourcePixels=512, rgbs=rgbs, candidateOnly=True,
                  recipeSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    return (paper, *colours, ink), report, fallback_ink


def prepare(key):
    masks, report, _ = prepared(int(key,16))
    return masks, report


def monochrome(key):
    return prepared(int(key,16))[2]
