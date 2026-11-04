"""A cmap or an empty COLR root alone is not drawing evidence."""
import sys
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/unicode'))
from outline_audit import drawn_glyph,routed_points,shaping_font,shaped_glyph_names


def test_empty_roots_need_a_real_outline_or_colour_layer():
    builder=FontBuilder(1000,isTTF=True)
    names=['.notdef','blank','ink','painted']
    builder.setupGlyphOrder(names)
    glyphs={}
    for name in names:
        pen=TTGlyphPen(None)
        if name=='ink':
            pen.moveTo((0,0));pen.lineTo((100,0));pen.lineTo((50,100));pen.closePath()
        glyphs[name]=pen.glyph()
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics({name:(500,0) for name in names})
    builder.setupCOLR({'painted':[('ink',0)]})
    builder.setupCPAL([[(0,0,0,1)]])
    assert drawn_glyph(builder.font,'ink')
    assert drawn_glyph(builder.font,'painted')
    assert not drawn_glyph(builder.font,'blank')


def test_routing_replays_the_app_instead_of_counting_unregistered_fonts():
    report=routed_points([ord('A'),0x1f600,0x10ffff])
    routes={cp:[report['files'][i] for i in indexes] for cp,indexes in report['routes']}
    assert 'assets/fonts/dad-lettering-unicode.woff2' in routes[ord('A')]
    assert routes[0x1f600]==['assets/fonts/dad-emoji.woff2']
    assert not routes[0x10ffff]
    assert report['gaps']==[{'cp':0x10ffff,'missing':[0x10ffff],'emojiFallbacks':[]}]


def test_empty_shorthand_inputs_are_checked_after_native_gsub_expansion():
    cp=0x1bc11
    report=routed_points([cp]);_,indexes=report['routes'][0]
    assert len(indexes)==1
    font=TTFont(ROOT/report['files'][indexes[0]])
    assert not drawn_glyph(font,font.getBestCmap()[cp])
    names=shaped_glyph_names(font,shaping_font(font),chr(cp))
    assert len(names)>1 and all(font.getGlyphID(n)>0 for n in names)
    assert any(drawn_glyph(font,n) for n in names)


def test_tatweel_audit_uses_the_explicit_painted_family_not_any_loaded_font():
    report=routed_points([0x640]);_,indexes=report['routes'][0]
    assert len(indexes)==1 and report['gaps']==[]
    assert report['files'][indexes[0]]=='assets/fonts/scripts/b081994f5e2f.woff2'
