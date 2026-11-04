"""The production compiler must emit all reviewed money/accessory layers."""
import hashlib
import json
import sys
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))


def test_registered_money_clothing_compiler_matches_both_reviewed_fonts():
    from build_emoji import outline
    from emoji_money_clothing import add_money_clothing
    glyphs,metrics,cmap,layers,review={},{},{},{},[]
    palette=[(255,255,255),(17,17,17)]
    sequences,variations=add_money_clothing(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    assert len(cmap)==19 and len(review)==19
    assert {int(e['codepoint'][2:],16) for e in review}==set(cmap)
    expected_aliases=set()
    for family,count in [('money',10),('clothing',9)]:
        path=ROOT/f'output/font-review/pen-translation/{family}-candidate.woff2'
        reference=json.loads(path.with_suffix('.json').read_text())
        assert len(reference['flags'])==count
        assert hashlib.sha256(path.read_bytes()).hexdigest()==reference['sha256']
        donor=TTFont(path)
        for entry in reference['flags']:
            name=family+'.'+entry['region'];old=entry['glyphName']
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
                assert cmap[ord(text.replace('\ufe0f',''))]==name
                if len(text)>1:expected_aliases.add(text)
    assert set(sequences)==expected_aliases and len(sequences)==2
    assert set(variations)=={(ord(text[0]),ord(text[1])) for text in sequences}
