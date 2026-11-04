"""Pen adaptation must keep mathematical alphabet weight distinctions visible."""
import json
from pathlib import Path
import sys

import pytest
from native_sfnt_loader import evidence_ttfont as TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from supplemental_pressure import raster


def test_math_bold_keeps_more_ink_than_its_native_normal_partner():
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ')[1].rstrip(';\n'))
    entry=next(e for e in manifest['fonts'] if e['source'].endswith('/NotoSansMath-Regular.ttf'))
    font=TTFont(ROOT/entry['file']);source=TTFont(ROOT/entry['source'])
    cmap=font.getBestCmap();native=source.getBestCmap()
    checked=0
    # Match the same mathematical family, slant and letter. Different outlines
    # alone could hide a loss of the bold distinction at the same em scale.
    pairs=[(0x1d434,0x1d468),(0x1d608,0x1d63c),(0x1d5a0,0x1d5d4)]
    for start,bold_start in pairs:
        for offset in (0,2,12,22):
            normal,bold=start+offset,bold_start+offset
            if not {normal,bold}<=cmap.keys() or not {normal,bold}<=native.keys():continue
            a=raster(font,cmap[normal],384)[0].sum();b=raster(font,cmap[bold],384)[0].sum()
            old_a=raster(source,native[normal],384)[0].sum();old_b=raster(source,native[bold],384)[0].sum()
            assert old_b>old_a*1.05,'Native fixture must express a real weight difference'
            assert b>a*1.05,(hex(normal),hex(bold),a,b)
            assert b/a>=.85*old_b/old_a,(hex(normal),hex(bold),b/a,old_b/old_a)
            assert cmap[normal]!=cmap[bold]
            checked+=1
    assert checked>=8
