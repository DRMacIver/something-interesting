"""Independent visible state checks for unregistered object candidates."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import pytest
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_remaining_objects import prepare
STRUCTURE={e['key']:e for e in json.loads((ROOT/'output/font-review/pen-translation/remaining-objects-source-structure.json').read_text())}

@pytest.mark.parametrize('key,raised,opened,door_index',[
 ('1f4eb',True,False,12),('1f4ea',False,False,12),
 ('1f4ec',True,True,2),('1f4ed',False,True,11)])
def test_mailbox_preserves_physical_flag_orientation_and_opening(key,raised,opened,door_index):
    (paper,*materials,ink),r=prepare(key)
    source=r['source'];raw=(ROOT/source['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==source['sha256']
    assert r['appliedStrength']>0 and not r['fallback']
    red=materials[r['colourNames'].index('red')];ys,xs=np.nonzero(red)
    assert bool(np.ptp(ys)>np.ptp(xs))==raised
    shape=STRUCTURE[key]['shapes'][door_index]
    pen=BoundsPen(None);parse_path(shape['attributes']['d'],pen)
    x0,y0,x1,y1=pen.bounds
    # Use the upper interior of the native door, clear of the letter and hinge.
    x=round((x0+x1)/2*12)+r['padding'];y=round((y0+(y1-y0)*.25)*12)+r['padding']
    darkness=float(ink[y-4:y+5,x-4:x+5].mean())
    if opened:
        assert darkness>.8
    else:
        assert darkness<.2


def test_email_uses_existing_comic_capital_e():
    _,r=prepare('1f4e7');lettering=r['lettering'];path=ROOT/lettering['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==lettering['sha256']
    assert len(lettering['letters'])==1
    letter=lettering['letters'][0];assert letter['character']=='E'
    assert letter['glyph']==TTFont(path).getBestCmap()[ord('E')]


def test_coloured_books_keep_four_distinct_pdf_cover_colours():
    colours=[]
    for key,name in [('1f4d5','red'),('1f4d7','green'),('1f4d8','blue'),('1f4d9','orange')]:
        (_,cover,ink),r=prepare(key)
        assert r['colourNames']==[name] and cover.any()
        colours.append(tuple(r['rgbs'][0]))
    assert len(set(colours))==4

@pytest.mark.parametrize('key,points_up',[('1f4e4',True),('1f4e5',False),('1f4e9',False)])
def test_mail_arrows_keep_their_direction(key,points_up):
    (_, *materials, _),r=prepare(key)
    arrow=materials[r['colourNames'].index('red')]
    ys,xs=np.nonzero(arrow);y0,y1=int(ys.min()),int(ys.max())
    # Compare the narrow tip with the rectangular tail, rather than
    # guessing where this source drawing places the arrowhead shoulder.
    upper=round(y0+(y1-y0)*.1);lower=round(y0+(y1-y0)*.9)
    a=float(arrow[upper-2:upper+3].sum(axis=1).mean())
    b=float(arrow[lower-2:lower+3].sum(axis=1).mean())
    if points_up:
        assert a<b*.7
    else:
        assert b<a*.7


def test_every_remaining_mail_source_has_a_candidate_recipe():
    from prototype_remaining_objects import RECIPES
    required={key for key,e in STRUCTURE.items() if e['subgroup']=='mail'}
    assert len(required)==13
    assert required<=set(RECIPES)


def test_parcel_keeps_every_native_handling_mark():
    import xml.etree.ElementTree as ET
    from scipy import ndimage as ndi
    from prototype_remaining_objects import raster
    (_, *_, ink),r=prepare('1f4e6')
    covered=ndi.binary_dilation(ink,iterations=6)
    raw=(ROOT/r['source']['path']).read_bytes()
    for index in range(50,58):
        root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
        shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
        for i,e in enumerate(shapes):
            if i!=index:parents[e].remove(e)
            else:
                e.attrib.pop('style',None);e.set('fill','#111111');e.set('stroke','none')
        for group in root.iter():
            if group.tag.split('}')[-1]=='g':
                group.attrib.pop('opacity',None)
                group.set('style',';'.join(rule for rule in group.get('style','').split(';') if rule.split(':',1)[0].strip()!='opacity'))
        reference=np.pad(raster(root),r['padding'])
        assert reference.sum()>0,index
        assert np.count_nonzero(reference&covered)/reference.sum()>.95,index


@pytest.mark.parametrize('key,indices',[
    ('1f4c3',range(1,6)),('1f4c4',range(1,6)),('1f4d1',range(10,15)),
    ('1f4dc',range(5,16)),('1f4d6',range(14,50)),('1f4f0',range(4,18))])
def test_document_writing_remains_visible_at_every_native_line(key,indices):
    (_, *_, ink),r=prepare(key)
    for index in indices:
        shape=STRUCTURE[key]['shapes'][index]
        if shape['tag']=='line':
            x0,y0,x1,y1=(float(shape['attributes'][a]) for a in ['x1','y1','x2','y2'])
        else:
            pen=BoundsPen(None)
            parse_path(shape['attributes']['d'],pen)
            x0,y0,x1,y1=pen.bounds
        x=round((x0+x1)/2*12)+r['padding']
        y=round((y0+y1)/2*12)+r['padding']
        assert ink[y-16:y+17,x-16:x+17].any(),(key,index)


def test_bookmark_tabs_keep_four_distinct_colours():
    (_, *materials, _),r=prepare('1f4d1')
    assert set(r['colourNames'])=={'yellow','blue','red','green'}
    assert len(set(map(tuple,r['rgbs'])))==4
    assert all(mask.sum()>100 for mask in materials)


def test_stacked_books_keep_cover_colours_and_vertical_order():
    (_, *materials, _),r=prepare('1f4da')
    covers=dict(zip(r['colourNames'],materials))
    assert set(covers)=={'red','blue','green'}
    assert len(set(map(tuple,r['rgbs'])))==3
    y={name:np.nonzero(mask)[0].mean() for name,mask in covers.items()}
    assert y['green']<y['red']<y['blue']


def test_ribbon_bookmark_keeps_white_star_inside_red_tag():
    (_, *materials, _),r=prepare('1f516')
    colours=dict(zip(r['colourNames'],zip(materials,r['rgbs'])))
    star,rgb=colours['white']
    assert tuple(rgb)==(255,255,255)
    assert star.sum()>100
    ys,xs=np.nonzero(star)
    assert abs((xs.mean()-r['padding'])/12-55)<3
    assert abs((ys.mean()-r['padding'])/12-79)<3


def test_composition_notebook_keeps_label_and_mottled_cover():
    from scipy import ndimage as ndi
    (_,ink),r=prepare('1f4d3')
    # Native label centre and a cover region well clear of the spine/pages.
    p=r['padding']
    x,y=round(66.68*12)+p,round(36.15*12)+p
    assert not ink[y-12:y+13,x-12:x+13].any()
    cover=ink[round(12*12)+p:round(100*12)+p,round(38*12)+p:round(95*12)+p]
    assert .5<float(cover.mean())<.95
    holes=ndi.binary_fill_holes(ink)&~ink
    assert ndi.label(holes)[1]>50


def test_book_paper_and_mail_candidate_inventory_is_complete():
    from prototype_remaining_objects import RECIPES
    required={key for key,e in STRUCTURE.items() if e['subgroup'] in {'book-paper','mail'}}
    assert len(required)==30
    assert required<=set(RECIPES)
