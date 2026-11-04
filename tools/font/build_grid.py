"""Build connected, lightly inked grid symbols from the pinned OFL Noto Mono.

Grid cell: 600 × 1000 units, baseline at y=0, top=800 and bottom=-200.
Connection endpoints and block fractions remain exact. Internal box edges have
small pen variation; this never displaces a shared edge between cells.
"""
import hashlib
import json
import math
from pathlib import Path
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'build/unicode-sources/noto/NotoSansMono-Regular.ttf'
LEGACY = ROOT / 'build/unicode-sources/unicodia/BabelStonePseudographica.ttf'
OUT = ROOT / 'assets/fonts/dad-grid.woff2'


def source_record(source_path=SOURCE):
    for path in (ROOT / 'data/font-sources').glob('*.json'):
        for entry in json.loads(path.read_text()).get('files', []):
            if entry['path'] == source_path.relative_to(ROOT).as_posix():
                assert hashlib.sha256(source_path.read_bytes()).hexdigest() == entry['sha256']
                return {'manifest': str(path.relative_to(ROOT)), **entry}
    raise ValueError('Grid source is not pinned')


class InkPen(BasePen):
    def __init__(self, target, strength=3, snap_edges=False):
        super().__init__(None)
        self.target = target
        self.strength = strength
        self.snap_edges = snap_edges
        self.previous = None

    def warp(self, point):
        x, y = point
        if self.snap_edges:
            if abs(x) <= 1.3: x = 0
            if abs(x-600) <= 1.3: x = 600
            if abs(y+200) <= 1.3: y = -200
            if abs(y-800) <= 1.3: y = 800
        strength = self.strength * math.sin(math.pi*x/600) * math.sin(math.pi*(y+200)/1000)
        return round(x + strength*math.sin(y/53)), round(y + strength*math.sin(x/47))

    def _moveTo(self, point):
        self.target.moveTo(self.warp(point)); self.previous = point

    def _lineTo(self, point):
        a = self.previous
        steps = max(1, math.ceil(math.dist(a, point)/60))
        for i in range(1, steps+1):
            self.target.lineTo(self.warp(tuple(a[k]+(point[k]-a[k])*i/steps for k in (0,1))))
        self.previous = point

    def _qCurveToOne(self, control, point):
        self.target.qCurveTo(self.warp(control), self.warp(point)); self.previous = point

    def _curveToOne(self, a, b, point):
        self.target.curveTo(self.warp(a), self.warp(b), self.warp(point)); self.previous = point

    def _closePath(self):
        self.target.closePath()

    def _endPath(self):
        self.target.endPath()


def braille(cp):
    pen = TTGlyphPen(None)
    # Standard dot numbering: left 1/2/3/7, right 4/5/6/8.
    positions = [(185,650),(185,420),(185,190),(415,650),(415,420),(415,190),(185,-40),(415,-40)]
    for bit, (cx,cy) in enumerate(positions):
        if not (cp-0x2800) & (1 << bit):
            continue
        points = []
        for k in range(16):
            angle = -2*math.pi*k/16
            radius = 53 + 2*math.sin(k*2.3 + bit)
            points.append((round(cx+radius*math.cos(angle)),round(cy+radius*math.sin(angle))))
        pen.moveTo(points[0])
        for point in points[1:]: pen.lineTo(point)
        pen.closePath()
    return pen.glyph()


def build():
    record = source_record()
    source = TTFont(SOURCE)
    gs = source.getGlyphSet(); source_cmap = source.getBestCmap()
    glyphs = {'.notdef': TTGlyphPen(None).glyph()}; cmap = {}
    for cp in [*range(0x2500,0x25a0),*range(0x2800,0x2900)]:
        name = f'u{cp:04X}'; cmap[cp] = name
        if cp >= 0x2800:
            glyphs[name] = braille(cp)
            continue
        pen = TTGlyphPen(None)
        if cp < 0x2580:
            # Source box connections extend slightly beyond its full block.
            # Map those exact endpoints onto the cell, without clipping curves.
            target = InkPen(pen)
            transform = (600/612, 0, 0, 1000/1225, 6*600/612, 246*1000/1225-200)
        else:
            target = pen
            transform = (1, 0, 0, 1000/1213, 0, 240*1000/1213-200)
        gs[source_cmap[cp]].draw(TransformPen(target, transform))
        glyphs[name] = pen.glyph()
    legacy_record = source_record(LEGACY)
    legacy_font = TTFont(LEGACY)
    legacy_glyphs = legacy_font.getGlyphSet()
    legacy_cmap = legacy_font.getBestCmap()
    names = {int(f[0],16): f[1] for line in (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines()
             if (f := line.split(';'))}
    for a, b in legacy_record['include_ranges']:
        for cp in range(a, b+1):
            name = f'u{cp:05X}'; cmap[cp] = name
            pen = TTGlyphPen(None)
            # BabelStone's full cell is x=0..1024, y=-224..800. Snap its
            # occasional 1–2-unit endpoint overshoot onto the shared boundary.
            standalone = any(a<=cp<=b for a,b in legacy_record.get('standalone_ink_ranges',[]))
            variation = 3 if standalone or names[cp].startswith(('BOX DRAWINGS','LARGE TYPE PIECE')) else 0
            target = InkPen(pen, strength=variation, snap_edges=True)
            drawing = DecomposingRecordingPen(legacy_glyphs)
            legacy_glyphs[legacy_cmap[cp]].draw(drawing)
            drawing.replay(TransformPen(target, (600/1024,0,0,1000/1024,0,224*1000/1024-200)))
            glyphs[name] = pen.glyph()
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(list(glyphs)); fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    # Match left-side bearings to actual outline bounds; TrueType scales from
    # the hmtx sidebearing, not just the contour's coordinate origin.
    fb.setupHorizontalMetrics({name:(600, getattr(glyph,'xMin',0)) for name,glyph in glyphs.items()})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    notices = {i: '\n'.join(sorted({n.toUnicode() for f in (source,legacy_font) for n in f['name'].names if n.nameID==i})) for i in (0,13,14)}
    fb.setupNameTable({'familyName':'Dad Grid','styleName':'Regular','uniqueFontIdentifier':'DadGrid-1',
        'fullName':'Dad Grid Regular','psName':'DadGrid-Regular','version':'Version 1.000',
        'copyright':notices[0]+'\nGrid adaptation and Braille drawings: calvins-dad contributors.',
        'licenseDescription':notices[13], 'licenseInfoURL':notices[14]})
    fb.setupOS2(sTypoAscender=800,sTypoDescender=-200,sTypoLineGap=0,usWinAscent=800,usWinDescent=200)
    fb.setupPost(); fb.setupMaxp()
    fb.font['head'].created = fb.font['head'].modified = 2082844800
    fb.font.recalcTimestamp = False
    fb.font.flavor = 'woff2'; fb.font.save(OUT)
    manifest = {'family':'Dad Grid','file':str(OUT.relative_to(ROOT)),
        'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'bytes':OUT.stat().st_size,
        'ranges':sorted([[0x2500,0x259f],[0x2800,0x28ff],*legacy_record['include_ranges']]),
        'squareCellRanges':legacy_record['structural_ranges'],
        'structuralRanges':sorted([[0x2500,0x259f],[0x2800,0x28ff],*legacy_record['structural_ranges']]), 'overrideBase':True,
        'source':record, 'legacySource':legacy_record, 'recipe':3,
        'style':'connected grid; subtle pen variation; semantic block geometry and Braille dots'}
    (ROOT/'js/grid-manifest.js').write_text('// Generated by tools/font/build_grid.py\nexport default '+json.dumps(manifest,separators=(',',':'))+';\n')
    return OUT

if __name__ == '__main__': print(build())
