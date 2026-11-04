"""Actual crown outlines, one-sided shaping and raster connections."""
import io,sys
from native_sfnt_loader import evidence_ttfont as TTFont
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from scipy.ndimage import label
from test_font_scripts import shape,ROOT,manifest
from test_font_arabic import entry
from test_font_cuneiform import outline
sys.path.insert(0,str(ROOT/'tools/font'))
from arabic_crowns import POINTS,BASES,tail_center


def test_crown_drawings_preserve_scaled_source_forms():
    font=TTFont(ROOT/entry()['file']);donor=TTFont(ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf')
    gs=donor.getGlyphSet();scale=font['head'].unitsPerEm/donor['head'].unitsPerEm
    assert len(POINTS)==22
    for cp in POINTS:
        actual=outline(font,cp);original=outline(donor,cp)
        x,y=tail_center(gs[donor.getBestCmap()[cp]],gs)
        dx,dy=-30-x*scale,91-y*scale
        expected=[original[1][0]*scale+dx,original[1][1]*scale+dy,original[1][2]*scale+dx,original[1][3]*scale+dy]
        assert actual[0] and actual[2]>0
        assert all(abs(a-b)<2 for a,b in zip(actual[1],expected)),hex(cp)


def test_native_and_legacy_shaping_obey_left_only_joining():
    p=ROOT/entry()['file'];font=TTFont(p);space=font.getGlyphID('space')
    for i,cp in enumerate(sorted(POINTS)):
        alias='\u200c'+chr(BASES[i])+chr(0xe0120+i)
        for before,after in [('', ''),('', 'ب'),('ب','ب'),('ب',''),('', '\u200cب'),('', '\u064eب')]:
            native=shape(p,before+chr(cp)+after,True)
            compat=shape(p,before+alias+after,True)
            assert [g for g in native if g[0]!=space]==[g for g in compat if g[0]!=space],hex(cp)
        joined=shape(p,'ب'+chr(cp)+'ب',True)
        assert joined[0][0]==shape(p,'بب',True)[0][0]
        assert joined[-1][0]==shape(p,'ب',True)[0][0]


def test_all_crown_connections_touch_only_when_joining_is_enabled():
    p=ROOT/entry()['file'];font=TTFont(p)
    # Map glyph IDs to temporary PUA values solely to rasterize exact HarfBuzz
    # output. This test font is in-memory and never distributed.
    for table in font['cmap'].tables:
        if table.format==12:table.cmap.update({0xf0000+i:n for i,n in enumerate(font.getGlyphOrder())})
    font.flavor=None;stream=io.BytesIO();font.save(stream);stream.seek(0)
    raster_font=ImageFont.truetype(stream,128);scale=128/font['head'].unitsPerEm
    for cp in POINTS:
        for enabled in [True,False]:
            rows=shape(p,chr(cp)+('' if enabled else '\u200c')+'ب',True)
            im=Image.new('L',(512,300));draw=ImageDraw.Draw(im);pen=20
            for gid,advance,_,ox,oy in rows:
                draw.text((pen+ox*scale,220-oy*scale),chr(0xf0000+gid),font=raster_font,fill=255,anchor='ls')
                pen+=advance*scale
            labels,_=label(np.asarray(im)>128,np.ones((3,3)))
            base_advance=rows[0][1]
            y=round(220-91*scale)
            left=labels[y,round(20+base_advance*scale/2)]
            right=labels[y,round(20+(base_advance+150)*scale)]
            if not left:
                # The beh bowl is curved; choose its non-dot body component
                # in this column, rather than assuming a flat baseline there.
                column=labels[max(0,y-25):y+15,round(20+base_advance*scale/2)]
                values,counts=np.unique(column[column>0],return_counts=True)
                left=values[counts.argmax()] if len(values) else 0
            assert left and right,(hex(cp),enabled)
            assert bool(left==right)==enabled,(hex(cp),enabled)


def test_all_assigned_arabic_characters_are_bundled_or_behavioural():
    from test_unicode_inventory import audit
    scripts=audit.properties(audit.DATA/'Scripts.txt');m=manifest()
    points={cp for e in m['fonts'] for a,b in e['ranges'] for cp in range(a,b+1)}
    points.update(cp for a,b in m['baseRanges']+m['behaviouralRanges'] for cp in range(a,b+1))
    assert {cp for cp in audit.inventory() if scripts.get(cp)=='Arabic'}<=points
