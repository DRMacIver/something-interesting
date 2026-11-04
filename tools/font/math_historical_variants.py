"""Licensed components and original strokes for historical math variations."""
import hashlib
import json
import math
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.boundsPen import BoundsPen

ROOT=Path(__file__).resolve().parents[2]
POINTS=[0x223d,0x2243,0x22cd,0x2242,0x2248,0x2a6c,0x22dc,0x22dd,0x1db10]
KURRENT=0x1d4cf
REFERENCES=[
    dict(url='https://www.unicode.org/wg2/docs/n5334R2-L-2603.Proposal.to.encode.historical.mathematical.relations.pdf',sha256='5911fbe09d86f80f1c37d2f6e438d3f61d926cd1c71f7704a66e4a96d874d46e',pages=[3,8,37,38],purpose='relation topology, math axis and Cartesian descender'),
    dict(url='https://www.unicode.org/wg2/docs/n5333R2-L-2533%20Proposal%20to%20encode%2012%20cossic%20characters.pdf',sha256='a14ca03cefa39340a8cc647d609432aa03b4dd43c310e24bb72a12910b252f61',pages=[4,9,10,12,19],purpose='looped descending kurrent z'),
]


def donor(spec_name,filename):
    spec=json.loads((ROOT/'data/font-sources'/spec_name).read_text())
    entry=next(e for e in spec['files'] if e['path'].endswith(filename))
    path=ROOT/entry['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
    return TTFont(path),dict(path=entry['path'],sha256=entry['sha256'])


def stroke(pen,points,width=30):
    """Original smooth pressure outline around a sampled design centreline."""
    sides=[[],[]]
    for i,(x,y) in enumerate(points):
        before=points[max(0,i-1)];after=points[min(len(points)-1,i+1)]
        dx,dy=after[0]-before[0],after[1]-before[1]
        length=math.hypot(dx,dy)
        assert length>0
        t=i/(len(points)-1)
        radius=width/2*(.92+.16*math.sin(math.pi*t))
        for side,sign in zip(sides,[1,-1]):side.append((x-sign*dy/length*radius,y+sign*dx/length*radius))
    contour=sides[0]+list(reversed(sides[1]))
    pen.moveTo(contour[0])
    for p in contour[1:]:pen.lineTo(p)
    pen.closePath()


def cubic_points(start,segments):
    points=[start]
    for a,b,end in segments:
        for i in range(1,81):
            t=i/80;s=1-t
            points.append(tuple(s**3*start[j]+3*s*s*t*a[j]+3*s*t*t*b[j]+t**3*end[j] for j in [0,1]))
        start=end
    return points


def cartesian(pen,advance,descender):
    points=cubic_points((80,370),[
        ((300,560),(350,80),(640,80)),
        ((940,80),(940,520),(650,520)),
        ((410,520),(360,190),(180,-180) if descender else (80,130)),
    ])
    stroke(pen,[(x*advance/1000,y) for x,y in points],38)


def draw_variant(pen,cp,math_font,advance):
    gs=math_font.getGlyphSet();cmap=math_font.getBestCmap()
    def lazy(center=250,scale=1,reverse=False):
        sy=-scale if reverse else scale
        # Normalize the licensed inverted lazy S to the native relation width.
        gs[cmap[0x223e]].draw(TransformPen(pen,(661/789,0,0,sy,56-56*661/789,center-250*sy)))
    def bar(y):stroke(pen,[(56,y),(722,y)],28)
    if cp==0x223d:lazy(reverse=True)
    elif cp in {0x2243,0x22cd}:
        lazy(350,.6,cp==0x22cd);bar(134)
    elif cp==0x2242:
        bar(366);lazy(150,.6)
    elif cp==0x2248:
        lazy(400,.58);lazy(100,.58)
    elif cp==0x2a6c:
        lazy(500,.58);bar(250);lazy(0,.58)
    elif cp in {0x22dc,0x22dd}:
        for y in [480,350]:stroke(pen,[(76,y),(702,y)],28)
        points=[(76,350),(702,20)] if cp==0x22dc else [(702,350),(76,20)]
        stroke(pen,points,28)
    elif cp==0x1db10:
        cartesian(pen,advance,True)
    elif cp==KURRENT:
        # Original design: curved top, closed descending loop, rising diagonal.
        points=cubic_points((130,380),[
            ((220,530),(430,530),(400,360)),
            ((370,280),(300,240),(210,230)),
            ((400,260),(530,70),(430,-100)),
            ((350,-220),(190,-200),(240,-55)),
            ((275,80),(465,350),(560,540)),
        ])
        stroke(pen,[(x*advance/700,y) for x,y in points],34)
    else:raise ValueError(hex(cp))


def install(font,include_kurrent=False):
    """Add explicit variants before the production NewCM subset/repair."""
    assert font['head'].unitsPerEm==1000
    cff=font['CFF '].cff;top=cff.topDictIndex[0];strings=top.CharStrings
    cmap=font.getBestCmap();order=list(font.getGlyphOrder())
    variation_table=next(t for t in font['cmap'].tables if t.format==14)
    records=[]

    def add(name,advance,draw):
        assert name not in order
        # CFF1 widths are stored relative to the donor's nominal width.
        pen=T2CharStringPen(advance-top.Private.nominalWidthX,None)
        draw(pen);program=pen.getCharString(private=top.Private,globalSubrs=cff.GlobalSubrs)
        if strings.charStringsAreIndexed:
            strings.charStrings[name]=len(strings.charStringsIndex)
            strings.charStringsIndex.append(program)
        else:strings[name]=program
        bounds=BoundsPen(None);draw(bounds)
        font['hmtx'][name]=(advance,math.floor(bounds.bounds[0]));order.append(name)

    for cp in [*POINTS,*([KURRENT] if include_kurrent else [])]:
        selector=0xfe02 if cp==KURRENT else 0xfe00
        default=cmap.get(cp);advance=font['hmtx'][default][0] if default else 1000
        if default is None:
            assert cp==0x1db10
            default='cartesianEqual.original'
            add(default,advance,lambda p:cartesian(p,advance,False))
            for table in font['cmap'].tables:
                if table.isUnicode() and table.format in {12,13}:table.cmap[cp]=default
        name=f'historical.u{cp:X}.vs{3 if cp==KURRENT else 1}'
        add(name,advance,lambda p:draw_variant(p,cp,font,advance))
        assert cp not in dict(variation_table.uvsDict.get(selector,[]))
        variation_table.uvsDict.setdefault(selector,[]).append((cp,name))
        records.append(dict(base=cp,selector=selector,glyph=name,defaultGlyph=default,
            construction='original looped kurrent-z centreline' if cp==KURRENT else 'original Cartesian default and descender centrelines' if cp==0x1db10 else 'two horizontal bars and one diagonal arm' if cp in {0x22dc,0x22dd} else 'licensed inverted-lazy-S curves transformed and composed with original horizontal strokes'))
    font.setGlyphOrder(order)
    top.charset=order
    for rows in variation_table.uvsDict.values():rows.sort()
    if font['GDEF'].table.GlyphClassDef:
        for record in records:
            for name in [record['glyph'],record['defaultGlyph']]:font['GDEF'].table.GlyphClassDef.classDefs[name]=1
    return records


