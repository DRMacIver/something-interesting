"""Semantic details of the unregistered general flag candidates."""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from emoji_general_flags_svg import prepare, RECIPES
TOPOLOGY={'1f3c1':(2,16),'1f6a9':(1,3),'1f38c':(5,11),'1f3f4':(1,1),'1f3f3':(1,4),'1f3f3_200d_1f308':(1,6),'1f3f3_200d_26a7':(1,5),'1f3f4_200d_2620':(4,4)}

@pytest.mark.parametrize('key',RECIPES)
def test_general_flag_keeps_source_features_and_colour_bands(key):
    (paper,*colours,ink),report=prepare(key)
    assert report['appliedStrength']>0 and not report['fallback']
    assert (report['sourceComponents'],report['sourceHoles'])==TOPOLOGY[key]
    source=report['source'];raw=(ROOT/source['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==source['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==source['git_blob_sha1']
    assert not np.any(ink&~paper)
    if key=='1f38c':
        assert report['colourNames']==['red']
        assert ndi.label(colours[0])[1]==2, 'Two independent Japanese sun discs'
    if key=='1f3f3_200d_1f308':
        assert report['colourNames']==['red','orange','yellow','green','blue','purple']
        assert len(set(map(tuple,report['rgbs'])))==6
        assert all(ndi.label(mask)[1]==1 for mask in colours)
        centroids=[ndi.center_of_mass(mask)[0] for mask in colours]
        assert centroids==sorted(centroids), 'Rainbow bands keep their vertical order'
    if key=='1f3f3_200d_26a7':
        assert report['colourNames']==['blue','pink','white']
        assert [ndi.label(mask)[1] for mask in colours]==[2,2,1]
        assert tuple(report['rgbs'][-1])==(255,255,255)
    if key=='1f3f4_200d_2620':
        assert not colours
        assert ndi.label(ink)[1]==4 and ndi.label(paper&~ink)[1]==4
