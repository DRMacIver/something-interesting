"""Isolated vector normal contrast experiment for dense nonjoining scripts.

Directional offsets narrow heavy vertical stems and broaden thin horizontals.
A KD-tree of native contour samples limits inward displacement to20% of local
opposing stroke width, and outward displacement to12.5% of the opposing gap.
It removes no native contour branches. Geometry/visual guards remain required.
Unused by production builders.
"""
import math
import numpy as np
from scipy.spatial import cKDTree
from skimage.measure import approximate_polygon
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen


class Contours(BasePen):
    def __init__(self,gs,step):super().__init__(gs);self.step=step;self.contours=[];self.current=[]
    def _moveTo(self,p):self.current=[p]
    def _lineTo(self,p):
        old=self._getCurrentPoint();n=max(1,math.ceil(math.dist(old,p)/self.step));self.current.extend(tuple(a+(b-a)*i/n for a,b in zip(old,p)) for i in range(1,n+1))
    def _qCurveToOne(self,p1,p2):
        p0=self._getCurrentPoint();n=max(2,math.ceil((math.dist(p0,p1)+math.dist(p1,p2))/self.step));self.current.extend(tuple((1-t)**2*a+2*t*(1-t)*b+t*t*c for a,b,c in zip(p0,p1,p2)) for t in np.linspace(0,1,n+1)[1:])
    def _curveToOne(self,*points):raise ValueError('Native TrueType experiment only')
    def _closePath(self):
        self._lineTo(self.current[0]);p=np.asarray(self.current[:-1]);keep=np.linalg.norm(p-np.roll(p,1,axis=0),axis=1)>.01;p=p[keep]
        if len(p)>=3:self.contours.append(p)
        self.current=[]
    def _endPath(self):self._closePath()


def transform(font,name,amount=.01,mode="balanced"):
    em=font['head'].unitsPerEm;gs=font.getGlyphSet();pen=Contours(gs,em*.01);gs[name].draw(pen)
    if not pen.contours:return None
    points=np.concatenate(pen.contours);normals=[]
    for p in pen.contours:
        tangent=np.roll(p,-1,axis=0)-np.roll(p,1,axis=0);length=np.linalg.norm(tangent,axis=1);normals.append(np.column_stack((-tangent[:,1],tangent[:,0]))/np.maximum(length[:,None],1e-6))
    normal=np.concatenate(normals);tree=cKDTree(points);_,ids=tree.query(points,k=min(64,len(points)))
    vectors=points[ids]-points[:,None,:];projection=np.sum(vectors*normal[:,None,:],axis=2);lateral=np.abs(vectors[:,:,0]*normal[:,None,1]-vectors[:,:,1]*normal[:,None,0]);opposing=np.sum(normal[ids]*normal[:,None,:],axis=2)<-.4
    aligned=opposing&(lateral<em*.012)
    stroke=np.min(np.where(aligned&(projection<-em*.001),-projection,np.inf),axis=1)
    gap=np.min(np.where(aligned&(projection>em*.001),projection,np.inf),axis=1)
    if mode=='inward-median':
        widths=stroke[np.isfinite(stroke)&(stroke>em*.004)&(stroke<em*.25)]
        median=float(np.median(widths)) if len(widths) else em*.025
        desired=np.maximum(0,np.where(np.isfinite(stroke),stroke,median)-median)*.5
        delta=-np.minimum(desired*.6,em*amount)*normal[:,0]**2
    elif mode=='balanced':delta=em*amount*(normal[:,1]**2-normal[:,0]**2)
    else:raise ValueError('Unknown contrast mode')
    delta*=1+.10*np.sin(points[:,0]/em*7+points[:,1]/em*5)
    delta=np.maximum(delta,-stroke*.2);delta=np.minimum(delta,gap*.125)
    moved=points+normal*delta[:,None]
    target=TTGlyphPen(None);offset=0
    for contour in pen.contours:
        n=len(contour);p=moved[offset:offset+n];offset+=n
        # Remove collinear sampling points before constructing round joins.
        p=approximate_polygon(np.concatenate([p,p[:1]]),tolerance=em*.00035)[:-1]
        if len(p)<3:continue
        incoming=p-np.roll(p,1,axis=0);outgoing=np.roll(p,-1,axis=0)-p
        li=np.linalg.norm(incoming,axis=1);lo=np.linalg.norm(outgoing,axis=1)
        radius=np.minimum(np.minimum(li,lo)*.15,em*.002)
        entry=p-incoming/np.maximum(li[:,None],1e-6)*radius[:,None]
        exit=p+outgoing/np.maximum(lo[:,None],1e-6)*radius[:,None]
        target.moveTo(tuple(exit[-1]))
        for a,b,c in zip(entry,p,exit):target.lineTo(tuple(a));target.qCurveTo(tuple(b),tuple(c))
        target.closePath()
    return target.glyph(),dict(method='native-directional-normal-contrast-experiment',amount=amount,mode=mode,nativeSamples=len(points),maximumDisplacement=float(np.max(abs(delta))),strokeLimited=int(np.sum(delta<0)),gapLimitFraction=.125,strokeLimitFraction=.2,limitations=['Native TrueType clockwise outer contours assumed','Nearest opposing contour samples approximate local stroke/gap widths','Raster/topology and actual-size review required; not production'])
