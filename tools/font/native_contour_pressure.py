"""Isolated fast contour-field experiment for dense, nonjoining drawings.

A smooth map of the native rectangle modulates local curve shape and stroke
compression. For normalized amplitude a<=.06 the displacement has infinity-norm
Lipschitz bound3*pi*a<1, hence the continuous map is injective and keeps native
contour topology. Font curves approximate that map adaptively; sample raster
checks still required. This is experimental and unused by production builders.
"""
import hashlib
import math
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen


class FieldPen(BasePen):
    def __init__(self,gs,bounds,phase,amplitude=.03,tolerance=.2):
        super().__init__(gs)
        if not 0<=amplitude<=.06:raise ValueError('amplitude outside injective field bound')
        self.bounds=bounds;self.phase=phase;self.amplitude=amplitude;self.tolerance=tolerance;self.pen=TTGlyphPen(None)
        self.segments=0

    def field(self,point):
        x,y=point;x0,y0,x1,y1=self.bounds;w=x1-x0;h=y1-y0
        u=(x-x0)/w if w else 0;v=(y-y0)/h if h else 0
        # Clamp only floating boundary noise; off-curve controls may legitimately
        # lie outside ink bounds, so do not clamp their native positions.
        a=self.amplitude
        return (x+w*a*math.sin(math.pi*u)*math.sin(2*math.pi*v+self.phase),
                y+h*a*math.sin(math.pi*v)*math.sin(2*math.pi*u-self.phase))

    def _moveTo(self,p):self.start=p;self.pen.moveTo(self.field(p))
    def _lineTo(self,p):
        # Native straight contours also receive smooth curvature.
        start=self._getCurrentPoint();mid=tuple((a+b)/2 for a,b in zip(start,p));self.quadratic(start,mid,p)
    def _qCurveToOne(self,p1,p2):self.quadratic(self._getCurrentPoint(),p1,p2)
    def quadratic(self,p0,p1,p2,depth=0):
        def bez(t):return tuple((1-t)**2*a+2*t*(1-t)*b+t*t*c for a,b,c in zip(p0,p1,p2))
        q0,q1,q2=self.field(p0),self.field(p1),self.field(p2)
        error=max(math.dist(self.field(bez(t)),tuple((1-t)**2*a+2*t*(1-t)*b+t*t*c for a,b,c in zip(q0,q1,q2))) for t in (.25,.5,.75))
        if error<=self.tolerance or depth>=12:
            self.pen.qCurveTo(q1,q2);self.segments+=1;return
        a=tuple((x+y)/2 for x,y in zip(p0,p1));b=tuple((x+y)/2 for x,y in zip(p1,p2));m=tuple((x+y)/2 for x,y in zip(a,b))
        self.quadratic(p0,a,m,depth+1);self.quadratic(m,b,p2,depth+1)
    def _curveToOne(self,p1,p2,p3):
        raise ValueError('Cubic source requires separate bounded conversion before experiment')
    def _closePath(self):
        self._lineTo(self.start)
        self.pen.closePath()
    def _endPath(self):self.pen.endPath()


def transform(font,name,amplitude=.03):
    gs=font.getGlyphSet();bp=BoundsPen(gs);gs[name].draw(bp)
    if not bp.bounds or bp.bounds[0]==bp.bounds[2] or bp.bounds[1]==bp.bounds[3]:return None
    phase=int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big')/(2**32)*2*math.pi
    pen=FieldPen(gs,bp.bounds,phase,amplitude);gs[name].draw(pen)
    return pen.pen.glyph(),dict(method='injective-native-contour-field-experiment',amplitude=amplitude,lipschitzBound=3*math.pi*amplitude,segments=pen.segments,tolerance=pen.tolerance,limitations=['Nonjoining isolated experiment only','Adaptive quadratic approximation is not exact continuous field','Requires native-counter and visual checks before production'])
