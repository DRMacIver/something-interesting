"""Dad's back and near sleeve in panel 2, left of Watterson's crop.

Draft A (dad2.py) refined over six Codex A/B rounds; variant 4 was the best
(Codex 5/10 against draft A's 4). Panel 2 ends at the scan's foot, which
already reaches his knee, so only his back, sleeve, elbow and the top of his
trousers show; the legs and shoe these variants also draw fall outside it.

Render a variant over the current export: python dad2_refine.py N [OUTDIR]
"""
import sys, copy
sys.path.insert(0, '/Users/drmaciver/Projects/calvins-dad/tools/extensions/reconstruction-v2')
import numpy as np
from PIL import Image
import dad2
from ink import Ink

ROOT = '/Users/drmaciver/Projects/calvins-dad'
BEST = '4'

def panel(image, d):
    """dad2.panel_two with the shoe drawn after the trousers (in front of the seat)."""
    from dad2 import Ink, composite, ImageDraw, np as _np
    w, h = image.size
    image = image.copy()
    image.paste(Image.open(dad2.HERE / 'locked-2.png').convert('L'), (800, 0))
    ink = Ink((w, h), seed=21)
    if d.get('shoe_first'):
        dad2.shoe(ink, d['shoe'])
    ink.fill(d['trousers'], wobble=1.0)
    for line, widths in d['trouser_whites']:
        ink.stroke(line, widths, colour=255, wobble=0.6)
    if not d.get('shoe_first'):
        dad2.shoe(ink, d['shoe'])
    ink.fill(d['back'] + d['hem'][1:] + [(800, 1186)], colour=255, wobble=0)
    ink.stroke(d['back'], [20, 22, 24, 24, 23, 22, 22, 21, 21, 20, 20])
    ink.stroke(d['hem'], [20, 20, 19, 18, 17, 16, 16])
    sleeve_ink, sleeve_shape = dad2.sleeve((w, h), d['sleeve'])
    ink.fill(d['upper_arm'] + [(800, 1812), (700, 1792), (600, 1780)], colour=255, wobble=0)
    ink.stroke(d['upper_arm'], [18, 20, 21, 21, 20, 20, 22])
    drawing = ink.mask()
    drawing[sleeve_shape] = False
    drawing |= sleeve_ink
    hem_ink = Ink((w, h), seed=23)
    lo = Image.new('1', (w, h), 0)
    ImageDraw.Draw(lo).polygon(d['sleeve_hem_clear'], fill=1)
    drawing[np.asarray(lo)] = False
    hem_ink.fill(d['sleeve_hem_clear'], colour=255, wobble=0)
    hem_ink.stroke(d['sleeve_hem'], d['hem_w'])
    drawing |= hem_ink.mask()
    yy, xx = np.mgrid[:h, :w]
    region = (xx < 800) | ((yy >= 2060) & (xx < 1540))
    return composite(image, drawing, region)


def variant(n):
    return globals()['variant' + n]()


def variant1():
    d = copy.deepcopy(dad2.A)
    d['shoe'] = dict(heel_x=450, toe_x=50,
        top=[(1.0, 100), (0.75, 100), (0.5, 94), (0.3, 84), (0.15, 70), (0.06, 54), (0.0, 32)],
        bottom=[(0.03, 10), (0.3, 0), (0.7, 0), (1.0, 0)],
        sole_inset=14, toe_cap=[(0.30, 2), (0.22, 20), (0.17, 36)])
    # seat projects behind the torso, settles on the heel; cuff narrows at the ankle
    d['trousers'] = ([(206, 1990), (150, 2038), (112, 2120), (116, 2200), (150, 2252),
                      (230, 2272), (330, 2290), (392, 2294), (410, 2310), (420, 2350),
                      (424, 2382), (700, 2385)] + dad2.knee_arc(90, -42) +
                     [(1033, 2040), (980, 2000), (870, 1960), (820, 2030), (800, 2047),
                      (700, 2041), (500, 2030), (300, 2016)])
    d['trouser_whites'] = [
        ([(1056, 2296), (900, 2268), (700, 2254), (520, 2262), (440, 2296)], [3, 12, 13, 9, 4, 2]),
        ([(160, 2120), (206, 2170), (262, 2196)], [2, 9, 2])]
    d['upper_arm'] = [(590, 1780), (580, 1830), (592, 1872), (620, 1902), (670, 1920),
                      (740, 1930), (800, 1938)]
    d['sleeve_hem'] = [(516, 1668), (580, 1714), (660, 1757), (740, 1792), (800, 1811)]
    d['sleeve_hem_clear'] = [(506, 1650), (800, 1790), (800, 1830), (740, 1818), (660, 1782),
                             (580, 1742), (506, 1698)]
    d['hem_w'] = [14, 18, 21, 20, 18]
    return d

def variant2():
    d = variant1()
    d['shoe'] = dict(heel_x=420, toe_x=52,
        top=[(1.0, 100), (0.75, 100), (0.5, 94), (0.3, 86), (0.15, 76), (0.06, 62), (0.0, 40)],
        bottom=[(0.02, 18), (0.08, 4), (0.3, 0), (0.7, 0), (1.0, 0)],
        sole_inset=14, toe_cap=[(0.30, 2), (0.22, 24), (0.17, 44)])
    arc = dad2.knee_arc(-2, -42, 1)  # placeholder to keep import use obvious
    d['trousers'] = ([(206, 1990), (160, 2036), (134, 2100), (130, 2170), (146, 2232),
                      (190, 2262), (290, 2268), (360, 2272), (392, 2290), (408, 2318),
                      (412, 2350), (418, 2382), (700, 2385), (900, 2385), (1000, 2372),
                      (1062, 2330), (1096, 2260), (1100, 2190)] +
                     dad2.knee_arc(0, -42)[1:] +
                     [(1033, 2040), (980, 2000), (870, 1960), (820, 2030), (800, 2047),
                      (700, 2041), (500, 2030), (300, 2016)])
    d['trouser_whites'] = [
        ([(1052, 2296), (900, 2268), (700, 2254), (520, 2260), (430, 2300)], [3, 12, 14, 10, 4, 2]),
        ([(170, 2110), (212, 2160), (262, 2190)], [2, 9, 2])]
    d['upper_arm'] = [(596, 1745), (584, 1800), (584, 1850), (604, 1892), (645, 1920),
                      (710, 1932), (800, 1938)]
    d['sleeve_hem'] = [(528, 1654), (584, 1708), (660, 1754), (740, 1791), (800, 1811)]
    d['sleeve_hem_clear'] = [(506, 1640), (800, 1790), (800, 1830), (740, 1818), (660, 1782),
                             (580, 1742), (506, 1690)]
    d['hem_w'] = [20, 20, 21, 19, 17]
    return d


def variant3():
    d = variant2()
    d['shoe_first'] = True
    d['shoe'] = dict(heel_x=470, toe_x=52,
        top=[(1.0, 112), (0.75, 108), (0.5, 98), (0.3, 86), (0.15, 74), (0.06, 60), (0.0, 38)],
        bottom=[(0.02, 18), (0.08, 4), (0.3, 0), (0.7, 0), (1.0, 0)],
        sole_inset=14, toe_cap=[(0.34, 2), (0.26, 24), (0.2, 44)])
    d['trousers'] = ([(206, 1990), (160, 2036), (134, 2100), (130, 2170), (146, 2232),
                      (190, 2260), (290, 2266), (346, 2268), (376, 2298), (410, 2340),
                      (446, 2383), (700, 2385), (900, 2385), (1000, 2372),
                      (1062, 2330), (1096, 2260), (1100, 2190)] +
                     dad2.knee_arc(0, -42)[1:] +
                     [(1033, 2040), (980, 2000), (870, 1960), (820, 2030), (800, 2047),
                      (700, 2041), (500, 2030), (300, 2016)])
    d['trouser_whites'] = [
        ([(1052, 2296), (900, 2268), (700, 2254), (540, 2262), (430, 2300), (392, 2318)], [3, 12, 14, 10, 4, 1]),
        ([(170, 2110), (212, 2160), (262, 2190)], [2, 9, 2])]
    d['upper_arm'] = [(604, 1722), (590, 1770), (588, 1830), (606, 1876), (648, 1906),
                      (712, 1925), (800, 1938)]
    d['sleeve_hem'] = [(528, 1654), (590, 1698), (665, 1741), (740, 1781), (800, 1811)]
    d['sleeve_hem_clear'] = [(506, 1640), (800, 1790), (800, 1830), (740, 1810), (665, 1772),
                             (590, 1732), (506, 1690)]
    d['hem_w'] = [20, 19, 18, 17, 16]
    return d


def variant4():
    d = variant3()
    d['shoe'] = dict(heel_x=480, toe_x=84,
        top=[(1.0, 126), (0.75, 120), (0.5, 108), (0.3, 94), (0.15, 80), (0.06, 64), (0.0, 42)],
        bottom=[(0.02, 20), (0.08, 5), (0.3, 0), (0.7, 0), (1.0, 0)],
        sole_inset=16, toe_cap=[(0.34, 2), (0.26, 26), (0.2, 48)])
    d['trousers'] = ([(206, 1990), (160, 2036), (134, 2100), (130, 2170), (148, 2236),
                      (192, 2262), (290, 2270), (346, 2276), (372, 2300), (394, 2336),
                      (430, 2368), (480, 2384), (700, 2385), (900, 2385), (1000, 2372),
                      (1062, 2330), (1096, 2260), (1100, 2190)] +
                     dad2.knee_arc(0, -42)[1:] +
                     [(1033, 2040), (980, 2000), (870, 1960), (820, 2030), (800, 2047),
                      (700, 2041), (500, 2030), (300, 2016)])
    d['trouser_whites'] = [
        ([(1052, 2312), (900, 2286), (700, 2276), (560, 2284), (440, 2312), (396, 2338)], [3, 12, 14, 10, 4, 1]),
        ([(168, 2100), (214, 2156), (270, 2190)], [2, 10, 2])]
    d['upper_arm'] = [(672, 1760), (654, 1806), (664, 1858), (704, 1904), (752, 1928),
                      (800, 1938)]
    d['sleeve_hem'] = [(528, 1654), (590, 1698), (665, 1741), (740, 1781), (800, 1811)]
    return d


def variant5():
    d = variant4()
    d['shoe'] = dict(heel_x=470, toe_x=120,
        top=[(1.0, 136), (0.75, 128), (0.5, 114), (0.3, 98), (0.15, 82), (0.06, 64), (0.0, 44)],
        bottom=[(0.02, 22), (0.08, 6), (0.3, 0), (0.7, 0), (1.0, 0)],
        sole_inset=16, toe_cap=[(0.4, 2), (0.3, 28), (0.22, 52)])
    d['trouser_whites'] = [
        ([(1056, 2318), (920, 2290), (760, 2278), (600, 2286), (470, 2316), (404, 2342)], [4, 22, 30, 24, 10, 2]),
        ([(168, 2100), (214, 2156), (270, 2190)], [2, 10, 2])]
    d['upper_arm'] = [(678, 1762), (662, 1806), (672, 1848), (708, 1886), (754, 1914), (800, 1938)]
    d['sleeve_hem'] = [(528, 1654), (592, 1700), (668, 1736), (742, 1776), (800, 1811)]
    d['hem_w'] = [22, 18, 20, 17, 16]
    return d


def variant6():
    d = variant4()
    d['shoe'] = dict(heel_x=480, toe_x=100,
        top=[(1.0, 130), (0.75, 124), (0.5, 112), (0.3, 98), (0.15, 82), (0.06, 64), (0.0, 42)],
        bottom=[(0.02, 20), (0.08, 5), (0.3, 0), (0.7, 0), (1.0, 0)],
        sole_inset=16, toe_cap=[(0.36, 2), (0.28, 26), (0.21, 48)])
    # seat: a small separate turn above the heel
    d['trousers'] = ([(206, 1990), (160, 2036), (134, 2100), (130, 2170), (148, 2232),
                      (190, 2256), (250, 2262), (300, 2258), (346, 2268), (372, 2298), (394, 2336),
                      (430, 2368), (480, 2384), (700, 2385), (900, 2385), (1000, 2372),
                      (1062, 2330), (1096, 2260), (1100, 2190)] +
                     dad2.knee_arc(0, -42)[1:] +
                     [(1033, 2040), (980, 2000), (870, 1960), (820, 2030), (800, 2047),
                      (700, 2041), (500, 2030), (300, 2016)])
    d['trouser_whites'] = [
        ([(1060, 2306), (960, 2284), (840, 2272), (740, 2270)], [3, 14, 10, 1]),
        ([(168, 2100), (214, 2156), (270, 2190)], [2, 10, 2])]
    d['upper_arm'] = [(678, 1764), (662, 1804), (672, 1842), (710, 1876), (756, 1906), (800, 1938)]
    return d


def panel_two(image):
    """The best refinement, drawn over the panel as assemble builds it."""
    return panel(image, variant(BEST))


if __name__ == '__main__':
    n = sys.argv[1]
    OUT = sys.argv[2] if len(sys.argv) > 2 else '.'
    base = Image.open(ROOT + '/assets/full-panels/panel2.png').convert('L')
    out = panel(base, variant(n))
    out.save(f'{OUT}/v{n}.png')
    out.crop((0, 1100, 1700, 2500)).save(f'{OUT}/v{n}-lower.png')
