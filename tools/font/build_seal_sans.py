"""Build the separate AGPL Seal supplement from pinned native cubic drawings.

Also included verbatim in the downloadable corresponding-source package.
Only fontTools and Brotli are needed; no upstream scripts are executed.
"""
# SPDX-License-Identifier: AGPL-3.0-only
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_STORED

from fontTools.fontBuilder import FontBuilder
from fontTools import subset
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = 'build/unicode-sources/seal-sans/DadSealSans-Regular.otf'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_font(source_path, spec, output):
    original = TTFont(source_path, recalcTimestamp=False)
    assert original['head'].unitsPerEm == 1024
    points = sorted({cp for a, b in spec['include_ranges'] for cp in range(a, b+1)})
    cmap = original.getBestCmap()
    assert len(points) == 139 and set(points) <= cmap.keys()
    shift = spec['baseline_translation']
    names = {cp: f'seal.u{cp:X}' for cp in points}
    order = ['.notdef'] + list(names.values())
    glyphs = original.getGlyphSet()
    charstrings = {}
    metrics = {}
    empty = T2CharStringPen(1024, None, roundTolerance=0)
    charstrings['.notdef'] = empty.getCharString()
    metrics['.notdef'] = (1024, 0)
    for cp, name in names.items():
        source_name = cmap[cp]
        advance, lsb = original['hmtx'][source_name]
        pen = T2CharStringPen(advance, None, roundTolerance=0)
        glyphs[source_name].draw(TransformPen(pen, (1, 0, 0, 1, 0, shift)))
        charstrings[name] = pen.getCharString()
        metrics[name] = (advance, lsb)
    fb = FontBuilder(1024, isTTF=False)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(names)
    fb.setupCFF('DadSealSans', {
        'FullName': 'Dad Seal Sans', 'FamilyName': 'Dad Seal Sans', 'Weight': 'Regular',
        'Copyright': original['name'].getDebugName(0),
        'Notice': 'Modified 2026-11-03: 139-character subset, baseline +340, renamed. AGPL-3.0; corresponding source supplied.',
    }, charstrings, {})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=852, descent=-172)
    fb.setupNameTable({
        'familyName': 'Dad Seal Sans', 'styleName': 'Regular',
        'uniqueFontIdentifier': 'Dad Seal Sans 1.0', 'fullName': 'Dad Seal Sans',
        'psName': 'DadSealSans', 'version': 'Version 1.000',
        'copyright': original['name'].getDebugName(0),
        'manufacturer': 'Ghimist; modified for calvins-dad', 'designer': 'Ghimist',
        'description': 'Modified 2026-11-03: 139 Seal drawings only, translated +340 y; native cubic curves and advances retained. Unrelated tone UVS and colour/layout tables excluded. Horizontal text only.',
        'licenseDescription': 'GNU Affero General Public License v3.0. See SealSans-AGPL-3.0.txt. Complete corresponding source: ../sources/DadSealSans-source.zip',
        'licenseInfoURL': 'https://www.gnu.org/licenses/agpl-3.0.html',
        'vendorURL': spec['repository'],
    })
    fb.setupOS2(sTypoAscender=852, sTypoDescender=-172, sTypoLineGap=0,
                usWinAscent=1024, usWinDescent=340)
    fb.setupPost()
    fb.font['head'].created = fb.font['head'].modified = 2082844800
    fb.font.recalcTimestamp = False
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fb.save(output)
    return output


def source_package(spec):
    output = ROOT/spec['source_package']
    output.parent.mkdir(parents=True, exist_ok=True)
    font = next(f for f in spec['files'] if f['path'].endswith('.otf'))
    archive = next(f for f in spec['files'] if f['path'].endswith('.zip'))
    readme = f'''Dad Seal Sans — complete corresponding source

Copyright (c) 2026 Ghimist. GNU Affero General Public License v3.0.
Modified 2026-11-03 for calvins-dad. Supplied separately from other fonts.
Upstream: {spec['repository']} at {spec['commit']}.

upstream.zip is the complete unmodified pinned upstream repository, including
the UFO, FontCreator project, mapping data, original font, scripts and licence.
SealSans-Regular_v1.otf is the exact original build input (also in upstream.zip).
build_seal_sans.py and seal-sans.json are our full modification source/recipe.

Rebuild using Python 3.12+:
  python -m pip install -r requirements.txt
  python build_seal_sans.py --source SealSans-Regular_v1.otf --spec seal-sans.json --output DadSealSans-Regular.otf
  python build_seal_sans.py --source SealSans-Regular_v1.otf --spec seal-sans.json --output DadSealSans-Regular.otf --woff2 rebuilt.woff2

The supplied make_webfont function implements the complete final packaging
steps for this font: subset these same 139 characters, rename to the manifest
family, and encode WOFF2. Its standalone output is tested byte-for-byte against
the app's font. See the source manifest for SHA-256 pins.
No Unicode chart artwork is used as build input.
All selected native cubic curves are translated +340 vertically; advances and
horizontal coordinates retained. Upstream tone UVS, colour, and layout tables
are excluded. No vertical typography is claimed. This is a provisional native
source style; reference topology was compared, not specialist reader approval.

The site exports raster PNGs; it does not embed font programs in exports.
Retain this source download and licence beside any redistributed webfont.
'''
    contents = {
        'README.txt': readme.encode(), 'seal-sans.json': json.dumps(spec, indent=2).encode(),
        'build_seal_sans.py': Path(__file__).read_bytes(),
        'requirements.txt': b'fonttools==4.68.0\nbrotli==1.2.1\n',
        'LICENSE': (ROOT/spec['licence']).read_bytes(),
        'SealSans-Regular_v1.otf': (ROOT/font['path']).read_bytes(),
        'upstream.zip': (ROOT/archive['path']).read_bytes(),
    }
    # Stable bytes without depending on local file mtimes.
    with ZipFile(output, 'w', compression=ZIP_STORED) as package:
        for name, raw in sorted(contents.items()):
            info = ZipInfo(name, (2026, 11, 3, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            package.writestr(info, raw)
    return output


def make_webfont(path, output):
    """Standalone reproduction of this source's generic app packaging steps."""
    identity = hashlib.sha256((OUTPUT+':0').encode()).hexdigest()[:12]
    family = 'Dad Script '+identity
    font = TTFont(path, recalcTimestamp=False)
    options = subset.Options()
    options.layout_features = ['*']
    options.name_IDs = ['*']; options.name_legacy = True; options.name_languages = ['*']
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=font.getBestCmap())
    sub.subset(font)
    for record in font['name'].names:
        if record.nameID in {1, 2, 3, 4, 6, 16, 17}:
            value = 'Regular' if record.nameID in {2, 17} else family.replace(' ', '') if record.nameID == 6 else family
            record.string = value.encode(record.getEncoding(), errors='replace')
    cff = font['CFF '].cff
    cff.fontNames = [family.replace(' ', '')]
    for top in cff.topDictIndex:
        top.FamilyName = top.FullName = family
    font.flavor = 'woff2'
    font.save(output)


def build_registered():
    spec = json.loads((ROOT/'data/font-sources/seal-sans.json').read_text())
    for entry in spec['files']:
        assert digest(ROOT/entry['path']) == entry['sha256']
    source = next(e for e in spec['files'] if e['path'].endswith('.otf'))
    path = make_font(ROOT/source['path'], spec, ROOT/OUTPUT)
    source_package(spec)
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source'); parser.add_argument('--spec'); parser.add_argument('--output'); parser.add_argument('--woff2')
    args = parser.parse_args()
    if args.source and args.spec and args.output:
        make_font(args.source, json.loads(Path(args.spec).read_text()), args.output)
        if args.woff2:make_webfont(args.output, args.woff2)
    else:
        print(build_registered())
