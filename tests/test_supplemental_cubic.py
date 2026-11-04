"""Cubic experiments must keep variant identity and reject missing input."""
import sys
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from supplemental_cubic import candidate
from supplemental_pressure import shaped


def test_cubic_pressure_preserves_native_math_variants_and_attachment(tmp_path):
    source=ROOT/'assets/fonts/dad-math-variants.woff2'
    output=tmp_path/'candidate.otf';text='ℋℋ\ufe01ℐℐ\ufe01≈≈\ufe00'
    report=candidate(source,text,output)
    a,b=TTFont(source),TTFont(output)
    assert report['shapingUnchanged']
    assert any(r['status']=='candidate' for r in report['glyphs'])
    assert shaped(a,text)==shaped(b,text)
    assert shaped(b,'ℋ')[0][0]!=shaped(b,'ℋ\ufe01')[0][0]
    for tag in ('GPOS','GSUB','GDEF','hmtx'):
        if tag in a:assert a[tag].compile(a)==b[tag].compile(b)
    assert a['head'].unitsPerEm==b['head'].unitsPerEm
    assert b['name'].getDebugName(1)=='Dad Cubic Pressure Experiment'


def test_cubic_candidate_rejects_missing_native_glyph(tmp_path):
    with pytest.raises(ValueError,match='Missing native glyph'):
        candidate(ROOT/'assets/fonts/dad-math-variants.woff2','\U0010ffff',tmp_path/'bad.otf')
    assert not (tmp_path/'bad.otf').exists()
