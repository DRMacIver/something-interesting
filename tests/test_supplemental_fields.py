"""Threshold-pore filtering cannot hide counter closure or missing ink."""
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from check_supplemental_fields import pore_filter
from prototype_unifont_lettering import validate_reconstruction
import pytest


def test_only_sub_four_pixel_white_pores_are_classified_as_raster_artifacts():
    ink=np.zeros((40,40),bool);ink[5:35,5:35]=True
    ink[10,10]=False;ink[20:22,20:22]=False
    filtered,report=pore_filter(ink)
    assert report['porePixelAreas']==[1]
    assert report['counterPixelAreas']==[4]
    assert filtered[10,10]
    assert not filtered[20,20]
    assert report['filteredTopology']==(1,1)


def test_real_counter_closure_and_missing_dot_still_fail():
    ink=np.zeros((60,60),bool);ink[10:45,10:45]=True;ink[18:37,18:37]=False;ink[2:5,2:5]=True
    original,_=pore_filter(ink)
    closed=ink.copy();closed[18:37,18:37]=True
    no_dot=ink.copy();no_dot[2:5,2:5]=False
    for changed in [closed,no_dot]:
        filtered,_=pore_filter(changed)
        with pytest.raises(ValueError):validate_reconstruction(original,filtered)
