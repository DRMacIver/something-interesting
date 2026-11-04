"""Preserve positive-area flag contours after font-unit rounding."""
from fontTools.pens.ttGlyphPen import TTGlyphPen

def clean_flag_outline(mask, transform, outline):
    original = outline(mask, transform)
    pen = TTGlyphPen(None)
    start = 0
    removed = 0
    for last in original.endPtsOfContours:
        points = list(original.coordinates[start:last+1])
        start = last+1
        area2 = sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points, points[1:]+points[:1]))
        # Rounding can collapse antialias slivers. Such contours have no
        # drawable area; omit them without deleting any positive-area outline.
        if area2 == 0:
            removed += 1
            continue
        pen.moveTo(points[0])
        for point in points[1:]:
            pen.lineTo(point)
        pen.closePath()
    return pen.glyph(), removed

