"""Standalone archaic SHRII signs retain their identity and spacing."""
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape, ROOT
from test_font_cuneiform import outline
from test_unicode_inventory import audit


def test_archaic_shrii_preserves_native_form_and_spacing_with_pen_adaptation():
    entry = next(e for e in manifest()['fonts'] if e['source'].endswith('/UnicodiaFunky.ttf'))
    source, font = TTFont(ROOT / entry['source']), TTFont(ROOT / entry['file'])
    for cp in (0xC5C, 0xCDC):
        original, actual = outline(source, cp), outline(font, cp)
        assert actual[0] and actual[0] != original[0]
        assert actual[2] == original[2] > 0
        assert all(abs(a - b) <= 4 for a, b in zip(actual[1], original[1]))
        # Independent letters/signs, not zero-width marks or decomposed SHRII.
        glyphs = shape(ROOT / entry['file'], chr(cp) * 3)
        assert len(glyphs) == 3 and all(g[0] and g[1] == actual[2] for g in glyphs)
        assert shape(ROOT / entry['source'], chr(cp)) == shape(ROOT / entry['file'], chr(cp))


def test_all_assigned_telugu_and_kannada_have_bundled_mappings():
    scripts = audit.properties(audit.DATA / 'Scripts.txt')
    required = {cp for cp in audit.inventory() if scripts.get(cp) in {'Telugu', 'Kannada'}}
    m = manifest()
    covered = {cp for e in m['fonts'] for a, b in e['ranges'] for cp in range(a, b + 1)}
    covered.update(cp for a, b in m['baseRanges'] + m['behaviouralRanges'] for cp in range(a, b + 1))
    assert required <= covered
