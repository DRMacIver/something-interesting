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
        self.displays={}
        self.gs=font.getGlyphSet();self.em=font['head'].unitsPerEm

    def __call__(self,resolution=1024,viewport=None):
        current=self.font['glyf'][self.name]
        if current is not self.object:
            self.object=current;self.displays.clear()
            bp=BoundsPen(self.gs);self.gs[self.name].draw(bp);self.bounds=bp.bounds
            if self.bounds:
                pen=SVGPathPen(self.gs);self.gs[self.name].draw(pen);self.commands=pen.getCommands()
        if not self.bounds:return None
        scale=resolution/self.em;x0,y0,x1,y1=self.bounds
        left=int(np.floor(x0*scale))-24;top=int(np.ceil(y1*scale))+24
        width=int(np.ceil(x1*scale))-left+24;height=top-int(np.floor(y0*scale))+24
        if viewport is not None:left,top,scale,width,height=viewport
        baseleft=math.floor(left);basetop=math.floor(top)
        key=(baseleft,basetop,scale,width,height)
        if key not in self.displays:
            svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><path d="{self.commands}" transform="translate({-baseleft} {basetop}) scale({scale} {-scale})"/></svg>'
            with pymupdf.open(stream=svg.encode(),filetype='svg') as doc:
                with pymupdf.open('pdf',doc.convert_to_pdf()) as pdf:
                    self.displays[key]=pdf[0].get_displaylist()
        dx=left-baseleft;dy=top-basetop
        matrix=pymupdf.Matrix(1,1).pretranslate(-dx,dy)
        pix=self.displays[key].get_pixmap(matrix=matrix,alpha=False)
        rgb=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3)
        rendered=rgb.max(axis=2)<128
        mask=np.zeros((height,width),dtype=bool)
        x0=max(0,pix.x);y0=max(0,pix.y);x1=min(width,pix.x+pix.width);y1=min(height,pix.y+pix.height)
        if x1>x0 and y1>y0:mask[y0:y1,x0:x1]=rendered[y0-pix.y:y1-pix.y,x0-pix.x:x1-pix.x]
        return mask,(left,top,scale)
