"""Pen finish changes must not merge features or destroy enclosed ink shapes."""
import sys
from pathlib import Path
import numpy as np
import pytest
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/font'))
from pen_translate import Settings, ink_mask, same_features, translate


def specimen():
    image = Image.new('L', (128, 128), 255)
    draw = ImageDraw.Draw(image)
    draw.ellipse((12, 12, 116, 116), outline=0, width=4)
    draw.ellipse((43, 44, 51, 57), fill=0)
    draw.ellipse((77, 44, 85, 57), fill=0)
    draw.arc((38, 55, 90, 95), 10, 170, fill=0, width=4)
    return ink_mask(image)


def test_reproducible_nontrivial_and_non_destructive():
    mask = specimen()
    original = mask.copy()
    first, report = translate(mask, Settings(seed=3))
    second, again = translate(mask, Settings(seed=3))
    assert first.tobytes() == second.tobytes() and report == again
    assert np.array_equal(mask, original)
    pad = report['padding']
    baseline = np.pad(mask, pad)
    assert report['appliedStrength'] > 0
    assert not np.array_equal(np.asarray(first) < 128, baseline)
    assert same_features(baseline, np.asarray(first) < 128)
    assert ((np.asarray(first) > 0) & (np.asarray(first) < 255)).any()


@pytest.mark.parametrize('strength', [.5, 1, 1.7])
@pytest.mark.parametrize('seed', [1, 7, 31])
def test_features_and_margins_survive(strength, seed):
    mask = specimen()
    result, report = translate(mask, Settings(strength=strength, seed=seed))
    actual = np.asarray(result)
    assert same_features(np.pad(mask, report['padding']), actual < 128)
    assert (actual[0] == 255).all() and (actual[-1] == 255).all()
    assert (actual[:, 0] == 255).all() and (actual[:, -1] == 255).all()


def test_feature_check_rejects_lost_eye_and_broken_head():
    original = specimen()
    missing = original.copy(); missing[40:61, 40:55] = False
    assert not same_features(original, missing)
    broken = original.copy(); broken[:30, 62:67] = False
    assert not same_features(original, broken)


def test_zero_strength_preserves_mask_exactly():
    mask = specimen()
    result, report = translate(mask, Settings(strength=0))
    assert np.array_equal(np.asarray(result) < 128, np.pad(mask, report['padding']))
    assert not report['fallback']


def test_transparent_black_background_is_not_ink():
    rgba = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(rgba); draw.rectangle((4, 4, 10, 10), fill=(0, 0, 0, 255))
    assert ink_mask(rgba).sum() == 49


@pytest.mark.parametrize('strength', [-1, 3, float('nan')])
def test_invalid_strength_is_rejected(strength):
    with pytest.raises(ValueError):
        translate(specimen(), Settings(strength=strength))


def test_fine_diagonal_counters_survive_with_reduced_boundary_smoothing():
    image=Image.new('L',(96,96),255);draw=ImageDraw.Draw(image)
    draw.rectangle((5,5,90,90),outline=0,width=2)
    for offset in range(-60,61,3):draw.line((5,5+offset,90,90+offset),fill=0,width=1)
    for x in range(15,90,19):draw.line((x,5,x,90),fill=0,width=1)
    mask=np.asarray(image)<128;original=mask.copy()
    settings=dict(strength=1.7,seed=21,pressure=.04,taper=0,bend=.001)
    _,legacy=translate(mask,Settings(**settings))
    assert legacy['fallback']
    image,report=translate(mask,Settings(**settings,boundary_blur=.2))
    assert report['appliedStrength']>0 and not report['fallback']
    baseline=np.pad(mask,report['padding']);actual=np.asarray(image)<128
    assert same_features(baseline,actual)
    assert not np.array_equal(np.uint8(~baseline)*255,np.asarray(image))
    assert ((np.asarray(image)>0)&(np.asarray(image)<255)).any()
    assert np.array_equal(mask,original)


@pytest.mark.parametrize('blur',[-1,float('nan'),float('inf')])
def test_invalid_boundary_blur_is_rejected(blur):
    mask=np.zeros((16,16),dtype=bool);mask[4:12,4:12]=True
    with pytest.raises(ValueError):translate(mask,Settings(boundary_blur=blur))
