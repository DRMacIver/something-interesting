"""Verify licensed source caches and audit their Unicode coverage.

These are candidate sources, not completed custom lettering. Do not add their
coverage to the delivered font report until derived assets are actually built.
"""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys
from zipfile import ZipFile

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/unicode"))
from audit import DATA, inventory, properties, ranges


def verify_sources():
    paths = []
    builders = []
    for manifest in sorted((ROOT / "data/font-sources").glob("*.json")):
        if "files" not in (source := json.loads(manifest.read_text())):
            continue
        if source.get("builder"):
            builders.append(source)
        for entry in source["files"]:
            path = ROOT / entry["path"]
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if digest != entry["sha256"]:
                raise ValueError(f"Source hash mismatch: {path}")
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != entry["git_blob_sha1"]:
                raise ValueError(f"Upstream blob mismatch: {path}")
            if path.suffix in {".ttf", ".otf"}:
                if entry.get("build_target") != "donor":
                    paths.append(path)
            elif path.suffix == ".zip":
                with ZipFile(path) as archive:
                    for name in archive.namelist():
                        # Extract only font files, never executable archive paths.
                        if name.endswith(".ttf") and Path(name).name == name:
                            target = path.parent.parent / "extracted" / name
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_bytes(archive.read(name))
                            paths.append(target)
    for builder in builders:
        if builder["builder"] == "seal":
            from build_seal import build
            paths.append(build())
        elif builder["builder"] == "seal-recovery":
            from build_seal_recovery import build
            paths.append(build(builder))
        elif builder["builder"] == "seal-sans":
            from build_seal_sans import build_registered
            paths.append(build_registered())
        elif builder["builder"] == "tai-yo":
            from build_tai_yo import build_registered
            paths.append(build_registered())
        elif builder["builder"] == "garay":
            from build_garay import build_registered
            paths.append(build_registered())
        elif builder["builder"] == "tolong":
            from build_tolong import build_registered
            paths.append(build_registered())
        elif builder["builder"] == "glyphs":
            from build_glyphs import build
            paths.append(build(builder))
        else:
            raise ValueError(f"Unknown font source builder: {builder}")
    return paths


def main():
    characters = inventory()
    scripts = properties(DATA / "Scripts.txt")
    scopes = {entry['path']: entry['include_ranges']
              for file in (ROOT / 'data/font-sources').glob('*.json')
              for entry in json.loads(file.read_text()).get('files', [])
              if 'include_ranges' in entry}
    fonts = []
    union = set()
    for path in verify_sources():
        with TTFont(path) as font:
            cmap = {cp for cp, name in font.getBestCmap().items() if font.getGlyphID(name) != 0}
            scope = scopes.get(path.relative_to(ROOT).as_posix())
            if scope is not None:
                cmap &= {cp for a, b in scope for cp in range(a, b + 1)}
            families = sorted({n.toUnicode() for n in font["name"].names if n.nameID == 1})
            notices = sorted({n.toUnicode() for n in font["name"].names if n.nameID in {0, 13, 14}})
            variation_count = sum(len(pairs) for t in font["cmap"].tables if t.format == 14
                                  for pairs in t.uvsDict.values())
            fonts.append({"path": path.relative_to(ROOT).as_posix(), "families": families,
                          "public_cmap_entries": len(cmap & characters.keys()),
                          "scripts": dict(Counter(scripts.get(cp, "Unknown") for cp in cmap & characters.keys())),
                          "has_gsub": "GSUB" in font, "has_gpos": "GPOS" in font,
                          "variation_mappings": variation_count, "notices": notices,
                          "style_validation": "candidate; not approved final custom lettering"})
            union.update(cmap)
    missing = characters.keys() - union
    report = {"unicode_version": "18.0.0", "status": "source inventory only",
              "public_characters": len(characters), "source_cmap_present": len(union & characters.keys()),
              "source_cmap_missing": len(missing),
              "missing_by_script": dict(Counter(scripts.get(cp, "Unknown") for cp in missing).most_common()),
              "missing_ranges": ranges(missing), "fonts": fonts}
    out = ROOT / "docs/unicode-font-sources.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(fonts)} font sources; {report['source_cmap_present']} public characters represented; "
          f"{len(missing)} still absent (includes behavioural characters)")
    print(report["missing_by_script"])


if __name__ == "__main__":
    main()
