"""Moving pieces of Watterson's own ink to new places and poses.

dad2.py uses transplant() to reuse Watterson's drawing in panel 2. (Dad in
panel 3 outside the scan now comes from dad3.py.)
"""
import numpy as np


def transplant(source, keep, closing, pivot, target, angle, flip=False,
               scale=(1.0, 1.0), axis=0.0, size=None):
    """Move a piece of Watterson's own ink to a new place and pose.

    `keep` is a polygon around the piece in `source`, `closing` a list of
    segments that close its outline where `keep` cuts it off (so its inside
    can be filled). The piece is optionally flipped top to bottom about
    `pivot`, scaled by `scale` along and across the direction `axis`
    (degrees), turned by `angle` degrees and moved so `pivot` lands on
    `target`. Returns its ink and filled silhouette as masks of `size`, and
    the function mapping source points to their new places.
    """
    from PIL import Image, ImageDraw
    from scipy import ndimage
    mask = Image.new('L', source.size, 0)
    ImageDraw.Draw(mask).polygon(keep, fill=255)
    ink = (np.asarray(source.convert('L')) < 128) & (np.asarray(mask) > 0)
    closed = Image.fromarray(ink)
    for segment in closing:
        ImageDraw.Draw(closed).line(segment, fill=1, width=14)
    silhouette = ndimage.binary_fill_holes(np.asarray(closed))
    def turn(degrees):
        t = np.radians(degrees)
        return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    stretch = turn(axis) @ np.diag(scale) @ turn(-axis)
    forward = turn(angle) @ stretch @ np.diag([1, -1 if flip else 1])
    inverse = np.linalg.inv(forward)
    pivot, target = np.asarray(pivot, float), np.asarray(target, float)
    w, h = size
    xs, ys = zip(*keep)
    reach = max(np.hypot(x - pivot[0], y - pivot[1]) for x, y in keep) * max(scale) + 10
    yy, xx = np.mgrid[max(0, int(target[1] - reach)):min(h, int(target[1] + reach)),
                      max(0, int(target[0] - reach)):min(w, int(target[0] + reach))]
    src = inverse @ np.stack([xx.ravel() - target[0], yy.ravel() - target[1]]) + pivot[:, None]
    out = []
    for layer in (ink, silhouette):
        sampled = ndimage.map_coordinates(layer.astype(float), [src[1], src[0]], order=1, cval=0)
        full = np.zeros((h, w), bool)
        full[yy.ravel(), xx.ravel()] = sampled > 0.5
        out.append(full)
    return out[0], out[1], lambda point: tuple(forward @ (np.asarray(point) - pivot) + target)
