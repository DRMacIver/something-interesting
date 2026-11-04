"""Edition aliases must not send source recovery to a book lacking the form."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_supplemental_thx_index_is_not_a_historical_thx_drawing(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from review_seal_editions import editions
    assert editions({'kSEAL_THXSrc':'TH-Y001', 'kSEAL_DYCSrc':'D-00007'}) == [
        {'edition':'DYC', 'sequence':'D-00007'}]
    assert editions({'kSEAL_THXSrc':'TH-Y003', 'kSEAL_QJZSrc':'K-00035'}) == [
        {'edition':'QJZ', 'sequence':'K-00035'}]
    assert editions({'kSEAL_THXSrc':'TH-Y001'}) == []
    # Ordinary and Xinfuzi references really do occur in the THX edition.
    for sequence in ['TH-00333', 'TH-X001']:
        assert editions({'kSEAL_THXSrc':sequence}) == [{'edition':'THX','sequence':sequence}]


def test_recovery_provenance_requires_the_exact_edition(monkeypatch):
    import pytest
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import validate_reference
    references={('3D007','kSEAL_THXSrc'):'TH-Y001', ('3D007','kSEAL_DYCSrc'):'D-00007'}
    valid={'codepoint':'3D007','sourceProperty':'kSEAL_DYCSrc','sequence':'D-00007'}
    validate_reference(valid,references)
    with pytest.raises(KeyError):
        validate_reference({**valid,'sourceProperty':'kSEAL_CCZSrc'},references)
    with pytest.raises(AssertionError):
        validate_reference({**valid,'sequence':'D-00008'},references)
    with pytest.raises(AssertionError):
        validate_reference({**valid,'sourceProperty':'kSEAL_THXSrc','sequence':'TH-Y001'},references)


def test_dyc_upper_bar_is_shorter_and_both_bars_are_complete(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3D007')
    assert record['sourceProperty']=='kSEAL_DYCSrc'
    _,ink=mask(record);labels,count=ndimage.label(ink)
    assert count==2 and not (ndimage.binary_fill_holes(ink)&~ink).any()
    parts=sorted((np.nonzero(labels==i) for i in range(1,3)),key=lambda p:p[0].mean())
    widths=[int(x.max()-x.min()+1) for y,x in parts]
    assert 0.4 < widths[0]/widths[1] < 0.7
    assert not ink[0].any() and not ink[-1].any()
    assert not ink[:,0].any() and not ink[:,-1].any()


def test_dyc_complex_form_preserves_separate_parts_and_enclosures(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3D055')
    _,ink=mask(record)
    assert ndimage.label(ink)[1]==4
    # Use the tracer's eight-connected background convention for enclosed spaces.
    holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3))) & ~ink
    labels,count=ndimage.label(holes,structure=np.ones((3,3)))
    assert count==3
    assert all(np.count_nonzero(labels==i)>10 for i in range(1,4))
    assert not ink[0].any() and not ink[-1].any()
    assert not ink[:,0].any() and not ink[:,-1].any()


def test_high_resolution_dyc_bars_only_remove_detached_ruling(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3D010')
    _,original=mask({k:v for k,v in record.items() if k!='clearRects'})
    _,ink=mask(record)
    changed=original & ~ink
    assert changed.sum()==2232 and not (ink & ~original).any()
    assert np.array_equal(original[:180],ink[:180])
    assert np.array_equal(original[205:],ink[205:])
    labels,count=ndimage.label(ink)
    assert count==2 and not (ndimage.binary_fill_holes(ink)&~ink).any()
    parts=sorted((np.nonzero(labels==i) for i in range(1,3)),key=lambda p:p[0].mean())
    widths=[int(x.max()-x.min()+1) for y,x in parts]
    assert 0.5 < widths[1]/widths[0] < 0.7
    assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()


def test_dyc_dot_stays_separate_at_middle_right(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3D087')
    _,ink=mask(record);labels,count=ndimage.label(ink)
    assert count==2 and not (ndimage.binary_fill_holes(ink)&~ink).any()
    core,dot=sorted((np.nonzero(labels==i) for i in range(1,3)),key=lambda p:len(p[0]),reverse=True)
    assert dot[1].min()>core[1].max()
    relative_y=(dot[0].mean()-core[0].min())/(core[0].max()-core[0].min())
    assert 0.35<relative_y<0.6
    assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()


def test_dyc_complex_enclosures_survive_small_source_scans(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,components,hole_count in [('3D0A8',5,8),('3D122',6,3)]:
        record=next(r for r in records if r['codepoint']==cp)
        assert not any(record.get(k) for k in ['clearRects','closingRects','verticalOpeningBands'])
        _,ink=mask(record)
        assert ndimage.label(ink)[1]==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3))) & ~ink
        labels,count=ndimage.label(holes,structure=np.ones((3,3)))
        assert count==hole_count
        assert all(np.count_nonzero(labels==i)>=8 for i in range(1,count+1))
        if cp=='3D0A8':
            # Two distinct four-cell components on the right, not a filled square.
            centers=[np.nonzero(labels==i)[0].mean() for i in range(1,count+1)]
            assert sum(y<45 for y in centers)==4
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()


def test_dyc_grass_loops_and_separate_strokes_survive(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,components,hole_count in [('3D182',2,2),('3D198',5,1)]:
        record=next(r for r in records if r['codepoint']==cp)
        _,ink=mask(record)
        assert ndimage.label(ink)[1]==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3))) & ~ink
        labels,count=ndimage.label(holes,structure=np.ones((3,3)))
        assert count==hole_count
        assert all(np.count_nonzero(labels==i)>20 for i in range(1,count+1))
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        if cp=='3D198':
            # Tight top boundary excludes the preceding character's detached arc.
            assert record['crop']==[831,530,48,66]
            assert ndimage.label(ink[:20])[1]==2


def test_qjz_forms_keep_enclosures_separate_marks_and_complete_stems(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,sequence,components,hole_count in [('3D025','K-00035',7,0),('3D02C','K-00041',6,6),('3D062','K-00094',5,3),('3D08B','K-00131',6,3)]:
        record=next(r for r in records if r['codepoint']==cp)
        assert record['sourceProperty']=='kSEAL_QJZSrc'
        assert record['sequence']==sequence
        assert not any(record.get(k) for k in ['clearRects','closingRects','verticalOpeningBands'])
        _,ink=mask(record)
        assert ndimage.label(ink)[1]==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3))) & ~ink
        labels,count=ndimage.label(holes,structure=np.ones((3,3)))
        assert count==hole_count
        assert all(np.count_nonzero(labels==i)>200 for i in range(1,count+1))
        # Two-pixel margins catch the formerly near-clipped outer stem of K-00041.
        assert not ink[:2].any() and not ink[-2:].any()
        assert not ink[:,:2].any() and not ink[:,-2:].any()


def test_dyc_water_grass_keeps_crowns_and_printed_pen_lifts(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3D21C')
    assert record['sequence']=='D-00503'
    assert not any(record.get(k) for k in ['clearRects','closingRects','verticalOpeningBands'])
    _,ink=mask(record)
    assert ndimage.label(ink)[1]==12
    assert not (ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink).any()
    # The two complete grass crowns must survive above the separate lower strokes.
    assert ndimage.label(ink[:33])[1]==2
    assert not ink[:2].any() and not ink[-2:].any()
    assert not ink[:,:2].any() and not ink[:,-2:].any()


def test_dyc_worn_scan_repair_preserves_real_counters_and_open_spaces(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    record=next(r for r in json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs'] if r['codepoint']=='3D2A6')
    assert record['sequence']=='D-00640' and record['fillSmallHoles']==20
    _,raw=mask({k:v for k,v in record.items() if k not in ['clearRects','fillSmallHoles']})
    _,ink=mask(record)
    background=np.ones((3,3),bool)
    holes=ndimage.binary_fill_holes(raw,structure=background)&~raw
    labels,count=ndimage.label(holes,structure=background)
    sizes=np.bincount(labels.ravel())
    small=(sizes>0)&(sizes<=20);small[0]=False
    # Only enclosed print pits gain ink; no external space or stroke gap does.
    assert np.array_equal(ink&~raw,small[labels])
    real=(sizes>20);real[0]=False
    final_holes=ndimage.binary_fill_holes(ink,structure=background)&~ink
    assert np.array_equal(final_holes,real[labels])
    assert ndimage.label(final_holes,structure=background)[1]==4
    assert ndimage.label(ink)[1]==11
    allowed=np.zeros_like(ink)
    for x0,y0,x1,y1 in record['clearRects']:allowed[y0:y1,x0:x1]=True
    assert not (raw&~ink&~allowed).any()
    assert (raw&~ink&allowed).any()
    assert not ink[:2].any() and not ink[-2:].any()
    assert not ink[:,:2].any() and not ink[:,-2:].any()


def test_dyc_bird_enclosures_and_detached_inner_bar_survive(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,sequence,components,counters in [('3D355','D-00800',3,10),('3D37A','D-00834',4,3)]:
        record=next(r for r in records if r['codepoint']==cp)
        assert record['sequence']==sequence
        assert not any(record.get(k) for k in ['clearRects','closingRects','verticalOpeningBands','fillSmallHoles'])
        _,ink=mask(record)
        assert ndimage.label(ink)[1]==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        assert ndimage.label(holes,structure=np.ones((3,3)))[1]==counters
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        if cp=='3D37A':
            # The separate bar must sit inside the lower enclosed component.
            inner=ink & ndimage.binary_fill_holes(holes,structure=np.ones((3,3)))
            assert ndimage.label(inner)[1]==1
            assert inner.any()


def test_dyc_mouth_and_walking_variants_keep_enclosures_and_pen_lifts(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,sequence,components,counters in [('3D40D','D-00981',2,3),('3D414','D-00986',4,5),('3D46B','D-01063',4,4),('3D4A0','D-01115',4,0),('3D4D5','D-01166',4,4)]:
        record=next(r for r in records if r['codepoint']==cp)
        assert record['sequence']==sequence
        assert not any(record.get(k) for k in ['clearRects','closingRects','verticalOpeningBands','fillSmallHoles'])
        _,ink=mask(record)
        assert ndimage.label(ink)[1]==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        labels,count=ndimage.label(holes,structure=np.ones((3,3)))
        assert count==counters
        assert all(np.count_nonzero(labels==i)>30 for i in range(1,count+1))
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        if cp=='3D414':
            # Four enclosed loops to the right of the mouth component.
            assert sum(np.nonzero(labels==i)[1].mean()>35 for i in range(1,count+1))==4


def test_dyc_volume_two_cells_and_descenders_survive(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,sequence,components,counters in [('3D54F','D-01284',4,4),('3D5B4','D-01371',3,6)]:
        record=next(r for r in records if r['codepoint']==cp)
        assert record['sequence']==sequence
        assert record['scan'].endswith('/dyc-02.pdf')
        assert not any(record.get(k) for k in ['clearRects','closingRects','verticalOpeningBands','fillSmallHoles'])
        _,ink=mask(record)
        labels,count=ndimage.label(ink)
        assert count==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        cells,n=ndimage.label(holes,structure=np.ones((3,3)))
        assert n==counters
        assert all(np.count_nonzero(cells==i)>30 for i in range(1,n+1))
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        if cp=='3D5B4':
            # The separate right-hand curve descends below the entire tooth part.
            parts=[np.argwhere(labels==i) for i in range(1,count+1)]
            parts.sort(key=lambda p:p[:,1].mean())
            assert parts[-1][:,0].max()>max(p[:,0].max() for p in parts[:-1])+15


def test_dyc_speech_components_and_separate_lifting_hands(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,sequence,counters in [('3D6CF','D-01636',4),('3D775','D-01800',3),('3D7D0','D-01880',4)]:
        record=next(r for r in records if r['codepoint']==cp)
        assert record['sequence']==sequence
        assert not any(record.get(k) for k in ['clearRects','closingRects','verticalOpeningBands','fillSmallHoles'])
        _,ink=mask(record)
        labels,n=ndimage.label(ink)
        assert n==3
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        assert ndimage.label(holes,structure=np.ones((3,3)))[1]==counters
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        if cp=='3D7D0':
            assert record['thresholdOffset']==0
            parts=sorted([np.argwhere(labels==i) for i in range(1,n+1)],key=lambda p:p[:,0].mean())
            # Four upper cells sit above two separate hand shapes, both with full stems.
            assert parts[0][:,0].max()<min(p[:,0].min() for p in parts[1:])
            assert all(p[:,0].max()-p[:,0].min()>45 for p in parts[1:])
            assert abs(parts[1][:,1].mean()-parts[2][:,1].mean())>25


def test_dyc_variants_preserve_flames_gaps_and_distinct_kill_forms(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,sequence,components,counters in [('3D893','D-02072',7,0),('3D8BF','D-02115',2,4),('3D8EF','D-02163',6,1),('3D8F3','D-02167',5,0)]:
        r=next(r for r in records if r['codepoint']==cp)
        assert r['sequence']==sequence
        assert not any(r.get(k) for k in ['clearRects','closingRects','verticalOpeningBands','fillSmallHoles'])
        _,ink=mask(r)
        assert ndimage.label(ink)[1]==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        assert ndimage.label(holes,structure=np.ones((3,3)))[1]==counters
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        if cp in ['3D893','3D8BF']:
            # Stronger thresholding incorrectly fuses a narrow printed gap.
            assert r['thresholdOffset']==0
            _,heavy=mask({**r,'thresholdOffset':20})
            assert ndimage.label(heavy)[1]<components
        if cp=='3D8EF':
            # This variant has a lozenge in its upper-left cross, unlike D-02167.
            y,x=np.nonzero(holes)
            assert x.mean()<ink.shape[1]/2 and y.mean()<ink.shape[0]/3


def test_dyc_eye_dot_and_knowledge_interior_survive(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,sequence,components in [('3D951','D-02257',2),('3D9C4','D-02367',3),('3DA15','D-02441',2)]:
        r=next(r for r in records if r['codepoint']==cp)
        assert r['sequence']==sequence
        assert not any(r.get(k) for k in ['clearRects','closingRects','verticalOpeningBands','fillSmallHoles'])
        _,ink=mask(r)
        assert ndimage.label(ink)[1]==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        assert ndimage.label(holes,structure=np.ones((3,3)))[1]==2
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        if cp=='3D9C4':
            # The enclosed central dot must remain detached within the eye.
            inner=ink & ndimage.binary_fill_holes(holes,structure=np.ones((3,3)))
            assert ndimage.label(inner)[1]==1 and inner.any()
            assert np.nonzero(inner)[0].mean()>ink.shape[0]/2


def test_dyc_bird_variants_keep_head_marks_and_paired_loops(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,components,counters in [('3DADD',5,11),('3DADF',3,11),('3DAEA',6,2),('3DB03',4,4)]:
        r=next(r for r in records if r['codepoint']==cp)
        assert not any(r.get(k) for k in ['clearRects','closingRects','verticalOpeningBands','fillSmallHoles'])
        _,ink=mask(r)
        assert ndimage.label(ink)[1]==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        cells,n=ndimage.label(holes,structure=np.ones((3,3)))
        assert n==counters
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        if cp=='3DB03':
            # All four counters belong to two hanging loop columns left of the bird.
            centres=np.array([np.argwhere(cells==i).mean(axis=0) for i in range(1,n+1)])
            assert np.all(centres[:,1]<ink.shape[1]*0.65)
            assert np.ptp(centres[:,0])>ink.shape[0]*0.25
            assert np.ptp(centres[:,1])>ink.shape[1]*0.15
        if cp=='3DADD':
            # This bird head encloses a detached mark; D-02639's mark joins its rim as printed.
            inner=ink & ndimage.binary_fill_holes(holes,structure=np.ones((3,3)))
            ys,xs=np.nonzero(inner)
            assert len(xs)>0 and xs.max()>ink.shape[1]*0.6 and ys.min()<ink.shape[0]*0.3


def test_dyc_hand_and_remains_preserve_original_components(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,components,counters in [('3DB6D',3,0),('3DBA2',2,1)]:
        r=next(r for r in records if r['codepoint']==cp)
        _,ink=mask(r)
        assert ndimage.label(ink)[1]==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        assert ndimage.label(holes,structure=np.ones((3,3)))[1]==counters
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        if cp=='3DBA2':
            # The two largest original components are the glyph. Cleanup must
            # remove only the detached commentary above the right-hand roof.
            _,raw=mask({**r,'clearRects':[]})
            labels,n=ndimage.label(raw)
            largest=sorted(range(1,n+1),key=lambda k:np.count_nonzero(labels==k),reverse=True)[:2]
            assert np.array_equal(ink,np.isin(labels,largest))
            removed=np.argwhere(raw&~ink)
            assert len(removed)>0 and removed[:,0].max()<30 and removed[:,1].min()>=70
        else:
            # Three separate strokes distinguish this variant from nearby forms.
            assert not r.get('clearRects')


def test_dyc_container_keeps_meaningful_small_dot(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    r=next(r for r in records if r['codepoint']=='3DD51')
    _,ink=mask(r)
    _,ordinary=mask({**r,'minimumComponentArea':70})
    dot=ink&~ordinary
    assert 20<=dot.sum()<70
    assert ndimage.label(dot)[1]==1
    assert np.all(ordinary<=ink)
    holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
    assert np.all(dot<=ndimage.binary_fill_holes(ordinary,structure=np.ones((3,3))))
    assert ndimage.label(ink)[1]==2
    assert ndimage.label(holes,structure=np.ones((3,3)))[1]==3
    assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()


def test_dyc_bamboo_variants_preserve_pen_lifts_and_counters(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,components,counters in [('3DD63',1,5),('3DD65',1,0),('3DDA4',3,0),('3DDA5',2,2)]:
        r=next(r for r in records if r['codepoint']==cp)
        _,ink=mask(r)
        labels,n=ndimage.label(ink)
        assert n==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        assert ndimage.label(holes,structure=np.ones((3,3)))[1]==counters
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        assert not r.get('clearRects') and not r.get('closingRects')
        if cp=='3DDA4':
            # Both bamboo crowns remain separate from the lower forked stroke.
            regions=[np.argwhere(labels==i) for i in range(1,n+1)]
            crowns=[a for a in regions if a[:,0].max()<ink.shape[0]*0.4]
            assert len(crowns)==2
            assert abs(crowns[0][:,1].mean()-crowns[1][:,1].mean())>ink.shape[1]*0.3


def test_dyc_vessel_variants_preserve_enclosed_marks(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,components,counters in [('3DDCE',5,3),('3DDFC',4,2),('3DE16',1,4)]:
        r=next(r for r in records if r['codepoint']==cp)
        _,ink=mask(r)
        labels,n=ndimage.label(ink)
        assert n==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        assert ndimage.label(holes,structure=np.ones((3,3)))[1]==counters
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        assert not r.get('clearRects') and not r.get('closingRects')
        if cp=='3DDCE':
            # The short bar inside the lower cup must survive debris removal.
            regions=[np.argwhere(labels==i) for i in range(1,n+1)]
            internal=[a for a in regions if a[:,0].min()>ink.shape[0]*0.7 and a[:,1].min()>ink.shape[1]*0.25 and a[:,1].max()<ink.shape[1]*0.8]
            assert len(internal)==1
        if cp=='3DE16':
            # Both fine stem crossbars enclose three windows below the bowl.
            cells,count=ndimage.label(holes,structure=np.ones((3,3)))
            lower=[np.argwhere(cells==i) for i in range(1,count+1) if np.argwhere(cells==i)[:,0].mean()>ink.shape[0]*0.45]
            assert len(lower)==3


def test_dyc_food_bar_survives_debris_filter(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    for cp,components,counters in [('3DE79',4,8),('3DEE5',5,2)]:
        r=next(r for r in records if r['codepoint']==cp)
        _,ink=mask(r)
        assert ndimage.label(ink)[1]==components
        holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
        assert ndimage.label(holes,structure=np.ones((3,3)))[1]==counters
        assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
        if cp=='3DEE5':
            _,ordinary=mask({**r,'minimumComponentArea':70})
            bar=ink&~ordinary
            assert 30<=bar.sum()<70 and ndimage.label(bar)[1]==1
            assert np.all(ordinary<=ink)
            assert np.all(bar<=ndimage.binary_fill_holes(ordinary,structure=np.ones((3,3))))
            ys,xs=np.nonzero(bar)
            assert xs.max()<ink.shape[1]*0.5
            assert np.ptp(xs)>np.ptp(ys)*2


def test_dyc_walking_variant_keeps_two_parts_and_lower_counter(monkeypatch):
    import json
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from build_seal_recovery import mask
    records=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['glyphs']
    r=next(r for r in records if r['codepoint']=='3DF72')
    _,ink=mask(r)
    assert ndimage.label(ink)[1]==2
    holes=ndimage.binary_fill_holes(ink,structure=np.ones((3,3)))&~ink
    assert ndimage.label(holes,structure=np.ones((3,3)))[1]==1
    ys,xs=np.nonzero(holes)
    assert ys.min()>ink.shape[0]*0.5 and xs.min()>ink.shape[1]*0.5
    assert not ink[[0,-1],:].any() and not ink[:,[0,-1]].any()
    assert not r.get('clearRects') and not r.get('closingRects')
