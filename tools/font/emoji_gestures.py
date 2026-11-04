"""Expressive hand gestures with reviewed skin masks and exact modifiers."""
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from fontTools.ttLib import TTFont
from emoji_licensed import raster
from pen_translate import Settings, translate

SYMBOLS='✊✋🖐🖖👌🤌🤏✌🤞🫰🤟🤘🤙👈👉👆🖕👇☝👎👊🤛🤜🤚👋🫱🫲🫳🫴🫵🫶🫷🫸👏👐🙌🙏🤲🤝'
POINTS=list(map(ord,SYMBOLS))


def prepare(font,cp):
    name=font.getBestCmap()[cp]
    source=raster(font.getGlyphSet(location={'wght':400}),name)
    treated,report=translate(source,Settings(strength=1.7,seed=cp))
    ink=np.asarray(treated)<128
    white=ndimage.binary_fill_holes(ink)
    labels,count=ndimage.label(white&~ink)
    sizes=np.bincount(labels.ravel());sizes[0]=0
    ranked=np.argsort(sizes)[::-1]
    excluded=np.zeros_like(ink)
    if cp==0x1F44C:
        assert count==3
        excluded=labels==ranked[1]  # Air inside the thumb/index circle.
    elif cp==0x1F91E:
        assert count==6 and sizes[ranked[-2]]<30
        excluded=(labels!=0)&(sizes[labels]<30)  # Tiny gap below crossed fingers.
    elif cp==0x1F90C:
        assert count==2 and sizes[ranked[1]]<250
        excluded=labels==ranked[1]  # Air between the pinched fingers.
        # The donor deliberately leaves the wrist open. Close only the fill
        # mask at its two reviewed endpoints; never add a black wrist stroke.
        pad=report['padding'];ys,xs=np.nonzero(ink)
        ends=[]
        for x,y in [(60,283),(160,340)]:
            distance=(xs-x-pad)**2+(ys-y-pad)**2
            j=distance.argmin();assert distance[j]<20**2
            ends.append((int(xs[j]),int(ys[j])))
        closed=Image.fromarray(ink.astype('uint8')*255)
        ImageDraw.Draw(closed).line(ends,fill=255,width=3)
        white=ndimage.binary_fill_holes(np.asarray(closed)>0)
    elif cp==0x1FAF6:
        assert count==3 and sizes[ranked[2]]>10000
        excluded=labels==ranked[2]  # Heart-shaped air between the two hands.
    wrist_pairs={
        0x1FAF7:[((316,245),(328,340))],
        0x1FAF8:[((73,245),(58,342))],
        0x1F64C:[((56,327),(128,326)),((261,326),(329,327))],
    }.get(cp,[])
    if wrist_pairs:
        assert count==(4 if cp==0x1F64C else 0)
        closed=Image.fromarray(ink.astype('uint8')*255)
        ys,xs=np.nonzero(ink);pad=report['padding']
        for pair in wrist_pairs:
            ends=[]
            for x,y in pair:
                distance=(xs-x-pad)**2+(ys-y-pad)**2
                j=distance.argmin();assert distance[j]<12**2
                ends.append((int(xs[j]),int(ys[j])))
            ImageDraw.Draw(closed).line(ends,fill=255,width=3)
        white=ndimage.binary_fill_holes(np.asarray(closed)>0)
        report['fillOnlyWristClosures']=len(wrist_pairs)
    # Paint underneath the strokes. Abutting separately traced fill/ink edges
    # otherwise expose white antialiasing seams, especially on dark tones.
    skin=white&~excluded
    assert skin.sum()>white.sum()*.25
    report.update(skinPixels=int(skin.sum()),whiteGapPixels=int(excluded.sum()))
    return (white,skin,ink),report,name


def handshake_masks(white, ink):
    """Partition the reviewed handshake, preserving its original black ink.

    The left-entering (rightwards) hand owns the main palm AND the tiny
    lowest fingertip. The right-entering hand owns the upper thumb and four
    curled fingers. See the pinned colour-reference review in the docs.
    """
    labels,count=ndimage.label(white&~ink)
    assert count==7
    sizes=np.bincount(labels.ravel())
    assert sizes[1]>10000 and sizes[2]>18000 and all(100<sizes[i]<1100 for i in range(3,8))
    second=np.isin(labels,[1,3,4,5,6])
    # Extend underneath ink to avoid independently traced edges exposing seams.
    second=ndimage.binary_dilation(second,iterations=3)&white
    return white,second


def mixed_handshakes(root):
    forms=[]
    for line in (root/'data/unicode/18.0.0/emoji/emoji-zwj-sequences.txt').read_text().splitlines():
        fields=line.split('#')[0].strip().split(';')
        if len(fields)<2 or fields[1].strip()!='RGI_Emoji_ZWJ_Sequence':continue
        points=[int(cp,16) for cp in fields[0].split()]
        if points[0]!=0x1FAF1:continue
        assert len(points)==5 and points[2:4]==[0x200D,0x1FAF2]
        assert all(0x1F3FB<=points[i]<=0x1F3FF for i in (1,4)) and points[1]!=points[4]
        forms.append(''.join(map(chr,points)))
    assert len(forms)==20 and len(set(forms))==20
    return forms


def add_gestures(root,glyphs,metrics,cmap,layers,review,outline):
    spec=json.loads((root/'data/font-sources/noto-emoji.json').read_text())['files'][0]
    assert {chr(cp)+chr(t) for cp in POINTS for t in range(0x1F3FB,0x1F400)} <= set(spec['include_sequences'])
    path=root/spec['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==spec['sha256']
    font=TTFont(path);sequences=[];rules=[]
    for cp in POINTS:
        assert cp not in cmap
        (white,skin,ink),treatment,source_name=prepare(font,cp)
        ys,xs=np.nonzero(white);x0,y0,x1,y1=map(int,(xs.min(),ys.min(),xs.max(),ys.max()))
        factor=760/max(x1-x0+1,y1-y0+1);transform=x0,y0,factor
        advance=round((x1-x0+1)*factor)+100;name=f'u{cp:X}'
        glyphs[name]=outline(ink,transform);metrics[name]=advance,50;cmap[cp]=name
        assert glyphs[name].numberOfContours>=treatment['sourceComponents']+treatment['sourceHoles']
        for suffix,mask in [('white',white),('skin',skin),('ink',ink)]:
            layer=name+'.'+suffix;glyphs[layer]=outline(mask,transform);metrics[layer]=advance,50
        layers[name]=[(name+'.white',0),(name+'.ink',1)]
        for i in range(5):
            variant=name+f'.tone{i+1}';glyphs[variant]=glyphs[name];metrics[variant]=advance,50
            layers[variant]=[(name+'.white',0),(name+'.skin',6+i),(name+'.ink',1)]
            sequences.append(chr(cp)+chr(0x1F3FB+i))
            rules.append(f'sub {name} tone{i+1} by {variant};')
        review.append(dict(codepoint=f'U+{cp:04X}',category='gestures',source=spec['path'],sourceGlyph=source_name,
                           sourceWeight=400,sourcePixels=384,advance=advance,bounds=[x0,y0,x1,y1],
                           penTreatment=treatment,license='NotoEmoji-OFL.txt',
                           fill='enclosed hand regions; reviewed air gaps remain white; open wrists closed only in fill'))
    # Longer ligatures must precede the individual hand modifier rules.
    mixed_rules=[]
    (white,skin,ink),treatment,source_name=prepare(font,0x1F91D)
    first,second=handshake_masks(white,ink)
    ys,xs=np.nonzero(white)
    factor=760/max(xs.max()-xs.min()+1,ys.max()-ys.min()+1)
    transform=int(xs.min()),int(ys.min()),factor
    base='u1F91D'
    glyphs[base+'.second']=outline(second,transform);metrics[base+'.second']=metrics[base]
    forms=mixed_handshakes(root)
    assert set(forms)<=set(spec['include_sequences'])
    for text in forms:
        a,b=ord(text[1])-0x1F3FB,ord(text[4])-0x1F3FB
        name=base+f'.mix{a+1}{b+1}'
        glyphs[name]=glyphs[base];metrics[name]=metrics[base]
        layers[name]=[(base+'.white',0),(base+'.skin',6+a),(base+'.second',6+b),(base+'.ink',1)]
        mixed_rules.append(f'sub u1FAF1 tone{a+1} joiner u1FAF2 tone{b+1} by {name};')
        review.append(dict(sequence=text,category='mixed-handshakes',glyphName=name,label=f'Tones {a+1} / {b+1}',
                           source=spec['path'],sourceGlyph=source_name,penTreatment=treatment,
                           license='NotoEmoji-OFL.txt',fill='first: main palm and lowest tip; second: upper thumb and four curled fingers'))
    sequences.extend(forms)
    rules=mixed_rules+rules
    variants=[]
    for line in (root/'data/unicode/18.0.0/emoji/emoji-variation-sequences.txt').read_text().splitlines():
        body=line.split('#')[0].strip()
        if not body:continue
        seq=[int(s,16) for s in body.split(';')[0].split()]
        if seq[0] in POINTS:variants.append(tuple(seq))
    return sequences,'\n'.join(rules),variants
