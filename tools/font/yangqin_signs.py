"""Yangqin tempo signs constructed from the pinned WenKai Suzhou strokes.

L2/24-071R3 page 4 documents two/three uprights and a cross on a shared
baseline. No outlines are extracted from the proposal's sample font.
"""
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

POINTS = {0x16FF4, 0x16FF5, 0x16FF6}


def add_signs(font):
    cmap = font.getBestCmap()
    assert not POINTS & cmap.keys()
    glyphs = font.getGlyphSet()
    base = cmap[0x3026]
    drawing = DecomposingRecordingPen(glyphs)
    glyphs[base].draw(drawing)
    # Retain the original baseline, bridging over its single upright. These
    # exact junctions deliberately pin the splice to the reviewed source.
    start = drawing.value.index(('lineTo', ((460, 353),)))
    end = drawing.value.index(('lineTo', ((528, 355),)))
    assert end-start == 6
    baseline = drawing.value[:start+1] + drawing.value[end:]
    order = list(font.getGlyphOrder())
    names = []
    for cp, source in [(0x16FF4,0x3022),(0x16FF5,0x3023),(0x16FF6,0x3024)]:
        pen = TTGlyphPen(None)
        for op, args in baseline:
            getattr(pen,op)(*args)
        strokes = DecomposingRecordingPen(glyphs)
        glyphs[cmap[source]].draw(strokes)
        part = RecordingPen()
        for op,args in strokes.value:
            getattr(part,op)(*args)
            if op not in ('closePath','endPath'):
                continue
            bounds = BoundsPen(glyphs); part.replay(bounds)
            x0,y0,x1,y1 = bounds.bounds
            # Fit each native upright to the short raised 3026 register;
            # overlap its foot with the slightly rising native baseline.
            scale = .53 if cp == 0x16FF6 else .44
            bottom = 320 + ((x0+x1)/2-58)*.0334
            part.replay(TransformPen(pen,(1,0,0,scale,0,bottom-y0*scale)))
            part = RecordingPen()
        name = f'yangqin{cp:X}'
        glyph = pen.glyph()
        # Strokes deliberately meet and overlap. Preserve nonzero filling.
        if len(glyph.flags): glyph.flags[0] |= 0x40
        font['glyf'][name] = glyph
        glyph.recalcBounds(font['glyf'])
        font['hmtx'][name] = (font['hmtx'][base][0], glyph.xMin)
        if 'vmtx' in font: font['vmtx'][name] = font['vmtx'][base]
        names.append(name)
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format == 12:
                table.cmap[cp] = name
    font.setGlyphOrder(order + names)
