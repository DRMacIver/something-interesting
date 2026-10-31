"""Tag every asset URL the pages use with a hash of the file's contents
(`?v=...`), so that browsers fetch a file again exactly when it has
changed, and use what they have cached otherwise.

- style.css's URL for the font;
- the pages' URLs for style.css and js/app.js, and an import map sending
  every module in js/ to its versioned URL (so that the modules' imports of
  each other, by plain paths, are versioned too);
- panels.json's URLs for the panel art (panels.json itself is always
  fetched afresh);
- the link preview image's URL in the page.

Run it after changing any of them: uv run tools/version_assets.py
"""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT = "assets/fonts/dad-lettering.woff2"
# Link previews need the preview image's full URL.
SITE = "https://drmaciver.github.io/something-interesting/"
PREVIEW = "assets/preview.png"
# Each page, and the path from it to the root.
PAGES = {"index.html": "", "tools/checks.html": "../", "tools/preview.html": "../"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:10]


def versioned(text, url, version):
    """The text with every reference to `url` (with or without a version)
    given `version`."""
    pattern = re.escape(url) + r"(\?v=[0-9a-f]+)?(?=[\"')\s])"
    return re.sub(pattern, f"{url}?v={version}", text)


def import_map(prefix):
    # Keys must be paths ("./js/..."), not bare names, to match the modules'
    # imports of each other once those are resolved to URLs.
    prefix = prefix or "./"
    modules = sorted((ROOT / "js").glob("*.js"))
    imports = {f"{prefix}js/{m.name}": f"{prefix}js/{m.name}?v={digest(m)}" for m in modules}
    body = json.dumps({"imports": imports}, indent=2).replace("\n", "\n      ")
    return f'<script type="importmap">\n      {body}\n    </script>'


def updated():
    """Each file that versioning changes, with its new contents, in the
    order they must be written (later hashes depend on earlier files)."""
    out = {}
    css = (ROOT / "style.css").read_text()
    css = versioned(css, FONT, digest(ROOT / FONT))
    out["style.css"] = css
    css_version = hashlib.sha256(css.encode()).hexdigest()[:10]

    for page, prefix in PAGES.items():
        html = (ROOT / page).read_text()
        html = versioned(html, f"{prefix}style.css", css_version)
        html = versioned(html, f"{prefix}js/app.js", digest(ROOT / "js/app.js"))
        html = versioned(html, SITE + PREVIEW, digest(ROOT / PREVIEW))
        block = re.compile(r'<script type="importmap">.*?</script>', re.S)
        if block.search(html):
            html = block.sub(lambda _: import_map(prefix), html)
        else:
            # Before any module script, in the head.
            html = html.replace("\n  </head>", f"\n    {import_map(prefix)}\n  </head>", 1)
        out[page] = html

    meta = json.loads((ROOT / "assets/panels.json").read_text())
    for panel in meta["panels"]:
        for holder in (panel, panel.get("signature") or {}):
            if "image" in holder:
                path = holder["image"].split("?")[0]
                holder["image"] = f"{path}?v={digest(ROOT / path)}"
    out["assets/panels.json"] = json.dumps(meta, separators=(",", ":"))
    return out


def stale():
    """The files whose asset URLs are out of date."""
    return [name for name, text in updated().items() if (ROOT / name).read_text() != text]


def update():
    for name, text in updated().items():
        if (ROOT / name).read_text() != text:
            (ROOT / name).write_text(text)
            print(f"updated {name}")


if __name__ == "__main__":
    update()
