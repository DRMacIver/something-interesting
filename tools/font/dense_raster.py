"""Dense experimental raster cache: draw curves once across validation phases.
Pixel semantics intentionally match supplemental_pressure.raster exactly.
"""
import math
import numpy as np
import pymupdf
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen


class GlyphRaster:
    def __init__(self,font,name):
        self.font=font;self.name=name;self.object=None;self.commands=None;self.bounds=None
        self.gs=font.getGlyphSet();self.em=font['head'].unitsPerEm

    def __call__(self,resolution=1024,viewport=None):
        current=self.font['glyf'][self.name]
        if current is not self.object:
            self.object=current
            bp=BoundsPen(self.gs);self.gs[self.name].draw(bp);self.bounds=bp.bounds
            if self.bounds:
                pen=SVGPathPen(self.gs);self.gs[self.name].draw(pen);self.commands=pen.getCommands()
        if not self.bounds:return None
        scale=resolution/self.em;x0,y0,x1,y1=self.bounds
        left=int(np.floor(x0*scale))-24;top=int(np.ceil(y1*scale))+24
        width=int(np.ceil(x1*scale))-left+24;height=top-int(np.floor(y0*scale))+24
        if viewport is not None:left,top,scale,width,height=viewport
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><path d="{self.commands}" transform="translate({-left} {top}) scale({scale} {-scale})"/></svg>'
        with pymupdf.open(stream=svg.encode(),filetype='svg') as doc:
            with pymupdf.open('pdf',doc.convert_to_pdf()) as pdf:
                pix=pdf[0].get_pixmap(alpha=False)
                rgb=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3)
                mask=rgb.max(axis=2)<128
        return mask,(left,top,scale)
