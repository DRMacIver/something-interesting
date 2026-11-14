"""The full-panel exports: Watterson's scan, with a drawing grafted round it."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/full-panels'
sys.path.insert(0, str(ROOT / 'tools/extensions/graft'))
import build  # noqa: E402
import graft  # noqa: E402
import shoe  # noqa: E402


def export(number):
    return Image.open(OUT / f'panel{number}.png')


def ink(number):
    return np.asarray(export(number)) < 128


def test_original_crops_are_preserved():
    for item in json.loads((OUT / 'verification.json').read_text()):
        number = item['panel']
        image = export(number)
        source = np.asarray(Image.open(OUT / f'original{number}.png'))
        x, y = item['originalOffset']
        width, height = item['originalSize']
        overlap = np.asarray(image.crop((x, y, x + width, y + height)))
        assert image.size == tuple(item['size'])
        # Every panel keeps Watterson's crop exactly.
        assert np.array_equal(overlap, source)
        assert item['changedOriginalPixels'] == 0


@pytest.fixture(scope='module')
def rebuilt():
    one, _ = build.panel(1)
    return {1: one, 2: build.panel(2, one)[0], 3: build.panel(3, one)[0]}


@pytest.mark.parametrize('number', [1, 2, 3])
def test_exports_are_what_the_build_makes(rebuilt, number):
    assert np.array_equal(np.asarray(rebuilt[number]), np.asarray(export(number)))


@pytest.mark.parametrize('number, limit', [(1, 60), (2, 350), (3, 250)])
def test_drawing_joins_the_scan_at_the_crop_s_edges(number, limit):
    # export px of the crop's edge with ink on one side and paper on the
    # other: lines that cross it add little, anything cut off along it a lot
    x0, _, x1, y1 = build.scan_box(number)
    assert graft.seam_mismatch(export(number), (x1 - x0, y1), x0, build.FRAMES[number]) < limit


@pytest.mark.parametrize('number', [2, 3])
def test_closeups_show_dad_kneeling_on_the_floor(number):
    drawing = ink(number)
    _, _, _, foot = build.scan_box(number)
    below = drawing[foot:]
    # his trousers: one solid black mass below the scan, about two of his
    # head widths long
    solid = ndimage.binary_opening(below[::4, ::4], iterations=8)
    labels, count = ndimage.label(solid)
    sizes = ndimage.sum(solid, labels, range(1, count + 1))
    xs = np.nonzero(labels == int(np.argmax(sizes)) + 1)[1] * 4
    head = build.PICKS[number]['head']
    assert 1.6 < (xs.max() - xs.min()) / head < 2.4
    # and a floor: everything he, Calvin and the player rest on ends within
    # a third of a head of one level, with blank paper beneath
    columns = np.nonzero(below.any(0))[0]
    bottoms = np.array([np.nonzero(below[:, x])[0].max() for x in columns])
    floor = np.percentile(bottoms, 90)
    assert bottoms.max() - floor < head / 3
    assert not below[int(bottoms.max()) + 1:].any()


@pytest.mark.parametrize('number', [2, 3])
def test_dads_shoe_is_panel_one_s(number):
    pick = build.PICKS[number]
    alpha, shoe_ink, _ = shoe.panel_one_shoe(export(1), pick['head'] / shoe.PANEL1_HEAD)
    h, w = alpha.shape
    x0, y0 = pick['shoe_at'][0] - w, pick['shoe_at'][1] - h
    # the toe: the front two fifths of the shoe, clear of his trousers
    toe = (slice(y0, y0 + h), slice(x0, x0 + 2 * w // 5))
    drawn = ink(number)[toe]
    his = shoe_ink[:, :2 * w // 5]
    assert drawn.sum() > 0.5 * his.sum()
    # the same shape, to within the thinning of its line
    assert ndimage.distance_transform_edt(~his)[drawn].mean() < 6
    assert ndimage.distance_transform_edt(~drawn)[his].mean() < 12


def test_panel_two_has_one_near_sleeve():
    # Watterson's scan already holds Dad's near sleeve: its front edge, and
    # most of its hem, the thick line that reaches the crop's left edge. The
    # drawing adds only the sleeve's back edge and the last of the hem.
    drawing = ink(2)
    left = build.scan_box(2)[0]
    # so between that back edge and the crop there is blank shirt above the
    # hem, not the edge of a second sleeve
    assert not drawing[1450:1780, left - 80:left].any()
    # and the hem arrives at the crop as one line no heavier than the scan's
    for x in (left - 12, left - 40):
        column = drawing[1700:1900, x].astype(np.int8)
        assert (np.diff(column) == 1).sum() == 1
        assert column.sum() <= drawing[1700:1900, left + 2].sum() + 4


def test_panel_three_s_lines_carry_on_below_the_scan():
    # every line of Dad's shirt that reaches the bottom of the scan has ink
    # directly beneath it in the drawing: none stops dead at the crop, and
    # none restarts to one side
    drawing = ink(3)
    left, _, right, foot = build.scan_box(3)
    above = drawing[foot - 1, left:right]
    below = ndimage.binary_dilation(drawing[foot:foot + 3, left:right].any(0), iterations=8)
    labels, count = ndimage.label(above)
    assert count >= 6
    stopped = [int(np.nonzero(labels == index)[0][0]) + left for index in range(1, count + 1)
               if not below[labels == index].any()]
    assert stopped == []


def test_panel_three_s_lines_keep_their_weight_below_the_scan():
    # a line that crosses the bottom of the scan is as wide just below it as
    # just above: the raised arm's upper line used to halve there
    drawing = ink(3)
    left, _, right, foot = build.scan_box(3)
    above, _ = ndimage.label(drawing[foot - 1, left:right])
    below, _ = ndimage.label(drawing[foot, left:right])
    stepped = []
    for index in range(1, above.max() + 1):
        run = above == index
        under = np.unique(below[run])
        under = under[under > 0]
        if run.sum() >= 15 and len(under) == 1:
            if abs(int(run.sum()) - int((below == under[0]).sum())) > 8:
                stepped.append(int(np.nonzero(run)[0][0]) + left)
    assert stepped == []


def test_scans_are_what_the_strip_s_page_gives():
    pdf = ROOT / 'calvin-and-hobbes.pdf'
    if not pdf.exists():
        pytest.skip('needs the scan of the book, which is not in the repository')
    import scans
    made = scans.prepare(pdf)
    assert sorted(made) == sorted(path.name for path in scans.SCANS.glob('*.png'))
    for name, image in made.items():
        assert np.array_equal(np.asarray(image), np.asarray(Image.open(scans.SCANS / name))), name


def local_links(page):
    import re
    for link in re.findall(r'(?:href|src)="([^"#]+)', (ROOT / page).read_text()):
        if '://' not in link:
            yield link.split('?')[0]


def test_review_page_links_only_to_files_in_the_repository():
    # the site is served from the repository, so a link to anything git
    # ignores (output/, say) is dead there
    import subprocess
    links = sorted(set(local_links('panels.html')))
    assert 'assets/full-panels/panel2.png' in links
    assert [link for link in links if not (ROOT / link).is_file()] == []
    ignored = subprocess.run(['git', 'check-ignore', *links], cwd=ROOT, capture_output=True, text=True)
    assert ignored.stdout.split() == []


def test_download_bundle_holds_the_current_exports():
    import zipfile
    with zipfile.ZipFile(ROOT / 'assets/full-panels.zip') as bundle:
        names = bundle.namelist()
        for number in range(1, 5):
            name = f'assets/full-panels/panel{number}.png'
            assert bundle.read(name) == (ROOT / name).read_bytes()
        assert 'panels.html' in names
        # the page inside works offline: every file it links to is beside it
        page = bundle.read('panels.html').decode()
    import re
    for link in re.findall(r'(?:href|src)="([^"#]+)', page):
        if '://' not in link:
            assert link.split('?')[0] in names, link
