"""Reviewed newer SVG drawings missing from the pinned monochrome donor."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from pen_translate import Settings,translate,same_features
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[2]
RECIPES={
    '1faf9':(8,{0,6,7},{6,7},1.8),
    '1fafa':(8,{0,6,7},{6,7},1.3),
    '1facc':(51,set(range(51)),{0,1,2,13,14,15}|set(range(44,51)),1.0),
    '1fa8e':(89,{0,3,4,5,7,9,10,11,12,13,15,17,18,20,22,23,24,25,26,27,28,29,30,35,36,37,38,39,40,41,42,43,44,45,46,47,57,59,62,65,67,69,70,71,73,75,77,78,81,84,86,88},{4,10,11,12,23,24,25,26,29,70},1.0),
    '1faef':(25,set(range(25)),set(range(25))-{3,6},1.8),
    '1fa8b':(34,{0,1,2,6}|set(range(8,34)),{1,6}|set(range(8,34)),1.8),
    '1f6d9':(40,{0,1,4,5,6,19,20,22,24,26,28,30,31,32,33,34,35},{4,5,6,19,20,24,28,30,31,33,34,35},1.8),
    '1f6d8':(24,{0,1,3,4,5,8,9,10,11,12,13,14,15,19,20},{3,4,10,11,12,13,14,15,19,20},1.3),
    '1fa8d':(19,set(range(14))|{15},set(range(13))|{15},1.8),
    '1fa8c':(12,{0,1,2,4},{0},1.8),
    '1fac8':(19,set(range(19)),{4,6,7,8,9,10,11,12,13,17,18},1.3),
    '1fae9':(10,{2,4,5,6,7,9},{4,5,7,9},1.8),
    '1faea':(9,{0,2,3,4,6,7},{2,4,7},1.8),
    '1faeb':(31,set(range(21))|{24,26,28,30},{26,28,30},1.8),
    '1fadc':(10,{0,3,5},{5},2.0),
    '1fadf':(4,{0},{0},1.8),
    '1facd':(11,{0,1,2,3,4,6,8,9,10},{0,1,3,4,8,9},1.8),
    '1fa89':(14,{0,7,8,9,10,11,12,13},{7,8,9,10,11,12,13},2.0),
    '1fa8a':(9,{0,1,2,3,6,8},{0,8},1.8),
    '1fa8f':(12,{0,2,3,6,9},{2},1.8),
    '1fabe':(4,set(range(4)),set(),2.2),
    '1fac6':(12,set(range(1,12)),set(range(1,12)),1.3),
    '1fadd':(10,set(range(7)),set(range(2,7)),1.8),
}


def prepare(key):
    expected,keep,solid,stroke=RECIPES[key]
    manifest=json.loads((ROOT/'data/font-sources/noto-emoji-new-svg.json').read_text())
    entry=next(e for e in manifest['files'] if e['path'].endswith(f'emoji_u{key}.svg'))
    raw=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
    root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
    shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
    assert len(shapes)==expected
    for i,e in enumerate(shapes):
        parent=parents.get(e);definition=False
        while parent is not None:
            if parent.tag.split('}')[-1] in {'defs','clipPath'}:definition=True
            parent=parents.get(parent)
        if definition:continue
        if i not in keep:parents[e].remove(e);continue
        style=e.attrib.pop('style','')
        retained=';'.join(part for part in style.split(';') if part and not part.strip().startswith(('fill:','stroke:','stroke-width:')))
        if retained:e.set('style',retained)
        e.set('fill','#111111' if i in solid else '#ffffff')
        if i not in solid:
            e.set('stroke','#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
    if key=='1facc':
        for i in set(range(3,13))|set(range(16,44)):
            shapes[i].set('stroke','none')
    if key=='1fa8e':
        for i in [7,9,15,20]:
            shapes[i].set('fill','none');shapes[i].set('stroke','#111111');shapes[i].set('stroke-width','1')
    if key=='1faef':
        # This spiral is an open stroked path, not a filled silhouette.
        shapes[24].set('fill','none');shapes[24].set('stroke','#111111');shapes[24].set('stroke-width','2')
    if key=='1facd':
        # Preserve the small black eye against the black body.
        shapes[3].set('stroke','#ffffff');shapes[3].set('stroke-width','1.8')
    pixels=1536 if key in {'1facc','1fa8e'} else 768
    root.set('width',str(pixels));root.set('height',str(pixels))
    doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
    mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
    removed_ink=removed_holes=0
    if key=='1facc':
        labels,n=ndimage.label(mask);sizes=np.bincount(labels.ravel())
        tiny=np.isin(labels,[i for i in range(1,n+1) if sizes[i]<8])
        removed_ink=int(tiny.sum());mask=mask&~tiny
    if key=='1fa8e':
        holes,n=ndimage.label(ndimage.binary_fill_holes(mask)&~mask);sizes=np.bincount(holes.ravel())
        tiny=np.isin(holes,[i for i in range(1,n+1) if sizes[i]<4])
        clean=mask|tiny;assert same_features(mask,clean)
        removed_holes=int(tiny.sum());mask=clean
    settings=Settings(strength=1.7,seed=int(key,16),pressure=.1,taper=0) if key in {'1facc','1fa8e'} else Settings(strength=1.7,seed=int(key,16))
    image,report=translate(mask,settings)
    if key in {'1facc','1fa8e'}:report.update(removedRasterInkPixels=removed_ink,removedRasterPinholePixels=removed_holes)
    assert report['appliedStrength']>0 and not report['fallback'],key
    ink=np.asarray(image)<128
    if key=='1facd':
        # Raster-only pinholes, smaller than any meaningful source counter.
        holes,n=ndimage.label(ndimage.binary_fill_holes(ink)&~ink)
        sizes=np.bincount(holes.ravel());tiny=np.isin(holes,[i for i in range(1,n+1) if sizes[i]<4])
        cleaned=ink|tiny;assert same_features(ink,cleaned)
        report['removedRasterPinholePixels']=int(tiny.sum());ink=cleaned
    white=ndimage.binary_fill_holes(ink)
    report.update(source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,keptPaths=sorted(keep),solidPaths=sorted(solid),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
    return (white,ink),report


def butterfly_fill(ink,report):
    """Match translated wing cells to orange source paint; keep white spots white."""
    source=ROOT/report['source']['path']
    root=ET.fromstring(source.read_bytes())
    pixels=report['sourcePixels'];root.set('width',str(pixels));root.set('height',str(pixels))
    doc=pymupdf.open(stream=ET.tostring(root),filetype='svg')
    pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
    rgb=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
    painted=(rgb[:,:,0]>220)&(rgb[:,:,1]>80)&(rgb[:,:,1]<200)&(rgb[:,:,2]<50)
    painted=np.pad(painted,report['padding']);assert painted.shape==ink.shape
    labels,count=ndimage.label(ndimage.binary_fill_holes(ink)&~ink)
    selected=[]
    for i in range(1,count+1):
        region=labels==i
        if (region&painted).sum()/region.sum()>.5:selected.append(i)
    fill=np.isin(labels,selected)
    # Underpaint only inside the silhouette, preserving every white wing spot.
    excluded=(labels>0)&~fill
    fill=ndimage.binary_dilation(fill,iterations=3)&ndimage.binary_fill_holes(ink)&~excluded
    palette_path=ROOT/'output/imagegen/emoji-production/heart-palette-source.json'
    palette=json.loads(palette_path.read_text())
    assert hashlib.sha256((ROOT/palette['pdf']).read_bytes()).hexdigest()==palette['pdfSha256']
    colour=next(s['rgb'] for s in palette['samples'] if s['colour']=='orange')
    return fill,dict(rgb=colour,orangeCells=selected,whiteCells=count-len(selected),
                     paletteSource=str(palette_path.relative_to(ROOT)),
                     paletteSha256=hashlib.sha256(palette_path.read_bytes()).hexdigest())


def add_new_svg(root,glyphs,metrics,cmap,layers,palette,review,outline):
    sequences,rules=[],[]
    for key in RECIPES:
        cp=int(key,16);assert cp not in cmap
        (white,ink),report=prepare(key)
        ys,xs=np.nonzero(white);x0,y0,x1,y1=map(int,(xs.min(),ys.min(),xs.max(),ys.max()))
        factor=760/max(x1-x0+1,y1-y0+1);transform=x0,y0,factor
        advance=round((x1-x0+1)*factor)+100;name='svg.'+key
        glyphs[name]=outline(ink,transform);metrics[name]=advance,50;cmap[cp]=name
        assert glyphs[name].numberOfContours>=report['sourceComponents']+report['sourceHoles']
        for suffix,mask in [('white',white),('ink',ink)]:
            glyphs[name+'.'+suffix]=outline(mask,transform);metrics[name+'.'+suffix]=advance,50
        layers[name]=[(name+'.white',0),(name+'.ink',1)]
        if key=='1facc':
            orange,details=butterfly_fill(ink,report)
            report['wingColour']=details
            rgb=tuple(details['rgb'])
            if rgb not in palette:palette.append(rgb)
            glyphs[name+'.orange']=outline(orange,transform);metrics[name+'.orange']=advance,50
            layers[name].insert(1,(name+'.orange',palette.index(rgb)))
        if key in {'1faf9','1fafa'}:
            for i in range(5):
                variant=name+f'.tone{i+1}'
                glyphs[variant]=glyphs[name];metrics[variant]=advance,50
                layers[variant]=[(name+'.white',6+i),(name+'.ink',1)]
                sequences.append(chr(cp)+chr(0x1F3FB+i))
                rules.append(f'sub {name} tone{i+1} by {variant};')
        source=report['source']
        review.append(dict(codepoint=f'U+{cp:04X}',glyphName=name,category='new-svg',source=source['path'],sourceSha256=source['sha256'],sourcePixels=report['sourcePixels'],sourceRecipe=key,bounds=[x0,y0,x1,y1],advance=advance,penTreatment=report,license='NotoEmoji-SVG-Apache-2.0.txt',notice='NotoEmoji-SVG-NOTICE.txt'))

    return sequences,'\n'.join(rules)
