"""Repair the source isolobal arrow's missing left head before pen adaptation."""
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen


def repair_isolobal(font):
    name=font.getBestCmap()[0x1F8D8]
    drawing=DecomposingRecordingPen(font.getGlyphSet())
    font.getGlyphSet()[name].draw(drawing)
    pen=TTGlyphPen(None);changed=0
    # Mirror the source's right head, connecting directly into the existing
    # shaft contour. Keep the lobe and its counter, with no overlapping paths.
    left=[(189,318),(224,279),(262,197),(218,197),(138,290),(51,334),
          (51,356),(138,400),(218,493),(262,493),(224,411),(189,372)]
    for operation,points in drawing.value:
        if operation=='lineTo' and points==((51,318),):
            for point in left:pen.lineTo(point)
            changed+=1
        elif operation=='lineTo' and points==((51,372),):
            changed+=1
        else:getattr(pen,operation)(*points)
    assert changed==2, 'Pinned source isolobal shaft changed'
    font['glyf'][name]=pen.glyph()
