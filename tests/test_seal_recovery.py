"""Recovered scans must have verified identities and survive font packaging."""
import pytest
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy import ndimage
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from test_font_scripts import shape

ROOT=Path(__file__).resolve().parents[1]
POINTS={0x3EEA6,0x3EE89,0x3EE59,0x3EE51,0x3EE47,0x3ED68,0x3ED9F,0x3EDBB,0x3ED25,0x3EC4C,0x3EC5D,0x3EC9A,0x3ECA7,0x3EB9C,0x3EBEA,0x3EC0C,0x3EBB1,0x3EBBD,0x3EB35,0x3EB15,0x3EB1F,0x3E968,0x3EA49,0x3EA7E,0x3EAEE,0x3E93F,0x3E8D0,0x3E7ED,0x3E85A,0x3E76D,0x3E7B8,0x3E57F,0x3E5A1,0x3E605,0x3E452,0x3E462,0x3E51F,0x3E542,0x3E3B1,0x3E3B3,0x3E3C7,0x3E377,0x3E33B,0x3E386,0x3E2E7,0x3E2FD,0x3E310,0x3E096,0x3E197,0x3E1BC,0x3E1E7,0x3E02A,0x3E073,0x3E0E7,0x3DF72,0x3DE79,0x3DEE5,0x3DDCE,0x3DDFC,0x3DE16,0x3DD63,0x3DD65,0x3DDA4,0x3DDA5,0x3DD51,0x3DB6D,0x3DBA2,0x3DADD,0x3DADF,0x3DAEA,0x3DB03,0x3D951,0x3D9C4,0x3DA15,0x3D893,0x3D8BF,0x3D8EF,0x3D8F3,0x3D6CF,0x3D775,0x3D7D0,0x3D54F,0x3D5B4,0x3D4D5,0x3D40D,0x3D414,0x3D46B,0x3D4A0,0x3D355,0x3D37A,0x3D2A6,0x3D21C,0x3D08B,0x3D025,0x3D02C,0x3D062,0x3D182,0x3D198,0x3D0A8,0x3D122,0x3D010,0x3D087,0x3D055,0x3D007,0x3DCE1,0x3EEB4,0x3F576,0x3F7EC,0x3FB65,0x3FB66,0x3FB72,0x3F60E,0x3F711,0x3F2B8,0x3F2B9,0x3F2BA,0x3F2BB,0x3F390,0x3F392,0x3F393,0x3F394,0x3F395,0x3F396,0x3F397,0x3F398,0x3F399,0x3F39A,0x3F39C,0x3F39D,0x3F39E,0x3F39F,0x3F3A0,0x3F3A1,0x3F3A3,0x3F214,0x3F215,0x3F216,0x3F217,0x3F218,0x3F21D,0x3EEAF,0x3EEB0,0x3EEB1,0x3EF2C,0x3EFC5,0x3EFC6,0x3EBF8,0x3F15C,0x3F15E,0x3F161,0x3F162,0x3F163,0x3E332,0x3E69B,0x3E888,0x3EA8A,0x3E69A,0x3E25E,0x3E394,0x3E53F,0x3E5AD,0x3E25D,0x3D766,0x3D88A,0x3E21F,0x3EEB3,0x3EEB6,0x3E0F2,0x3E4EA,0x3F283,0x3F8FD,0x3E4E9,0x3E1E3,0x3EE98,0x3EEB5,0x3D7A9,0x3D66B,0x3ED3A,0x3ED3B,0x3EEB2,0x3ED77,0x3EE93,0x3EFD3,0x3F1EE,0x3EA3A,0x3EA3B,0x3EA59,0x3EB6D,0x3E0F4,0x3E1E5,0x3E1E6,0x3E56E,0x3F27D,0x3F27E,0x3F79D,0x3F603,0x3F604,0x3F605,0x3E1D1,0x3E298,0x3E2A5,0x3E4ED,0x3F482,0x3F4F1,0x3F5CD,0x3D4B8,0x3DD2A,0x3DDF2,0x3DDF3,0x3D7A8,0x3DB0E,0x3F5B1,0x3F5F1,0x3F622,0x3F623,0x3F625,0x3F8FC}


def entry():
    data=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    return next(e for e in data['fonts'] if e['source'].endswith('/DadSealRecovery-Regular.ttf'))


def test_recovered_seal_identity_and_packaged_outlines(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    spec=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())
    fonts=[TTFont(ROOT/entry()[key]) for key in ['source','file']]
    assert all(set(f.getBestCmap())==POINTS for f in fonts)
    refs={}
    for line in (ROOT/'data/unicode/18.0.0/SealSources.txt').read_text().splitlines():
        fields=line.split('\t')
        if len(fields)==3:
            cp,prop,seq=fields;refs[cp[2:],prop]=seq
    for record in spec['glyphs']:
        cp=int(record['codepoint'],16)
        assert record['sequence']==refs[record['codepoint'],record.get('sourceProperty','kSEAL_CCZSrc')]
        _,ink=mask(record)
        components=ndimage.label(ink)[1]
        # Marching squares connects the low/background pixels diagonally.
        # Match that convention: a diagonal white opening is not a lost hole.
        background=np.ones((3,3),bool)
        holes=ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]
        drawings=[]
        for f in fonts:
            name=f.getBestCmap()[cp];gs=f.getGlyphSet();pen=RecordingPen();gs[name].draw(pen);drawings.append(pen.value)
            glyph=f['glyf'][name]
            assert glyph.numberOfContours>=components+holes
            assert 100<=glyph.xMin<glyph.xMax<=900 and -1<=glyph.yMin<glyph.yMax<=761
        assert drawings[0]==drawings[1]
        shaped=shape(ROOT/entry()['file'],chr(cp),True)
        assert len(shaped)==1 and shaped[0][0]!=0 and shaped[0][1]==1000
    assert 0x3E34F not in POINTS  # The proposed scan lacks its lower component.


def test_recovery_builder_reproduces_font_bytes(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    import build_seal_recovery as b
    before=hashlib.sha256(b.OUTPUT.read_bytes()).hexdigest()
    b.OUTPUT.with_suffix('.built.json').unlink(missing_ok=True)
    b.build()
    assert hashlib.sha256(b.OUTPUT.read_bytes()).hexdigest()==before


def test_adjacent_seal_forms_keep_horizontal_bar_versus_two_uprights(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    # The official C-03515/C-03516 references distinguish these upper-right
    # components. In particular, a pencil rule must not bridge the uprights.
    for cp,region,count in [('3DDF2',(slice(0,70),slice(110,None)),1),
                            ('3DDF3',(slice(0,90),slice(90,None)),2)]:
        _,ink=mask(records[cp]);labels,n=ndimage.label(ink[region])
        assert n==count
        for rows,columns in ndimage.find_objects(labels):
            height,width=rows.stop-rows.start,columns.stop-columns.start
            assert width>2*height if count==1 else height>2*width


def test_crop_shortlist_respects_reading_order_and_keeps_ambiguous_candidates(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from review_seal_candidates import shortlist
    def row(sequence='', y=100, x=300, **changes):
        return dict(commons_title='book', page='1', side='right', pitch='100',
                    x=str(x), y=str(y), w='60', h='90', sequence=sequence,
                    codepoint='3D000' if sequence else '',
                    status='aligned' if sequence else 'rejected', **changes)
    before, after = row('C-00001'), row('C-00004', y=400)
    first, second = row(y=200), row(y=300)
    rows = [before, after, row(y=50), first, second, row(y=500), row(x=200)]
    result = shortlist(rows, [('3D001', 'C-00002'), ('3D002', 'C-00003')])
    # Both unassigned crops remain possibilities for both gaps. The tool must
    # not turn geometric proximity into an automatic character assignment.
    assert len(result)==2
    assert all(r['candidates']==[first, second] for r in result)
    empty=shortlist([before,after],[('3D001','C-00002')],include_empty=True)
    assert len(empty)==1 and empty[0]['candidates']==[]
    assert empty[0]['before']==before and empty[0]['after']==after
    after['commons_title']='another book'
    assert shortlist(rows, [('3D001', 'C-00002')])==[]


def test_book_four_cleanup_retains_enclosures_and_repairs_only_local_stem(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,components,holes in [('3E1D1',4,4),('3E298',4,6),('3E2A5',4,2),('3E4ED',2,0)]:
        _,ink=mask(records[cp])
        assert ndimage.label(ink)[1]==components
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
    record=records['3E4ED'];_,repaired=mask(record)
    _,before=mask({k:v for k,v in record.items() if k!='closingRects'})
    changed=repaired!=before
    assert changed.any() and not (before & ~repaired).any()
    allowed=np.zeros_like(changed);allowed[155:195,0:25]=True
    assert not (changed & ~allowed).any()


def test_split_crop_recoveries_keep_both_left_enclosures(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    # Upstream crops mostly captured the right component. Each complete sign
    # has two left enclosures; checking the full glyph's contour count alone
    # would not catch loss of these components.
    background=np.ones((3,3),bool)
    for cp,right,bottom in [('3F603',65,90),('3F604',59,140),('3F605',63,150)]:
        _,ink=mask(records[cp]);left=ink[:bottom,:right]
        holes=ndimage.binary_fill_holes(left,structure=background)&~left
        assert ndimage.label(holes,structure=background)[1]==2


def test_adjacent_headword_and_inline_form_retain_distinct_bases(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    # C-08671 has one bottom bar; its inline C-08672 form has two. Both had
    # pointed to the same unrelated crop before full-page identity review.
    for cp,count in [('3F27D',1),('3F27E',2)]:
        _,ink=mask(records[cp]);widths=ink.sum(axis=1)
        bars=widths[int(len(widths)*.75):]>widths.max()*.6
        assert ndimage.label(bars)[1]==count


def test_cup_and_inner_stem_repairs_preserve_separate_components(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,components,holes in [('3E0F4',5,18),('3E1E5',1,2)]:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==components
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
        _,before=mask({k:v for k,v in record.items() if k!='closingRects'})
        changed=ink!=before;allowed=np.zeros_like(ink)
        for x0,y0,x1,y1,_ in record['closingRects']:allowed[y0:y1,x0:x1]=True
        assert changed.any() and not (before & ~ink).any()
        assert not (changed & ~allowed).any()
    # The repaired cup must not join the separate cross-in-circle below it.
    _,ink=mask(records['3E0F4']);labels,_=ndimage.label(ink)
    cup=set(np.unique(labels[110:135,:75]))-{0}
    lower=set(np.unique(labels[160:200,:75]))-{0}
    assert len(cup)==len(lower)==1 and cup.isdisjoint(lower)


def test_book_five_shared_component_retains_four_spaces(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp in ['3EA3A','3EA3B']:
        _,ink=mask(records[cp]);head=ink[:90,:70]
        assert ndimage.label(ndimage.binary_fill_holes(head,structure=background)&~head,structure=background)[1]==4
    record=records['3EA3B'];_,ink=mask(record)
    _,before=mask({k:v for k,v in record.items() if k!='closingRects'})
    changed=ink!=before;allowed=np.zeros_like(ink);allowed[55:78,33:45]=True
    assert changed.any() and not (changed & ~allowed).any()
    assert not (before & ~ink).any()


def test_short_break_repair_reconnects_only_one_outer_stroke(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3ED3A')
    _,ink=mask(record)
    _,before=mask({k:v for k,v in record.items() if k!='closingRects'})
    assert ndimage.label(before)[1]==5 and ndimage.label(ink)[1]==4
    allowed=np.zeros_like(ink);allowed[50:70,8:30]=True
    assert not ((ink!=before) & ~allowed).any()
    assert not (before & ~ink).any()


def test_corrected_roofs_keep_distinct_interiors_and_bounded_repairs(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,components,holes in [('3E4E9',3,1),('3E4EA',2,4)]:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==components
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
        _,before=mask({k:v for k,v in record.items() if k!='closingRects'})
        allowed=np.zeros_like(ink)
        for x0,y0,x1,y1,_ in record['closingRects']:allowed[y0:y1,x0:x1]=True
        changed=ink!=before
        assert changed.any() and not (changed & ~allowed).any()
        assert not (before & ~ink).any()
    # The page rule above C-05270 is excluded; its roof stem survives below it.
    _,ink=mask(records['3E4E9'])
    assert not ink[:21].any() and ink[21:45,80:110].any()


def test_shadow_threshold_preserves_spaces_without_page_edge(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3D766')
    _,ink=mask(record)
    _,standard=mask({**record,'thresholdOffset':20})
    assert not ink[:14].any() and standard[:14].any()
    assert ndimage.label(ink)[1]==3
    bowl=ink[115:195,70:149];background=np.ones((3,3),bool)
    assert ndimage.label(ndimage.binary_fill_holes(bowl,structure=background)&~bowl,structure=background)[1]==2
    _,before=mask({k:v for k,v in record.items() if k!='closingRects'})
    allowed=np.zeros_like(ink);allowed[150:165,95:115]=True
    assert (ink!=before).any() and not ((ink!=before)&~allowed).any()
    assert not (before&~ink).any()


def test_dense_book_four_repair_and_margin_cleanup_keep_native_detail(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    record=records['3E53F'];_,ink=mask(record)
    _,before=mask({k:v for k,v in record.items() if k!='closingRects'})
    background=np.ones((3,3),bool)
    assert ndimage.label(before)[1]==4 and ndimage.label(ink)[1]==2
    assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==11
    allowed=np.zeros_like(ink);allowed[100:170,85:125]=True
    assert not ((ink!=before)&~allowed).any() and not (before&~ink).any()
    record=records['3E5AD'];_,ink=mask(record)
    _,before=mask({k:v for k,v in record.items() if k!='clearRects'})
    assert ndimage.label(ink)[1]==4
    assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==3
    allowed=np.zeros_like(ink)
    for x0,y0,x1,y1 in record['clearRects']:allowed[y0:y1,x0:x1]=True
    assert not ((ink!=before)&~allowed).any() and not (ink&~before).any()
    assert not ink[:27,70:].any()


def test_cross_page_recoveries_reconnect_only_reviewed_breaks(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,old_components,new_components,holes in [('3EA8A',8,6,1),('3E69A',5,4,6)]:
        record=records[cp];_,ink=mask(record)
        _,before=mask({k:v for k,v in record.items() if k!='closingRects'})
        assert ndimage.label(before)[1]==old_components
        assert ndimage.label(ink)[1]==new_components
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
        allowed=np.zeros_like(ink)
        for x0,y0,x1,y1,_ in record['closingRects']:allowed[y0:y1,x0:x1]=True
        assert (ink!=before).any() and not ((ink!=before)&~allowed).any()
        assert not (before&~ink).any()
    # The mountain, three separate verticals and lower base retain their gaps.
    _,ink=mask(records['3EA8A']);labels,_=ndimage.label(ink)
    assert len(set(np.unique(labels[80:105,75:150]))-{0})==3


def test_water_radicals_keep_native_spaces_after_pencil_cleanup(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,components,holes in [('3EBF8',4,5),('3F15C',5,2),('3F15E',8,1),('3F161',8,4),('3F162',5,3),('3F163',6,8)]:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==components
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
        _,before=mask({k:v for k,v in record.items() if k not in ('clearRects','verticalOpeningBands')})
        allowed=np.zeros_like(ink)
        for key in ('clearRects','verticalOpeningBands'):
            for x0,y0,x1,y1 in record.get(key,[]):allowed[y0:y1,x0:x1]=True
        assert not ((ink!=before)&~allowed).any()
        assert not (ink&~before).any()
    # The rule above the first glyph and pencil below the water radical vanish.
    _,ink=mask(records['3EBF8']);assert not ink[:12].any()
    _,ink=mask(records['3F15C']);assert not ink[212:].any()


def test_shifted_mapping_replacements_keep_distinct_scan_structure(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,components,holes in [('3EEAF',3,6),('3EEB0',2,4),('3EEB1',4,9),('3EF2C',6,1),('3EFC5',8,0),('3EFC6',6,0)]:
        _,ink=mask(records[cp])
        assert ndimage.label(ink)[1]==components
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
    # A lighter threshold separates the middle-left lobe from the central stem.
    record=records['3EF2C'];_,ink=mask(record);labels,_=ndimage.label(ink)
    assert labels[105,30] and labels[105,72] and labels[105,30]!=labels[105,72]
    _,standard=mask({**record,'thresholdOffset':20});labels,_=ndimage.label(standard)
    assert labels[105,30]==labels[105,72]
    # Repair the worn notch only within the existing long water stem.
    record=records['3EFC6'];_,ink=mask(record)
    _,before=mask({k:v for k,v in record.items() if k!='closingRects'})
    allowed=np.zeros_like(ink);allowed[123:144,44:64]=True
    assert (ink!=before).any() and not ((ink!=before)&~allowed).any()
    assert not (before&~ink).any()
    # Pencil ink outside the lower-right component is excluded.
    _,ink=mask(records['3EFC5']);assert not ink[180:,144:].any()


def test_fish_cluster_removes_rules_without_losing_dense_interiors(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,components,holes in [('3F214',5,6),('3F215',4,6),('3F216',2,6),('3F217',6,4),('3F218',3,2),('3F21D',5,14)]:
        record=records[cp];_,ink=mask(record)
        labels,count=ndimage.label(ink)
        assert count==components
        assert np.bincount(labels.ravel())[1:].min()>=70
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
        if 'clearRects' in record:
            _,before=mask({k:v for k,v in record.items() if k!='clearRects'})
            bottom=record['clearRects'][0][3]
            assert before[:bottom].any() and not ink[:bottom].any()
            assert np.array_equal(ink[bottom:],before[bottom:])
            assert not (ink&~before).any()


def test_alternate_pdf_source_checks_page_pixels_and_polarity(monkeypatch):
    import pytest
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import source_image
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3F392')
    image=source_image(record)
    assert image.size==(4014,2900)
    assert image.getpixel((0,0))==255
    assert np.asarray(image).min()==0
    for bad in [{'page':1},{'size':[2008,1450]},{'pixelSha256':'0'*64}]:
        with pytest.raises(AssertionError):
            source_image({**record,'pdfImage':{**record['pdfImage'],**bad}})
    with pytest.raises(AssertionError):source_image({**record,'scanSha256':'0'*64})


def test_alternate_copy_preserves_reviewed_structure_and_clears_only_margins(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    expected=[('3F390',4,4),('3F392',3,1),('3F393',4,5),('3F394',4,1),('3F395',5,3),('3F396',3,3),('3F397',4,4),('3F398',1,3),('3F399',3,1),('3F39A',3,4),('3F39C',3,3),('3F39D',4,1),('3F39E',4,0),('3F39F',4,0),('3F3A0',3,2),('3F3A1',2,0),('3F3A3',5,2)]
    for cp,components,holes in expected:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==components
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
        if 'clearRects' in record:
            _,before=mask({k:v for k,v in record.items() if k!='clearRects'})
            allowed=np.zeros_like(ink)
            for x0,y0,x1,y1 in record['clearRects']:allowed[y0:y1,x0:x1]=True
            assert (ink!=before).any() and not ((ink!=before)&~allowed).any()
            assert not (ink&~before).any()
            # Margin fragments vanish whole; no printed component is shortened.
            labels,count=ndimage.label(before)
            for label in range(1,count+1):
                pixels=labels==label
                if (pixels&~ink).any():assert not (pixels&ink).any()
    assert not {'3F38D','3F38E','3F38F','3F391'} & records.keys()


def test_gate_variants_keep_distinct_interiors_and_full_outer_stems(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,components,holes in [('3F2B8',4,5),('3F2B9',4,4),('3F2BA',5,4),('3F2BB',4,6)]:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==components
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
        assert ink[195:220,:45].any() and ink[195:220,145:].any()
        # The narrower candidate crop amputated the right outer stem.
        if cp in ['3F2B9','3F2BA']:
            _,short=mask({**record,'crop':record['crop'][:2]+[78,record['crop'][3]]})
            assert not short[195:220,145:].any()


def test_inline_thread_forms_retain_open_loops(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    # The paired thread loops have deliberate openings, not scan damage.
    # Only the crossed cap of C-09811 encloses two white regions.
    for cp,holes in [('3F60E',0),('3F711',2)]:
        _,ink=mask(records[cp])
        assert ndimage.label(ink)[1]==1
        enclosed=ndimage.binary_fill_holes(ink,structure=background)&~ink
        assert ndimage.label(enclosed,structure=background)[1]==holes
        if holes:assert not enclosed[90:].any()
    # C-09409 is recovered only from the cleaner alternate copy.
    assert records['3F576']['pdfImage']['page']==273


def test_final_locations_keep_separate_components_and_restore_only_worn_loop(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,components,holes in [('3F7EC',5,1),('3FB65',2,3),('3FB66',2,4),('3FB72',4,0)]:
        _,ink=mask(records[cp])
        assert ndimage.label(ink)[1]==components
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
    record=records['3FB65'];_,ink=mask(record)
    _,before=mask({k:v for k,v in record.items() if k!='closingRects'})
    allowed=np.zeros_like(ink);allowed[80:117,25:56]=True
    assert (ink&~before).sum()==14 and not (before&~ink).any()
    assert not ((ink!=before)&~allowed).any()
    # The normal threshold falsely joins the left and right components.
    _,joined=mask({**record,'thresholdOffset':15})
    assert ndimage.label(joined)[1]==1


def test_cleaner_copy_recovers_deferred_forms_without_binding_shadow(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,components,holes in [('3DCE1',2,6),('3EEB4',4,5),('3F576',3,5)]:
        _,ink=mask(records[cp])
        assert ndimage.label(ink)[1]==components
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
    record=records['3DCE1'];_,ink=mask(record)
    _,before=mask({k:v for k,v in record.items() if k!='clearRects'})
    assert ndimage.label(before)[1]==1  # Printed contact joins the two stems.
    allowed=np.zeros_like(ink);allowed[164:192,55:59]=True
    assert (before&~ink).sum()==103 and not (ink&~before).any()
    assert not ((ink!=before)&~allowed).any()
    # The complete tip of each long stem survives the local separation.
    assert ink[195:205,:30].any() and ink[195:205,40:55].any()
    assert '3F510' not in records and '3E34F' not in records


def test_alternate_dyc_enclosure_preserves_counters_and_printed_pen_lift(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    record=next(r for r in records if r['codepoint']=='3E0E7')
    _,ink=mask(record)
    background=np.ones((3,3),bool)
    holes=ndimage.binary_fill_holes(ink,structure=background)&~ink
    labels,n=ndimage.label(holes,structure=background)
    assert ndimage.label(ink)[1]==1 and n==8
    assert min(np.bincount(labels.ravel())[1:])>2000
    # The lower-left end of the inner enclosure is printed as a pen lift.
    assert not ink[351:359,110:145].any()
    assert ink[330:345,110:145].any() and ink[360:375,110:145].any()
    _,before=mask({k:v for k,v in record.items() if k!='fillSmallHoles'})
    filled=ink&~before
    assert filled.any() and not (before&~ink).any()
    assert not (filled&~ndimage.binary_fill_holes(before,structure=background)).any()
    _,unfiltered=mask({**record,'minimumComponentArea':70})
    debris=unfiltered&~ink
    assert ndimage.label(debris)[1]==1 and 70<=debris.sum()<200
    assert not (ink&~unfiltered).any()


def test_alternate_dyc_wood_preserves_enclosed_marks_and_separate_strokes(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,parts,counters in [('3E02A',6,4),('3E073',5,0)]:
        r=records[cp];_,ink=mask(r)
        labels,n=ndimage.label(ink)
        assert n==parts
        holes=ndimage.binary_fill_holes(ink,structure=background)&~ink
        assert ndimage.label(holes,structure=background)[1]==counters
        _,before=mask({k:v for k,v in r.items() if k!='fillSmallHoles'})
        assert not (before&~ink).any()
        assert not ((ink&~before)&~ndimage.binary_fill_holes(before,structure=background)).any()
        if cp=='3E02A':
            # Both small marks remain detached, inside the two halves of the oval.
            sizes=np.bincount(labels.ravel());small=[i for i in range(1,n+1) if sizes[i]<1000]
            assert len(small)==2
            for label in small:
                ys,xs=np.where(labels==label)
                assert 275<ys.min()<ys.max()<345 and 235<xs.min()<xs.max()<390
            assert ink[280:345,235:305].any() and ink[275:345,315:390].any()
        else:
            # The complete tree remains one component; neighbours do not join it.
            tree=labels==labels[20,75]
            assert tree.any()
            ys,xs=np.where(tree)
            assert ys.min()<10 and ys.max()>400 and xs.max()<151


def test_late_dyc_variants_preserve_separate_parts_and_enclosed_details(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,parts,counters in [('3E096',9,3),('3E197',2,0),('3E1BC',4,0),('3E1E7',2,8)]:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==parts
        holes=ndimage.binary_fill_holes(ink,structure=background)&~ink
        assert ndimage.label(holes,structure=background)[1]==counters
        assert not any(k in record for k in ['clearRects','closingRects','fillSmallHoles','verticalOpeningBands'])
    record=records['3E1BC'];_,ink=mask(record)
    # The former crop included a detached commentary dot above the two curved caps.
    _,wide=mask({**record,'crop':[841,388,46,68]})
    labels,n=ndimage.label(wide);assert n==5
    sizes=np.bincount(labels.ravel());sizes[0]=wide.size
    dot=labels==np.argmin(sizes)
    assert dot.sum()==133 and not dot[17:].any()
    # Tightening removes that dot, while both complete curved caps survive.
    assert ink[:10,15:50].any() and ink[:10,57:91].any()
    assert ink[90:105,18:66].any()  # Detached lowest horizontal remains.


def test_fifth_dyc_volume_restores_faint_enclosure_without_merging_bar(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,parts,counters in [('3E2E7',4,6),('3E2FD',5,1),('3E310',7,1)]:
        _,ink=mask(records[cp]);assert ndimage.label(ink)[1]==parts
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==counters
    record=records['3E2FD'];_,ink=mask(record)
    _,faint=mask({**record,'thresholdOffset':0})
    assert ndimage.label(faint)[1]==6
    assert not (ndimage.binary_fill_holes(faint,structure=background)&~faint).any()
    labels,n=ndimage.label(ink)
    # The circular enclosure closes, while its internal bar stays detached.
    pieces=ndimage.find_objects(labels)
    lower=[i for i,box in enumerate(pieces,1) if box[0].start>70]
    assert len(lower)==2
    areas={i:int((labels==i).sum()) for i in lower}
    bar=labels==min(areas,key=areas.get)
    without_bar=ink&~bar
    assert (bar&ndimage.binary_fill_holes(without_bar,structure=background)).sum()==bar.sum()
    assert not any(k in record for k in ['clearRects','closingRects','fillSmallHoles'])


def test_dyc_day_and_moon_preserve_counters_and_detached_details(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,parts,counters in [('3E33B',5,1),('3E386',2,2)]:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==parts
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==counters
        assert not any(k in record for k in ['clearRects','closingRects','fillSmallHoles'])
    # The moon variant needs its faint left connection, while its two halves
    # must stay separate. The unadjusted extraction loses one enclosed region.
    _,faint=mask({**records['3E386'],'thresholdOffset':0})
    assert ndimage.label(faint)[1]==3
    assert ndimage.label(ndimage.binary_fill_holes(faint,structure=background)&~faint,structure=background)[1]==1
    # Excessive darkening falsely closes a second region in the day variant.
    _,dark=mask({**records['3E33B'],'thresholdOffset':40})
    assert ndimage.label(ndimage.binary_fill_holes(dark,structure=background)&~dark,structure=background)[1]==2


def test_dyc_variants_and_alternate_three_circle_form_preserve_identity(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,parts,counters in [('3E3B1',1,1),('3E3B3',2,4),('3E3C7',1,0),('3E377',2,3)]:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==parts
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==counters
        assert not any(k in record for k in ['clearRects','closingRects','verticalOpeningBands'])
    # This alternate source has an empty detached upper circle and two empty
    # circles attached to the stem, unlike the adjacent three-day variant.
    _,ink=mask(records['3E377']);labels,n=ndimage.label(ink)
    pieces=ndimage.find_objects(labels)
    upper=min(range(1,n+1),key=lambda i:pieces[i-1][0].start)
    ring=labels==upper;stem=ink&~ring
    assert pieces[upper-1][0].stop<next(box[0].start for i,box in enumerate(pieces,1) if i!=upper)
    assert ndimage.label(ndimage.binary_fill_holes(ring,structure=background)&~ring,structure=background)[1]==1
    assert ndimage.label(ndimage.binary_fill_holes(stem,structure=background)&~stem,structure=background)[1]==2
    assert not (ring&ndimage.binary_fill_holes(stem,structure=background)).any()


def test_dyc_rice_variants_keep_small_details_and_full_top_stem(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,parts,counters in [('3E452',6,0),('3E462',2,12),('3E51F',1,5),('3E542',2,6)]:
        _,ink=mask(records[cp]);assert ndimage.label(ink)[1]==parts
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==counters
        ys,xs=np.where(ink)
        assert 0<ys.min() and ys.max()<ink.shape[0]-1
        assert 0<xs.min() and xs.max()<ink.shape[1]-1
    record=records['3E51F'];_,ink=mask(record)
    _,before=mask({k:v for k,v in record.items() if k!='clearRects'})
    # The removed commentary is a complete detached component, not part of
    # the glyph. A narrower top crop would shorten the glyph's own stem.
    labels,n=ndimage.label(before);assert n==2
    removed=before&~ink
    assert removed.sum()==162 and not (ink&~before).any()
    assert any(np.array_equal(removed,labels==i) for i in range(1,n+1))
    assert ink[7:20,50:65].any()
    assert not removed[:,40:].any()


def test_dyc_sickness_variants_exclude_commentary_without_clipping(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,parts,counters in [('3E57F',3,4),('3E5A1',4,1),('3E605',4,1)]:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==parts
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==counters
        ys,xs=np.where(ink)
        assert 0<ys.min() and ys.max()<ink.shape[0]-1
        assert 0<xs.min() and xs.max()<ink.shape[1]-1
        assert not any(k in record for k in ['clearRects','closingRects','verticalOpeningBands'])
    # Expanding below this glyph includes a detached commentary mark; the
    # chosen crop must keep the glyph's top and complete lower stem instead.
    record=records['3E5A1'];_,ink=mask(record)
    x,y,w,h=record['crop'];_,expanded=mask({**record,'crop':[x,y,w,h+6]})
    assert ndimage.label(expanded)[1]>ndimage.label(ink)[1]
    assert np.array_equal(ink,expanded[:ink.shape[0]])


def test_dyc_volume6_preserves_detached_stems_and_faint_foot(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp in ['3E76D','3E7B8']:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==5
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==1
        ys,xs=np.where(ink)
        assert 0<ys.min() and ys.max()<ink.shape[0]-1
        assert 0<xs.min() and xs.max()<ink.shape[1]-1
        assert not any(k in record for k in ['clearRects','closingRects','verticalOpeningBands'])
    # Ordinary thresholding falsely joins one of the detached upper stems.
    _,joined=mask({**records['3E76D'],'thresholdOffset':0})
    assert ndimage.label(joined)[1]==4
    # Darkening too far merges an upper detached part in the cloth variant.
    _,joined=mask({**records['3E7B8'],'thresholdOffset':30})
    assert ndimage.label(joined)[1]==4
    _,ink=mask(records['3E7B8'])
    _,faint=mask({**records['3E7B8'],'thresholdOffset':0})
    assert ink[110:135,85:].sum()>faint[110:135,85:].sum()+10


def test_dyc_garment_and_foot_preserve_open_strokes_without_page_rule(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,parts in [('3E7ED',10),('3E85A',2)]:
        record=records[cp];_,ink=mask(record)
        assert ndimage.label(ink)[1]==parts
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==1
        ys,xs=np.where(ink)
        assert 0<ys.min() and ys.max()<ink.shape[0]-1
        assert 0<xs.min() and xs.max()<ink.shape[1]-1
        assert not any(k in record for k in ['clearRects','closingRects','verticalOpeningBands'])
    record=records['3E7ED'];_,ink=mask(record)
    x,y,w,h=record['crop'];_,expanded=mask({**record,'crop':[x,y,w,h+6]})
    # The page rule is a separate component below the complete glyph.
    labels,n=ndimage.label(expanded)
    assert n>ndimage.label(ink)[1]
    boxes=ndimage.find_objects(labels)
    assert any(box[0].start>=ink.shape[0] and box[1].stop-box[1].start>50 for box in boxes)
    # Excessive darkening merges intended gaps and picks up a neighbouring rule.
    _,dark=mask({**record,'thresholdOffset':40})
    assert ndimage.label(dark)[1]!=ndimage.label(ink)[1]


def test_dyc_head_retains_counters_without_joining_detached_strokes(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3E93F')
    background=np.ones((3,3),bool)
    def topology(offset):
        _,ink=mask({**record,'thresholdOffset':offset})
        holes=ndimage.binary_fill_holes(ink,structure=background)&~ink
        return ndimage.label(ink)[1],ndimage.label(holes,structure=background)[1]
    assert record['thresholdOffset']==40
    assert topology(40)==(6,7)
    assert topology(35)==(6,6)  # Faint enclosure remains open.
    assert topology(45)==(4,7)  # Distinct lower strokes merge.
    _,ink=mask(record);ys,xs=np.where(ink)
    assert 0<ys.min() and ys.max()<ink.shape[0]-1
    assert 0<xs.min() and xs.max()<ink.shape[1]-1
    assert not any(k in record for k in ['clearRects','closingRects','verticalOpeningBands'])


def test_dyc_head_ghost_open_counters_and_clean_crop(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    def topology(ink):
        return ndimage.label(ink)[1],ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]
    for cp,expected in [('3E968',(3,4)),('3EA49',(5,5)),('3EA7E',(2,4)),('3EAEE',(2,3))]:
        r=records[cp];_,ink=mask(r)
        assert topology(ink)==expected
        ys,xs=np.where(ink)
        assert 0<ys.min() and ys.max()<ink.shape[0]-1
        assert 0<xs.min() and xs.max()<ink.shape[1]-1
        assert not any(k in r for k in ['clearRects','closingRects','verticalOpeningBands'])
    # Darker extraction closes an intentional opening in the mountain form.
    _,dark=mask({**records['3EA7E'],'thresholdOffset':40})
    assert topology(dark)==(2,5)
    # Broad crop catches page rulings. The tight crop preserves only two parts.
    _,wide=mask({**records['3EA7E'],'crop':[1101,433,65,73]})
    assert topology(wide)[0]==4
    # Lighter extraction loses a real lower counter in the head form.
    _,light=mask({**records['3E968'],'thresholdOffset':0})
    assert topology(light)==(3,3)


def test_dyc_stones_preserve_eye_bars_and_detached_parts(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,parts,holes in [('3EB15',4,1),('3EB1F',3,4),('3EB35',6,1)]:
        r=records[cp];_,ink=mask(r)
        assert ndimage.label(ink)[1]==parts
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
        ys,xs=np.where(ink)
        assert 0<ys.min() and ys.max()<ink.shape[0]-1
        assert 0<xs.min() and xs.max()<ink.shape[1]-1
        assert not any(k in r for k in ['clearRects','closingRects','verticalOpeningBands'])
    # Ordinary extraction breaks both eye bars; offset20 repairs only one.
    for threshold,holes in [(0,2),(20,3)]:
        _,ink=mask({**records['3EB1F'],'thresholdOffset':threshold})
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes


def test_dyc_horses_keep_detached_components_and_counter_shapes(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,holes in [('3EBB1',5),('3EBBD',6)]:
        r=records[cp];_,ink=mask(r)
        assert ndimage.label(ink)[1]==2
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
        ys,xs=np.where(ink)
        assert 2<xs.min() and xs.max()<ink.shape[1]-3
        assert 2<ys.min() and ys.max()<ink.shape[0]-3
        assert not any(k in r for k in ['clearRects','closingRects','verticalOpeningBands'])
    # Excessive darkening joins the horse and right-hand component.
    _,dark=mask({**records['3EBBD'],'thresholdOffset':30})
    assert ndimage.label(dark)[1]==1


def test_dyc_later_horses_preserve_eye_bars_and_separate_interior_marks(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    def topology(ink):
        return ndimage.label(ink)[1],ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]
    for cp,expected in [('3EB9C',(4,1)),('3EBEA',(6,3)),('3EC0C',(7,3))]:
        r=records[cp];_,ink=mask(r)
        assert topology(ink)==expected
        ys,xs=np.where(ink)
        assert 0<xs.min() and xs.max()<ink.shape[1]-1
        assert 0<ys.min() and ys.max()<ink.shape[0]-1
        assert not any(k in r for k in ['clearRects','closingRects','verticalOpeningBands'])
    # A narrow threshold interval repairs an eye bar without merging the grains.
    for threshold,expected in [(10,(7,2)),(12,(7,3)),(16,(6,3))]:
        _,ink=mask({**records['3EC0C'],'thresholdOffset':threshold})
        assert topology(ink)==expected


def test_dyc_deer_rabbit_dogs_preserve_enclosures_and_dense_detail(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    def topology(ink):
        return ndimage.label(ink)[1],ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]
    for cp,expected in [('3EC4C',(4,2)),('3EC5D',(1,2)),('3EC9A',(2,11)),('3ECA7',(3,0))]:
        r=records[cp];_,ink=mask(r)
        assert topology(ink)==expected
        ys,xs=np.where(ink)
        assert 2<xs.min() and xs.max()<ink.shape[1]-3
        assert 2<ys.min() and ys.max()<ink.shape[0]-3
        assert not any(k in r for k in ['clearRects','closingRects','verticalOpeningBands'])
    # The source is worn at the enclosure edges; lighter thresholds lose a loop.
    for cp,threshold,expected in [('3EC4C',0,(4,1)),('3EC5D',30,(1,1))]:
        _,ink=mask({**records[cp],'thresholdOffset':threshold})
        assert topology(ink)==expected


def test_dyc_forest_fire_keeps_five_detached_components(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3ED25')
    _,ink=mask(record)
    assert ndimage.label(ink)[1]==5
    assert not (ndimage.binary_fill_holes(ink,structure=np.ones((3,3),bool))&~ink).any()
    ys,xs=np.where(ink)
    assert 0<xs.min() and xs.max()<ink.shape[1]-1
    assert 0<ys.min() and ys.max()<ink.shape[0]-1
    assert not any(k in record for k in ['clearRects','closingRects','verticalOpeningBands'])


def test_dyc_fire_roof_preserves_contacts_and_counters(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records={r['codepoint']:r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']}
    background=np.ones((3,3),bool)
    for cp,parts,holes in [('3ED68',6,2),('3ED9F',4,4),('3EDBB',2,2)]:
        r=records[cp];_,ink=mask(r)
        assert ndimage.label(ink)[1]==parts
        assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==holes
        ys,xs=np.where(ink)
        assert 0<xs.min() and xs.max()<ink.shape[1]-1
        assert 0<ys.min() and ys.max()<ink.shape[0]-1
        assert not any(k in r for k in ['clearRects','closingRects','verticalOpeningBands'])
    # Lighter extraction breaks the intentional interior contact in the vessel.
    _,ink=mask({**records['3ED68'],'thresholdOffset':0})
    assert ndimage.label(ndimage.binary_fill_holes(ink,structure=background)&~ink,structure=background)[1]==1


def test_D07328_separates_printing_bridge_without_changing_other_ink():
    import sys
    sys.path.insert(0,str(ROOT/'tools/font'))
    from build_seal_recovery import mask,trace
    spec=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())
    r=next(e for e in spec['glyphs'] if e['codepoint']=='3EE47')
    assert r['sequence']=='D-07328' and r['pdfImage']['page']==105
    assert r['clearRects']==[[118,0,128,128],[62,22,65,52]]
    _,before=mask({k:v for k,v in r.items() if k!='clearRects'})
    _,after=mask(r)
    allowed=np.zeros_like(before)
    for x0,y0,x1,y1 in r['clearRects']:allowed[y0:y1,x0:x1]=True
    assert np.array_equal(before[~allowed],after[~allowed])
    assert not (after&~before).any()
    assert (before&allowed).sum()<before.sum()*.12
    assert ndimage.label(after)[1]==2
    assert ndimage.label(ndimage.binary_fill_holes(after)&~after)[1]==2
    assert trace(after).numberOfContours==4




def test_D07337_keeps_its_intentional_contact_and_three_counters():
    import sys
    sys.path.insert(0,str(ROOT/'tools/font'))
    from build_seal_recovery import mask,trace
    spec=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())
    r=next(e for e in spec['glyphs'] if e['codepoint']=='3EE51')
    assert r['sequence']=='D-07337' and r['pdfImage']['page']==106
    assert not any(k in r for k in ['clearRects','closingRects','verticalOpeningBands','fillSmallHoles'])
    _,ink=mask(r)
    assert ndimage.label(ink)[1]==1
    assert ndimage.label(ndimage.binary_fill_holes(ink)&~ink)[1]==3
    assert trace(ink).numberOfContours==4




def test_D07344_keeps_four_coils_with_only_nine_documented_repair_pixels():
    import sys
    sys.path.insert(0,str(ROOT/'tools/font'))
    from build_seal_recovery import mask,trace
    r=next(e for e in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if e['codepoint']=='3EE59')
    assert r['sequence']=='D-07344' and r['pdfImage']['page']==106
    assert r['closingRects']==[[7,57,13,63,2],[24,66,33,74,2]]
    _,before=mask({k:v for k,v in r.items() if k!='closingRects'})
    _,after=mask(r)
    assert (after&~before).sum()==9 and not (before&~after).any()
    allowed=np.zeros_like(before)
    for x0,y0,x1,y1,_ in r['closingRects']:allowed[y0:y1,x0:x1]=True
    assert np.array_equal(before[~allowed],after[~allowed])
    assert ndimage.label(after)[1]==1
    holes=ndimage.binary_fill_holes(after,np.ones((3,3)))&~after
    labels,count=ndimage.label(holes,np.ones((3,3)))
    assert count==4
    centres=[ndimage.center_of_mass(labels==i) for i in range(1,5)]
    assert all((labels==i).sum()>100 for i in range(1,5))
    assert len({(y<50,x<40) for y,x in centres})==4
    g=trace(after);areas=[];start=0
    for end in g.endPtsOfContours:
        ps=list(g.coordinates[start:end+1]);start=end+1
        areas.append(sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(ps,ps[1:]+ps[:1])))
    assert len(areas)==5 and sum(a<0 for a in areas)==1 and sum(a>0 for a in areas)==4




@pytest.mark.parametrize('sequence,count',[('07328',212),('07337',213),('07344',214),('07391',215),('07419',216)])
def test_D073_recoveries_preserve_every_previous_drawing(sequence,count):
    baseline=json.loads((ROOT/f'output/font-review/seal-pending/pre-D-{sequence}-shaping.json').read_text())
    assert len(baseline)==count
    f=TTFont(ROOT/'build/unicode-sources/seal-recovery/DadSealRecovery-Regular.ttf')
    for cp,e in baseline.items():
        assert f.getBestCmap()[int(cp)]==e['name']
        g=f['glyf'][e['name']];c,ends,flags=g.getCoordinates(f['glyf'])
        assert list(map(list,c))==e['coordinates'] and list(ends)==e['endPts'] and list(flags)==e['flags']
        assert list(f['hmtx'][e['name']])==e['metric']


def test_D07391_preserves_both_complete_separate_parts_without_repairs():
    import sys
    sys.path.insert(0,str(ROOT/'tools/font'))
    from build_seal_recovery import mask,trace
    r=next(e for e in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if e['codepoint']=='3EE89')
    assert r['sequence']=='D-07391' and r['pdfImage']['page']==112
    assert not any(k in r for k in ['clearRects','closingRects','verticalOpeningBands','fillSmallHoles'])
    _,ink=mask(r);labels,count=ndimage.label(ink)
    assert count==2 and not (ndimage.binary_fill_holes(ink)&~ink).any()
    parts=sorted([np.nonzero(labels==i) for i in range(1,3)],key=lambda p:p[1].mean())
    assert .8<np.ptp(parts[0][0])/np.ptp(parts[1][0])<1.2
    assert all(len(p[0])>100 for p in parts)
    assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
    assert trace(ink).numberOfContours==2


def test_D07419_preserves_the_outer_and_inner_arch_and_lower_part():
    import sys
    sys.path.insert(0,str(ROOT/'tools/font'))
    from build_seal_recovery import mask,trace
    r=next(e for e in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if e['codepoint']=='3EEA6')
    assert r['sequence']=='D-07419' and r['pdfImage']['page']==115
    assert not any(k in r for k in ['clearRects','closingRects','verticalOpeningBands','fillSmallHoles'])
    _,ink=mask(r);labels,count=ndimage.label(ink)
    assert count==3 and not (ndimage.binary_fill_holes(ink)&~ink).any()
    parts=sorted([np.nonzero(labels==i) for i in range(1,4)],key=lambda p:len(p[0]),reverse=True)
    main,*detached=parts
    assert all(p[1].mean()>main[1].mean() for p in detached)
    assert all(np.ptp(p[0])<np.ptp(main[0]) for p in detached)
    assert min(p[0].mean() for p in detached)<max(p[0].mean() for p in detached)-15
    assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
    assert trace(ink).numberOfContours==3
