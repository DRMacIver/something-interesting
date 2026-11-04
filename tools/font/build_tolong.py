"""Compile the reviewed Tolong stroke reconstruction with native mark positioning.

Review output only until shaping and browser validation permit production use.
The pixel donor is GNU Unifont 18.0.01, used under OFL 1.1. Combining marks
come from the already pinned OFL Noto Sans donor.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from skimage.measure import find_contours, approximate_polygon
from prototype_unifont_lettering import ROOT, SHA, raster, prepare_letter

ABOVE = {0x303, 0x306, 0x307, 0x308, 0x304}
BELOW = {0x330, 0x324, 0x323, 0x331}
MARKS = ABOVE | BELOW


def bounds(glyph):
    pen = BoundsPen(None)
    glyph.draw(pen, None)
    return pen.bounds


def trace(mask):
    pen = TTGlyphPen(None)
    # Prototype's 384x512 image is the source viewBox -8,-56,48,64.
    # Keep the original baseline and a 1000-unit em, not per-glyph fitting.
    for contour in find_contours(np.pad(mask.astype(float), 1), .5):
        contour = approximate_polygon(contour, tolerance=.35)
        points = [(round(((x-1)/8-8)*1000/64),
                   round((56-(y-1)/8)*1000/64)) for y,x in contour]
        if len(set(points)) < 3:
            continue
        pen.moveTo(points[0])
        for point in points[1:-1]:
            pen.lineTo(point)
        pen.closePath()
    return pen.glyph()


def build(source, output):
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SHA
    original = TTFont(source)
    assert original['head'].unitsPerEm == 64
    entry = next(e for e in json.loads((ROOT/'data/font-sources/noto.json').read_text())['files']
                 if e['path'].endswith('/NotoSans-Regular.ttf'))
    donor_path = ROOT/entry['path']
    assert hashlib.sha256(donor_path.read_bytes()).hexdigest() == entry['sha256']
    donor = TTFont(donor_path)
    points = [int(line.split(';')[0],16) for line in
              (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines()
              if 0x11DB0 <= int(line.split(';')[0],16) <= 0x11DEF]
    assert len(points) == 54
    glyphs = {'.notdef': TTGlyphPen(None).glyph(), 'space': TTGlyphPen(None).glyph()}
    metrics = {'.notdef': (500,0), 'space': (250,0)}
    cmap = {32: 'space'}
    review = []
    for cp in points:
        image, record = prepare_letter(raster(original, cp), cp)
        name = f'u{cp:X}'
        glyphs[name] = trace(np.asarray(image) < 128)
        box = bounds(glyphs[name])
        metrics[name] = (500, round(box[0]))
        cmap[cp] = name
        review.append(dict(codepoint=f'U+{cp:04X}', **record))
    # Normalize each mark around x=0 and its near edge at y=0; GPOS sets
    # clearance relative to each individual base, including short letters.
    donor_set = donor.getGlyphSet()
    scale = 1000/donor['head'].unitsPerEm
    for cp in sorted(MARKS):
        name = f'u{cp:X}'
        # Decompose composite marks through a recording pen before transforming.
        from fontTools.pens.recordingPen import DecomposingRecordingPen
        recording = DecomposingRecordingPen(donor_set)
        donor_set[donor.getBestCmap()[cp]].draw(recording)
        bp = BoundsPen(None); recording.replay(bp)
        x0,y0,x1,y1 = bp.bounds
        pen = TTGlyphPen(None)
        recording.replay(TransformPen(pen, (scale,0,0,scale,-(x0+x1)*scale/2,
                                            -(y0 if cp in ABOVE else y1)*scale)))
        glyphs[name] = pen.glyph()
        metrics[name] = (0, round(bounds(glyphs[name])[0]))
        cmap[cp] = name
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(list(glyphs)); fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs); fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=1100, descent=-450)
    notices = '\n'.join(sorted({n.toUnicode() for f in (original,donor)
                                for n in f['name'].names if n.nameID == 0}))
    fb.setupNameTable(dict(familyName='Dad Tolong Review', styleName='Regular',
                          uniqueFontIdentifier='DadTolongReview-1',
                          fullName='Dad Tolong Review', psName='DadTolongReview',
                          version='Version 0.001', copyright=notices,
                          licenseDescription='Licensed under the SIL Open Font License, Version 1.1.',
                          licenseInfoURL='https://openfontlicense.org/'))
    fb.setupOS2(sTypoAscender=1100,sTypoDescender=-450,sTypoLineGap=0,
                usWinAscent=1100,usWinDescent=450)
    fb.setupPost(); fb.setupMaxp()
    rules = ['languagesystem DFLT dflt;', 'languagesystem tols dflt;']
    for cp in sorted(MARKS):
        cls = 'above' if cp in ABOVE else 'below'
        rules.append(f'markClass u{cp:X} <anchor 0 0> @{cls};')
    rules.append('feature mark {')
    for cp in points:
        name = cmap[cp]; x0,y0,x1,y1 = bounds(glyphs[name]); x = round((x0+x1)/2)
        rules.append(f'pos base {name} <anchor {x} {round(y1+55)}> mark @above '
                     f'<anchor {x} {round(y0-55)}> mark @below;')
    rules.append('} mark;')
    rules.append('feature mkmk {')
    for cp in sorted(MARKS):
        name = cmap[cp]; box = bounds(glyphs[name])
        cls = 'above' if cp in ABOVE else 'below'
        edge = box[3]+55 if cp in ABOVE else box[1]-55
        rules.append(f'pos mark {name} <anchor 0 {round(edge)}> mark @{cls};')
    rules.append('} mkmk;')
    addOpenTypeFeaturesFromString(fb.font, '\n'.join(rules))
    fb.font['head'].created = fb.font['head'].modified = 3406620153
    output.parent.mkdir(parents=True, exist_ok=True)
    fb.save(output)
    output.with_suffix('.json').write_text(json.dumps(dict(
        status='review only; not delivered coverage', sourceSha256=SHA,
        markSource=entry['path'], markSourceSha256=entry['sha256'],
        glyphs=review, marks=[f'U+{cp:04X}' for cp in sorted(MARKS)]), indent=2)+'\n')
    print(f'Built {output}: 54 Tolong characters and 9 combining marks', flush=True)
    return output



def build_registered():
    """Build a cached derivative; source verification runs before this hook."""
    source = ROOT/'build/unicode-sources/unifont/unifont_upper-18.0.01.otf'
    output = ROOT/'build/unicode-sources/tolong/DadTolong.ttf'
    stamp = output.with_suffix('.build.json')
    inputs = [Path(__file__), ROOT/'tools/font/prototype_unifont_lettering.py',
              ROOT/'tools/font/unifont_strokes.py', ROOT/'tools/font/pen_translate.py',
              ROOT/'data/font-sources/noto.json', ROOT/'data/font-sources/tolong.json',
              ROOT/'data/unicode/18.0.0/UnicodeData.txt', source,
              ROOT/'build/unicode-sources/noto/NotoSans-Regular.ttf']
    fingerprint = hashlib.sha256(b''.join(p.read_bytes() for p in inputs)).hexdigest()
    if output.exists() and stamp.exists():
        old = json.loads(stamp.read_text())
        if old.get('recipe') == fingerprint and old.get('sha256') == hashlib.sha256(output.read_bytes()).hexdigest():
            return output
    build(source, output)
    stamp.write_text(json.dumps(dict(recipe=fingerprint,sha256=hashlib.sha256(output.read_bytes()).hexdigest()),indent=2)+'\n')
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'output/font-review/tolong/DadTolongReview.ttf')
    args = parser.parse_args()
    build(args.source, args.output)
