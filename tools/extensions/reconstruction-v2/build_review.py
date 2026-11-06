"""Build the standalone review page and downloadable artwork bundle."""
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
    note={1:'Original central artwork with the existing completed left extension.',2:'Dad points to the record, sitting back on his heels. His trousers and trailing shoe are drawn in code (drawn_legs.py) after panel 1. The player uses the grille and knobs from panel 1.',3:'Dad rests his hand on his thigh. His trousers, knee and trailing shoe are drawn in code (drawn_legs.py) after panel 1. Calvin looks up at Dad with his feet still toward the player. His figure and the player come from panel 1, enlarged by 56% for this closer view.',4:'Original night scene with the existing completed left side of the bed.'}[n]
    parts.append(f'''<section id="panel-{n}"><h2>Panel {n}</h2><p>{note}</p>
<p class="details">{w} × {h} pixels · original-crop agreement: {match}% · <a href="assets/full-panels/panel{n}.png?v={digest}" download="panel{n}.png">Download PNG</a> · <a href="assets/full-panels/panel{n}.png?v={digest}" target="_blank" rel="noopener">Open full size</a></p>
<label><input class="show-source" type="checkbox"> Show original crop overlay</label>
<div class="scroll"><div class="stage" style="--native-width:{w}px"><img class="complete" src="assets/full-panels/panel{n}.png?v={digest}" width="{w}" height="{h}" alt="Completed comic panel {n} without dialogue" loading="lazy"><img class="source" src="assets/full-panels/original{n}.png" style="left:{100*x/w}%;top:{100*y/h}%;width:{100*ow/w}%" width="{ow}" height="{oh}" alt="Original crop of panel {n}" hidden></div></div></section>''')
page='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Completed comic panels</title>
<style>
*{box-sizing:border-box}body{margin:0;padding:24px;background:#eee;color:#222;font:16px/1.5 system-ui,sans-serif}main{max-width:1400px;margin:auto}h1{margin:0;font-size:1.8rem}h2{margin-bottom:8px}a{color:#164d91}nav{display:flex;gap:20px;flex-wrap:wrap;margin:20px 0}.controls{display:flex;align-items:center;gap:24px;flex-wrap:wrap;padding:16px;background:white;border:1px solid #bbb;position:sticky;top:0;z-index:2}section{margin:36px 0 56px}section p{max-width:900px}.details{font-size:.92rem}.scroll{overflow:auto;margin-top:12px;max-height:85vh;border:1px solid #aaa;background:white}.stage{position:relative;width:var(--native-width);background:white}.fit .stage{width:min(100%,var(--native-width))}.complete{display:block;width:100%;height:auto}.source{position:absolute;height:auto;opacity:.5;outline:2px solid #b92323;pointer-events:none}.source[hidden]{display:none}input[type=range]{vertical-align:middle}footer{font-size:.9rem;padding-bottom:30px;max-width:900px}
</style></head><body class="fit"><main><h1>Completed comic panels</h1><p>All four panels, without dialogue. Use the original-crop overlay to compare the source artwork, or open each PNG at full resolution.</p><nav><a href="#panel-1">Panel 1</a><a href="#panel-2">Panel 2</a><a href="#panel-3">Panel 3</a><a href="#panel-4">Panel 4</a><a href="assets/full-panels/kneeling-comparison.png">Compare the two kneels</a><a href="output/full-panels.zip" download>Download all four</a><a href="index.html">Comic editor</a></nav>
<div class="controls"><label><input id="fit" type="checkbox" checked> Fit to window</label><label>Original overlay opacity <input id="opacity" type="range" min="0" max="100" value="50" aria-label="Original overlay opacity"></label></div>
'''+''.join(parts)+'''<footer><p>The source comparisons use the cleaned, smoothed artwork extracted from page 247, with lettering and balloons removed. Panel 4’s signature remains a separate asset. Agreement percentages count every pixel in the original crop, including white background; panel 2 includes the earlier elbow repair. Panel 3 preserves every original ink pixel and directly reuses the original seated Calvin and record player.</p><p><a href="assets/full-panels/verification.json">Pixel comparison results</a> · <a href="assets/full-panels/provenance.json">Artwork sources and rebuild steps</a></p></footer></main>
<script>
document.querySelector('#fit').addEventListener('change',e=>document.body.classList.toggle('fit',e.target.checked));
document.querySelector('#opacity').addEventListener('input',e=>document.querySelectorAll('.source').forEach(image=>image.style.opacity=e.target.value/100));
document.querySelectorAll('.show-source').forEach(input=>input.addEventListener('change',()=>input.closest('section').querySelector('.source').hidden=!input.checked));
</script></body></html>'''
(ROOT/'panels.html').write_text(page)
provenance={'source':'The Indispensable Calvin and Hobbes, local scanned PDF','sourcePage':247,'stripDate':'1990-06-05','sourceProcessing':'Existing build_assets.py ink/background extraction, lettering removal, and ART_SCALE=2 smoothing.','references':{'8':'Two-knee pose with folded shins and trailing shoes, mirrored for the scene','110':'Bottom strip, panels 3 and 4. Folded-leg reference and directly sampled sneaker ink.','226':'Compact folded lower legs and shoes','237':'Crouching hip, diagonal thigh and torso','247':'Original four panels, seated Calvin, portable record player'},'generation':'Built-in imagegen supplied panel 3\'s lower shirt and hand (see prompts-page-110.json in tools/extensions/reconstruction-v2/). Dad\'s trousers and shoes below both close-up crops are drawn programmatically by drawn_legs.py with the ink.py brush kit, modelled on panel 1\'s trousers and shoes and the kneeling Dad on page 8.','directReuse':{'1':'Entire cleaned original panel; existing left extension retained.','2':'Prior repaired upper artwork, including original head, hands, record and Calvin expression. The legs and shoe below the crop are drawn by drawn_legs.py. The grille and paired knobs come from panel 1, with the seated pose and player as drawing guides.','3':'Entire cleaned scan crop retained. Lower shirt and hand generated; trousers, knee and shoe drawn by drawn_legs.py. Calvin and the player from panel 1 are enlarged 1.56×. The original upward-looking head joins the reflected seated body at its collar. The shoes point toward the player in both close-ups.','4':'Entire cleaned original night panel; existing left bed extension retained.'},'scaleCheck':{'metric':'Calvin head width / Dad head width, thresholded ink at full resolution','panel2':[602,493],'panel3':[693,562]},'rebuild':['.venv/bin/python tools/extensions/reconstruction-v2/prepare_inputs.py','.venv/bin/python tools/extensions/reconstruction-v2/assemble.py','.venv/bin/python tools/extensions/reconstruction-v2/build_review.py'],'outputs':records}
(OUT/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
(ROOT/'output').mkdir(exist_ok=True)
with zipfile.ZipFile(ROOT/'output/full-panels.zip','w',zipfile.ZIP_DEFLATED) as bundle:
    offline=page.replace('<a href="output/full-panels.zip" download>Download all four</a>','').replace('<a href="index.html">Comic editor</a>','')
    bundle.writestr('panels.html',offline)
    for file in sorted(OUT.iterdir()):
        if file.suffix in ('.png','.json'):bundle.write(file,file.relative_to(ROOT))
print('Created panels.html and output/full-panels.zip')
