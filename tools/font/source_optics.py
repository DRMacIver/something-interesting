"""Source-specific optical size without moving native curves or anchors.

Changing the em preserves all design-space geometry, OpenType attachments and
advance proportions, while increasing the complete native field at dialogue
size. Applied only to already renamed browser derivatives, never pinned input.
"""
from pathlib import Path

SCALES = {'ArefRuqaa-Regular.ttf': 1.16, 'Gaegu-Regular.ttf': 1.16,
          'DadTolong.ttf': 1.10, 'NotoSerifOldUyghur-Regular.ttf': 1.35}


def apply(font, source):
    scale = SCALES.get(Path(source).name, 1)
    if scale == 1:
        return None
    original = font['head'].unitsPerEm
    adjusted = round(original / scale)
    if not 16 <= adjusted <= 16384:
        raise ValueError('Optical em outside OpenType range')
    font['head'].unitsPerEm = adjusted
    return {'method': 'optical-em', 'originalUnitsPerEm': original,
            'unitsPerEm': adjusted, 'scale': original / adjusted}
