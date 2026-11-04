"""Native-reference checks for the staged couple drawings."""
import sys
from pathlib import Path
import pytest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from couple_sources import validate_couple_sources
from prototype_couples_svg import RECIPES,prepare


def test_all_native_couple_head_tones():
    reports=validate_couple_sources(ROOT)
    assert len(reports)==208


@pytest.mark.parametrize('key',RECIPES)
def test_couple_masks_keep_separate_faces_and_heart(key):
    (white,*materials,ink),report=prepare(key)
    regions=dict(zip(report['colourNames'],materials))
    assert set(regions)=={'left','right','red'}
    assert all(not np.any(regions[a]&regions[b]) for a,b in [('left','right'),('left','red'),('right','red')])
    # Physical positions are independent of the SVG path order, which differs
    # between the neutral and gendered drawings.
    centres={name:tuple(np.array(np.nonzero(mask)).mean(axis=1)) for name,mask in regions.items()}
    assert centres['left'][1]<ink.shape[1]/2<centres['right'][1]
    assert centres['red'][0]<min(centres['left'][0],centres['right'][0])
    assert report['appliedStrength']>0 and not report['fallback']
