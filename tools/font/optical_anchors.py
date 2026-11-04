"""Place accents over the local top/bottom of a handwritten letter.

An outline's full bounding box loses its lean. Use the horizontal extent of
its upper/lower fifth; flattening is only for attachment coordinates and never
changes the letter outline.
"""
from fontTools.pens.basePen import BasePen


class ProfilePen(BasePen):
    def __init__(self, glyphs):
        super().__init__(glyphs)
        self.edges = []
        self.start = None

    def _moveTo(self, point):
        self.start = point

    def _lineTo(self, point):
        self.edges.append((self._getCurrentPoint(), point))

    def _curveToOne(self, p1, p2, p3):
        p0 = self._getCurrentPoint()
        previous = p0
        for i in range(1, 33):
            t = i / 32
            u = 1-t
            point = tuple(u**3*p0[j]+3*u*u*t*p1[j]+3*u*t*t*p2[j]+t**3*p3[j] for j in (0, 1))
            self.edges.append((previous, point))
            previous = point

    def _closePath(self):
        if self.start is not None:
            self.edges.append((self._getCurrentPoint(), self.start))
        self.start = None

    def _endPath(self):
        self.start = None


def accent_centres(glyph, glyphs, box, top_fraction=.2):
    x0, y0, x1, y1 = box
    middle = (x0+x1)/2
    if y1 <= y0:
        return middle, middle
    pen = ProfilePen(glyphs)
    glyph.draw(pen)

    def centre(low, high):
        xs = []
        for (a, b), (c, d) in pen.edges:
            if b == d:
                if low <= b <= high:
                    xs.extend((a, c))
                continue
            first, last = sorted(((low-b)/(d-b), (high-b)/(d-b)))
            first, last = max(0, first), min(1, last)
            if first <= last:
                xs.extend((a+(c-a)*first, a+(c-a)*last))
        return (min(xs)+max(xs))/2 if xs else middle

    height = y1-y0
    return centre(y1-height*top_fraction, y1), centre(y0, y0+height*.2)
