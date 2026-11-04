"""Isolated native-outline pressure experiments; never edits pinned inputs.

Raster distance-field pressure varies stroke width smoothly. Coordinates,
advances, OpenType substitution and positioning remain in the native em.
Candidates are guarded at high resolution but still require visual review.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pymupdf
import uharfbuzz as hb
from PIL import Image
from scipy import ndimage as ndi
from skimage.measure import approximate_polygon, find_contours
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from prototype_unifont_lettering import validate_reconstruction

ROOT = Path(__file__).resolve().parents[2]


def pressure(mask, amount=.7, seed=1, protected=None, bend=0):
    """Smooth pressure with bounded, per-component/counter acceptance."""
    inside = ndi.distance_transform_edt(mask)
    outside = ndi.distance_transform_edt(~mask)
    field = np.where(mask, inside-.5, .5-outside)
    # Fine hairlines constrain local pressure; broad strokes may breathe more.
    radius = np.minimum(inside, 32)
    radius = ndi.maximum_filter(radius, size=17)
    y, x = np.mgrid[:mask.shape[0], :mask.shape[1]]
    phase = (seed % 997) / 997 * np.pi*2
    wave = .65*np.sin(x/97+y/139+phase)+.35*np.sin(x/51-y/113-phase)
    # Centre pressure independently around each native component. This permits
    # expressive thick/thin contrast without simply swelling or thinning the
    # whole letter, and leaves tiny detached marks effectively unchanged.
    labels,count=ndi.label(mask,structure=np.ones((3,3)))
    nearest=ndi.distance_transform_edt(~mask,return_distances=False,return_indices=True)
    owners=labels[tuple(nearest)]
    centred=wave.copy()
    edge=np.abs(field)<1.5
    for component in range(1,count+1):
        region=owners==component
        boundary=region&edge
        weights=radius[boundary]
        offset=np.average(wave[boundary],weights=weights) if weights.sum() else 0
        centred[region]-=offset
    delta = amount*radius*centred
    # Optional long-wave contour drift experiments. The existing pressure-only
    # default remains stable for independent category reviewers.
    drift=np.zeros_like(field)
    if bend:
        protection=1 if protected is None else protected
        dx=bend*protection*np.sin(x/173+y/211+phase)
        dy=bend*.65*protection*np.sin(x/223-y/157-phase)
        drift=ndi.map_coordinates(field,[y+dy,x+dx],order=1,mode='constant',cval=-24)-field
    if protected is not None: delta *= protected
    for reduction in (1, .75, .5, .25, .125):
        candidate = field+(delta+drift)*reduction >= 0
        try: checks = validate_reconstruction(mask, candidate)
        except ValueError: continue
        return candidate, dict(amount=amount*reduction, bend=bend*reduction, changedPixels=int(np.sum(candidate != mask)), **checks)
    raise ValueError('No nonzero pressure candidate preserves native components/counters')


def raster(font, name, resolution=1024, viewport=None):
    gs = font.getGlyphSet(); bp = BoundsPen(gs); gs[name].draw(bp)
    if not bp.bounds: return None
    em = font['head'].unitsPerEm; scale = resolution/em
    x0,y0,x1,y1=bp.bounds
    # Fixed native coordinates avoid independently normalising marks or letters.
    left=int(np.floor(x0*scale))-24; top=int(np.ceil(y1*scale))+24
    width=int(np.ceil(x1*scale))-left+24
    height=top-int(np.floor(y0*scale))+24
    if viewport is not None:
        left,top,scale,width,height=viewport
    pen=SVGPathPen(gs); gs[name].draw(pen)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><path d="{pen.getCommands()}" transform="translate({-left} {top}) scale({scale} {-scale})"/></svg>'
    doc=pymupdf.open(stream=svg.encode(),filetype='svg'); pdf=pymupdf.open('pdf',doc.convert_to_pdf()); pix=pdf[0].get_pixmap(alpha=False)
    mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
    return mask, (left,top,scale)


def outline(mask, transform):
    left,top,scale=transform; pen=TTGlyphPen(None)
    for contour in find_contours(np.pad(mask.astype(float),1),.5):
        contour=approximate_polygon(contour,.3)
        coords=[((x-1+left)/scale,(top-y+1)/scale) for y,x in contour]
        if len(coords)<4: continue
        pen.moveTo(coords[0])
        for point in coords[1:-1]: pen.lineTo(point)
        pen.closePath()
    return pen.glyph()


def shaped(font, text):
    font.flavor=None; stream=io.BytesIO();font.save(stream)
    hf=hb.Font(hb.Face(stream.getvalue()));buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(hf,buf)
    return [(font.getGlyphName(i.codepoint), p.x_advance,p.y_advance,p.x_offset,p.y_offset) for i,p in zip(buf.glyph_infos,buf.glyph_positions)]


def candidate(source, text, output, amount=.7, bend=0):
    font=TTFont(source)
    if 'glyf' not in font: raise ValueError('Prototype supports native TrueType outlines only')
    before=shaped(font,text); records=[]
    # All compound references are resolved before replacing sample glyphs.
    inputs={name:raster(font,name) for name,*_ in before}
    for name,item in inputs.items():
        if item is None: continue
        mask,transform=item
        # Protect native joining boundaries at x=0 and x=advance. This is a
        # conservative guard, not proof that arbitrary joining is unchanged.
        left,top,scale=transform; advance=font['hmtx'][name][0]*scale
        xx=np.arange(mask.shape[1])+left
        protected=np.minimum(1,np.minimum(abs(xx),abs(xx-advance))/20)[None,:]
        try:
            new,record=pressure(mask,amount,int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big'),protected,bend=bend)
        except ValueError as error:
            records.append(dict(glyph=name,status='rejected',reason=str(error)));continue
        original=font['glyf'][name]
        glyph=outline(new,transform)
        font['glyf'][name]=glyph
        # Repaint vectors in the original viewport before accepting the contour
        # simplification; do not compare differently cropped masks.
        vector,_=raster(font,name,viewport=(*transform,mask.shape[1],mask.shape[0]))
        try: record['vectorChecks']=validate_reconstruction(mask,vector)
        except ValueError as error:
            font['glyf'][name]=original
            records.append(dict(glyph=name,status='rejected-vector',reason=str(error)))
            continue
        records.append(dict(glyph=name,status='candidate',**record))
    assert shaped(font,text)==before, 'Native shaping positions changed'
    for rec in font['name'].names:
        if rec.nameID in {1,3,4,6,16,17}: rec.string='Dad Pressure Experiment'.encode(rec.getEncoding(),errors='replace')
    font.flavor=None;output.parent.mkdir(parents=True,exist_ok=True);font.save(output)
    return dict(source=str(source),sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),text=text,output=str(output),shapingUnchanged=True,glyphs=records,limitations=['Only sample-shaped glyphs treated; not a production font','Native anchor and advance values retained; joining requires whole-sentence review','Raster guards do not establish linguistic identity or style acceptance'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--numbers',default='26,32,54,76,105,163');p.add_argument('--output',type=Path,default=ROOT/'output/font-review/supplemental-pressure');p.add_argument('--bend',type=float,default=0);args=p.parse_args()
    review=json.loads((ROOT/'docs/source-style-review.json').read_text()); numbers={int(x) for x in args.numbers.split(',')}; records=[];samples=[]
    for row in review['sources']:
        if row['number'] not in numbers:continue
        # Packaged derivatives already carry lawful names and native repairs.
        source=ROOT/row['fonts'][0]['file'];out=args.output/f"{row['number']}.ttf"
        rec=candidate(source,row['sample'],out,bend=args.bend);rec['sourceNumber']=row['number'];records.append(rec)
        for label,path in [('source',source),('pressure',out)]:samples.append(dict(label=f"{row['number']} {Path(row['source']).stem} {label}",font=str(path),text=row['sample']))
    args.output.mkdir(parents=True,exist_ok=True);(args.output/'review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));(args.output/'spec.json').write_text(json.dumps(dict(samples=samples),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
