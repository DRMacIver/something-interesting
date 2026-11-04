"""Alternate Bargiya BA: native diagonal outline with BA shaping, never RA rules.

L2/22-268R documents the shared isolated form with Assamese RA and the shared
conjunct behavior with BA. Expand input rules only; existing outputs are kept.
"""
from copy import deepcopy
from indic_input_rules import extend_inputs
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

POINT = 0x11DF1
SELECTOR = 0xE0150


def add_letter(font):
    cmap = font.getBestCmap()
    old, drawing = cmap[0x9AC], cmap[0x9F0]
    new = 'alternateBa-beng'
    assert POINT not in cmap and font['hmtx'][old] == font['hmtx'][drawing]
    order = list(font.getGlyphOrder())
    font['glyf'][new] = deepcopy(font['glyf'][drawing])
    font['hmtx'][new] = font['hmtx'][old]
    font.setGlyphOrder(order + [new])

    extend_inputs(font, old, new)
    if not any(t.isUnicode() and t.format == 12 for t in font['cmap'].tables):
        extended = CmapSubtable.newSubtable(12)
        extended.platformID, extended.platEncID, extended.language = 3, 10, 0
        extended.cmap = dict(cmap)
        font['cmap'].tables.append(extended)
    for table in font['cmap'].tables:
        if table.isUnicode() and table.format == 12: table.cmap[POINT] = new
    uvs = CmapSubtable.newSubtable(14)
    uvs.platformID, uvs.platEncID, uvs.language = 0, 5, 0
    uvs.cmap = {}; uvs.uvsDict = {SELECTOR: [(0x9AC, new)]}
    font['cmap'].tables.append(uvs)
