"""Every standardized CJK sequence selects its specified compatibility drawing."""
import hashlib
from pathlib import Path
import json
import sys

from fontTools.pens.recordingPen import DecomposingRecordingPen
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import ROOT, shape
from font_baseline_checks import reviewed_dense_change, reviewed_later_change

sys.path.insert(0, str(ROOT/'tools/font'))
import build_cjk_variants as builder

PATH = ROOT/'assets/fonts/dad-cjk-variants.woff2'


def assert_cjk_variant_lineage(path,manifest_path,review_path,isolated_root=None):
    expected = set(builder.variants())
    assert len(expected) == 1002
    report = json.loads(review_path.read_text())
    manifest = json.loads(manifest_path.read_text().split('export default ',1)[1].rstrip(';\n'))
    assert {(r['base'], r['selector'], r['target']) for r in report['variants']} == expected
    sources = {p['member']: f for f, p in builder.sources()}
    source_glyphs = {name: f.getGlyphSet() for name, f in sources.items()}
    font = TTFont(path)
    if manifest.get('denseTreatment'):
        frozen=ROOT/'output/font-review/supplemental-production-baselines/dad-cjk-variants.woff2'
        before=json.loads(frozen.with_suffix('.json').read_text())
        if isolated_root is None:assert reviewed_later_change(before,manifest)
        else:assert reviewed_dense_change(before,manifest,isolated_root=isolated_root)
        native=TTFont(frozen)
        assert report['mixedNativeInput']==manifest['mixedNativeInput']
        assert report['denseTreatment']==manifest['denseTreatment']
    else:
        native=font
    glyphs = native.getGlyphSet()
    for row in report['variants']:
        base, selector, target = row['base'], row['selector'], row['target']
        source_name = row['drawing']['source']
        source = sources[source_name]
        source_glyph = source.getBestCmap()[target]
        assert source_glyph == row['drawing']['sourceGlyph']
        a = DecomposingRecordingPen(source_glyphs[source_name])
        b = DecomposingRecordingPen(glyphs)
        source_glyphs[source_name][source_glyph].draw(a)
        glyphs[row['glyph']].draw(b)
        # Always prove pinned compatibility identity on the frozen native input;
        # dense output is separately verified against approved native cache keys.
        assert a.value == b.value, row
        assert native['hmtx'][row['glyph']] == source['hmtx'][source_glyph], row
        assert font['hmtx'][row['glyph']] == native['hmtx'][row['glyph']], row
        shaped = shape(path, chr(base)+chr(selector), True)
        assert shaped == [(font.getGlyphID(row['glyph']), source['hmtx'][source_glyph][0], 0, 0, 0)], row
        assert shaped[0][1] > 0


def test_all_standardized_cjk_pairs_keep_pinned_native_identity_and_reviewed_finish():
    assert_cjk_variant_lineage(PATH,ROOT/'js/cjk-variant-manifest.js',ROOT/'docs/cjk-variant-review.json')


def test_cjk_variants_reproduce_font_manifest_and_review():
    import tempfile
    (ROOT/'tmp').mkdir(exist_ok=True)
    # The builder's relative asset URLs use repository-root paths. Keep the
    # temporary output inside that root, with no public font/manifest writes.
    with tempfile.TemporaryDirectory(prefix='cjk-variant-reproduction-',dir=ROOT/'tmp') as directory:
        output=Path(directory)
        builder.build(output_root=output)
        assert (output/'assets/fonts/dad-cjk-variants.woff2').read_bytes()==PATH.read_bytes()
        expected=json.loads((ROOT/'js/cjk-variant-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
        actual=json.loads((output/'js/cjk-variant-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
        assert (ROOT/actual['file']).resolve()==(output/'assets/fonts/dad-cjk-variants.woff2').resolve()
        actual['file']=expected['file']
        assert actual==expected
        assert (output/'docs/cjk-variant-review.json').read_bytes()==(ROOT/'docs/cjk-variant-review.json').read_bytes()


def test_cjk_variant_inventory_is_exact_and_ordinary_bases_are_not_overrides():
    manifest = json.loads((ROOT/'js/cjk-variant-manifest.js').read_text().split('export default ', 1)[1].rstrip(';\n'))
    assert manifest['variationOnly'] and not manifest.get('overrideBase')
    assert set(manifest['variationSequences']) == {chr(cp)+chr(vs) for cp, vs, _ in builder.variants()}
    font = TTFont(PATH)
    assert len(font.getBestCmap()) == 902
    assert font['name'].getDebugName(1) == 'Dad CJK Variants'
    assert manifest['sha256'] == hashlib.sha256(PATH.read_bytes()).hexdigest()
