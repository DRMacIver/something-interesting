"""Experimental stroke reconstruction from an eight-connected pixel skeleton."""
import numpy as np
from PIL import Image, ImageDraw
from skimage.morphology import skeletonize
from scipy import ndimage as ndi


def paths_from_pixels(pixels):
    points=set(map(tuple,np.argwhere(skeletonize(pixels))))
    graph={p:set() for p in points}
    for y,x in points:
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                q=y+dy,x+dx
                if q==(y,x) or q not in points:continue
                # A diagonal across an existing orthogonal corner is a shortcut,
                # not an additional stroke or tiny counter.
                if dy and dx and ((y+dy,x) in points or (y,x+dx) in points):continue
                graph[y,x].add(q)
    edges={tuple(sorted((p,q))) for p in points for q in graph[p]}
    paths=[]
    def walk(p,q):
        path=[p,q];edges.remove(tuple(sorted((p,q))))
        while len(graph[q])==2:
            nxt=next(n for n in graph[q] if n!=p)
            edge=tuple(sorted((q,nxt)))
            if edge not in edges:break
            edges.remove(edge);path.append(nxt);p,q=q,nxt
        return path
    for p in sorted(points):
        if len(graph[p])==0:paths.append([p])
        elif len(graph[p])!=2:
            for q in sorted(graph[p]):
                if tuple(sorted((p,q))) in edges:paths.append(walk(p,q))
    while edges:
        p,q=min(edges);paths.append(walk(p,q))
    return paths


def rounded_path(path,iterations=2):
    p=np.array(path,dtype=float)
    if len(p)<3:return p
    closed=np.array_equal(p[0],p[-1])
    if closed:p=p[:-1]
    for _ in range(iterations):
        pairs=list(zip(p,np.roll(p,-1,axis=0))) if closed else list(zip(p[:-1],p[1:]))
        q=[] if closed else [p[0]]
        for a,b in pairs:q.extend([.75*a+.25*b,.25*a+.75*b])
        if not closed:q.append(p[-1])
        p=np.array(q)
    if closed:p=np.vstack([p,p[0]])
    return p


def reconstruct(mask,pixel_size=32,width=.9,loop_width=.75,counter_margin=0):
    # The pinned font uses complete square pixels, aligned to this em canvas.
    pixels=mask[pixel_size//2::pixel_size,pixel_size//2::pixel_size]
    assert np.array_equal(mask,np.repeat(np.repeat(pixels,pixel_size,axis=0),pixel_size,axis=1))
    pixels=pixels.copy();labels,count=ndi.label(pixels,structure=np.ones((3,3)))
    dots=[]
    for i in range(1,count+1):
        yy,xx=np.nonzero(labels==i)
        if len(yy)<=4 and np.ptp(yy)<2 and np.ptp(xx)<2:
            dots.append((float(xx.mean()),float(yy.mean()),len(yy)))
            pixels[labels==i]=False
    paths=paths_from_pixels(pixels)
    def in_cycle(index):
        path=paths[index]
        if len(path)<2:return False
        if path[0]==path[-1]:return True
        seen={path[0]};queue=[path[0]]
        while queue:
            point=queue.pop()
            for j,other in enumerate(paths):
                if j==index or len(other)<2:continue
                for a,b in ((other[0],other[-1]),(other[-1],other[0])):
                    if a!=point or b in seen:continue
                    if b==path[-1]:return True
                    seen.add(b);queue.append(b)
        return False
    warped={p:np.asarray(p,dtype=float) for path in paths for p in path}
    if counter_margin:
        holes,count=ndi.label(ndi.binary_fill_holes(mask)&~mask)
        for i in range(1,count+1):
            yy,xx=np.nonzero(holes==i)
            area=len(yy)/pixel_size**2
            if area>3:continue
            center=(np.array([yy.mean(),xx.mean()])+.5)/pixel_size-.5
            minimum=np.sqrt(area/np.pi)+loop_width/2+counter_margin
            for point in warped:
                delta=np.asarray(point)-center;distance=np.linalg.norm(delta)
                if 0<distance<minimum:
                    warped[point]+=delta/distance*min(minimum-distance,.3)
        for point in warped:
            delta=warped[point]-point;distance=np.linalg.norm(delta)
            if distance>.3:warped[point]=np.asarray(point)+delta*.3/distance
    out=Image.new('L' ,(mask.shape[1],mask.shape[0]),0);draw=ImageDraw.Draw(out)
    for x,y,area in dots:
        x=(x+.5)*pixel_size;y=(y+.5)*pixel_size;rr=np.sqrt(area/np.pi)*pixel_size
        draw.ellipse((x-rr,y-rr,x+rr,y+rr),fill=255)
    for index,path in enumerate(paths):
        local_width=loop_width if in_cycle(index) else width
        radius=local_width*pixel_size/2
        points=rounded_path([warped[p] for p in path])*pixel_size+pixel_size/2
        xy=[(float(x),float(y)) for y,x in points]
        if len(points)>1:draw.line(xy,fill=255,width=round(local_width*pixel_size),joint='curve')
        # Round joins and endpoints; single-pixel dots retain their source area.
        rr=pixel_size/np.sqrt(np.pi) if len(points)==1 else radius
        for x,y in xy:draw.ellipse((x-rr,y-rr,x+rr,y+rr),fill=255)
    return np.asarray(out)>127,dict(method='skeleton-paths',strokeWidth=width,loopWidth=loop_width,paths=len(paths),dots=len(dots),counterMargin=counter_margin)
