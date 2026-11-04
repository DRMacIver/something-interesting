"""New SVG identities, topology, sequence boundaries and optical companions."""
import hashlib,json
from pathlib import Path
import numpy as np
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'assets/fonts/dad-emoji.woff2'


@pytest.mark.parametrize('key,components,counters,name',[
    ('1facc',1,36,'MONARCH BUTTERFLY'),('1fa8e',8,60,'TREASURE CHEST'),
    ('1faf9',1,5,'LEFTWARDS THUMB SIGN'),('1fafa',1,5,'RIGHTWARDS THUMB SIGN'),
    ('1faef',8,9,'FIGHT CLOUD'),
    ('1fa8b',10,2,'METEOR'),
    ('1f6d9',3,6,'LIGHTHOUSE'),
    ('1f6d8',9,5,'LANDSLIDE'),
    ('1fa8d',2,30,'NET WITH HANDLE'),
    ('1fa8c',6,3,'ERASER'),
    ('1fac8',2,8,'HAIRY CREATURE'),
    ('1fae9',6,3,'FACE WITH BAGS UNDER EYES'),
    ('1faea',4,3,'DISTORTED FACE'),('1faeb',3,23,'CRACKING FACE'),
    ('1fadc',3,2,'ROOT VEGETABLE'),('1fadf',3,0,'SPLATTER'),('1facd',2,3,'ORCA'),
    ('1fa89', 2, 8, 'HARP'),('1fa8a', 2, 12, 'TROMBONE'),('1fa8f', 1, 6, 'SHOVEL'),
    ('1fabe',1,5,'LEAFLESS TREE'),('1fac6',10,0,'FINGERPRINT'),('1fadd',6,2,'PICKLE')])
def test_new_svg_identity_topology_and_sequence_boundaries(key,components,counters,name,monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_new_svg import prepare
    from emoji_sequences import qualified_forms
    cp=int(key,16);text=chr(cp)
    unicode_data=(ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines()
    assert next(line.split(';')[1] for line in unicode_data if line.startswith(f'{cp:X};'))==name
    (white,ink),report=prepare(key)
    assert (report['sourceComponents'],report['sourceHoles'])==(components,counters)
    assert report['settings']['strength']==1.7 and report['appliedStrength']>0 and not report['fallback']
    if key=='1facd':assert report['removedRasterPinholePixels']==6
    assert np.all(white[ink])
    (white2,ink2),again=prepare(key)
    assert np.array_equal(ink,ink2) and np.array_equal(white,white2) and again==report
    source=report['source'];raw=(ROOT/source['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==source['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==source['git_blob_sha1']
    assert set(qualified_forms(ROOT,text))=={form for form in source['include_sequences'] if len(form)==1}
    font=TTFont(PATH);glyph=font.getBestCmap()[cp]
    assert glyph=='svg.'+key
    assert font['glyf'][glyph].numberOfContours==components+counters
    layers=font['COLR'].ColorLayers[glyph]
    assert (layers[0].name,layers[0].colorID)==(glyph+'.white',0)
    assert (layers[-1].name,layers[-1].colorID)==(glyph+'.ink',1)
    assert len(layers)==(3 if key=='1facc' else 2)
    result=shape(PATH,text,True)
    assert len(result)==1 and result[0][0]>0 and result[0][1]>0
    for form in qualified_forms(ROOT,text):assert shape(PATH,form,True)==result
    assert shape(PATH,text+text,True)==result+result
    assert shape(PATH,'😀'+text+'😀',True)==shape(PATH,'😀',True)+result+shape(PATH,'😀',True)
    assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==result


@pytest.mark.parametrize('key',['1faf9','1fafa'])
def test_directional_thumb_tones_cover_whole_hand_and_keep_sequence_boundaries(key):
    font=TTFont(PATH);base=chr(int(key,16));name=font.getBestCmap()[ord(base)]
    registry=json.loads((ROOT/'data/font-sources/noto-emoji-new-svg.json').read_text())
    entry=next(e for e in registry['files'] if e['path'].endswith(f'emoji_u{key}.svg'))
    assert entry['include_sequences']==[base]+[base+chr(cp) for cp in range(0x1f3fb,0x1f400)]
    plain=shape(PATH,base,True)
    for i in range(5):
        text=base+chr(0x1f3fb+i);result=shape(PATH,text,True)
        assert len(result)==1 and result[0][1]>0
        glyph=font.getGlyphName(result[0][0]);assert glyph==name+f'.tone{i+1}'
        assert [(l.name,l.colorID) for l in font['COLR'].ColorLayers[glyph]]==[(name+'.white',6+i),(name+'.ink',1)]
        assert shape(PATH,base+text+base,True)==plain+result+plain
        assert shape(PATH,text+text,True)==result+result
        assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2',text,True)==result


def test_monarch_colour_keeps_white_spots_and_uses_pinned_comic_orange(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_new_svg import prepare,butterfly_fill
    from scipy import ndimage
    (white,ink),report=prepare('1facc');fill,details=butterfly_fill(ink,report)
    labels,n=ndimage.label(white&~ink)
    assert n==36
    assert details['orangeCells']==[2,4,8,12,15,18,19,21,22,23,25,26,27,28,30,31,33,35]
    assert details['whiteCells']==18
    assert report['removedRasterInkPixels']==17
    for i in range(1,n+1):
        assert np.all(fill[labels==i])== (i in details['orangeCells'])
        if i not in details['orangeCells']:assert not np.any(fill[labels==i])
    font=TTFont(PATH);layers=font['COLR'].ColorLayers['svg.1facc']
    assert layers[1].name=='svg.1facc.orange'
    colour=font['CPAL'].palettes[0][layers[1].colorID]
    assert [colour.red,colour.green,colour.blue]==details['rgb']
    assert font['glyf'][layers[1].name].numberOfContours==len(details['orangeCells'])
