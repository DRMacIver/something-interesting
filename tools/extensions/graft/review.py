"""Build the review page for the full panels, and the bundle it offers.

    uv run tools/extensions/graft/review.py

Writes panels.html, assets/full-panels/provenance.json and
assets/full-panels.zip (the four panels with an offline copy of the page)
from what `build.py` left in assets/full-panels.
"""
from pathlib import Path
import hashlib, json, zipfile

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'assets/full-panels'
records=json.loads((OUT/'verification.json').read_text())
parts=[]
for r in records:
    n=r['panel'];w,h=r['size'];x,y=r['originalOffset'];ow,oh=r['originalSize']
    digest=hashlib.sha256((OUT/f'panel{n}.png').read_bytes()).hexdigest()[:10]
    match=f"{100*r['originalMatchFraction']:.3f}".rstrip('0').rstrip('.')
    note={1: "Dad walks towards Calvin. The scan cut off his trailing heel and the back of that trouser leg; they come from a whole-scene drawing by Codex's image generation, fitted to the scan (tools/extensions/graft).", 2: "Dad kneels and sets the record on the player. Everything outside the scanned crop (his back, legs and shoe, the player, the rest of Calvin) comes from a whole-scene drawing by Codex's image generation, fitted to the scan so its lines carry on from Watterson's. His shoe is Watterson's own from panel 1, mirrored and enlarged to this panel's scale.", 3: "Dad kneels and gestures towards Calvin. Everything outside the scanned crop (his body below the chest, Calvin and the player) comes from a whole-scene drawing by Codex's image generation, fitted to the scan so its lines carry on from Watterson's. His shoe is Watterson's own from panel 1, mirrored and enlarged to this panel's scale.", 4: 'Original night scene with the existing completed left side of the bed.'}[n]
    parts.append(f'''<section id="panel-{n}"><h2>Panel {n}</h2><p>{note}</p>
<p class="details">{w} × {h} pixels · original-crop agreement: {match}% · <a href="assets/full-panels/panel{n}.png?v={digest}" download="panel{n}.png">Download PNG</a> · <a href="assets/full-panels/panel{n}.png?v={digest}" target="_blank" rel="noopener">Open full size</a></p>
<label><input class="show-source" type="checkbox"> Show original crop overlay</label>
<div class="scroll"><div class="stage" style="--native-width:{w}px"><img class="complete" src="assets/full-panels/panel{n}.png?v={digest}" width="{w}" height="{h}" alt="Completed comic panel {n} without dialogue" loading="lazy"><img class="source" src="assets/full-panels/original{n}.png" style="left:{100*x/w}%;top:{100*y/h}%;width:{100*ow/w}%" width="{ow}" height="{oh}" alt="Original crop of panel {n}" hidden></div></div></section>''')
page='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Completed comic panels</title>
<style>
*{box-sizing:border-box}body{margin:0;padding:24px;background:#eee;color:#222;font:16px/1.5 system-ui,sans-serif}main{max-width:1400px;margin:auto}h1{margin:0;font-size:1.8rem}h2{margin-bottom:8px}a{color:#164d91}nav{display:flex;gap:20px;flex-wrap:wrap;margin:20px 0}.controls{display:flex;align-items:center;gap:24px;flex-wrap:wrap;padding:16px;background:white;border:1px solid #bbb;position:sticky;top:0;z-index:2}section{margin:36px 0 56px}section p{max-width:900px}.details{font-size:.92rem}.scroll{overflow:auto;margin-top:12px;max-height:85vh;border:1px solid #aaa;background:white}.stage{position:relative;width:var(--native-width);background:white}.fit .stage{width:min(100%,var(--native-width))}.complete{display:block;width:100%;height:auto}.source{position:absolute;height:auto;opacity:.5;outline:2px solid #b92323;pointer-events:none}.source[hidden]{display:none}input[type=range]{vertical-align:middle}footer{font-size:.9rem;padding-bottom:30px;max-width:900px}
</style></head><body class="fit"><main><h1>Completed comic panels</h1><p>All four panels, without dialogue. Use the original-crop overlay to compare the source artwork, or open each PNG at full resolution.</p><nav><a href="#panel-1">Panel 1</a><a href="#panel-2">Panel 2</a><a href="#panel-3">Panel 3</a><a href="#panel-4">Panel 4</a><a href="assets/full-panels.zip" download>Download all four</a><a href="index.html">Comic editor</a></nav>
<div class="controls"><label><input id="fit" type="checkbox" checked> Fit to window</label><label>Original overlay opacity <input id="opacity" type="range" min="0" max="100" value="50" aria-label="Original overlay opacity"></label></div>
'''+''.join(parts)+'''<footer><p>The source comparisons use the cleaned, smoothed artwork extracted from page 247, with lettering and balloons removed. Panel 4’s signature remains a separate asset. Agreement percentages count every pixel in the original crop, including white background; every panel keeps its original crop exactly.</p><p><a href="assets/full-panels/verification.json">Pixel comparison results</a> · <a href="assets/full-panels/provenance.json">Artwork sources and rebuild steps</a></p></footer></main>
<script>
document.querySelector('#fit').addEventListener('change',e=>document.body.classList.toggle('fit',e.target.checked));
document.querySelector('#opacity').addEventListener('input',e=>document.querySelectorAll('.source').forEach(image=>image.style.opacity=e.target.value/100));
document.querySelectorAll('.show-source').forEach(input=>input.addEventListener('change',()=>input.closest('section').querySelector('.source').hidden=!input.checked));
</script></body></html>'''
(ROOT/'panels.html').write_text(page)
provenance=dict({'source': 'The Indispensable Calvin and Hobbes, local scanned PDF', 'sourcePage': 247, 'stripDate': '1990-06-05', 'sourceProcessing': 'Existing build_assets.py ink/background extraction, lettering removal, and ART_SCALE=2 smoothing.', 'generation': "Panels 1 to 3: everything outside the scanned crop comes from one whole-scene drawing per panel made by Codex's image generation from the scan (prompts in tools/extensions/graft/prompts, chosen drawings in tools/extensions/graft/picks). graft.py registers each drawing to the scan, bends it to agree with the scan inside the crop, joins its lines to the scan's at the crop's edges, and re-inks it at the scan's line weight and smoothing. The scan itself is pasted back unchanged.", 'directReuse': {'1': 'Entire cleaned original panel.', '2': "Entire cleaned scan crop. Dad's shoe is panel 1's planted shoe, mirrored and enlarged by the ratio of his head widths (shoe.py); the join with his trousers is from a tidied redraw (patch.py).", '3': "Entire cleaned scan crop. Dad's shoe is panel 1's planted shoe, as in panel 2.", '4': 'Entire cleaned original night panel; existing left bed extension retained.'}, 'rebuild': ['uv run tools/extensions/graft/scans.py', 'uv run tools/extensions/graft/build.py', 'uv run tools/extensions/graft/review.py']}, outputs=records)
(OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
# the bundle is committed, so the same panels must give the same bytes: no
# dates, and the files in a fixed order
def add(bundle, name, data):
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    bundle.writestr(info, data)


with zipfile.ZipFile(ROOT/'assets/full-panels.zip', 'w') as bundle:
    offline = page.replace('<a href="assets/full-panels.zip" download>Download all four</a>', '').replace('<a href="index.html">Comic editor</a>', '')
    add(bundle, 'panels.html', offline)
    for file in sorted(OUT.iterdir()):
        if file.suffix in ('.png', '.json'):
            add(bundle, file.relative_to(ROOT).as_posix(), file.read_bytes())
print('Created panels.html and assets/full-panels.zip')
