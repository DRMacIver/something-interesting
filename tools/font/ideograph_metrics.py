"""Correct two zero-advance Tangut letters in the pinned UFS source.

These are ordinary ideographic letters, not combining marks. Preserve all
outlines/bearings and use the source's 1000-unit ideograph cell advance.
"""

def repair_ufs_metrics(font):
    assert font['head'].unitsPerEm == 1000
    cmap = font.getBestCmap()
    for cp in (0x17D0B, 0x180DF):
        name = cmap[cp]
        advance, bearing = font['hmtx'][name]
        if advance != 0:
            raise ValueError(f'Pinned source metric changed at {cp:X}: {advance}')
        charstring = font['CFF '].cff.topDictIndex[0].CharStrings[name]
        charstring.decompile()
        # The pinned source explicitly writes a zero width before rmoveto.
        # Keep CFF's intrinsic width consistent with the OpenType hmtx table.
        if charstring.program[0] != -charstring.private.nominalWidthX:
            raise ValueError(f'Pinned CFF width changed at {cp:X}')
        charstring.program[0] = 1000 - charstring.private.nominalWidthX
        font['hmtx'][name] = (1000, bearing)
