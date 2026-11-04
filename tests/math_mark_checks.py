"""Geometric assertions for Unicode accents in the shipped math fonts."""
from fontTools.pens.boundsPen import BoundsPen
from test_font_scripts import shape


def positioned_ink(font, path, text):
    gs=font.getGlyphSet();x=y=0;result=[]
    for gid,advance,vertical,dx,dy in shape(path,text,True):
        name=font.getGlyphName(gid);pen=BoundsPen(gs);gs[name].draw(pen)
        assert pen.bounds is not None,(text,name)
        left,bottom,right,top=pen.bounds
        result.append((name,(left+x+dx,bottom+y+dy,right+x+dx,top+y+dy),advance))
        x+=advance;y+=vertical
    return result


def assert_accent_geometry(font,path,base,check_center=True):
    plain=positioned_ink(font,path,base)
    assert len(plain)==1
    name,box,advance=plain[0]
    optical=(box[0]+box[2])/2
    if 'MATH' in font:
        table=font['MATH'].table.MathGlyphInfo.MathTopAccentAttachment
        if table and name in table.TopAccentCoverage.glyphs:
            optical=table.TopAccentAttachment[table.TopAccentCoverage.glyphs.index(name)].Value
    for suffix in ['\u0301','\u0302\u0307','\u0323\u0302\u0307']:
        rows=positioned_ink(font,path,base+suffix)
        assert len(rows)==len(suffix)+1,(base,suffix,rows)
        assert rows[0]==plain[0]
        assert all(row[2]==0 for row in rows[1:]),(base,suffix,rows)
        above=rows[2:] if suffix.startswith('\u0323') else rows[1:]
        if suffix.startswith('\u0323'):
            assert rows[1][1][3]<box[1],(base,suffix,rows)
        previous_top=box[3]
        for _,ink,_ in above:
            assert ink[1]>previous_top,(base,suffix,rows)
            if check_center:
                assert abs((ink[0]+ink[2])/2-optical)<=font['head'].unitsPerEm*.04,(base,suffix,rows)
            previous_top=ink[3]
        assert sum(row[2] for row in rows)==advance
