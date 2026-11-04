"""Frozen dense-script native-centerline pen kernel.

Median pen radii are spatially smoothed, tapered and capped by native counter
clearance. Every native centerline pixel is retained; no branch is pruned.
Accepted direction reviewed in docs/dense-skeleton-review.json. This module is
independent of the first15 supplemental-production pressure recipe hashes.
"""
import math
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import medial_axis
from prototype_unifont_lettering import topology

def validate_reconstruction(before,after):
    # Label once and compute all component/counter overlaps with histograms.
    # This is the same guard as the reviewed prototype, avoiding a full mask
    # scan for every tiny CJK component and counter.
    a,n=ndi.label(before,structure=np.ones((3,3)))
    b,m=ndi.label(after,structure=np.ones((3,3)))
    old_holes=ndi.binary_fill_holes(before)&~before
    new_holes=ndi.binary_fill_holes(after)&~after
    holes,k=ndi.label(old_holes);_,l=ndi.label(new_holes)
    if (n,k)!=(m,l):raise ValueError('Changed topology')
    joint=np.bincount((a.ravel()*(m+1)+b.ravel()),minlength=(n+1)*(m+1)).reshape(n+1,m+1)
    old_area=np.bincount(a.ravel(),minlength=n+1)
    new_area=np.bincount(b.ravel(),minlength=m+1)
    seen=set();ratios=[]
    for i in range(1,n+1):
        ids=np.flatnonzero(joint[i,1:])+1
        if len(ids)!=1 or int(ids[0]) in seen:raise ValueError('Merged or lost native component')
        j=int(ids[0]);seen.add(j);ratio=float(new_area[j]/old_area[i]);ratios.append(ratio)
        if not .75<=ratio<=1.20:raise ValueError('Component mass outside finer-ink bounds')
    hole_area=np.bincount(holes.ravel(),minlength=k+1)
    overlap=np.bincount(holes.ravel(),weights=new_holes.ravel(),minlength=k+1)
    retention=(overlap[1:]/hole_area[1:]).tolist()
    if any(value<.75 for value in retention):raise ValueError('Counter retention below75percent')
    return dict(componentAreaRatios=ratios,counterOverlap=retention,minimumComponentAreaRatio=.75)


def reink_candidates(mask,seed):
    skeleton,dist=medial_axis(mask,return_distance=True,rng=0)
    distance_to_skeleton,nearest_skeleton=ndi.distance_transform_edt(~skeleton,return_indices=True)
    labels,count=ndi.label(mask,structure=np.ones((3,3)))
    y,x=np.mgrid[:mask.shape[0],:mask.shape[1]]
    phase=seed/2**32*math.tau
    wave=.65*np.sin(x/157+y/211+phase)+.35*np.sin(x/269-y/173-phase)
    background=medial_axis(~mask,rng=0)
    clearance=ndi.distance_transform_edt(~background)
    maxradius=dist+np.maximum(0,clearance-dist)*.25
    baseline=np.zeros(mask.shape)
    for label in range(1,count+1):
        points=skeleton&(labels==label)
        if points.any():baseline[points]=np.median(dist[points])
    for strength in (1,.75,.5,.25,.125):
        radius=np.maximum(.75,dist*(1-strength)+baseline*strength*(1+.18*wave))
        # Smooth native pressure along nearby centerlines, then preserve
        # tapering tips and narrow counter clearances with local caps.
        weights=ndi.gaussian_filter(skeleton.astype(float),5)
        smoothed=ndi.gaussian_filter(radius*skeleton,5)/np.maximum(weights,1e-9)
        radius=np.minimum(smoothed,maxradius)
        radius=np.minimum(radius,np.maximum(dist*1.35,baseline*.45))
        # Re-ink all native centerlines as overlapping round pen disks. Small
        # terminal fans remain in place; no semantic tick is pruned.
        # Radius field is smooth along native centerlines; nearest-centerline
        # EDT reconstructs its envelope without stamping thousands of disks.
        new=distance_to_skeleton <= radius[tuple(nearest_skeleton)]-.35
        new|=skeleton
        try:checks=validate_reconstruction(mask,new)
        except ValueError:continue
        yield new,{'strength':strength,'sourceTopology':topology(mask),'skeletonPixels':int(skeleton.sum()),'skeletonRetained':bool(np.all(new[skeleton])),'branchesPruned':0,**checks}



