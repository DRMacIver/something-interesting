"""Byte-equivalent histogram implementation of the frozen TT geometry guard.

The reference remains the production recipe/reproducibility implementation.
This private warming backend changes validation cost, never pressure geometry.
Exact source hash, errors, component order and result values are preserved.
"""
import hashlib
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from prototype_unifont_lettering import validate_reconstruction as REFERENCE

REFERENCE_SHA256='23bc39876fb5d1d9d97678a2246c56ef9cbb77065420edce0eb6ced05191e70f'


def assert_reference():
    path=Path(__file__).with_name('prototype_unifont_lettering.py')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=REFERENCE_SHA256:
        raise RuntimeError('Frozen geometry reference changed; fast predicate needs a new equivalence review')


def validate_reconstruction(before,after):
    if (type(before) is not np.ndarray or type(after) is not np.ndarray or
            before.dtype!=bool or after.dtype!=bool or before.shape!=after.shape):
        return REFERENCE(before,after)
    a,n=ndi.label(before,structure=np.ones((3,3)))
    b,m=ndi.label(after,structure=np.ones((3,3)))
    old_holes=ndi.binary_fill_holes(before)&~before
    new_holes=ndi.binary_fill_holes(after)&~after
    holes,k=ndi.label(old_holes);_,l=ndi.label(new_holes)
    if (n,k)!=(m,l):raise ValueError('Reconstruction changed topology')
    # Extremely fragmented arbitrary masks retain the reference path rather
    # than allocating a quadratic-size histogram. Scoped font masks are small.
    if (n+1)*(m+1)>4_000_000:return REFERENCE(before,after)
    joint=np.bincount(a.ravel()*(m+1)+b.ravel(),minlength=(n+1)*(m+1)).reshape(n+1,m+1)
    old_area=np.bincount(a.ravel(),minlength=n+1)
    new_area=np.bincount(b.ravel(),minlength=m+1)
    seen=set();ratios=[]
    # Keep the same first-error order as the reference while avoiding N full
    # bitmap scans. Integer histograms reproduce its exact counts.
    for i in range(1,n+1):
        ids=np.flatnonzero(joint[i,1:])+1
        if len(ids)!=1 or int(ids[0]) in seen:
            raise ValueError('Reconstruction merged or lost a component')
        j=int(ids[0]);seen.add(j);ratio=float(new_area[j]/old_area[i]);ratios.append(ratio)
        if not .8<=ratio<=1.2:raise ValueError('Reconstruction changed component area too far')
    hole_area=np.bincount(holes.ravel(),minlength=k+1)
    overlap=np.bincount(holes.ravel(),weights=new_holes.ravel(),minlength=k+1)
    retention=[]
    for i in range(1,k+1):
        fraction=float(overlap[i]/hole_area[i]);retention.append(fraction)
        if fraction<.75:raise ValueError('Reconstruction reduced a counter too far')
    return dict(componentAreaRatios=ratios,counterOverlap=retention)


def install():
    assert_reference()
    import supplemental_adapter
    import supplemental_pressure
    supplemental_adapter.validate_reconstruction=validate_reconstruction
    supplemental_pressure.validate_reconstruction=validate_reconstruction
    return dict(module='tools/font/fast_supplemental_validation.py',sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),referenceSha256=REFERENCE_SHA256,scope='predicate only; original floating pressure geometry and source recipe hash unchanged')
