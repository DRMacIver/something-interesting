"""Compile Tai Yo's licensed horizontal forms with native body/mark attachment."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from prototype_unifont_lettering import ROOT, SHA, raster, prepare_letter
from build_garay import SOURCE, trace, translate_glyph
from build_tolong import bounds

MARKS={0x1E6E3,0x1E6E6,0x1E6EE,0x1E6EF,0x1E6F5}


def build(output,source=SOURCE):
    assert hashlib.sha256(source.read_bytes()).hexdigest()==SHA
    original=TTFont(source);assert original['head'].unitsPerEm==64
    points=[int(line.split(';')[0],16) for line in
            (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines()
            if 0x1E6C0<=int(line.split(';')[0],16)<=0x1E6FF]
    assert len(points)==55
    glyphs={'.notdef':TTGlyphPen(None).glyph(),'space':TTGlyphPen(None).glyph()}
    metrics={'.notdef':(500,0),'space':(250,0)};cmap={32:'space'};review=[];shifts={}
    for cp in points:
        image,record=prepare_letter(raster(original,cp,wide=True),cp)
        glyph=trace(np.asarray(image)<128);x0,y0,x1,y1=bounds(glyph)
        if cp in MARKS:
            glyph=translate_glyph(glyph,-round((x0+x1)/2),-y0);advance=0
        else:
            shifts[cp]=50-x0
            glyph=translate_glyph(glyph,shifts[cp],0);advance=round(x1-x0)+100
        name=f'u{cp:X}';glyphs[name]=glyph;cmap[cp]=name
        metrics[name]=(advance,round(bounds(glyph)[0]))
        review.append(dict(codepoint=f'U+{cp:X}',advance=advance,**record))
    fb=FontBuilder(1000,isTTF=True);fb.setupGlyphOrder(list(glyphs));fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=1500,descent=-300)
    notice='\n'.join(sorted({n.toUnicode() for n in original['name'].names if n.nameID==0}))
    fb.setupNameTable(dict(familyName='Dad Tai Yo',styleName='Regular',uniqueFontIdentifier='DadTaiYo-1',
        fullName='Dad Tai Yo',psName='DadTaiYo',version='Version 0.001',copyright=notice,
        licenseDescription='Licensed under the SIL Open Font License, Version 1.1.',
        licenseInfoURL='https://openfontlicense.org/'))
    fb.setupOS2(sTypoAscender=1500,sTypoDescender=-300,sTypoLineGap=0,usWinAscent=1500,usWinDescent=300)
    fb.setupPost();fb.setupMaxp()
    rules=['languagesystem DFLT dflt;','languagesystem tayo dflt;']
    for cp in sorted(MARKS):rules.append(f'markClass u{cp:X} <anchor 0 0> @m{cp:X};')
    rules.append('feature mark {');anchors=[]
    for cp in points:
        if cp in MARKS:continue
        x0,y0,x1,y1=bounds(glyphs[cmap[cp]])
        rule=f'pos base u{cp:X}'
        for mark in sorted(MARKS):
            x=round((x0+x1)/2);y=round(y1+55)
            # Figure 16-10 places narrow marks over the body, not the tail.
            # Long AU/OM signs need the full top clearance to avoid crossing it.
            if cp in (0x1E6CD,0x1E6D5) and mark in (0x1E6E3,0x1E6EE,0x1E6EF):
                x=round(24*1000/48+shifts[cp])
                if cp==0x1E6CD:
                    body_top=24 if mark==0x1E6EF else 28
                    y=round(body_top*1000/48+55)
            rule+=f' <anchor {x} {y}> mark @m{mark:X}'
            anchors.append(dict(base=f'U+{cp:X}',mark=f'U+{mark:X}',x=x,y=y))
        rules.append(rule+';')
    rules.append('} mark;');rules.append('feature mkmk {')
    for previous in sorted(MARKS):
        rule=f'pos mark u{previous:X}'
        for following in sorted(MARKS):
            # In horizontal Tai Yo the next mark goes to the right, sharing
            # the attachment baseline. Width-dependent gap preserves AY+ANG.
            dx=round(bounds(glyphs[cmap[previous]])[2]-bounds(glyphs[cmap[following]])[0]+55)
            rule+=f' <anchor {dx} 0> mark @m{following:X}'
        rules.append(rule+';')
    rules.append('} mkmk;');addOpenTypeFeaturesFromString(fb.font,'\n'.join(rules))
    fb.font['head'].created=fb.font['head'].modified=3406620153
    output.parent.mkdir(parents=True,exist_ok=True);fb.save(output)
    output.with_suffix('.json').write_text(json.dumps(dict(status='compiled; packaging and browser review required',
        sourceSha256=SHA,sourceLicence='assets/fonts/licenses/Unifont-OFL.txt',glyphs=review,anchors=anchors),indent=2)+'\n')
    print(f'Built {output}: 55 Tai Yo characters including five native marks',flush=True)
    return output



def build_registered():
    output=ROOT/'build/unicode-sources/tai-yo/DadTaiYo.ttf'
    stamp=output.with_suffix('.build.json')
    inputs=[Path(__file__),SOURCE,ROOT/'tools/font/prototype_unifont_lettering.py',
            ROOT/'tools/font/unifont_strokes.py',ROOT/'tools/font/pen_translate.py',
            ROOT/'tools/font/build_garay.py',ROOT/'tools/font/build_tolong.py',
            ROOT/'data/font-sources/tai-yo.json',ROOT/'data/font-sources/tolong.json',
            ROOT/'data/unicode/18.0.0/UnicodeData.txt']
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
    p.add_argument('--output',type=Path,default=ROOT/'output/font-review/tai-yo/DadTaiYo.ttf')
    args=p.parse_args();build(args.output)
