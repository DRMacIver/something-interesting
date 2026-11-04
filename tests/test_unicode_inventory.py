"""The full Unicode inventory must not shrink to what our fonts cover."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools/unicode" / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


audit = module("audit")


def test_pinned_inventory_expands_ranges_and_excludes_private_use():
    chars = audit.inventory()
    for cp in [0x4E00, 0x4E01, 0xAC00, 0xAC01, 0x13000, 0x18E00, 0x3D000]:
        assert cp in chars, hex(cp)
    for cp in [0xD800, 0xE000, 0xF0000, 0x10FFFF]:
        assert cp not in chars, hex(cp)
    assert len(chars) > 172000


def test_unicode_sources_match_pinned_hashes():
    assert module("sources").verify() >= 26


def test_browser_tables_are_reproducible():
    assert (ROOT / "js/unicode-data.js").read_text() == module("build_tables").build()


def test_sequence_inventory_includes_joiners_modifiers_flags_and_variants():
    sequences = audit.sequence_inventory()
    all_sequences = set().union(*sequences.values())
    for text in ["👩🏽‍🚀", "🇫🇷", "❤️", "1️⃣"]:
        assert tuple(map(ord, text)) in all_sequences


def test_qualified_emoji_audit_does_not_count_components_or_unqualified_aliases(tmp_path, monkeypatch):
    (tmp_path/'emoji').mkdir()
    (tmp_path/'emoji/emoji-test.txt').write_text('''# subgroup: faces
1F600 ; fully-qualified # face
# subgroup: emotion
2764 ; unqualified # text heart is not the fully qualified emoji
2764 FE0F ; fully-qualified # emoji heart
# subgroup: skin-tone
1F3FB ; component # modifier alone is not a complete emoji
# subgroup: country-flag
1F1EB 1F1F7 ; fully-qualified # France
''')
    monkeypatch.setattr(audit, 'DATA', tmp_path)
    report = audit.fully_qualified_emoji_gaps({(0x1F600,), (0x2764,), (0x1F3FB,)})
    assert (report['required'], report['custom_encoded'], report['missing']) == (3, 1, 2)
    groups = {row['subgroup']: row for row in report['subgroups']}
    assert 'skin-tone' not in groups
    assert groups['faces']['missing'] == 0
    assert groups['emotion']['missing_examples'] == ['❤️']
    assert groups['country-flag']['missing_examples'] == ['🇫🇷']


def test_sequence_components_do_not_inflate_visible_glyph_coverage():
    from fontTools.ttLib import TTFont
    report=audit.audit()
    font=next(f for f in report['fonts'] if f['path']=='assets/fonts/dad-emoji.woff2')
    # Derive the expected split from actual drawings, independently of the
    # routing manifest consumed by the audit. Fixed early-prototype totals
    # become stale whenever a new emoji group is added.
    public = audit.inventory()
    with TTFont(ROOT/'assets/fonts/dad-emoji.woff2') as emoji:
        cmap = emoji.getBestCmap()
        drawn = {cp for cp, name in cmap.items()
                 if cp in public and emoji['glyf'][name].numberOfContours != 0}
        empty = {cp for cp, name in cmap.items()
                 if emoji['glyf'][name].numberOfContours == 0}
    assert ord('😀') in drawn
    assert set(range(0x1F3FB, 0x1F400)) <= drawn
    assert 0x200D in empty  # Joining control remains an invisible GSUB input.
    assert font['public_cmap_entries'] == len(drawn)
    assert font['sequence_component_only_entries'] == len(empty)
    assert font['public_cmap_entries'] < len(set(cmap) & public.keys())
    companion=next(f for f in report['fonts'] if f['path']=='assets/fonts/dad-emoji-ink.woff2')
    assert companion['public_cmap_entries'] == len(drawn)
    assert companion['sequence_component_only_entries'] == len(empty)
    assert any(row['custom_encoded'] for row in report['sequence_inventories'].values())
