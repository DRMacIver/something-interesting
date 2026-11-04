"""Deterministic, conservative pen treatment for monochrome drawings.

This changes stroke finish and gentle geometry, not expression design. It is
an opt-in prototype: it does not alter the production font or source images.
"""
import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize


@dataclass(frozen=True)
class Settings:
    strength: float = 1.0
    seed: int = 17
    bend: float = .012  # fraction of drawing size, not independent pixel jitter
    pressure: float = .45  # fraction of typical stroke radius
    taper: float = .25
    supersample: int = 3
    boundary_blur: float = .45  # source distance-field smoothing, in pixels


def ink_mask(image):
    rgba = np.asarray(image.convert('RGBA'), dtype=float)
    rgb = rgba[:, :, :3]*rgba[:, :, 3:4]/255 + 255-rgba[:, :, 3:4]
    return rgb.max(axis=2) < 128


def holes(mask):
    # A background border preserves the exterior flood-fill on edge-touching ink.
    # Other input kinds retain the original SciPy semantics unchanged.
    if type(mask) is np.ndarray and mask.dtype == np.bool_ and mask.ndim == 2:
        rows = np.flatnonzero(mask.any(axis=1))
        cols = np.flatnonzero(mask.any(axis=0))
        if not len(rows):
            return 0
        mask = np.pad(mask[rows[0]:rows[-1]+1, cols[0]:cols[-1]+1], 1,
                      constant_values=False)
    labels, _ = ndi.label(ndi.binary_fill_holes(mask) & ~mask)
    # Ignore 1-3 pixel scan pinholes, not meaningful enclosed features.
    return int((np.bincount(labels.ravel())[1:] >= 4).sum())


def same_features(before, after):
    """One-to-one overlapping components; each keeps its holes and bulk.

    This catches broken head contours, merged eyes and lost tiny details.
    It cannot prove that an expression still reads correctly to a person.
    """
    a, na = ndi.label(before)
    b, nb = ndi.label(after)
    if na != nb:
        return False
    used = set()
    for i in range(1, na+1):
        old = a == i
        overlap = set(np.unique(b[old])) - {0}
        if len(overlap) != 1:
            return False
        j = overlap.pop()
        if j in used:
            return False
        used.add(j)
        new = b == j
        if holes(old) != holes(new):
            return False
        if not .5 <= new.sum()/old.sum() <= 1.8:
            return False
    return True


def translate(mask, settings=Settings()):
    """Return antialiased black-on-white image and reproducible audit data."""
    if not np.isfinite(settings.strength) or not 0 <= settings.strength <= 2:
        raise ValueError('strength must be between 0 and 2')
    if settings.supersample not in (2, 3, 4):
        raise ValueError('supersample must be 2, 3 or 4')
    if not all(np.isfinite(v) and v >= 0 for v in
               (settings.bend, settings.pressure, settings.taper, settings.boundary_blur)):
        raise ValueError('bend, pressure, taper and boundary blur must be finite and nonnegative')
    mask = np.asarray(mask, dtype=bool)
    if mask.ndim != 2 or not mask.any():
        raise ValueError('expected a nonempty two-dimensional ink mask')
    yy, xx = np.nonzero(mask)
    size = max(np.ptp(xx)+1, np.ptp(yy)+1)
    # Work with padding so pressure and bending cannot crop the illustration.
    pad = int(np.ceil(size*(settings.bend*settings.strength*2+.02)))+8
    source = np.pad(mask, pad)
    inside = ndi.distance_transform_edt(source)
    outside = ndi.distance_transform_edt(~source)
    # The half-pixel boundary correction avoids bloating thin strokes.
    signed = np.where(source, inside-.5, .5-outside)
    signed = ndi.gaussian_filter(signed, settings.boundary_blur)
    skeleton = skeletonize(source)
    radii = inside[skeleton]
    radius = float(np.percentile(radii, 35))
    neighbors = ndi.convolve(skeleton.astype(int), np.ones((3, 3)), mode='constant')
    endpoints = skeleton & (neighbors == 2) & (inside <= radius*1.8)
    endpoint_distance = (ndi.distance_transform_edt(~endpoints) if endpoints.any()
                         else np.full(source.shape, np.inf))
    taper = np.exp(-np.square(endpoint_distance/max(radius*2.5, 1)))
    h, w = source.shape
    y, x = np.mgrid[:h, :w]
    xn, yn = (x-pad-xx.min())/size, (y-pad-yy.min())/size
    rng = np.random.default_rng(settings.seed)
    phase = rng.uniform(0, 2*np.pi, 6)
    # Low-frequency, correlated fields; no high-frequency edge distress.
    dx = size*settings.bend*(.7*np.sin(2*np.pi*yn+phase[0]) +
                             .3*np.sin(2*np.pi*(xn+yn)+phase[1]))
    dy = size*settings.bend*(.7*np.sin(2*np.pi*xn+phase[2]) +
                             .3*np.sin(2*np.pi*(xn-yn)+phase[3]))
    pressure = radius*settings.pressure*(.65*np.sin(2*np.pi*(1.4*xn+.6*yn)+phase[4]) +
                                        .35*np.sin(2*np.pi*(.4*xn-1.3*yn)+phase[5]))
    pressure -= radius*settings.taper*taper
    scale = settings.supersample
    hy, hx = np.mgrid[:h*scale, :w*scale]/scale + (.5/scale-.5)
    report = {'settings': asdict(settings), 'strokeRadius': radius, 'padding': pad,
              'sourceComponents': int(ndi.label(source)[1]), 'sourceHoles': holes(source)}
    if settings.strength == 0:
        report.update(appliedStrength=0, backoffs=0, fallback=False)
        return Image.fromarray(np.uint8(~source)*255), report
    for backoff in range(7):
        amount = settings.strength * .75**backoff
        low = ndi.map_coordinates(signed, [y+amount*dy, x+amount*dx], order=1,
                                  mode='constant', cval=-pad) + amount*pressure
        candidate = low >= 0
        if not same_features(source, candidate):
            continue
        # Supersample the continuous distance field, then downsample for smooth
        # edges. Validate the actual exported mask too, not only the low-res draft.
        high = ndi.map_coordinates(low, [hy, hx], order=1, mode='constant', cval=-pad)
        alpha = (high >= 0).reshape(h, scale, w, scale).mean(axis=(1, 3))
        pixels = np.uint8(np.rint(255*(1-alpha)))
        if not same_features(source, pixels < 128):
            continue
        if (pixels[0] < 255).any() or (pixels[-1] < 255).any() or (pixels[:, 0] < 255).any() or (pixels[:, -1] < 255).any():
            continue
        report.update(appliedStrength=amount, backoffs=backoff, fallback=False)
        return Image.fromarray(pixels), report
    report.update(appliedStrength=0, backoffs=7, fallback=True)
    return Image.fromarray(np.uint8(~source)*255), report


from pen_translation_cache import cached_translation
translate = cached_translation(translate, __file__)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--box', type=int, nargs=4, metavar=('LEFT', 'TOP', 'RIGHT', 'BOTTOM'))
    parser.add_argument('--strength', type=float, default=1)
    parser.add_argument('--seed', type=int, default=17)
    parser.add_argument('--bend', type=float, default=.012)
    parser.add_argument('--pressure', type=float, default=.45)
    parser.add_argument('--taper', type=float, default=.25)
    parser.add_argument('--boundary-blur', type=float, default=.45)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error('output must differ from source')
    image = Image.open(args.source)
    if args.box:
        l, t, r, b = args.box
        if not 0 <= l < r <= image.width or not 0 <= t < b <= image.height:
            parser.error('box must lie inside the source image')
        image = image.crop(args.box)
    result, record = translate(ink_mask(image), Settings(strength=args.strength, seed=args.seed,
                                                              bend=args.bend, pressure=args.pressure, taper=args.taper, boundary_blur=args.boundary_blur))
    record.update(source=str(args.source), sourceSha256=hashlib.sha256(args.source.read_bytes()).hexdigest(),
                  box=args.box, output=str(args.output), recipeSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output)
    args.output.with_suffix('.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
