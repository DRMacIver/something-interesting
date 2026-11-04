"""Record and verify pinned upstream data hashes and download locations."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "data/unicode"
MANIFEST = BASE / "sources.json"
EMOJI_FILES = {"emoji-sequences.txt", "emoji-zwj-sequences.txt", "emoji-test.txt"}


def snapshot():
    files = []
    for path in sorted((BASE / "18.0.0").rglob("*.txt")):
        relative = path.relative_to(BASE / "18.0.0").as_posix()
        upstream = ("emoji/" + path.name if path.name in EMOJI_FILES else "ucd/" + relative)
        files.append({"path": path.relative_to(BASE).as_posix(),
                      "url": "https://www.unicode.org/Public/18.0.0/" + upstream,
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    licence = BASE / "LICENSE.txt"
    files.append({"path": "LICENSE.txt", "url": "https://www.unicode.org/license.txt",
                  "sha256": hashlib.sha256(licence.read_bytes()).hexdigest()})
    return {"unicode_version": "18.0.0", "licence": "LICENSE.txt", "files": files}


def verify():
    saved = json.loads(MANIFEST.read_text())
    if saved != snapshot():
        raise ValueError("Unicode source files differ from their pinned manifest")
    return len(saved["files"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true", help="Record reviewed upstream files (not a verification)")
    args = parser.parse_args()
    if args.record:
        MANIFEST.write_text(json.dumps(snapshot(), indent=2) + "\n")
    else:
        print(f"Verified {verify()} pinned Unicode source files")
