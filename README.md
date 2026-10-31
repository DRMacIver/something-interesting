# Two Types of Things

A static, backend-free generator for the "Calvin's dad explains there are two
types of things" meme. Type Dad's lines into the first three panels and the
text flows around the artwork; long text either makes the panels taller or
shrinks the lettering to fit.

## Running locally

The page fetches its assets, so serve it over HTTP rather than opening the
file directly:

```bash
python3 -m http.server 8765
```

Then open <http://localhost:8765>.

## Deploying

Everything is static. On GitHub, enable Pages for the repository with
"Deploy from a branch", pointing at the root of the default branch.

## How it works

- `source/original-strip.png` is the original strip.
- `tools/build_assets.py` cuts out the four panels, erases Dad's lettering,
  upscales the line art, and records which parts of each panel are open
  space (white space connected to the top of the panel) in
  `assets/panels.json`. Re-run it with `uv run tools/build_assets.py`.
- `js/layout.js` is the text-flow engine: it places text line by line,
  using the widest gap the art leaves free at each height, and searches for
  the panel height or font size that makes everything fit.
- `js/app.js` draws the comic on a canvas and handles the controls. The
  current text and settings are stored in the URL, so links are shareable.

## Tests

```bash
npm test
```
