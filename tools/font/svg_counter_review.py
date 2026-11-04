"""Check fine source counters after polygon simplification and font rounding."""
import numpy as np
from scipy import ndimage as ndi
from fontTools.pens.pointInsidePen import PointInsidePen


def review_counters(mask,transform,glyph,*,max_small_losses=0,small_area=64):
    """Allow bounded subpixel loss only when every larger counter still exists.

    Areas are source-raster pixels, before scaling to font units. The ordinary
    pen guard ignores holes below four pixels. A permitted tiny-counter loss
    must also retain a distinct compiled hole for each larger source counter.
    """
    labels,_=ndi.label(ndi.binary_fill_holes(mask)&~mask)
    sizes=np.bincount(labels.ravel())
    meaningful=np.flatnonzero(sizes[1:]>=4)+1
    components=ndi.label(mask)[1]
    lost=components+len(meaningful)-glyph.numberOfContours
    assert 0<=lost<=max_small_losses,('Contour count changed',components,len(meaningful),glyph.numberOfContours)
    if not lost:return dict(smallCounterLosses=0,largeCountersChecked=0)
    polygons=[];start=0
    for last in glyph.endPtsOfContours:
        points=list(glyph.coordinates[start:last+1]);start=last+1
        area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1]))
        assert area!=0,'Zero-area contour is not a preserved feature'
        polygons.append((area,points))
    outer_sign=max(polygons,key=lambda item:abs(item[0]))[0]
    assert sum(area*outer_sign>0 for area,_ in polygons)==components,'Compiled component loss'
    counters=[points for area,points in polygons if area*outer_sign<0]
    counter_areas=[abs(area) for area,_ in polygons if area*outer_sign<0]
    x0,y0,factor=transform;used=set();checked=0
    slices=ndi.find_objects(labels)
    for index in meaningful:
        if sizes[index]<small_area:continue
        sy,sx=slices[index-1]
        local=np.pad(labels[sy,sx]==index,1)
        y,x=np.unravel_index(ndi.distance_transform_edt(local).argmax(),local.shape)
        y+=sy.start-1;x+=sx.start-1
        point=((x-x0)*factor+50,760-(y-y0)*factor)
        matches=[]
        for j,points in enumerate(counters):
            pen=PointInsidePen(None,point);pen.moveTo(points[0])
            for p in points[1:]:pen.lineTo(p)
            pen.closePath()
            if pen.getResult():matches.append(j)
        # An island's enclosed region lies inside the ocean counter too.
        # Match its innermost containing contour; distinct source regions
        # must still map to distinct compiled counters.
        if len(matches)>1:matches=[min(matches,key=lambda j:counter_areas[j])]
        assert len(matches)==1 and matches[0] not in used,('Lost or merged source counter',int(sizes[index]),point)
        used.add(matches[0]);checked+=1
    return dict(smallCounterLosses=int(lost),largeCountersChecked=checked,
                smallAreaLimit=int(small_area),smallAreaLimitFontUnits=small_area*factor**2)
