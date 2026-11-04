"""Review candidate for nine Unicode 18 historical relation variations.

Use licensed donor curves, component transforms, and an original Cartesian
descender drawing. Unicode proposal pages are semantic references only; their
font programs and artwork are not extracted into the candidate.
"""
import hashlib
import json
import math
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
import pymupdf

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/font-review/historical-math-variants'
from math_historical_variants import POINTS,KURRENT,REFERENCES,donor,draw_variant,cartesian


def build(out=OUT,points=POINTS):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    math_font,math_source=donor('newcm.json','NewCMMath-Regular.otf')
    order=['.notdef'];charstrings={};metrics={};cmap={};variations={};records=[]
    p=T2CharStringPen(500,None);charstrings['.notdef']=p.getCharString();metrics['.notdef']=(500,0)
    for cp in points:
        source=math_font
        assert source['head'].unitsPerEm==1000
        gs=source.getGlyphSet();native=source.getBestCmap().get(cp);advance=source['hmtx'][native][0] if native else 1000
        selector=0xfe02 if cp==KURRENT else 0xfe00
        base=f'u{cp:X}';variant=base+'.variant'
        default_draw=lambda p:cartesian(p,advance,False) if cp==0x1db10 else gs[native].draw(p)
        for name,draw in [(base,default_draw),(variant,lambda p:draw_variant(p,cp,math_font,advance))]:
            pen=T2CharStringPen(advance,None);draw(pen);charstrings[name]=pen.getCharString()
            bounds=BoundsPen(None);draw(bounds)
            metrics[name]=(advance,math.floor(bounds.bounds[0]));order.append(name)
        cmap[cp]=base;variations.setdefault(selector,[]).append((cp,variant))
        records.append(dict(base=cp,selector=selector,defaultGlyph=base,variantGlyph=variant,
            defaultSourceGlyph=native,advance=advance,
            construction='original looped kurrent-z centreline' if cp==KURRENT else 'original Cartesian default and descender centrelines' if cp==0x1db10 else 'two horizontal bars and one diagonal arm' if cp in {0x22dc,0x22dd} else 'licensed NewCM inverted-lazy-S curves, transformed and composed with original horizontal strokes'))
    fb=FontBuilder(1000,isTTF=False);fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap)
    copyright=math_font['name'].getDebugName(0)
    fb.setupCFF('DadHistoricalMathCandidate',dict(FullName='Dad Historical Math Candidate',FamilyName='Dad Historical Math Candidate',Weight='Regular',Notice=copyright),charstrings,{})
    fb.setupHorizontalMetrics(metrics);fb.setupHorizontalHeader(ascent=850,descent=-250)
    fb.setupOS2(sTypoAscender=850,sTypoDescender=-250,usWinAscent=850,usWinDescent=250)
    fb.setupNameTable(dict(familyName='Dad Historical Math Candidate',styleName='Regular',uniqueFontIdentifier='DadHistoricalMathCandidate',fullName='Dad Historical Math Candidate',psName='DadHistoricalMathCandidate',version='Version 0.001',copyright=copyright,description='Modified NewCM subset with original relation stroke designs; upstream author does not maintain this candidate. See candidate.json.',licenseDescription='GUST Font License 1.0 / LPPL 1.3c; see candidate.json and copied notices.'))
    fb.setupPost();font=fb.font
    table=CmapSubtable.newSubtable(14);table.platformID=0;table.platEncID=5;table.language=0;table.cmap={};table.uvsDict=variations;font['cmap'].tables.append(table)
    font['head'].created=font['head'].modified=2082844800;font.recalcTimestamp=False
    path=out/'candidate.otf';font.save(path)
    data=ROOT/'data/unicode/18.0.0/StandardizedVariants.txt'
    pin=next(e['sha256'] for e in json.loads((ROOT/'data/unicode/sources.json').read_text())['files'] if e['path']=='18.0.0/StandardizedVariants.txt')
    assert hashlib.sha256(data.read_bytes()).hexdigest()==pin
    standard={tuple(int(c,16) for c in fields[0].split()) for row in data.read_text().splitlines() if (fields:=row.split('#')[0].strip().split(';'))[0]}
    assert {(r['base'],r['selector']) for r in records}<=standard
    result=dict(candidateOnly=True,scope=f'{len(points)} historical mathematical variants; combining attachment and production integration pending',sources=[math_source],references=REFERENCES if KURRENT in points else REFERENCES[:1],variants=records,fontSha256=hashlib.sha256(path.read_bytes()).hexdigest(),licences=['assets/fonts/licenses/NewCM-GUST.txt','assets/fonts/licenses/NewCM-LPPL.txt','assets/fonts/licenses/NewCM-Package-License.txt'],upstream=json.loads((ROOT/'data/font-sources/newcm.json').read_text()))
    # Notices are required even for an isolated review font.
    for notice in result['licences']:
        assert (ROOT/notice).is_file(),notice
        (out/Path(notice).name).write_bytes((ROOT/notice).read_bytes())
    (out/'README.txt').write_text('Dad Historical Math Candidate is a modified NewCM derivative.\n'
        'Copyright and licences from NewCM are retained in the font and supplied notices.\n'
        'The upstream author does not maintain this candidate. Ordinary math\n'
        'drawings and variants are included. Eight defaults and transformed lazy-S\n'
        'curves derive from NewCM; Cartesian defaults/descenders and straight relation\n'
        'strokes and kurrent z (when included) are original designs. Unicode proposal artwork is not extracted.\n'
        'Source: tools/font/prototype_historical_math_variants.py in this project.\n'
        'Original source, upstream revision and licences: candidate.json.\n'
        'Combining attachment, production integration and comic style review pending.\n')
    (out/'candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    specimen(path,out/'specimen.png',points)
    print(f'{len(points)} candidate variants: {path}')
    return result


def specimen(path,output,points=POINTS):
    # Pillow without libraqm silently ignores variation selectors. Draw the
    # actual named glyph paths; HarfBuzz routing is checked separately.
    font=TTFont(path);gs=font.getGlyphSet()
    height=len(points)*145+80
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}"><rect width="1200" height="{height}" fill="white"/><text x="25" y="35" font-size="24">Default / explicit variant / repeated variant: review candidate</text>']
    for row,cp in enumerate(points):
        y=145+row*145
        svg.append(f'<text x="20" y="{y-40}" font-size="20">U+{cp:X}</text>')
        for x,name in [(220,f'u{cp:X}'),*[(x,f'u{cp:X}.variant') for x in [470,720,840,960]]]:
            pen=SVGPathPen(gs);gs[name].draw(pen)
            svg.append(f'<path transform="translate({x},{y}) scale(.095,-.095)" d="{pen.getCommands()}"/>')
    svg.append('</svg>')
    data=''.join(svg).encode();Path(output).with_suffix('.svg').write_bytes(data)
    doc=pymupdf.open(stream=data,filetype='svg');doc[0].get_pixmap().save(output)


if __name__=='__main__':build()
