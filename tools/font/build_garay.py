"""Compile licensed Garay stroke drawings with RTL-safe native mark attachment."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from skimage.measure import find_contours, approximate_polygon
from prototype_unifont_lettering import ROOT, SHA, raster, prepare_letter
from build_tolong import bounds

MARKS=set(range(0x10D69,0x10D6E))
SOURCE=ROOT/'build/unicode-sources/unifont/unifont_upper-18.0.01.otf'


def trace(mask):
    pen=TTGlyphPen(None)
    for contour in find_contours(np.pad(mask.astype(float),1),.5):
        contour=approximate_polygon(contour,tolerance=.35)
        points=[(round(((x-1)/8-8)*1000/48),round((64-(y-1)/8)*1000/48)) for y,x in contour]
        if len(set(points))<3:continue
        pen.moveTo(points[0])
        for point in points[1:-1]:pen.lineTo(point)
        pen.closePath()
    return pen.glyph()


def translate_glyph(glyph,dx,dy):
    pen=TTGlyphPen(None);glyph.draw(TransformPen(pen,(1,0,0,1,dx,dy)),None)
    return pen.glyph()


def build(output,source=SOURCE):
    assert hashlib.sha256(source.read_bytes()).hexdigest()==SHA
    original=TTFont(source);assert original['head'].unitsPerEm==64
    points=[int(line.split(';')[0],16) for line in
            (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines()
            if 0x10D40<=int(line.split(';')[0],16)<=0x10D8F]
    assert len(points)==69
    glyphs={'.notdef':TTGlyphPen(None).glyph(),'space':TTGlyphPen(None).glyph()}
    metrics={'.notdef':(500,0),'space':(250,0)};cmap={32:'space'};review=[]
    for cp in points:
        image,record=prepare_letter(raster(original,cp,wide=True),cp)
        glyph=trace(np.asarray(image)<128);x0,y0,x1,y1=bounds(glyph)
        if cp in MARKS:
            # Review-only translation is removed by centering marks at zero.
            glyph=translate_glyph(glyph,-round((x0+x1)/2),-y0)
            advance=0
        else:
            glyph=translate_glyph(glyph,50-x0,0)
            advance=round(x1-x0)+100
        name=f'u{cp:X}';glyphs[name]=glyph;cmap[cp]=name
        metrics[name]=(advance,round(bounds(glyph)[0]))
        review.append(dict(codepoint=f'U+{cp:X}',advance=advance,**record))
    fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(list(glyphs));fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=1250,descent=-300)
    notice='\n'.join(sorted({n.toUnicode() for n in original['name'].names if n.nameID==0}))
    fb.setupNameTable(dict(familyName='Dad Garay',styleName='Regular',uniqueFontIdentifier='DadGaray-1',
        fullName='Dad Garay',psName='DadGaray',version='Version 0.001',copyright=notice,
        licenseDescription='Licensed under the SIL Open Font License, Version 1.1.',
        licenseInfoURL='https://openfontlicense.org/'))
    fb.setupOS2(sTypoAscender=1250,sTypoDescender=-300,sTypoLineGap=0,usWinAscent=1250,usWinDescent=300)
    fb.setupPost();fb.setupMaxp()
    rules=['languagesystem DFLT dflt;','languagesystem gara dflt;']
    for cp in sorted(MARKS):rules.append(f'markClass u{cp:X} <anchor 0 0> @above;')
    rules.append('feature mark {')
    for cp in points:
        if cp in MARKS:continue
        x0,y0,x1,y1=bounds(glyphs[cmap[cp]])
        rules.append(f'pos base u{cp:X} <anchor {round((x0+x1)/2)} {round(y1+55)}> mark @above;')
    rules.append('} mark;');rules.append('feature mkmk {')
    for cp in sorted(MARKS):
        rules.append(f'pos mark u{cp:X} <anchor 0 {round(bounds(glyphs[cmap[cp]])[3]+55)}> mark @above;')
    rules.append('} mkmk;');addOpenTypeFeaturesFromString(fb.font,'\n'.join(rules))
    fb.font['head'].created=fb.font['head'].modified=3406620153
    output.parent.mkdir(parents=True,exist_ok=True);fb.save(output)
    output.with_suffix('.json').write_text(json.dumps(dict(status='compiled; packaging and browser review required',
        sourceSha256=SHA,sourceLicence='assets/fonts/licenses/Unifont-OFL.txt',glyphs=review),indent=2)+'\n')
    print(f'Built {output}: 69 Garay characters including five native combining marks',flush=True)
    return output



def build_registered():
    output=ROOT/'build/unicode-sources/garay/DadGaray.ttf'
    stamp=output.with_suffix('.build.json')
    inputs=[Path(__file__),SOURCE,ROOT/'tools/font/prototype_unifont_lettering.py',
            ROOT/'tools/font/unifont_strokes.py',ROOT/'tools/font/pen_translate.py',
            ROOT/'tools/font/build_tolong.py',ROOT/'data/font-sources/garay.json',
            ROOT/'data/font-sources/tolong.json',ROOT/'data/unicode/18.0.0/UnicodeData.txt']
    recipe=hashlib.sha256(b''.join(p.read_bytes() for p in inputs)).hexdigest()
    if output.exists() and stamp.exists():
        old=json.loads(stamp.read_text())
        if old.get('recipe')==recipe and old.get('sha256')==hashlib.sha256(output.read_bytes()).hexdigest():
            return output
    build(output)
    stamp.write_text(json.dumps(dict(recipe=recipe,sha256=hashlib.sha256(output.read_bytes()).hexdigest()),indent=2)+'\n')
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'output/font-review/garay/DadGaray.ttf')
    args=p.parse_args();build(args.output)
