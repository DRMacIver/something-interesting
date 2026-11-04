"""Semantic stroke graph checks for the review-only licensed-source experiment."""
from pathlib import Path
import numpy as np
import pytest
from scipy import ndimage as ndi

ROOT=Path(__file__).resolve().parents[1]


def render(monkeypatch, points):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from unifont_strokes import reconstruct
    mask=np.zeros((12,12),dtype=bool)
    for y,x in points:mask[y,x]=True
    source=np.repeat(np.repeat(mask,32,axis=0),32,axis=1)
    result,report=reconstruct(source)
    return source,result,report


def test_orthogonal_corner_does_not_invent_a_diagonal_loop(monkeypatch):
    _,result,_=render(monkeypatch,[(4,4),(4,5),(5,5)])
    assert ndi.label(result)[1]==1
    assert not (ndi.binary_fill_holes(result)&~result).any()


def test_loop_with_a_stem_preserves_its_counter_and_attachment(monkeypatch):
    points=[(y,x) for y in range(3,7) for x in range(3,7) if y in (3,6) or x in (3,6)]
    points += [(7,6),(8,6)]
    _,result,_=render(monkeypatch,points)
    assert ndi.label(result)[1]==1
    holes,count=ndi.label(ndi.binary_fill_holes(result)&~result)
    assert count==1 and holes[4*32+16,4*32+16]
    assert result[8*32+16,6*32+16]


def test_detached_compact_dots_keep_area_instead_of_becoming_dashes(monkeypatch):
    points=[(y,x) for y in (3,4,7,8) for x in (5,6)]
    source,result,report=render(monkeypatch,points)
    assert report['dots']==2
    assert ndi.label(result)[1]==2
    assert .8<=result.sum()/source.sum()<=1.2
    labels,count=ndi.label(result)
    for label in range(1,count+1):
        ys,xs=np.nonzero(labels==label)
        assert abs(np.ptp(xs)-np.ptp(ys))<=1


def test_same_topology_cannot_hide_a_half_filled_counter(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from prototype_unifont_lettering import topology, validate_reconstruction
    before=np.zeros((16,16),dtype=bool)
    before[4:12,4:12]=True;before[6:10,6:10]=False
    after=before.copy();after[6:8,6:10]=True
    assert topology(before)==topology(after)
    assert after.sum()/before.sum()<1.2
    with pytest.raises(ValueError,match='counter'):
        validate_reconstruction(before,after)


def test_empty_source_cannot_pass_reconstruction(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from prototype_unifont_lettering import prepare_letter
    with pytest.raises(ValueError,match='No source ink'):
        prepare_letter(np.zeros((64,64),dtype=bool),0x10d69)


def test_wide_garay_letters_and_negative_origin_marks_are_not_clipped(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from prototype_unifont_lettering import raster
    from fontTools.ttLib import TTFont
    font=TTFont(ROOT/'build/unicode-sources/unifont/unifont_upper-18.0.01.otf')
    for cp in (0x10d51,0x10d69,0x10d6d):
        mask=raster(font,cp,wide=True)
        assert mask.any() and not mask[[0,-1],:].any() and not mask[:,[0,-1]].any()
        with pytest.raises(AssertionError,match='clipped viewport'):
            raster(font,cp)


@pytest.mark.parametrize('cp',[0x10D42,0x10D4C,0x10D69,0x10D6F,0x10D75])
def test_garay_special_recipes_preserve_source_structure(monkeypatch,cp):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from prototype_unifont_lettering import raster,prepare_letter,validate_reconstruction
    from fontTools.ttLib import TTFont
    font=TTFont(ROOT/'build/unicode-sources/unifont/unifont_upper-18.0.01.otf')
    source=raster(font,cp,wide=True)
    image,record=prepare_letter(source,cp)
    after=np.asarray(image)<128
    validate_reconstruction(source,after)
    if cp in (0x10D4C,0x10D69):
        # A comma must retain a broad head and a narrow, descending tail.
        ys,xs=np.nonzero(source)
        middle=(ys.min()+ys.max())//2
        assert after[:middle].sum()>after[middle:].sum()*1.5
        assert np.nonzero(after)[0].max()>ys.max()-16
