"""Review-only smooth lettering experiment from a pinned, licensed pixel donor.

No production font or coverage manifest is changed. The Unifont diagonal pixel
contacts use eight-connected foreground topology; smoothing makes those contacts
real strokes while preserving separate parts and enclosed counters.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy import ndimage as ndi
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from pen_translate import Settings, translate

SHA='472201e45a050bff4c7658208b8c73e34ebce3764b287a5a46c7774038ef9391'
ROOT=Path(__file__).resolve().parents[2]


def topology(mask):
    parts=ndi.label(mask,structure=np.ones((3,3)))[1]
    holes=ndi.label(ndi.binary_fill_holes(mask)&~mask)[1]
    return int(parts),int(holes)


def smooth(mask, pixel_size=32):
    """Search bounded rounding; reject changed parts, counters or major mass."""
    original=topology(mask)
    for radius in (.6,.5,.4,.3):
        field=ndi.gaussian_filter(mask.astype(float),pixel_size*radius)
        for threshold in (.5,.45,.4,.35):
            candidate=field>=threshold
            if topology(candidate)!=original:continue
            if ndi.label(ndi.binary_erosion(candidate,iterations=2))[1]!=original[0]:continue
            # Check each source component maps to a different surviving part.
            a,n=ndi.label(mask,structure=np.ones((3,3)))
            b,_=ndi.label(candidate,structure=np.ones((3,3)))
            seen=set();valid=True
            for i in range(1,n+1):
                hits=set(np.unique(b[a==i]))-{0}
                if len(hits)!=1 or seen&hits:valid=False;break
                j=hits.pop();seen.add(j)
                if not .8<=(b==j).sum()/(a==i).sum()<=1.2:valid=False;break
            old_holes=ndi.binary_fill_holes(mask)&~mask
            new_holes=ndi.binary_fill_holes(candidate)&~candidate
            labels,count=ndi.label(old_holes)
            for i in range(1,count+1):
                hole=labels==i
                if (hole&new_holes).sum()<hole.sum()*.75:valid=False;break
            if valid:return candidate,dict(radius=radius,threshold=threshold,topology=original)
    raise ValueError('No topology-preserving smoothing candidate')


def validate_reconstruction(before,after):
    if topology(before)!=topology(after):raise ValueError('Reconstruction changed topology')
    a,count=ndi.label(before,structure=np.ones((3,3)))
    b,_=ndi.label(after,structure=np.ones((3,3)))
    used=set();ratios=[]
    for i in range(1,count+1):
        ids=set(np.unique(b[a==i]))-{0}
        if len(ids)!=1 or ids&used:raise ValueError('Reconstruction merged or lost a component')
        j=ids.pop();used.add(j);ratio=float((b==j).sum()/(a==i).sum());ratios.append(ratio)
        if not .8<=ratio<=1.2:raise ValueError('Reconstruction changed component area too far')
    old=ndi.binary_fill_holes(before)&~before;new=ndi.binary_fill_holes(after)&~after
    labels,count=ndi.label(old);retention=[]
    for i in range(1,count+1):
        hole=labels==i;fraction=float((hole&new).sum()/hole.sum());retention.append(fraction)
        if fraction<.75:raise ValueError('Reconstruction reduced a counter too far')
    return dict(componentAreaRatios=ratios,counterOverlap=retention)


def raster(font,cp,wide=False):
    name=font.getBestCmap()[cp];pen=SVGPathPen(font.getGlyphSet());font.getGlyphSet()[name].draw(pen)
    # 64 source units per em; pixels occupy 4 units. Preserve the shared
    # baseline/scale across glyphs instead of fitting each bounding box.
    from fontTools.pens.boundsPen import BoundsPen
    bp=BoundsPen(font.getGlyphSet());font.getGlyphSet()[name].draw(bp)
    shift=64 if wide and font['hmtx'][name][0]==0 else 0
    x0,y0,width,height=(-8,-64,80,80) if wide else (-8,-56,48,64)
    if bp.bounds:
        left,bottom,right,top=bp.bounds
        assert x0<left+shift and right+shift<x0+width and -y0-height<bottom and top<-y0, (hex(cp),bp.bounds,'clipped viewport')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width*8}" height="{height*8}" viewBox="{x0} {y0} {width} {height}"><rect x="{x0}" y="{y0}" width="{width}" height="{height}" fill="white"/><path transform="translate({shift} 0) scale(1 -1)" d="{pen.getCommands()}" fill="black"/></svg>'
    doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
    return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128


def prepare_letter(mask,cp,method='strokes'):
    """Return a guarded deterministic candidate; raises on any rejected form."""
    if not mask.any():raise ValueError('No source ink in raster')
    if method=='strokes':
        from unifont_strokes import reconstruct
        chosen=None
        for counter_margin in (0,.15,.25):
            for stroke_width in (.9,1.0,.95):
                for loop_width in (.75,.7,.65):
                    candidate,metadata=reconstruct(mask,width=stroke_width,loop_width=loop_width,counter_margin=counter_margin)
                    try:metadata.update(validate_reconstruction(mask,candidate))
                    except ValueError:continue
                    chosen=candidate,metadata;break
                if chosen is not None:break
            if chosen is not None:break
        # Garay's sharper digits/cross and two-loop JA need different widths;
        # these are reviewed source-specific recipes, subject to identical guards.
        garay_widths={0x10D42:(.75,.6),
                      0x10D6F:(.75,.6),0x10D75:(.75,.8)}
        if chosen is None and cp in garay_widths:
            width,loop=garay_widths[cp]
            candidate,metadata=reconstruct(mask,width=width,loop_width=loop)
            metadata.update(validate_reconstruction(mask,candidate))
            chosen=candidate,metadata
        if chosen is None and cp in (0x10D4C,0x10D69):
            # Preserve the comma's broad head and thin tail; a uniform skeleton
            # stroke cannot preserve both within the component-area bound.
            candidate,metadata=smooth(mask,pixel_size=24 if cp==0x10D4C else 32)
            metadata.update(validate_reconstruction(mask,candidate))
            metadata['method']='rounded-asymmetric-mark'
            chosen=candidate,metadata
        if chosen is None:raise ValueError('No stroke widths preserve components and counters')
        rounded,record=chosen
        chosen=None
        for strength in (.6,.45,.3,.15,0):
            image,treatment=translate(rounded,Settings(strength=strength,seed=cp,pressure=.2,taper=.1,bend=.006))
            pad=treatment['padding'];image=image.crop((pad,pad,image.width-pad,image.height-pad))
            try:checks=validate_reconstruction(mask,np.asarray(image)<128)
            except ValueError:continue
            chosen=image,treatment,checks;break
        if chosen is None:raise ValueError('No pressure treatment preserves components and counters')
        treated,treatment,checks=chosen;record.update(checks)
    else:
        rounded,record=smooth(mask)
        treated,treatment=translate(rounded,Settings(strength=.6,seed=cp,pressure=.2,taper=.1,bend=.006))
        pad=treatment['padding'];treated=treated.crop((pad,pad,treated.width-pad,treated.height-pad))
    final=np.asarray(treated)<128
    if topology(final)!=topology(mask):raise ValueError('Pen treatment changed topology')
    old_holes=ndi.binary_fill_holes(mask)&~mask
    new_holes=ndi.binary_fill_holes(final)&~final
    labels,count=ndi.label(old_holes)
    for i in range(1,count+1):
        hole=labels==i
        if (hole&new_holes).sum()<hole.sum()*.75:
            raise ValueError('Pen treatment reduced a counter too far')
    if method=='strokes':record.update(validate_reconstruction(mask,final))
    record.update(status='structural checks pass; visual review still required',penTreatment=treatment)
    return treated,record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--script',choices=['tolong','garay','tai-yo'],default='tolong')
    parser.add_argument('--method',choices=['outline','strokes'],default='outline')
    parser.add_argument('--output',type=Path,default=ROOT/'output/font-review/unifont-prototype')
    args=parser.parse_args();assert hashlib.sha256(args.source.read_bytes()).hexdigest()==SHA
    font=TTFont(args.source);assert font['head'].unitsPerEm==64
    low,high={'tolong':(0x11DB0,0x11DEF),'garay':(0x10D40,0x10D8F),'tai-yo':(0x1E6C0,0x1E6FF)}[args.script]
    points=[]
    for line in (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines():
        cp=int(line.split(';')[0],16)
        if low<=cp<=high:points.append(cp)
    args.output.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(1200,((len(points)+5)//6)*160),'#f5f2eb');draw=ImageDraw.Draw(sheet)
    records=[]
    for j,cp in enumerate(points):
        mask=raster(font,cp,wide=args.script!='tolong')
        try:
            treated,record=prepare_letter(mask,cp,args.method)
        except ValueError as error:
            # A rejected experiment must never masquerade as accepted lettering.
            treated=Image.fromarray(np.uint8(~mask)*255)
            record=dict(status='rejected; source shown unchanged',reason=str(error))
        x=j%6*200;y=j//6*160
        before=Image.fromarray(np.uint8(~mask)*255)
        for im,dx in [(before,0),(treated,90)]:
            sheet.paste(ImageOps.contain(im,(84,112),Image.Resampling.LANCZOS),(x+dx,y))
        sheet.paste(ImageOps.contain(treated,(18,24),Image.Resampling.LANCZOS),(x+177,y+66))
        draw.text((x+6,y+120),f'U+{cp:X} '+('NEEDS REDRAW' if record['status'].startswith('rejected') else 'source / smooth'),font=ImageFont.load_default(size=12),fill='black')
        record.update(codepoint=f'U+{cp:X}')
        records.append(record)
    sheet.save(args.output/f'{args.script}-comparison.png')
    (args.output/'review.json').write_text(json.dumps(dict(status='prototype only; not bundled; linguistic review and mark attachment pending',method=args.method,sourceSha256=SHA,sourceLicense='SIL OFL 1.1',glyphs=records),indent=2)+'\n')
    print(f'{len(records)} {args.script} prototypes; {sum(r["status"].startswith("rejected") for r in records)} rejected; output {args.output}')


if __name__=='__main__':main()
