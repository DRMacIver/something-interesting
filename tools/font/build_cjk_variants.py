"""Map standardized CJK variants to their specified compatibility drawings.

Unicode defines these sequences by an existing compatibility ideograph, not by
an approximate stylistic description. Copy its pinned CC0 Jigmo drawing into an independently verified native
variant, then apply the guarded finer pen finish.
Ordinary Han lettering remains in the existing script fonts.
"""
import argparse
import hashlib
import io
import json
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

from native_variations import variation_ranges

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/'data/unicode/18.0.0'


def variants():
    pins = json.loads((ROOT/'data/unicode/sources.json').read_text())['files']
    for name in ['StandardizedVariants.txt', 'UnicodeData.txt']:
        expected = next(e['sha256'] for e in pins if e['path'] == '18.0.0/'+name)
        if hashlib.sha256((DATA/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Unverified Unicode source: '+name)
    decompositions = {int(f[0], 16): f[5] for line in (DATA/'UnicodeData.txt').read_text().splitlines()
                      if (f := line.split(';'))}
    for line in (DATA/'StandardizedVariants.txt').read_text().splitlines():
        body = line.split('#', 1)[0].strip()
        if not body:
            continue
        sequence, description, *_ = body.split(';')
        if not description.strip().startswith('CJK COMPATIBILITY IDEOGRAPH-'):
            continue
        base, selector = (int(cp, 16) for cp in sequence.split())
        target = int(description.strip().rsplit('-', 1)[1], 16)
        if decompositions[target].split() != [f'{base:04X}']:
            raise ValueError('Compatibility decomposition disagrees with standardized variant')
        yield base, selector, target


def sources():
    spec = json.loads((ROOT/'data/font-sources/jigmo.json').read_text())
    entry = next(e for e in spec['files'] if e['path'].endswith('.zip'))
    path = ROOT/entry['path']
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError('Unverified Jigmo archive')
    result = []
    with ZipFile(path) as archive:
        for name in ['Jigmo.ttf', 'Jigmo2.ttf', 'Jigmo3.ttf']:
            raw = archive.read(name)
            font = TTFont(io.BytesIO(raw))
            result.append((font, dict(archive=entry['path'], archiveSha256=entry['sha256'],
                                     member=name, sha256=hashlib.sha256(raw).hexdigest(),
                                     licence='assets/fonts/licenses/Jigmo-CC0.txt')))
    assert len({font['head'].unitsPerEm for font, _ in result}) == 1
    return result


def build(output_root=None):
    output_root = Path(output_root) if output_root is not None else ROOT
    if not output_root.is_absolute():
        output_root = ROOT / output_root
    donors = sources()
    glyphs = {'.notdef': TTGlyphPen(None).glyph()}
    metrics = {'.notdef': (1024, 0)}
    mapping, uvs, review = {}, {}, []

    def copy_glyph(font, source_name, name, prefix):
        if name in glyphs:
            return
        glyph = deepcopy(font['glyf'][source_name])
        if glyph.isComposite():
            for component in glyph.components:
                child = prefix+'.'+component.glyphName
                copy_glyph(font, component.glyphName, child, prefix)
                component.glyphName = child
        glyphs[name] = glyph
        metrics[name] = font['hmtx'][source_name]

    def copy(cp, name):
        font, provenance = next((f, p) for f, p in donors if cp in f.getBestCmap())
        source_name = font.getBestCmap()[cp]
        # Retain native contours (including repeated closing points), component
        # transforms and instructions rather than retracing the drawing.
        copy_glyph(font, source_name, name, provenance['member'].replace('.ttf', ''))
        return dict(source=provenance['member'], sourceGlyph=source_name, codepoint=cp)

    for base, selector, target in variants():
        if base not in mapping:
            mapping[base] = f'u{base:X}'
            copy(base, mapping[base])
        name = f'u{base:X}.vs{selector:X}'
        provenance = copy(target, name)
        uvs.setdefault(selector, []).append((base, name))
        review.append(dict(base=base, selector=selector, target=target, glyph=name, drawing=provenance))
    font = donors[0][0]
    fb = FontBuilder(font['head'].unitsPerEm, isTTF=True)
    fb.setupGlyphOrder(list(glyphs))
    fb.setupCharacterMap(mapping)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=995, descent=-169)
    fb.setupOS2(sTypoAscender=880, sTypoDescender=-144, sTypoLineGap=92,
                usWinAscent=995, usWinDescent=169)
    fb.setupNameTable(dict(familyName='Dad CJK Variants', styleName='Regular',
                          uniqueFontIdentifier='DadCJKVariants-001', fullName='Dad CJK Variants',
                          psName='DadCJKVariants', version='Version 0.001'))
    fb.setupPost()
    fb.setupMaxp()
    table = CmapSubtable.newSubtable(14)
    table.platformID, table.platEncID, table.language, table.cmap = 0, 5, 0, {}
    table.uvsDict = uvs
    fb.font['cmap'].tables.append(table)
    fb.font['head'].created = fb.font['head'].modified = 2082844800
    fb.font.recalcTimestamp = False
    # The frozen native variant proves the mixed donor identities separately
    # from their pen finish; a profile name is not a single-donor provenance.
    frozen = ROOT/'output/font-review/supplemental-production-baselines/dad-cjk-variants.woff2'
    if not frozen.exists():
        raise ValueError('Freeze the native CJK variant and its manifest before applying the dense finish')
    mixed_input = dict(file=frozen.relative_to(ROOT).as_posix(),
                       sha256=hashlib.sha256(frozen.read_bytes()).hexdigest(),
                       sources=[p for _, p in donors])
    from dense_native_adapter import apply as apply_dense, recipe_hash
    treatment = apply_dense(fb.font, 'Jigmo.ttf',
                            report_dir=ROOT/'output/font-review/dense-production')
    fb.font.flavor = 'woff2'
    path = output_root/'assets/fonts/dad-cjk-variants.woff2'
    path.parent.mkdir(parents=True, exist_ok=True)
    fb.save(path)
    entry = dict(family='Dad CJK Variants', variationOnly=True, file=path.relative_to(ROOT).as_posix(),
                 sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size,
                 ranges=[[cp, cp] for cp in sorted(mapping)], nativeVariations=variation_ranges(fb.font),
                 variationSequences=[chr(r['base'])+chr(r['selector']) for r in review],
                 sources=[p for _, p in donors], licence='assets/fonts/licenses/Jigmo-CC0.txt',
                 mixedNativeInput=mixed_input, denseTreatment=treatment,
                 recipe='native-compatibility:dense-native-pen:'+recipe_hash('Jigmo.ttf'),
                 style='Native compatibility identities with guarded finer pen treatment; rejected details retain their native drawings; specialist review provisional')
    manifest_path=output_root/'js/cjk-variant-manifest.js'
    manifest_path.parent.mkdir(parents=True,exist_ok=True)
    manifest_path.write_text('// Generated by tools/font/build_cjk_variants.py\nexport default '+json.dumps(entry, separators=(',', ':'))+';\n')
    report = dict(unicode='18.0.0', dataSha256=hashlib.sha256((DATA/'StandardizedVariants.txt').read_bytes()).hexdigest(),
                  sources=entry['sources'], mixedNativeInput=mixed_input, denseTreatment=treatment,
                  status='Native compatibility identities retained through guarded finer ink; representative visual and specialist review recorded separately', variants=review)
    review_path=output_root/'docs/cjk-variant-review.json'
    review_path.parent.mkdir(parents=True,exist_ok=True)
    review_path.write_text(json.dumps(report, indent=2)+'\n')
    print(f'{len(review)} standardized CJK variants on {len(mapping)} bases; {entry["bytes"]} bytes')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root',type=Path,help='Write isolated assets/manifests/review under this directory')
    build(parser.parse_args().output_root)
