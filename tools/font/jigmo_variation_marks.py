"""Keep the Jigmo family's native CJK marks with supplementary IVS bases.

All three donors are from the same pinned CC0 archive. Preserve native glyphs,
metrics, classes and hinting; no new mark drawings or anchors are invented.
"""
from copy import deepcopy

POINTS=frozenset([*range(0x302a,0x3030),0x3099,0x309a])


def add_marks(font,donor,points=POINTS):
    points=set(points)
    assert points<=POINTS
    assert font['head'].unitsPerEm==donor['head'].unitsPerEm
    for tag in ['fpgm','prep','cvt ']:
        assert font.getTableData(tag)==donor.getTableData(tag),f'Incompatible donor hinting: {tag}'
    source=donor.getBestCmap();existing=font.getBestCmap()
    assert not points&existing.keys(),'Do not replace native drawings'
    order=list(font.getGlyphOrder())
    for cp in sorted(points):
        original=source[cp];name=f'ivsMark.u{cp:X}'
        assert name not in order
        glyph=donor['glyf'][original]
        assert not glyph.isComposite(),'Review component/hint closure before importing a composite'
        font['glyf'][name]=deepcopy(glyph)
        font['hmtx'][name]=donor['hmtx'][original]
        font['vmtx'][name]=donor['vmtx'][original]
        font['GDEF'].table.GlyphClassDef.classDefs[name]=donor['GDEF'].table.GlyphClassDef.classDefs[original]
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format in {4,12}:table.cmap[cp]=name
        order.append(name)
    font.setGlyphOrder(order)
    return points
