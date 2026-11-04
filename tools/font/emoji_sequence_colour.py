"""Reviewed colour masks for exact lime and brown-mushroom sequences."""
import hashlib
import json
import numpy as np
from scipy import ndimage

COLOURS = {'🍋\u200d🟩':'green', '🍄\u200d🟫':'brown'}


def colour_masks(ink, sequence):
    white=ndimage.binary_fill_holes(ink)
    interiors,count=ndimage.label(white & ~ink)
    sizes=np.bincount(interiors.ravel());sizes[0]=0
    main=interiors==sizes.argmax()
    if sequence=='🍋\u200d🟩':
        # The curved rind is the largest enclosed region; the five citrus
        # sections remain white. Paint under all ink to avoid pale seams.
        assert count==6 and main.sum()>white.sum()*.15
        return (white, main | ink, ink), dict(colourRegion='largest enclosed rind',whiteRegions=5)
    assert sequence=='🍄\u200d🟫'
    # The donor encodes the brown cap as solid black. Keep the original glyph
    # for monochrome fallback, but open a brown interior inside that silhouette
    # in the COLR drawing. The large lower hole is the stem; the two small upper
    # holes are highlights. Derive the dividing row from this pinned anatomy.
    assert count==3 and main.sum()>sizes.sum()*.8
    stem_top=np.where(main)[0].min()
    rows=np.indices(ink.shape)[0]
    cap=ndimage.binary_fill_holes(ink & (rows<stem_top))
    highlights=(white & ~ink) & ~main
    assert not (highlights & ~cap).any()
    ys,xs=np.where(ink)
    border=max(2,round(max(np.ptp(ys),np.ptp(xs))*.025))
    core=ndimage.distance_transform_edt(cap)>border
    assert core.sum()>cap.sum()*.5
    final_ink=ink & ~core
    fill=cap & ~highlights
    assert not (fill & main).any()
    return (white,fill,final_ink),dict(colourRegion='solid donor cap opened inside an inset border',
        capBorderPixels=border,stemTop=int(stem_top),highlightPixels=int(highlights.sum()),
        monochromeFallback='original solid cap',whiteRegions=3)


def read_colour(root, colour):
    filename='apple-palette-source.json' if colour=='green' else 'heart-palette-source.json'
    path=root/'output/imagegen/emoji-production'/filename
    record=json.loads(path.read_text())
    assert hashlib.sha256((root/record['pdf']).read_bytes()).hexdigest()==record['pdfSha256']
    sample=next(s for s in record['samples'] if s['colour']==colour)
    if 'reusedPalette' in record:
        reused=record['reusedPalette'];original=root/reused['path']
        assert hashlib.sha256(original.read_bytes()).hexdigest()==reused['sha256']
        assert sample in json.loads(original.read_text())['samples']
    return tuple(sample['rgb']),dict(paletteSource=str(path.relative_to(root)),
        paletteSha256=hashlib.sha256(path.read_bytes()).hexdigest())
