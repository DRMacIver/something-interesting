"""Build provisional Seal glyphs from verified, provenance-labelled SVGs.

The caller verifies all source blobs first. Use only assigned Unicode 18 Seal
characters whose scan sequence agrees with Unicode's normative CCZ reference.
Upstream review status is retained: alignment is not human glyph approval.
"""
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import Counter
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'build/unicode-sources/kaiyuan'
OUTPUT = SOURCE / 'DadSealSource-Regular.ttf'
# Locally compared with the Unicode chart and compiled outlines. Upstream
# sequence labels alone cannot establish that an automatic crop is correct.
IDENTITY_EXCLUSIONS = {
    0x3F2B9: 'C-08731 crop depicts C-08730 instead',
    0x3F2BA: 'C-08732 crop contains a truncated C-08733 and a page rule',
    0x3F218: 'C-08570 crop contains only part of C-08566 and a page rule',
    0x3EEB1: 'C-07716 crop depicts C-07714 instead',
    0x3EFC6: 'C-07987 crop depicts adjacent C-07986 instead',
    0x3E69A: 'C-05696 crop depicts adjacent C-05697 instead',
    0x3E25D: 'C-04631 crop depicts adjacent C-04632 instead',
    0x3E4E9: 'C-05270 crop contains a damaged C-05271 instead',
    0x3EEB3: 'C-07718 crop contains only the right component of C-07719',
    0x3EEB6: 'C-07721 crop depicts C-07720 instead',
}


def build():
    from audit import inventory
    manifest = ROOT / 'data/font-sources/kaiyuan.json'
    reference = ROOT / 'data/unicode/18.0.0/SealSources.txt'
    fingerprint = hashlib.sha256(manifest.read_bytes() + reference.read_bytes() + Path(__file__).read_bytes()).hexdigest()
    cache = SOURCE / 'built.json'
    if cache.exists() and OUTPUT.exists():
        saved = json.loads(cache.read_text())
        if saved['input'] == fingerprint and saved['output'] == hashlib.sha256(OUTPUT.read_bytes()).hexdigest():
            return OUTPUT
    refs = {}
    for line in reference.read_text().splitlines():
        if '\tkSEAL_CCZSrc\t' in line:
            cp, _, value = line.split('\t')
            refs[int(cp[2:], 16)] = value
    public = inventory()
    rows = {int(r['codepoint'], 16): r for r in csv.DictReader((SOURCE / 'data/provenance/glyphs.csv').open()) if r['codepoint']}
    glyphs = {'.notdef': TTGlyphPen(None).glyph()}
    cmap, statuses, rejected = {}, Counter(), []
    for path in sorted((SOURCE / 'glyphs').glob('u*.svg')):
        cp = int(path.stem[1:], 16)
        row = rows.get(cp)
        reason = None
        if cp in IDENTITY_EXCLUSIONS:
            reason = IDENTITY_EXCLUSIONS[cp]
        elif cp not in public or cp not in refs:
            reason = 'not an assigned public Seal character'
        elif not row or row['status'] not in {'approved', 'manual', 'aligned'}:
            reason = 'no accepted upstream mapping'
        elif row['sequence'] != refs[cp]:
            reason = 'scan reference differs from Unicode 18 CCZ source'
        if reason:
            rejected.append({'codepoint': f'{cp:05X}', 'reason': reason})
            continue
        svg = ET.fromstring(path.read_text())
        if svg.get('data-source') != 'ccz ' + row['sequence']:
            raise ValueError(f'SVG provenance mismatch: {path}')
        recording = RecordingPen()
        for item in svg.findall('{http://www.w3.org/2000/svg}path'):
            parse_path(item.attrib['d'], TransformPen(recording, (1,0,0,-1,0,0)))
        bounds, area = BoundsPen(None), AreaPen(None)
        recording.replay(bounds)
        recording.replay(area)
        if not bounds.bounds or not area.value:
            rejected.append({'codepoint': f'{cp:05X}', 'reason': 'empty outline'})
            continue
        x0,y0,x1,y1 = bounds.bounds
        if x0 < -2 or x1 > 1002 or y0 < -122 or y1 > 882:
            rejected.append({'codepoint': f'{cp:05X}', 'reason': 'outline escapes source em box'})
            continue
        pen = TTGlyphPen(None)
        target = Cu2QuPen(pen, max_err=1.0)
        if area.value > 0:
            target = ReverseContourPen(target)
        recording.replay(target)
        name = path.stem
        glyphs[name] = pen.glyph()
        cmap[cp] = name
        statuses[row['status']] += 1
    font = FontBuilder(1000, isTTF=True)
    font.setupGlyphOrder(list(glyphs))
    font.setupCharacterMap(cmap)
    font.setupGlyf(glyphs)
    for glyph in font.font['glyf'].glyphs.values():
        glyph.recalcBounds(font.font['glyf'])
    font.setupHorizontalMetrics({name: (1000, getattr(glyph, 'xMin', 0)) for name, glyph in glyphs.items()})
    font.setupHorizontalHeader(ascent=880, descent=-120)
    font.setupNameTable({'familyName':'Dad Seal Source', 'styleName':'Regular',
        'uniqueFontIdentifier':'DadSealSource-1.0', 'fullName':'Dad Seal Source Regular',
        'psName':'DadSealSource-Regular', 'version':'Version 1.000',
        'copyright':'Copyright (c) 2026 Kaiyuan Small Seal Font Contributors; derivative packaging for this project.',
        'licenseDescription':(SOURCE/'OFL.txt').read_text(), 'licenseInfoURL':'https://openfontlicense.org'})
    font.setupOS2(sTypoAscender=880, sTypoDescender=-120, usWinAscent=880, usWinDescent=120, fsType=0)
    font.setupPost()
    # Deterministic font timestamps, in seconds since the OpenType epoch.
    font.font['head'].created = font.font['head'].modified = 3876336000
    font.font.recalcTimestamp = False
    font.save(OUTPUT)
    cache.write_text(json.dumps({'input':fingerprint,'output':hashlib.sha256(OUTPUT.read_bytes()).hexdigest()})+'\n')
    report = {'status':'provisional native outlines, not final comic styling', 'unicode':'18.0.0',
        'mapped':len(cmap),'source_review_status':dict(statuses),'rejected':rejected,
        'validation':'Each included SVG data-source and provenance sequence match the Unicode 18 CCZ reference. This does not prove each automatic crop is correct.',
        'provenance':'build/unicode-sources/kaiyuan/data/provenance/glyphs.csv'}
    (ROOT/'docs/seal-source-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Seal:',len(cmap),'mapped;',dict(statuses),';',len(rejected),'excluded',flush=True)
    return OUTPUT
