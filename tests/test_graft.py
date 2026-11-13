"""The graft: a redrawn whole scene fitted onto a scanned close-up.

These use a synthetic scene so they need neither the book nor an image
model: a "scan" cut from the middle of a line drawing, and a "candidate"
that is the same drawing at another size, turned, bent and inked heavier.
"""
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools' / 'extensions' / 'graft'))
import graft  # noqa: E402

CROP = (300, 0, 620, 300)  # in scene px, which are scan px
FRAME = graft.Frame(left=200, right=200, below=200)


def scene(width, scale=1.0, bend=0.0, size=(900, 560)):
    """A figure of crossing lines and one solid mass, some crossing every
    side of CROP. `bend` pushes it sideways in a slow wave."""
    big = 4
    image = Image.new('L', (int(size[0] * scale) * big, int(size[1] * scale) * big), 255)
    draw = ImageDraw.Draw(image)

    def at(x, y):
        x += bend * np.sin(y / 70.0)
        return (x * scale * big, y * scale * big)

    def stroke(points):
        fine = []
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            fine += [at(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t) for t in np.linspace(0, 1, 40)]
        draw.line(fine, fill=0, width=int(width * scale * big), joint='curve')

    stroke([(120, 520), (180, 300), (340, 120), (470, 60), (560, 110), (600, 240), (760, 500)])
    stroke([(380, 90), (400, 250), (360, 420), (420, 520)])
    stroke([(520, 150), (500, 330), (640, 420)])
    stroke([(230, 200), (460, 210), (700, 180)])
    stroke([(440, 40), (455, 100)])
    draw.polygon([at(430, 350), at(560, 340), at(600, 470), at(450, 500)], fill=0)
    return image.resize((image.width // big, image.height // big), Image.LANCZOS)


@pytest.fixture(scope='module')
def result():
    truth = scene(6)
    # the scan as the pipeline stores it: the crop at twice its size
    scan = truth.crop(CROP).resize((640, 600), Image.LANCZOS)
    candidate = scene(9, scale=0.8, bend=5.0).rotate(1.5, fillcolor=255)
    panel, report = graft.graft(scan, candidate, FRAME, scales=np.linspace(0.9, 1.6, 15))
    return truth, scan, panel, report


def test_registration_recovers_the_scale(result):
    *_, report = result
    assert report.scale == pytest.approx(1 / 0.8, rel=0.02)


def test_scan_is_kept_pixel_for_pixel(result):
    _, scan, panel, _ = result
    x0 = FRAME.left * 2
    assert panel.crop((x0, 0, x0 + scan.width, scan.height)).tobytes() == scan.tobytes()


def test_warp_improves_the_fit_inside_the_crop(result):
    *_, report = result
    assert report.fit_warped < report.fit_rigid
    assert report.fit_warped < 1.0


def test_lines_cross_the_crop_edge_unbroken(result):
    *_, report = result
    assert report.edges_matched >= 10
    assert report.edges_lost == 0 and report.edges_extra == 0


def test_drawing_outside_the_crop_matches_the_true_scene(result):
    truth, _, panel, _ = result
    # the true scene in the panel's frame, at export size
    full = Image.new('L', ((FRAME.left + 320 + FRAME.right) * 2, (300 + FRAME.below) * 2), 255)
    piece = truth.crop((CROP[0] - FRAME.left, 0, CROP[2] + FRAME.right, 300 + FRAME.below))
    full.paste(piece.resize((piece.width * 2, piece.height * 2), Image.LANCZOS), (0, 0))
    want, got = np.asarray(full) < 128, np.asarray(panel) < 128
    assert want.shape == got.shape
    # within 150 scan px of the crop, where the warp is still in force
    near = np.zeros(want.shape, bool)
    near[:900, 100:1340] = True
    near[:600, 400:1040] = False
    distance = ndimage.distance_transform_edt(~want)
    assert distance[got & near].mean() < 3.0  # export px


def test_candidate_lines_take_the_scan_weight(result):
    *_, report = result
    assert report.weight_before > report.weight_scan + 1.5
    assert abs(report.weight_after - report.weight_scan) <= 1.0


def test_match_edges_drops_matches_that_would_fold():
    scan = np.zeros(200, bool)
    cand = np.zeros(200, bool)
    scan[50:56] = scan[70:76] = True
    cand[52:58] = True   # 2 px to the right of the first scan line
    cand[60:66] = True   # nearest to the second scan line, but 10 px left
    pairs, lost, extra = graft.match_edges(scan, cand, reach=14)
    shifts = sorted({shift for _, shift in pairs})
    assert shifts == [2.0]
    assert lost == 2 and extra == 2


def test_match_edges_reaches_further_for_solid_blacks():
    scan = np.zeros(400, bool)
    cand = np.zeros(400, bool)
    scan[:120] = True    # a solid black that ends at 120 in the scan
    cand[:200] = True    # and 80 px later in the candidate
    scan[300:306] = cand[340:346] = True  # a line 40 px out is not matched
    pairs, lost, extra = graft.match_edges(scan, cand, reach=14)
    assert pairs == [(119.5, 80.0)]
    assert lost == 2 and extra == 2


def test_a_black_drawn_too_large_is_not_cut_off_flat():
    """The candidate's solid mass reaches further along the crop's foot
    than the scan's; grafted, its edge has to leave the crop where the
    scan's does, not run along it."""
    def drawing(right):
        image = Image.new('L', (500, 400), 255)
        draw = ImageDraw.Draw(image)
        draw.polygon([(60, 150), (right, 150), (right + 60, 380), (40, 380)], fill=0)
        draw.line([(40, 60), (460, 90)], fill=0, width=6)
        draw.line([(420, 40), (400, 370)], fill=0, width=6)
        return image

    scan = drawing(200).crop((0, 0, 500, 200)).resize((1000, 400), Image.LANCZOS)
    frame = graft.Frame(left=0, right=0, below=200)
    _, report = graft.graft(scan, drawing(260), frame, scales=np.linspace(0.9, 1.1, 5))
    assert report.seam < 40


def test_shift_profile_eases_to_nothing():
    profile = graft.shift_profile([(100.5, 6.0), (110.5, 6.0)], 300)
    assert profile[105] == pytest.approx(6.0, abs=0.2)
    assert profile[20] == 0 and profile[200] == 0
    assert np.abs(np.diff(profile)).max() < 0.5


def two_figures(second=1.0, width=5):
    """A large figure on the left and a small one on the right, the small
    one drawn `second` times its size about its own middle."""
    big = 4
    image = Image.new('L', (700 * big, 400 * big), 255)
    draw = ImageDraw.Draw(image)

    def stroke(points, about=None, scale=1.0):
        if about:
            points = [(about[0] + (x - about[0]) * scale, about[1] + (y - about[1]) * scale) for x, y in points]
        draw.line([(x * big, y * big) for x, y in points], fill=0, width=width * big, joint='curve')

    stroke([(60, 340), (90, 120), (200, 60), (300, 130), (330, 330)])
    stroke([(120, 200), (280, 210)])
    stroke([(200, 60), (190, 330)])
    middle = (520, 200)
    for points in ([(440, 120), (520, 90), (640, 130)], [(450, 200), (540, 215), (650, 190)],
                   [(520, 90), (530, 300)], [(440, 290), (640, 280)], [(470, 150), (480, 260)]):
        stroke(points, middle, second)
    return image.resize((700, 400), Image.LANCZOS)


def test_each_figure_gets_its_own_fit():
    # the crop's right edge runs through the small figure, as panel 2's
    # runs through Calvin's head
    truth = two_figures()
    scan = truth.crop((0, 0, 560, 400)).resize((1120, 800), Image.LANCZOS)
    candidate = two_figures(second=1.25, width=7)
    frame = graft.Frame(left=0, right=140, below=0)

    ink = graft.to_ink(truth.crop((0, 0, 560, 400)))
    assert len(graft.figures(ink)) == 2

    panel, report = graft.graft(scan, candidate, frame, scales=np.linspace(0.9, 1.2, 7))
    assert report.edges_lost == 0 and report.edges_extra == 0
    # right of the crop, the small figure is back at its true size
    want = np.asarray(truth.resize((1400, 800), Image.LANCZOS)) < 128
    got = np.asarray(panel) < 128
    distance = ndimage.distance_transform_edt(~want)
    assert distance[:, 1120:][got[:, 1120:]].mean() < 4.0  # export px


def test_patch_takes_only_the_part_that_was_redrawn():
    import patch

    def drawing(shoe):
        image = Image.new('L', (900, 600), 255)
        draw = ImageDraw.Draw(image)
        draw.polygon([(350, 250), (800, 230), (820, 520), (330, 520)], fill=0)   # trousers
        draw.line([(100, 80), (700, 120), (860, 60)], fill=0, width=14)          # a line elsewhere
        draw.ellipse(shoe, outline=0, width=16)
        return image

    panel = drawing((230, 380, 400, 520))
    # the redraw: a longer shoe, and everything else a few pixels off
    edit = drawing((80, 400, 400, 520)).rotate(0.3, fillcolor=255, translate=(4, -2))
    patched, mask = patch.patch(panel, edit, (0, 0, 900, 600))

    before, after = np.asarray(panel) < 128, np.asarray(patched) < 128
    assert after[440:480, 85:110].any()                    # the new shoe's toe is there
    assert not mask[:200].any()                            # the line elsewhere was left alone
    assert (before[~mask] == after[~mask]).all()           # and so was everything outside the part
    assert not mask[:, 500:].any()


def test_a_line_drawn_along_the_crop_s_edge_is_moved_clear_of_it():
    """The drawing has a line running down the crop's left edge, half in
    and half out (a sleeve hem, say), where the scan has only paper. Pasting
    the scan back would slice it lengthways; it should stand whole just
    outside the crop instead."""
    frame = graft.Frame(left=100, right=0, below=0)
    scan = np.zeros((300, 200), bool)
    scan[60:68] = scan[220:228] = True             # two lines that cross the edge
    drawing = np.zeros((300, 300), np.float32)
    drawing[60:68] = drawing[220:228] = 1
    drawing[60:228, 96:104] = 1                    # the hem, centred on the edge
    solid = drawing.copy()
    solid[100:180, 40:104] = 1                     # in another drawing, a black cut by the crop

    def pushed(candidate):
        return graft.warp(candidate, graft.push_out(scan, candidate, frame, weight=8.0)) > 0.5

    before, after = drawing > 0.5, pushed(drawing)
    middle = slice(90, 200)                        # between the crossing lines
    assert before[middle, 98:100].all()            # sliced: ink right up to the crop
    assert not after[middle, 98:100].any()         # now there is air beside the crop
    assert (after[middle, 60:100].sum(1) >= 7).all()   # and the hem is whole (it was 8 wide)
    assert after[64, 90:100].all() and after[224, 90:100].all()   # the crossing lines still arrive
    # a solid black is not a line: it is left for `snap`
    assert np.array_equal(pushed(solid), solid > 0.5)
