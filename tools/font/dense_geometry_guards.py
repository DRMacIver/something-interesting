"""Frozen per-component/counter guards for dense native pen candidates."""
import numpy as np
from scipy import ndimage as ndi

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

