"""Prepare the sixteen drawings as cached glyph assets for main-font assembly.

This module does artwork processing only on a content-addressed cache miss.
"""
import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.measure import find_contours, approximate_polygon
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

ROOT=Path(__file__).resolve().parents[2]
LIBRARIES={name:version(name) for name in ('numpy','scipy','scikit-image','Pillow','fonttools')}
ART=ROOT/'assets/emoji-concepts'
POINTS=[0x2603,0x26c4,0x1f996,0x1f995,0x1f680,0x1f6f8,0x1f47d,0x1f47e,
        0x1fa90,0x2604,0x1f4e6,0x1f4a3,0x1f405,0x1f42f,0x1f409,0x1f480]
SELECTIONS=json.loads((ART/'selected-sources.json').read_text())
REPLACEMENTS={int(cp,16):(entry['file'],tuple(entry['crop']) if entry.get('crop') else None)
              for cp,entry in SELECTIONS.items()}


def artwork(index,cp):
    source=ART/'sprite-sheet-v1.png'
    im=Image.open(source).convert('RGBA')
    x,y=index%4,index//4
    box=tuple(round(v) for v in (x*im.width/4,y*im.height/4,(x+1)*im.width/4,(y+1)*im.height/4))
    if cp in REPLACEMENTS:
        file,box=REPLACEMENTS[cp];source=ART/file;im=Image.open(source).convert('RGBA')
    if box:im=im.crop(box)
    resolution=SELECTIONS.get(f'{cp:X}',{}).get('resolution',384)
    im.thumbnail((resolution,resolution),Image.Resampling.LANCZOS)
    rgba=np.array(im);rgb=rgba[:,:,:3]
    # White CLI backgrounds are removed only where connected to the outside.
    white=(rgb.min(axis=2)>237)&(rgb.max(axis=2)-rgb.min(axis=2)<15)
    passable=white|(rgba[:,:,3]<128)
    seed=np.zeros(passable.shape,bool);seed[0]=passable[0];seed[-1]=passable[-1]
    seed[:,0]=passable[:,0];seed[:,-1]=passable[:,-1]
    exterior=ndimage.binary_propagation(seed,mask=passable)
    opaque=(rgba[:,:,3]>=128)&~exterior
    labels,_=ndimage.label(opaque);sizes=np.bincount(labels.ravel())
    opaque &= sizes[labels]>=50*max(1,max(im.size)/384)**2
    yy,xx=np.nonzero(opaque)
    assert len(xx),hex(cp)
    crop=(slice(yy.min(),yy.max()+1),slice(xx.min(),xx.max()+1))
    rgb=rgb[crop];opaque=opaque[crop]
    ink=opaque&(rgb.max(axis=2)<135)
    # Keep black contours and white underpaint. Three flat washes per icon
    # preserve its colour while avoiding vectorising watercolor pixel noise.
    chroma=rgb.max(axis=2).astype(int)-rgb.min(axis=2).astype(int)
    coloured=opaque&~ink&((chroma>22)|(rgb.mean(axis=2)<207))
    if cp in {0x1f405,0x1f42f} and not SELECTIONS[f'{cp:X}'].get('preserveGreys'):coloured[:]=False
    masks=[(opaque,(255,255,255))]
    if coloured.any():
        pixels=rgb[coloured]
        quant=Image.fromarray(pixels.reshape(1,-1,3)).quantize(colors=3,method=Image.Quantize.MEDIANCUT)
        palette=quant.getpalette();labels=np.asarray(quant).reshape(-1)
        for label in sorted(set(labels)):
            colour=tuple(palette[label*3:label*3+3])
            mask=np.zeros(opaque.shape,bool);mask[coloured]=labels==label
            mask=ndimage.median_filter(mask,size=3)&coloured
            if mask.sum()>8:masks.append((mask,colour))
    masks.append((ink,(17,17,17)))
    return masks,dict(source=source.relative_to(ROOT).as_posix(),
                      sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),crop=box,
                      pixels=[opaque.shape[1],opaque.shape[0]])


def outline(mask,factor,curves=False):
    pen=TTGlyphPen(None)
    if curves:
        import potrace
        target=Cu2QuPen(pen,max_err=.2)
        def point(p):return 50+p.x*factor,760-p.y*factor
        for curve in potrace.Bitmap(~mask).trace(turdsize=0,alphamax=1.,opttolerance=.2):
            target.moveTo(point(curve.start_point))
            for segment in curve.segments:
                if segment.is_corner:
                    target.lineTo(point(segment.c));target.lineTo(point(segment.end_point))
                else:target.curveTo(point(segment.c1),point(segment.c2),point(segment.end_point))
            target.closePath()
        return pen.glyph()
    for contour in find_contours(np.pad(mask.astype(float),1),.5):
        points=approximate_polygon(contour,tolerance=.48)
        if len(points)<4:continue
        points=[(round(50+(x-1)*factor),round(760-(y-1)*factor)) for y,x in points]
        pen.moveTo(points[0])
        for p in points[1:-1]:pen.lineTo(p)
        pen.closePath()
    return pen.glyph()


def prepare_glyph(index, cp, cache):
    from fontTools.pens.recordingPen import RecordingPen
    source=ART/'sprite-sheet-v1.png'
    im=Image.open(source).convert('RGBA');x,y=index%4,index//4
    box=tuple(round(v) for v in (x*im.width/4,y*im.height/4,(x+1)*im.width/4,(y+1)*im.height/4))
    if cp in REPLACEMENTS:
        file,box=REPLACEMENTS[cp];source=ART/file;im=Image.open(source).convert('RGBA')
    if box:im=im.crop(box)
    # Hash the actual source cell: changing another cell in a shared sheet
    # must not trigger preparation of this glyph.
    inputs=dict(schema=1,codepoint=cp,sourcePixels=hashlib.sha256(im.tobytes()).hexdigest(),
                size=list(im.size),recipe=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),libraries=LIBRARIES,
                preserveGreys=bool(SELECTIONS.get(f'{cp:X}',{}).get('preserveGreys')),
                resolution=SELECTIONS.get(f'{cp:X}',{}).get('resolution',384),
                curves=bool(SELECTIONS.get(f'{cp:X}',{}).get('curves')))
    if inputs['curves']:inputs['curveLibrary']=version('potracer')
    def commands(glyph):
        pen=RecordingPen();glyph.draw(pen,None);return pen.value
    def compute():
        masks,record=artwork(index,cp);height,width=masks[0][0].shape
        factor=min(760/height,1100/width)
        return dict(advance=round(width*factor)+100,base=commands(outline(masks[-1][0],factor,inputs['curves'])),
                    layers=[dict(outline=commands(outline(mask,factor,inputs['curves'])),rgb=colour) for mask,colour in masks])
    prepared=cache.prepare(inputs,compute)
    # Provenance reflects the current source file, even if its unchanged cell
    # reused an artifact after a different cell in the sheet was edited.
    record=dict(codepoint=f'U+{cp:04X}',emoji=chr(cp),source=source.relative_to(ROOT).as_posix(),
                sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),crop=box,
                artifactKey=cache.keys[-1],advance=prepared['advance'],
                resolution=inputs['resolution'],curves=inputs['curves'])
    return prepared,record


def build():
    # Compatibility entry point; production assembly now emits one main font.
    from build_emoji import build as assemble
    return assemble()


if __name__=='__main__':build()
