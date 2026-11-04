"""The private fast guard must preserve exact reference decisions/cache bytes."""
import io
import json
from pathlib import Path
import sys
import numpy as np
import pytest
from scipy import ndimage as ndi
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
import fast_supplemental_validation as fast
import supplemental_adapter as adapter
import supplemental_pressure as pressure_module


def outcome(fn,a,b):
    try:return ('pass',fn(a,b))
    except ValueError as error:return ('error',str(error))


def test_exact_decisions_arrays_and_first_errors_on_thresholds_and_damage():
    fast.assert_reference();cases=[]
    base=np.zeros((64,160),bool);base[10:20,20:120]=True
    for count in (799,800,1000,1200,1201):
        changed=np.zeros_like(base);flat=np.argwhere(np.ones((13,100),bool))[:count]
        changed[flat[:,0]+10,flat[:,1]+20]=True;cases.append((base,changed))
    ring=np.zeros((64,64),bool);ring[10:50,10:50]=True;ring[20:28,20:28]=False
    for keep in (64,48,47,0):
        changed=ring.copy();changed[20:28,20:28]=True
        points=np.argwhere(np.ones((8,8),bool))[:keep]
        changed[points[:,0]+20,points[:,1]+20]=False;cases.append((ring,changed))
    dots=ring.copy();dots[2:5,2:5]=True;cases.append((dots,ring))
    rng=np.random.default_rng(1847)
    for _ in range(100):
        old=ndi.gaussian_filter(rng.random((48,64)),.8)>.57
        changed=old.copy();y,x=rng.integers(0,48),rng.integers(0,64);changed[y,x]=~changed[y,x]
        cases.extend([(old,old),(old,changed),(old,ndi.binary_dilation(old))])
    cases.append((np.zeros((0,0),bool),np.zeros((0,0),bool)))
    for a,b in cases:assert outcome(fast.REFERENCE,a,b)==outcome(fast.validate_reconstruction,a,b)


@pytest.mark.parametrize('number,text',[(23,'ἄβ'),(20,'لا'),(45,'𒀀𒀇')])
def test_actual_glyph_font_and_cache_bytes_are_identical(tmp_path,monkeypatch,number,text):
    rows=json.loads((ROOT/'docs/source-style-review.json').read_text())['sources'];row=next(r for r in rows if r['number']==number)
    source=ROOT/'output/font-review/supplemental-production-baselines'/Path(row['fonts'][0]['file']).name
    if not source.exists():source=ROOT/row['fonts'][0]['file']
    native=TTFont(source,recalcTimestamp=False);options=subset.Options();options.layout_features=['*'];sub=subset.Subsetter(options=options);sub.populate(text=text);sub.subset(native)
    native.flavor=None;stream=io.BytesIO();native.save(stream);data=stream.getvalue()
    monkeypatch.setattr(adapter,'ROOT',tmp_path);monkeypatch.setattr(adapter,'baseline',lambda source:None)
    monkeypatch.setattr(adapter,'CACHE',tmp_path/'reference-cache')
    monkeypatch.setattr(adapter,'validate_reconstruction',fast.REFERENCE)
    monkeypatch.setattr(pressure_module,'validate_reconstruction',fast.REFERENCE)
    reference=TTFont(io.BytesIO(data),recalcTimestamp=False);recipe=adapter.recipe_hash(row['source']);report=adapter.apply(reference,row['source'])
    records=(tmp_path/report['report']).read_bytes()
    reference_bytes=io.BytesIO();reference.save(reference_bytes)
    monkeypatch.setattr(adapter,'CACHE',tmp_path/'fast-cache');backend=fast.install()
    candidate=TTFont(io.BytesIO(data),recalcTimestamp=False);new_report=adapter.apply(candidate,row['source']);candidate_bytes=io.BytesIO();candidate.save(candidate_bytes)
    assert adapter.recipe_hash(row['source'])==recipe
    assert new_report==report
    assert (tmp_path/new_report['report']).read_bytes()==records
    assert candidate_bytes.getvalue()==reference_bytes.getvalue()
    old_files={p.name:p.read_bytes() for p in (tmp_path/'reference-cache').glob('*')}
    new_files={p.name:p.read_bytes() for p in (tmp_path/'fast-cache').glob('*')}
    assert new_files==old_files
    assert backend['referenceSha256']==fast.REFERENCE_SHA256


def test_unknown_reference_is_not_silently_optimized(monkeypatch):
    monkeypatch.setattr(fast,'REFERENCE_SHA256','unreviewed')
    with pytest.raises(RuntimeError,match='reference changed'):fast.assert_reference()
