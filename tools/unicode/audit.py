"""Audit bundled cmap coverage against the pinned Unicode inventory.

This deliberately does NOT equate cmap coverage with shaping or style quality.
Run with the project's Python environment; no host unicodedata dependency.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
VERSION = "18.0.0"
DATA = ROOT / "data" / "unicode" / VERSION


def records(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        body = line.split("#", 1)[0].strip()
        if body:
            yield [field.strip() for field in body.split(";")]


def code_range(field):
    bounds = field.split("..")
    return range(int(bounds[0], 16), int(bounds[-1], 16) + 1)


def properties(path):
    result = {}
    for fields in records(path):
        for cp in code_range(fields[0]):
            result[cp] = fields[1]
    return result


def font_dependent_formats():
    return {cp for fields in records(DATA/'PropList.txt')
            if fields[1]=='Prepended_Concatenation_Mark' for cp in code_range(fields[0])}


def inventory():
    """Assigned public characters, excluding surrogates and private use.

    Expand UnicodeData First/Last ranges: counting rows alone would omit
    almost all Han ideographs and Hangul syllables.
    """
    result = {}
    start = None
    for fields in records(DATA / "UnicodeData.txt"):
        cp, name, category = int(fields[0], 16), fields[1], fields[2]
        if name.endswith(", First>"):
            start = (cp, category)
            continue
        if name.endswith(", Last>"):
            if start is None or start[1] != category:
                raise ValueError("Malformed UnicodeData range")
            points = range(start[0], cp + 1)
            start = None
        else:
            points = [cp]
        if category not in {"Co", "Cs", "Cn"}:
            result.update((point, category) for point in points)
    if start is not None:
        raise ValueError("Unclosed UnicodeData range")
    return result


def sequence_inventory():
    result = defaultdict(set)
    for name in ("emoji/emoji-sequences.txt", "emoji/emoji-zwj-sequences.txt",
                 "emoji/emoji-variation-sequences.txt", "StandardizedVariants.txt"):
        for fields in records(DATA / name):
            if ".." in fields[0]:
                values = ((cp,) for cp in code_range(fields[0]))
            else:
                values = [tuple(int(cp, 16) for cp in fields[0].split())]
            result[name].update(values)
    for name, cps in records(DATA / "NamedSequences.txt"):
        result["NamedSequences.txt"].add(tuple(int(cp, 16) for cp in cps.split()))
    return result


def ranges(points):
    out = []
    for cp in sorted(points):
        if out and cp == out[-1][1] + 1:
            out[-1][1] = cp
        else:
            out.append([cp, cp])
    return [f"{a:04X}" if a == b else f"{a:04X}..{b:04X}" for a, b in out]


def fully_qualified_emoji_gaps(custom_sequences):
    """Keep sequence work visible even when all component codepoints exist."""
    groups = defaultdict(set)
    subgroup = None
    for line in (DATA / 'emoji/emoji-test.txt').read_text().splitlines():
        if line.startswith('# subgroup: '):
            subgroup = line.partition(': ')[2]
        fields = line.partition('#')[0].strip().split(';')
        if len(fields) != 2 or fields[1].strip() != 'fully-qualified':
            continue
        assert subgroup is not None
        groups[subgroup].add(tuple(int(cp, 16) for cp in fields[0].split()))
    rows = []
    for name, required in groups.items():
        missing = required - custom_sequences
        rows.append(dict(subgroup=name, required=len(required),
                         custom_encoded=len(required & custom_sequences),
                         missing=len(missing),
                         missing_examples=[''.join(map(chr, seq))
                                           for seq in sorted(missing)[:6]]))
    return dict(scope='Fully-qualified emoji-test sequences; exact manifest encoding, not proof of rendering or style',
                required=sum(row['required'] for row in rows),
                custom_encoded=sum(row['custom_encoded'] for row in rows),
                missing=sum(row['missing'] for row in rows),
                subgroups=sorted(rows, key=lambda row: (-row['missing'], row['subgroup'])))


def audit():
    chars = inventory()
    scripts = properties(DATA / "Scripts.txt")
    ignorable = set()
    for fields in records(DATA / "DerivedCoreProperties.txt"):
        if fields[1] == "Default_Ignorable_Code_Point":
            ignorable.update(code_range(fields[0]))
    # Most controls require behaviour only. Prepended concatenation marks also
    # have visible drawings, so the drawing/behaviour sets overlap explicitly.
    behavioural = {cp for cp, cat in chars.items()
                   if cat in {"Cc", "Cf", "Zs", "Zl", "Zp"} or cp in ignorable}
    format_glyphs=font_dependent_formats()&chars.keys()
    visible = (set(chars) - behavioural)|format_glyphs
    covered = set()
    fonts = []
    components = {}
    custom_sequences = set()
    native_variations = set()
    packaged_variations = set()
    for manifest_path in (ROOT / 'js').glob('*-manifest.js'):
        entry = json.loads(manifest_path.read_text().split('export default ', 1)[1].rstrip(';\n'))
        custom_sequences.update(tuple(map(ord,text)) for text in entry.get('sequences', []))
        native_variations.update(tuple(map(ord,text)) for text in entry.get('variationSequences', []))
        if entry.get('componentOnly'):
            components[entry['file']] = set(entry['componentOnly'])
            for companion in entry.get('companions', []):
                components[companion['file']] = set(companion.get('componentOnly', entry['componentOnly']))
    for path in sorted((ROOT / "assets/fonts").rglob("*")):
        if path.suffix not in {".woff2", ".ttf", ".otf"}:
            continue
        with TTFont(path) as font:
            cmap = {cp for cp, glyph in font.getBestCmap().items()
                    if font.getGlyphID(glyph) != 0}
            for table in font['cmap'].tables:
                if table.format == 14:
                    packaged_variations.update((cp, selector)
                        for selector, rows in table.uvsDict.items() for cp, _ in rows)
        component_only = cmap & components.get(path.relative_to(ROOT).as_posix(), set())
        cmap -= component_only  # Invisible GSUB inputs are not visible glyph coverage.
        covered.update(cmap)
        fonts.append({"path": str(path.relative_to(ROOT)),
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "public_cmap_entries": len(cmap & chars.keys()),
                      "sequence_component_only_entries": len(component_only)})
    by_script = defaultdict(Counter)
    for cp in visible:
        group = by_script[scripts.get(cp, "Unknown")]
        group["required"] += 1
        group["cmap_present" if cp in covered else "cmap_missing"] += 1
    return {
        "unicode_version": VERSION,
        "status": "incomplete",
        "scope": "Assigned public characters and standardised sequences; no private use or surrogates",
        "assigned_public_characters": len(chars),
        "behavioural_characters": len(behavioural),
        "drawing_and_behaviour_characters":len(visible&behavioural),
        "font_dependent_format_characters":len(format_glyphs),
        "font_dependent_format_ranges":ranges(format_glyphs),
        "visible_characters": len(visible),
        "visible_cmap_present": len(visible & covered),
        "visible_cmap_missing": len(visible - covered),
        "missing_ranges": ranges(visible - covered),
        "by_script": dict(sorted(by_script.items())),
        "sequence_inventories": {name: {"required": len(values), "custom_encoded": len(values & custom_sequences), "standalone_native_variations_encoded": len(values & native_variations), "packaged_format14_encoded": len(values & packaged_variations), "validated": 0}
                                 for name, values in sequence_inventory().items()},
        "fully_qualified_emoji": fully_qualified_emoji_gaps(custom_sequences),
        "fonts": fonts,
        "validation": {
            "cmap": "Presence only, not proof of correct outlines or shaping",
            "shaping": "pending", "visual_style": "pending",
            "browser_rendering": "pending", "sequences": "pending",
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/unicode-coverage.json")
    args = parser.parse_args()
    result = audit()
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"Unicode {VERSION}: {result['visible_cmap_present']} / "
          f"{result['visible_characters']} visible characters have bundled cmap entries")


if __name__ == "__main__":
    main()
