"""Provisional right-side Vietnamese reading marks from licensed WenKai ink.

L2/17-373R pp. 4–5 identifies the usual forms with U+4E87 and U+21FE8.
These are spacing combining marks (Mc, class 6). Positive advances reserve
room beside the base, including when browser fallback crosses font shards.
Historical base-specific mergers and above/below variants remain unimplemented.
"""
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

POINTS = {0x16FF0, 0x16FF1}


def add_marks(font):
    cmap = font.getBestCmap()
    assert not POINTS & cmap.keys()
    glyphs = font.getGlyphSet()
    order = list(font.getGlyphOrder())
    names = []
    for cp, source, height, advance in [
        (0x16FF0, 0x4E87, 460, 340),
        (0x16FF1, 0x21FE8, 350, 220),
    ]:
        drawing = DecomposingRecordingPen(glyphs)
        glyphs[cmap[source]].draw(drawing)
        bounds = BoundsPen(None); drawing.replay(bounds)
        x0, y0, x1, y1 = bounds.bounds
        # Uniform scaling preserves the donor's stroke proportions. Centre
        # within the reserved side space and the Han mid-height register.
        scale = min(height / (y1-y0), (advance-60) / (x1-x0))
        pen = TTGlyphPen(None)
        drawing.replay(TransformPen(pen, (scale,0,0,scale,
            (advance-(x1-x0)*scale)/2-x0*scale,
            450-(y0+y1)*scale/2)))
        name = f'vietnamese{cp:X}'
        glyph = pen.glyph()
        font['glyf'][name] = glyph
        glyph.recalcBounds(font['glyf'])
        font['hmtx'][name] = (advance,glyph.xMin)
        if 'vmtx' in font: font['vmtx'][name] = font['vmtx'][cmap[source]]
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format == 12:
                table.cmap[cp] = name
        names.append(name)
    font.setGlyphOrder(order+names)
