"""A font-rounding exception must never hide loss of a real enclosed feature."""
import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/font'))
from build_emoji import outline
from svg_counter_review import review_counters


def source():
    mask=np.zeros((64,64),dtype=bool);mask[8:56,8:56]=True
    mask[16:28,16:28]=False;mask[40:42,40:42]=False
    return mask


def test_explicit_small_counter_exception_still_preserves_the_large_counter():
    mask=source();compiled=mask.copy();compiled[40:42,40:42]=True
    glyph=outline(compiled,(0,0,1))
    report=review_counters(mask,(0,0,1),glyph,max_small_losses=1)
    assert report['smallCounterLosses']==1 and report['largeCountersChecked']==1
    with pytest.raises(AssertionError):review_counters(mask,(0,0,1),glyph)


def test_small_counter_exception_rejects_missing_large_counter():
    mask=source();compiled=mask.copy();compiled[16:28,16:28]=True
    with pytest.raises(AssertionError):
        review_counters(mask,(0,0,1),outline(compiled,(0,0,1)),max_small_losses=1)


def nested_source():
    mask=np.zeros((96,96),dtype=bool);mask[8:88,8:88]=True
    mask[16:80,16:80]=False;mask[32:64,32:64]=True
    mask[40:56,40:56]=False;mask[40:42,10:12]=False
    return mask


def test_nested_counters_match_the_innermost_compiled_region():
    mask=nested_source();compiled=mask.copy();compiled[40:42,10:12]=True
    report=review_counters(mask,(0,0,1),outline(compiled,(0,0,1)),max_small_losses=1)
    assert report['smallCounterLosses']==1 and report['largeCountersChecked']==2


def test_nested_counter_exception_rejects_merging_an_island_into_the_ocean():
    mask=nested_source();compiled=mask.copy();compiled[44:48,32:40]=False
    with pytest.raises(AssertionError):
        review_counters(mask,(0,0,1),outline(compiled,(0,0,1)),max_small_losses=1)
