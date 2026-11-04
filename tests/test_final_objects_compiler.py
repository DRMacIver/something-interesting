"""The production compiler must emit all reviewed final object layers."""
import hashlib
import json
import sys
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))


def test_registered_final_objects_compiler_matches_every_reviewed_layer():
    from build_emoji import outline
    from emoji_final_objects import add_final_objects,FAMILIES,PROMOTABLE_COMPONENTS
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    glyphs,metrics,cmap,layers,review={},{},{},{},[]
    palette=[(255,255,255),(17,17,17)]
    for cp in [0x1f426,0x200d,0x1f525]:
        name=f'existing.{cp:X}';cmap[cp]=name;glyphs[name]=TTGlyphPen(None).glyph();metrics[name]=(123,7)
    old={name:(glyphs[name],metrics[name]) for name in cmap.values()}
    for cp,name in PROMOTABLE_COMPONENTS.items():
        cmap[cp]=name;glyphs[name]=TTGlyphPen(None).glyph();metrics[name]=(0,0)
    sequences,variations,rule=add_final_objects(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    assert len(cmap)==66 and len(review)==64
    assert {int(e['codepoint'][2:],16) for e in review if 'codepoint' in e}==set(cmap)-{0x1f426,0x200d,0x1f525}
    assert rule=='sub existing.1F426 existing.200D existing.1F525 by phoenix.1f426_200d_1f525;'
    for name,(glyph,metric) in old.items():assert glyphs[name] is glyph and metrics[name]==metric
    for cp,name in PROMOTABLE_COMPONENTS.items():
        assert cmap[cp]==name and glyphs[name].numberOfContours>0 and metrics[name][0]>0
    expected_aliases=set()
    for family,count in [(family,count) for family,count,_ in FAMILIES]+[('phoenix',1)]:
        path=ROOT/f'output/font-review/pen-translation/{family}-candidate.woff2'
        reference=json.loads(path.with_suffix('.json').read_text())
        assert len(reference['flags'])==count
        assert hashlib.sha256(path.read_bytes()).hexdigest()==reference['sha256']
        donor=TTFont(path)
        for entry in reference['flags']:
            cp=int(entry['region'],16) if family!='phoenix' else None
            name=cmap[cp] if cp is not None else 'phoenix.'+entry['region']
            old=entry['glyphName']
            expected=donor['COLR'].ColorLayers[old]
            assert len(layers[name])==len(expected)
            pairs=[(name,old),*[(a,b.name) for (a,_),b in zip(layers[name],expected)]]
            for actual,reference_name in pairs:
                a=glyphs[actual];b=donor['glyf'][reference_name]
                assert a.numberOfContours==b.numberOfContours
                ac,ae,af=a.getCoordinates(None);bc,be,bf=b.getCoordinates(donor['glyf'])
                assert (list(ac),list(ae),list(af))==(list(bc),list(be),list(bf))
                a.recalcBounds(None)
                assert (metrics[actual][0],getattr(a,'xMin',0))==donor['hmtx'][reference_name]
            for (_,index),expected_layer in zip(layers[name],expected):
                colour=donor['CPAL'].palettes[0][expected_layer.colorID]
                assert tuple(palette[index])==(colour.red,colour.green,colour.blue)
            for text in entry['qualificationForms']:
                if family!='phoenix':assert cmap[ord(text.replace('\ufe0f',''))]==name
                if len(text)>1:expected_aliases.add(text)
    assert set(sequences)==expected_aliases and len(sequences)==16
    assert set(variations)=={(ord(text[0]),ord(text[1])) for text in sequences if len(text)==2}


def test_singleton_compiler_cannot_overwrite_existing_real_or_unnamed_art(tmp_path):
    import pytest
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from emoji_svg_family import add_svg_family
    folder=tmp_path/'data/font-sources';folder.mkdir(parents=True)
    (folder/'noto-emoji-protected-svg.json').write_text(json.dumps({'files':[dict(path='emoji_u1f308.svg',include_sequences=['🌈'],build_target='emoji-artwork')]}))
    def unexpected_prepare(key):raise AssertionError('prepare must not run')
    for name,drawn,advance in [('flag-component.u1F308',True,0),('flag-component.u1F308',False,100),('unapproved.name',False,0)]:
        pen=TTGlyphPen(None)
        if drawn:
            pen.moveTo((0,0));pen.lineTo((10,0));pen.lineTo((0,10));pen.closePath()
        with pytest.raises(AssertionError,match='Only empty named shaping components'):
            add_svg_family(tmp_path,{name:pen.glyph()},{name:(advance,0)},{0x1f308:name},{},[],[],None,'protected',unexpected_prepare,1,0,promotable_components={0x1f308:'flag-component.u1F308'})
