"""Light pen variation for supplemental alphabet outlines, without case folding.

A small smooth deformation preserves counters/stem relationships and leaves
advances and shaping anchors intact. It is a provisional visual adaptation,
not a replacement for historical/phonetic review of the source letterforms.
"""
import math
from fontTools.pens.basePen import BasePen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.boundsPen import BoundsPen


class InkPen(BasePen):
    def __init__(self, target):
        super().__init__(None)
        self.target = target
        self.previous = None

    def warp(self, p):
        x,y=p
        return (round(x+3*math.sin(y/83)*math.sin(x/129)),
                round(y+3*math.sin(x/91)*math.sin(y/137)))

    def _moveTo(self, p):
        self.target.moveTo(self.warp(p)); self.previous=p

    def _lineTo(self, p):
        a=self.previous
        for i in range(1, (steps:=max(1,math.ceil(math.dist(a,p)/60)))+1):
            self.target.lineTo(self.warp(tuple(a[k]+(p[k]-a[k])*i/steps for k in (0,1))))
        self.previous=p

    def _qCurveToOne(self, control, p):
        self.target.qCurveTo(self.warp(control),self.warp(p)); self.previous=p

    def _curveToOne(self, a,b,p):
        self.target.curveTo(self.warp(a),self.warp(b),self.warp(p));self.previous=p

    def _closePath(self): self.target.closePath()
    def _endPath(self): self.target.endPath()


def adapt(font, points):
    glyphs=font.getGlyphSet()
    cmap=font.getBestCmap()
    # Capture every original component before changing any shared glyph.
    drawings={}
    for name in {cmap[cp] for cp in points if cp in cmap}:
        pen=DecomposingRecordingPen(glyphs);glyphs[name].draw(pen)
        drawings[name]=pen
    for name,drawing in drawings.items():
        advance,_=font['hmtx'][name]
        if 'glyf' in font:
            pen=TTGlyphPen(None);drawing.replay(InkPen(pen))
            glyph=pen.glyph();font['glyf'][name]=glyph
            glyph.recalcBounds(font['glyf'])
            bearing=getattr(glyph,'xMin',0)
        else:
            top=font['CFF '].cff.topDictIndex[0]
            original=top.CharStrings[name]
            pen=T2CharStringPen(advance,None);drawing.replay(InkPen(pen))
            charstring=pen.getCharString(private=original.private,globalSubrs=original.globalSubrs)
            top.CharStrings[name]=charstring
            bounds=BoundsPen(None);drawing.replay(InkPen(bounds))
            bearing=round(bounds.bounds[0]) if bounds.bounds else 0
        font['hmtx'][name]=(advance,bearing)
