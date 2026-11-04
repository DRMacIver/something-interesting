from font_baseline_checks import pinned_packaging_font
"""Native default and explicit variation drawings must survive subsetting."""
import sys
import json
from pathlib import Path

import pytest
from fontTools import subset
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/font'))
from native_variations import retain_selectors, variation_bases, variation_ranges


def test_standardized_mapping_inventory_has_only_the_tested_contextual_exceptions():
    from fontTools.ttLib import TTFont as MetadataTTFont
    standard=set()
    for row in (ROOT/'data/unicode/18.0.0/StandardizedVariants.txt').read_text().splitlines():
        body=row.split('#')[0].strip()
        if body:standard.add(tuple(int(v,16) for v in body.split(';')[0].split()))
    paths=set()
    for name in ['font-manifest','cjk-variant-manifest','math-variant-manifest','egyptian-variant-manifest']:
        manifest=json.loads((ROOT/f'js/{name}.js').read_text().split('export default ',1)[1].rstrip(';\n'))
        paths.update(e['file'] for e in manifest.get('fonts',[manifest]))
    mapped=set()
    for path in paths:
        with MetadataTTFont(ROOT/path,lazy=True) as font:
            mapped.update((cp,s) for t in font['cmap'].tables if t.format==14 for s,rows in t.uvsDict.items() for cp,_ in rows)
    contextual={pair for pair in standard if 0x1800<=pair[0]<=0x18af or 0xa840<=pair[0]<=0xa87f or 0x10ac0<=pair[0]<=0x10aff}
    # The separate contextual suite proves actual source drawing/position
    # changes in four word positions; this check only closes inventory gaps.
    assert len(standard)==1437 and len(contextual)==128
    assert len(standard&mapped)==1309
    assert standard-mapped==contextual


@pytest.mark.parametrize('source', [
    'noto/NotoSansMath-Regular.ttf',
    'wenkai/fonts/TTF/LXGWWenKai-Regular.ttf',
    'unicodia/PadaukBook-Regular.ttf',
])
def test_native_variants_keep_drawings_metrics_and_only_requested_bases(source):
    font = TTFont(ROOT/'build/unicode-sources'/source)
    records = [(selector, cp, name) for table in font['cmap'].tables
               if table.format == 14 for selector, rows in table.uvsDict.items()
               for cp, name in rows]
    assert records
    # Split a source as the real builder does; do not keep unrelated UVS bases.
    points = {cp for _, cp, _ in records[::2]}
    source_variants = {(selector, cp): name or font.getBestCmap()[cp]
                       for selector, cp, name in records}
    requested = {key for key in source_variants if key[1] in points}
    before = {key: (font['glyf'][name].compile(font['glyf']), font['hmtx'][name])
              for key, name in source_variants.items()}
    options = subset.Options()
    options.glyph_names = True
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=retain_selectors(font, points))
    sub.subset(font)
    actual = {(selector, cp): name or font.getBestCmap()[cp]
              for table in font['cmap'].tables if table.format == 14
              for selector, rows in table.uvsDict.items() for cp, name in rows}
    # Layout closure can retain additional ordinary base mappings. Their UVS
    # records are valid too; no retained base may lose its native variant.
    expected = {key: name for key, name in source_variants.items()
                if key[1] in font.getBestCmap()}
    assert requested <= set(actual)
    assert actual == expected
    for key, name in actual.items():
        assert (font['glyf'][name].compile(font['glyf']), font['hmtx'][name]) == before[key]
    metadata = variation_ranges(font)
    assert {(int(selector), cp) for selector, ranges in metadata.items()
            for a, b in ranges for cp in range(a, b+1)} == set(expected)


def test_selector_is_not_requested_for_an_absent_base():
    font = TTFont(ROOT/'build/unicode-sources/noto/NotoSansMath-Regular.ttf')
    assert retain_selectors(font, set()) == set()
    assert variation_bases(font)


@pytest.mark.parametrize('source', [
    'noto/NotoSansMath-Regular.ttf',
    'wenkai/fonts/TTF/LXGWWenKai-Regular.ttf',
    'unicodia/PadaukBook-Regular.ttf',
])
def test_production_shards_retain_native_variation_outlines_and_metadata(source):
    manifest = json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ', 1)[1].rstrip(';\n'))
    entries = [e for e in manifest['fonts'] if e['source'] == 'build/unicode-sources/'+source]
    assert entries
    original = TTFont(ROOT/'build/unicode-sources'/source)
    original_glyphs = original.getGlyphSet()
    source_records = {(selector, cp): name or original.getBestCmap()[cp]
                      for t in original['cmap'].tables if t.format == 14
                      for selector, rows in t.uvsDict.items() for cp, name in rows}
    checked = 0
    for entry in entries:
        packaged = TTFont(ROOT/entry['file'])
        native = pinned_packaging_font(entry)
        cmap = packaged.getBestCmap()
        expected = {key: name for key, name in source_records.items() if key[1] in cmap}
        actual = {(selector, cp): name or cmap[cp]
                  for t in packaged['cmap'].tables if t.format == 14
                  for selector, rows in t.uvsDict.items() for cp, name in rows}
        assert expected.keys() <= actual.keys(), entry['file']
        assert entry['nativeVariations'] == variation_ranges(packaged)
        glyphs = native.getGlyphSet()
        native_cmap=native.getBestCmap()
        native_records={(selector,cp):name or native_cmap[cp] for t in native['cmap'].tables if t.format==14 for selector,rows in t.uvsDict.items() for cp,name in rows}
        for key, original_name in expected.items():
            name = native_records[key]
            a = DecomposingRecordingPen(original_glyphs)
            b = DecomposingRecordingPen(glyphs)
            original_glyphs[original_name].draw(a)
            glyphs[name].draw(b)
            assert a.value == b.value, (entry['file'], key)
            assert original['hmtx'][original_name] == native['hmtx'][name] == packaged['hmtx'][actual[key]]
            checked += 1
    assert checked > 0


def test_variations_are_packaged_even_when_ordinary_bases_have_an_earlier_font():
    manifest = json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ', 1)[1].rstrip(';\n'))
    entries = manifest['fonts']
    base, selector = 0x3402, 0xe0101
    ordinary = next(e for e in entries if any(a <= base <= b for a, b in e['ranges']))
    assert not ordinary['source'].endswith('/Jigmo.ttf')
    variant = next(e for e in entries if any(a <= base <= b for a, b in e.get('nativeVariations', {}).get(str(selector), [])))
    assert variant['source'].endswith('/Jigmo.ttf')
    font = TTFont(ROOT/variant['file'])
    records = {cp: name for t in font['cmap'].tables if t.format == 14
               for cp, name in t.uvsDict.get(selector, [])}
    assert records[base] and records[base] != font.getBestCmap()[base]
    original = TTFont(ROOT/variant['source'])
    original_records = {cp: name for t in original['cmap'].tables if t.format == 14
                        for cp, name in t.uvsDict.get(selector, [])}
    a = DecomposingRecordingPen(original.getGlyphSet())
    native=pinned_packaging_font(variant)
    native_records={cp:name for t in native['cmap'].tables if t.format==14 for cp,name in t.uvsDict.get(selector,[])}
    b = DecomposingRecordingPen(native.getGlyphSet())
    original.getGlyphSet()[original_records[base]].draw(a)
    native.getGlyphSet()[native_records[base]].draw(b)
    assert a.value == b.value
    assert original['hmtx'][original_records[base]] == font['hmtx'][records[base]]
