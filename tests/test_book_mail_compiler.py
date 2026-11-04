"""The production compiler must emit the reviewed isolated candidate art."""
import hashlib
import json
import sys
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))


def test_registered_compiler_matches_all_reviewed_book_mail_layers():
    from build_emoji import outline
    from emoji_book_mail import add_book_mail
    path=ROOT/'output/font-review/pen-translation/book-mail-candidate.woff2'
    reference=json.loads(path.with_suffix('.json').read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==reference['sha256']
    donor=TTFont(path)
    glyphs,metrics,cmap,layers,review={},{},{},{},[]
    palette=[(255,255,255),(17,17,17)]
    sequences,variations=add_book_mail(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    assert len(cmap)==30 and len(review)==30
    assert {int(e['codepoint'][2:],16) for e in review}==set(cmap)
    assert set(sequences)=={text for e in reference['flags'] for text in e['qualificationForms'] if len(text)>1}
    assert set(variations)=={(ord(text[0]),ord(text[1])) for text in sequences}
    for entry in reference['flags']:
        name='book-mail.'+entry['region']
        old=entry['glyphName']
        expected_layers=donor['COLR'].ColorLayers[old]
        assert len(layers[name])==len(expected_layers)
        pairs=[(name,old),*[(a,b.name) for (a,_),b in zip(layers[name],expected_layers)]]
        for actual,expected in pairs:
            a=glyphs[actual]
            b=donor['glyf'][expected]
            assert a.numberOfContours==b.numberOfContours
            ac,ae,af=a.getCoordinates(None)
            bc,be,bf=b.getCoordinates(donor['glyf'])
            assert (list(ac),list(ae),list(af))==(list(bc),list(be),list(bf))
            a.recalcBounds(None)
            assert (metrics[actual][0],getattr(a,'xMin',0))==donor['hmtx'][expected]
        for (_,index),expected in zip(layers[name],expected_layers):
            colour=donor['CPAL'].palettes[0][expected.colorID]
            assert tuple(palette[index])==(colour.red,colour.green,colour.blue)
        for text in entry['qualificationForms']:
            assert cmap[ord(text.replace('\ufe0f',''))]==name
