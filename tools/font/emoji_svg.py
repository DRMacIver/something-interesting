"""Convert reviewed, pinned Noto SVG paths into expressive ink and skin masks."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import pymupdf
from scipy import ndimage
from pen_translate import Settings, translate, same_features

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'build/unicode-sources/noto-emoji-svg-probe/emoji_u1f930.svg'
KEEP = {0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 18}
SOLID = {0, 8, 9, 10, 13, 14, 15, 18}
RECIPES = {
    '1f469_200d_1f37c': (38, {0,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,22,24,26,27,29,31,32,35,37}, {0,9,10,11,12,13,14,18,19}),
    '1f9d1_200d_1f37c': (40, {0,1,2,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,22,24,25,27,29,30,33,35,36,37,38,39}, {0,9,10,11,12,16,17,36,37,38,39}),
    '1f931': (30, {0,2,3,4,5,6,7,8,9,10,11,12,13,14,16,18,19,20,21,22,24,27,28}, {0,8,9,10,11,12,13}),
    '1f930': (20, KEEP, SOLID),
    '1fac3': (18, {0,2,3,4,5,6,7,8,9,12,13,14,17}, {7,8,9,12,13,14,17}),
    '1fac4': (18, {0,2,3,4,5,6,7,8,9,12,13,14,17}, {7,8,9,12,13,14,17}),
    '1f468_200d_1f37c': (40, {0,1,2,3,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,22,24,26,27,29,31,32,35,37,38,39}, {0,9,10,11,12,13,14,18,19,38,39}),
}

SKIN_PATHS = {
    '1f930': {4,5,6,7}, '1fac3': {3,4,5,6}, '1fac4': {3,4,5,6},
    '1f468_200d_1f37c': {1,2,7,8,31,37},
    '1f469_200d_1f37c': {6,7,8,31,37},
    '1f9d1_200d_1f37c': {1,6,7,8,29,35},
    '1f931': {4,5,6,7,24,27},
}

EXPECTED_REGIONS = {'1f469_200d_1f37c': (25, [1, 2, 4, 6, 21]), '1f9d1_200d_1f37c': (25, [1, 2, 3, 5, 6, 9, 23]), '1f931': (25, [1, 2, 5, 7, 18, 23]), '1f930': (7, [1, 2, 5, 6]), '1fac3': (9, [1, 3, 6, 7]), '1fac4': (7, [1, 2, 5, 6]), '1f468_200d_1f37c': (26, [1, 2, 3, 7, 23])}


def render_recipe(pixels, stroke, codepoint):
    source = SOURCE.with_name(f'emoji_u{codepoint}.svg')
    expected, keep, solid = RECIPES[codepoint]
    spec = json.loads((ROOT/'data/font-sources/noto-emoji-svg.json').read_text())
    record = next(f for f in spec['files'] if f['path'] == str(source.relative_to(ROOT)))
    raw = source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record['sha256']
    masks=[]
    for material in [False, True]:
        root=ET.fromstring(raw)
        shapes=[x for x in root.iter() if x.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
        parents={c:p for p in root.iter() for c in p}
        assert len(shapes)==expected
        for i,element in reversed(list(enumerate(shapes))):
            if i not in keep:
                parents[element].remove(element);continue
            style=element.attrib.pop('style','')
            assert not style or (style.strip().startswith('fill:') and style.count(':')==1)
            black=i in (SKIN_PATHS[codepoint] if material else solid)
            element.set('fill','#111111' if black else '#ffffff')
            if i not in solid:
                element.set('stroke',('#111111' if i in SKIN_PATHS[codepoint] else '#ffffff') if material else '#111111')
                element.set('stroke-width',str(stroke))
                element.set('stroke-linejoin','round');element.set('stroke-linecap','round')
        for element in list(root):
            if element.tag.split('}')[-1]=='aipgf':root.remove(element)
        root.set('width',str(pixels));root.set('height',str(pixels))
        doc=pymupdf.open(stream=ET.tostring(root),filetype='svg')
        pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
        masks.append(np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128)
    return *masks,record


def convert_layers(pixels=768, stroke=1.3, codepoint='1f930'):
    mask,material,record=render_recipe(pixels,stroke,codepoint)
    removed=0
    if codepoint in {'1f931','1f469_200d_1f37c'}:
        # Discard only sub-four-pixel raster pinholes: the feature guard already
        # excludes these from meaningful counters. Never close strokes globally.
        labels,n=ndimage.label(ndimage.binary_fill_holes(mask)&~mask)
        sizes=np.bincount(labels.ravel());tiny=np.isin(labels,[i for i in range(1,n+1) if sizes[i]<4])
        cleaned=mask|tiny;assert same_features(mask,cleaned)
        removed=int(tiny.sum());mask=cleaned
    seed=int(codepoint,16) if '_' not in codepoint else int.from_bytes(hashlib.sha256(codepoint.encode()).digest()[:4],'big')
    settings=Settings(strength=1.7,seed=seed)
    if codepoint=='1f469_200d_1f37c':settings=Settings(strength=1.7,seed=seed,pressure=.1,taper=0)
    image,report=translate(mask,settings)
    report.update(source=record,sourcePixels=pixels,svgStrokeWidth=stroke,
                  removedRasterPinholePixels=removed,
                  keptPaths=sorted(RECIPES[codepoint][1]),solidInkPaths=sorted(RECIPES[codepoint][2]),
                  skinPaths=sorted(SKIN_PATHS[codepoint]),
                  programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
    return image,report,np.pad(material,report['padding'])


def convert(pixels=768,stroke=1.3,codepoint='1f930'):
    image,report,_=convert_layers(pixels,stroke,codepoint)
    return image,report


def prepare(codepoint):
    image,report,material=convert_layers(codepoint=codepoint)
    assert report['appliedStrength']>0 and not report['fallback'],codepoint
    ink=np.asarray(image)<128;white=ndimage.binary_fill_holes(ink)
    labels,count=ndimage.label(white&~ink);sizes=np.bincount(labels.ravel())
    overlaps=np.bincount(labels[material],minlength=count+1)
    selected=[i for i in range(1,count+1) if sizes[i]>=32 and overlaps[i]/sizes[i]>.5]
    assert (count,selected)==EXPECTED_REGIONS[codepoint],(codepoint,count,selected)
    interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
    skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
    assert skin.sum()>5000 and selected
    report.update(enclosedRegions=count,skinRegions=selected,skinPixels=int(skin.sum()),
                  regionAreas=sizes[1:].tolist(),skinOverlapFractions=[round(float(overlaps[i]/sizes[i]),4) for i in range(1,count+1)])
    return (white,skin,ink),report
