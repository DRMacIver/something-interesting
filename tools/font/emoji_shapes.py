"""Original pen outlines for the Unicode coloured circle/square families."""
from fontTools.pens.ttGlyphPen import TTGlyphPen
import math
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen

COLOURS=['red','blue','orange','yellow','green','purple','brown']
SHAPES={**{cp:('circle',c,700) for cp,c in zip([0x1F534,0x1F535,*range(0x1F7E0,0x1F7E5)],COLOURS)},
        **{cp:('square',c,700) for cp,c in zip(range(0x1F7E5,0x1F7EC),COLOURS)},
        0x26AA:('circle','white',550),0x26AB:('circle','black',550),
        0x2B1B:('square','black',700),0x2B1C:('square','white',700),
        0x25AA:('square','black',250),0x25AB:('square','white',250),
        0x25FB:('square','white',550),0x25FC:('square','black',550),
        0x25FD:('square','white',400),0x25FE:('square','black',400)}


def draw(pen,kind):
    # Deliberately slight asymmetry, with continuous round curves. Coordinates
    # describe a 700-unit cell and are scaled as one drawing for smaller signs.
    if kind=='circle':
        # Eight quadratic arcs approximate a circle within 0.2%, instead of
        # the visibly squared four-arc approximation. A tiny ellipse/asymmetry
        # keeps the pen character without changing the circular silhouette.
        pen.moveTo((700,350))
        for i in range(8):
            mid=(i+0.5)*math.pi/4;end=(i+1)*math.pi/4
            control=(350+350*math.cos(mid)/math.cos(math.pi/8),350+348*math.sin(mid)/math.cos(math.pi/8))
            point=(350+350*math.cos(end),350+348*math.sin(end))
            pen.qCurveTo(control,point)
    else:
        pen.moveTo((48,0));pen.lineTo((650,3));pen.qCurveTo((701,3),(700,54))
        pen.lineTo((697,650));pen.qCurveTo((697,701),(647,700))
        pen.lineTo((51,697));pen.qCurveTo((-1,697),(0,647))
        pen.lineTo((3,48));pen.qCurveTo((3,-1),(48,0))
    pen.closePath()


def add_shapes(root,glyphs,metrics,cmap,layers,palette,review,heart_record):
    colours={s['colour']:tuple(s['rgb']) for s in heart_record['samples']}
    colours.update(black=(17,17,17),white=(255,255,255))
    for cp,(kind,colour,size) in SHAPES.items():
        name=f'u{cp:X}';scale=size/700;left=50;bottom=(700-size)/2
        transform=(scale,0,0,scale,left,bottom)
        outer=TTGlyphPen(None);draw(TransformPen(outer,transform),kind)
        ring=TTGlyphPen(None);draw(TransformPen(ring,transform),kind)
        # A 32-unit pen at full size; retain an 18-unit minimum on small signs.
        stroke=max(18,32*scale);inner=(size-2*stroke)/700
        draw(TransformPen(ReverseContourPen(ring),(inner,0,0,inner,left+stroke,bottom+stroke)),kind)
        glyphs[name+'.fill']=outer.glyph();glyphs[name+'.ink']=ring.glyph()
        glyphs[name]=glyphs[name+'.fill'] if colour=='black' else glyphs[name+'.ink']
        for key in [name,name+'.fill',name+'.ink']: metrics[key]=(size+100,left)
        rgb=colours[colour]
        if rgb not in palette:palette.append(rgb)
        layers[name]=[(name+'.fill',palette.index(rgb)),(name+'.ink',1)]
        cmap[cp]=name
        review.append(dict(codepoint=f'U+{cp:04X}',shape=kind,colour=colour,rgb=rgb,size=size,
                           advance=size+100,design='original asymmetric pen geometry; distinct Unicode sizes; sampled semantic colours'))
    variants=[]
    for line in (root/'data/unicode/18.0.0/emoji/emoji-variation-sequences.txt').read_text().splitlines():
        points=line.split(';')[0].strip().split()
        if len(points)==2 and not points[0].startswith('#'):
            try:cp,vs=map(lambda x:int(x,16),points)
            except ValueError:continue
            if cp in SHAPES:variants.append((cp,vs))
    return variants
