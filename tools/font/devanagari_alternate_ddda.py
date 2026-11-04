"""Build alternate Sindhi DDDA from native DA and the native implosive stroke.

Retain DDDA's attachment and shaping rules. Fit the DA body into the same
headline-to-stroke band as the existing DDDA so below-vowels have native room.
"""
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from hebrew_marks import bounds
from indic_input_rules import extend_inputs

POINT = 0x11B0A
SELECTOR = 0xE0160


def add_letter(font):
    cmap = font.getBestCmap(); old = cmap[0x97E]; da = cmap[0x926]
    new = 'alternateDdda-deva'
    source = RecordingPen(); font.getGlyphSet()[old].draw(source)
    contours = []; current = []
    for command in source.value:
        current.append(command)
        if command[0] in ('closePath', 'endPath'):
            contours.append(current); current = []
    assert len(contours) == 2 and not current
    # The pinned source's second contour is the separate horizontal stroke.
    from fontTools.pens.boundsPen import BoundsPen
    body = RecordingPen(); body.value = contours[0]
    target_pen = BoundsPen(None); body.replay(target_pen)
    target = target_pen.bounds; original = bounds(font, da)
    sx = (target[2] - target[0]) / (original[2] - original[0])
    sy = (target[3] - target[1]) / (original[3] - original[1])
    dx, dy = target[0] - sx * original[0], target[1] - sy * original[1]
    pen = TTGlyphPen(None)
    font.getGlyphSet()[da].draw(TransformPen(pen, (sx, 0, 0, sy, dx, dy)))
    stroke = RecordingPen(); stroke.value = contours[1]; stroke.replay(pen)
    order = list(font.getGlyphOrder()); font['glyf'][new] = pen.glyph()
    font.setGlyphOrder(order + [new]); font['hmtx'][new] = font['hmtx'][old]
    extend_inputs(font, old, new)
    if not any(t.isUnicode() and t.format == 12 for t in font['cmap'].tables):
        extended = CmapSubtable.newSubtable(12)
        extended.platformID, extended.platEncID, extended.language = 3, 10, 0
        extended.cmap = dict(cmap); font['cmap'].tables.append(extended)
    for table in font['cmap'].tables:
        if table.isUnicode() and table.format == 12: table.cmap[POINT] = new
    uvs = CmapSubtable.newSubtable(14)
    uvs.platformID, uvs.platEncID, uvs.language = 0, 5, 0
    uvs.cmap = {}; uvs.uvsDict = {SELECTOR: [(0x97E, new)]}
    font['cmap'].tables.append(uvs)
