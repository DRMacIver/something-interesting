"""Bounded weighted-centerline union experiment, not a production dependency."""
import numpy as np
from scipy import ndimage as ndi


def union(skeleton,radii,bands=24):
    maximum=float(radii[skeleton].max(initial=0))
    if maximum<=0:return np.zeros_like(skeleton)
    # Fine radius levels protect native small marks; larger strokes need fewer
    # distinct bands. Always quantize inward, then restore all source skeletons.
    split=min(6,maximum)
    levels=np.unique(np.r_[np.linspace(.5,split,bands//2),np.linspace(split,maximum,bands-bands//2)])
    result=skeleton.copy()
    for radius in levels:
        eligible=skeleton&(radii>=radius)
        if not eligible.any():continue
        result|=ndi.distance_transform_edt(~eligible)<=radius
    return result
