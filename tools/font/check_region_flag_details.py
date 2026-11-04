"""Preflight regional flag colour islands through warping and font rounding.

This candidate check does not register artwork or replace actual-strip review.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from prototype_region_flags import prepare, EXAMPLES, ROOT, label
from build_emoji import outline
from skimage.measure import find_contours, approximate_polygon


def inspect(region):
    (paper, *masks, ink), report = prepare(region)
    ys, xs = np.nonzero(paper)
    transform = xs.min(), ys.min(), 760 / max(np.ptp(xs) + 1, np.ptp(ys) + 1)
    details = []
    for mask, colour in zip(masks, report['regions']):
        labels, count = ndi.label(mask)
        sizes = np.bincount(labels.ravel())[1:]
        glyph = outline(mask, transform)
        end = 0
        degenerate = 0
        areas = []
        for last in glyph.endPtsOfContours:
            points = np.asarray(glyph.coordinates[end:last + 1], dtype=np.int64)
            end = last + 1
            area2 = abs(int(np.sum(points[:, 0] * np.roll(points[:, 1], -1) - points[:, 1] * np.roll(points[:, 0], -1))))
            areas.append(area2 / 2)
            degenerate += area2 == 0
        lost_areas = []
        for contour in find_contours(np.pad(mask.astype(float), 1), .5):
            contour = approximate_polygon(contour, tolerance=.65)
            if len(contour) < 4:
                continue
            xy = contour[:-1, ::-1] - 1
            rounded = np.column_stack((np.rint((xy[:, 0]-transform[0])*transform[2]+50),
                                       np.rint(760-(xy[:, 1]-transform[1])*transform[2])))
            def area(points):
                return abs(float(np.sum(points[:,0]*np.roll(points[:,1],-1)-points[:,1]*np.roll(points[:,0],-1))))/2
            if area(rounded) == 0:
                lost_areas.append(area(xy)*transform[2]**2)
        details.append(dict(maximumCollapsedAreaBeforeRounding=max(lost_areas, default=0), sourceRGB=colour['sourceRGB'], islands=int(count),
                            islandsAtLeast4Pixels=int(np.sum(sizes >= 4)),
                            contours=int(glyph.numberOfContours), degenerateContours=degenerate,
                            minimumContourArea=min(areas, default=0)))
    # The European flag's twelve separate gold stars must remain twelve
    # positive-area outlines, independent of its blue background.
    if region == 'EU':
        gold = next(d for d in details if d['sourceRGB'][0] > 200 and d['sourceRGB'][1] > 150 and d['sourceRGB'][2] < 100)
        assert gold['islandsAtLeast4Pixels'] == gold['contours'] == 12, gold
        assert gold['degenerateContours'] == 0, gold
    if region == 'US':
        blue = next(d for d in details if d['sourceRGB'] == [60, 59, 110])
        # One outer canton contour and fifty separate star counters.
        assert blue['contours'] == 51 and blue['degenerateContours'] == 0, blue
    if region == 'KR':
        black = next(d for d in details if d['sourceRGB'] == [0, 0, 0])
        assert black['islandsAtLeast4Pixels'] == black['contours'] == 18, black
        assert black['degenerateContours'] == 0, black
    if region == 'NP':
        white = next(d for d in details if d['sourceRGB'] == [255, 255, 255])
        assert white['islandsAtLeast4Pixels'] == white['contours'] == 2, white
        assert white['degenerateContours'] == 0, white
    return dict(region=region, colours=details,
                degenerateContours=sum(d['degenerateContours'] for d in details))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--regions', nargs='*', default=EXAMPLES)
    args = parser.parse_args()
    if args.regions == ['all']:
        registry = json.loads((ROOT/'docs/flags-emoji-svg-source-probe.json').read_text())
        args.regions = sorted({label(e['sequence']) for e in registry['files'] if e.get('licenseFamily') == 'region-flags-public-domain'})
        assert len(args.regions) == 262
    results = []
    failures = []
    target = ROOT / 'output/font-review/pen-translation/region-flags-contour-preflight.json'
    for region in args.regions:
        try:
            result = inspect(region)
        except Exception as error:
            result = dict(region=region, error=repr(error))
            failures.append(region)
            print(region, 'FAILED:', repr(error), flush=True)
        results.append(result)
        target.write_text(json.dumps(results, indent=2) + '\n')
        if 'error' not in result:
            print(region, 'degenerate contours:', result['degenerateContours'], flush=True)
    target = ROOT / 'output/font-review/pen-translation/region-flags-contour-preflight.json'
    target.write_text(json.dumps(results, indent=2) + '\n')
    if failures:
        raise SystemExit(f'Flag preflight failed: {failures}')


if __name__ == '__main__':
    main()
