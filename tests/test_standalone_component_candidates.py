"""Preserve lettering, source topology and meaning in standalone candidates."""
import json
import sys

import numpy as np
from fontTools.ttLib import TTFont
from scipy import ndimage as ndi
from test_font_scripts import ROOT

sys.path.insert(0,str(ROOT/'tools/font'))
from emoji_standalone_components import POINTS, prepare, monochrome, sources
from emoji_licensed import raster
from svg_counter_review import review_counters


def test_existing_hand_lettered_capitals_are_reused_for_all_regional_indicators():
    _,_,_,dad,lettering,_ = sources()
    for cp in range(0x1f1e6,0x1f200):
        key = f'{cp:x}'
        (_,ink), report = prepare(key)
        expected = raster(lettering,dad.getBestCmap()[ord('A')+cp-0x1f1e6],512)
        assert np.array_equal(ink,expected)
        assert np.array_equal(monochrome(key),expected)
        assert report['treatment'].startswith('reuse existing hand-lettered capital')


def test_skin_components_retain_all_native_hatching_with_distinct_sampled_fills():
    tones = json.loads((ROOT/'output/imagegen/emoji-production/skin-palette-source.json').read_text())['skinTones']
    for cp in range(0x1f3fb,0x1f400):
        (paper,fill,ink), report = prepare(f'{cp:x}')
        assert report['rgbs'] == [tones[cp-0x1f3fb]]
        assert np.array_equal(fill,paper)
        assert np.array_equal(ink,monochrome(f'{cp:x}'))
        assert report['appliedStrength'] > 0 and not report['fallback']


def test_red_hair_colour_is_inset_and_preserves_dashed_component_frame():
    (paper,fill,ink), report = prepare('1f9b0')
    fallback = monochrome('1f9b0')
    assert fill.sum() > 1000 and not (fill & ~fallback).any()
    assert np.array_equal(ink|fill,fallback)
    assert not (ink&fill).any()
    # All smaller ink components, including every frame dash, remain black.
    labels,count = ndi.label(fallback)
    sizes = np.bincount(labels.ravel());sizes[0]=0
    assert not (fill & ((labels!=0)&(labels!=sizes.argmax()))).any()
    assert report['monochromeFallback'] == 'original solid hair'


def test_all_candidate_fallback_and_display_contours_preserve_source_counters():
    font = TTFont(ROOT/'output/font-review/pen-translation/standalone-components-candidate.woff2')
    for cp in POINTS:
        key=f'{cp:x}'
        (paper,*_,ink),_ = prepare(key)
        ys,xs=np.nonzero(paper)
        transform=xs.min(),ys.min(),760/max(np.ptp(xs)+1,np.ptp(ys)+1)
        name='standalone-components.'+key
        review_counters(monochrome(key),transform,font['glyf'][name])
        last=font['COLR'].ColorLayers[name][-1].name
        review_counters(ink,transform,font['glyf'][last])
