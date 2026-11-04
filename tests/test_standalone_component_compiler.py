import json
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from test_font_scripts import ROOT

sys.path.insert(0,str(ROOT/'tools/font'))
from emoji_standalone_component_compiler import COMPONENT_NAMES,add_standalone_components
from build_emoji import outline


def test_promoted_components_match_every_reviewed_candidate_layer():
    glyphs={n:TTGlyphPen(None).glyph() for n in COMPONENT_NAMES.values()}
    metrics={n:(0,0) for n in glyphs}
    cmap=dict(COMPONENT_NAMES)
    layers,review={},[]
    palette=[(255,255,255),(17,17,17)]
    assert add_standalone_components(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)==set(COMPONENT_NAMES)
    assert cmap==COMPONENT_NAMES and len(review)==35
    path=ROOT/'output/font-review/pen-translation/standalone-components-candidate.woff2'
    donor=TTFont(path)
    for cp,name in COMPONENT_NAMES.items():
        reference=f'standalone-components.{cp:x}'
        expected=donor['COLR'].ColorLayers[reference]
        assert len(layers[name])==len(expected)
        for a,b in [(name,reference),*[(a,b.name) for (a,_),b in zip(layers[name],expected)]]:
            ga,gb=glyphs[a],donor['glyf'][b]
            ac,ae,af=ga.getCoordinates(None);bc,be,bf=gb.getCoordinates(donor['glyf'])
            assert (list(ac),list(ae),list(af))==(list(bc),list(be),list(bf))
            ga.recalcBounds(None)
            assert (metrics[a][0],getattr(ga,'xMin',0))==donor['hmtx'][b]
        for (_,index),layer in zip(layers[name],expected):
            rgb=donor['CPAL'].palettes[0][layer.colorID]
            assert tuple(palette[index])==(rgb.red,rgb.green,rgb.blue)
