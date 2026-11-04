"""Scoped catalog proofs reuse work, never mutable evidence or glyph assertions."""
import json
import os
from pathlib import Path
import pytest
import font_baseline_checks as checks
from test_marked_catalog_lineage import marked_case
from test_dense_baseline_checks import dense_fixture


def test_batch_authenticates_once_but_compares_every_glyph(marked_case,monkeypatch):
    root,base,marked,before,after=marked_case
    counts={'parent':0,'manifest':0,'variation':0}
    original=checks._authenticate_catalog_dense_parent
    def parent(*args):counts['parent']+=1;return original(*args)
    monkeypatch.setattr(checks,'_authenticate_catalog_dense_parent',parent)
    read=Path.read_text
    def text(path,*args,**kwargs):
        if path.name=='font-manifest.js':counts['manifest']+=1
        return read(path,*args,**kwargs)
    monkeypatch.setattr(Path,'read_text',text)
    import native_variations
    variation=native_variations.variation_ranges
    def ranges(font):counts['variation']+=1;return variation(font)
    monkeypatch.setattr(native_variations,'variation_ranges',ranges)
    with checks.catalog_evidence_batch():
        for _ in range(12):checks.assert_drawing_equal_or_optical(before,after,marked['file'],72)
        wrong=dict(after,path=after['path']+'M0 0L1 1')
        with pytest.raises(AssertionError):checks.assert_drawing_equal_or_optical(before,wrong,marked['file'],72)
    assert counts['parent']==1 and counts['manifest']==1
    # Complete parent proof also reads variation data: repeated glyph calls
    # must add no further variation scans after their first call.
    with checks.catalog_evidence_batch():
        checks.assert_drawing_equal_or_optical(before,after,marked['file'],72)
        first=counts['variation']
        for _ in range(12):checks.assert_drawing_equal_or_optical(before,after,marked['file'],72)
        assert counts['variation']==first


@pytest.mark.parametrize('target',['manifest','donor','raw','cache','report','marked'])
def test_batch_rejects_same_size_restored_mtime_edits(marked_case,target):
    root,base,marked,before,after=marked_case
    import dense_native_adapter as dense
    report=json.loads((root/base['denseTreatment']['report']).read_text())
    key=report['records'][0]['cacheKey']
    path={'manifest':root/'js/marked-cjk-variant-manifest.js','donor':root/marked['markSource'],'raw':root/base['source'],'cache':dense.CACHE/key[:2]/(key+'.json'),'report':root/base['denseTreatment']['report'],'marked':root/marked['file']}[target]
    original=path.read_bytes();stat=path.stat()
    try:
        with pytest.raises(AssertionError,match='Evidence changed'):
            with checks.catalog_evidence_batch():
                checks.assert_drawing_equal_or_optical(before,after,marked['file'],72)
                # Same bytes, size and mtime: ctime still proves mutable evidence.
                path.write_bytes(original);os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
    finally:path.write_bytes(original)


def test_batch_rejects_in_memory_metadata_change(marked_case):
    root,base,marked,before,after=marked_case
    with pytest.raises(AssertionError,match='metadata changed'):
        with checks.catalog_evidence_batch():
            bases=checks.catalog_bases()
            checks.marked_catalog_context(marked['file'],bases)
            bases[0]['family']='tampered'


def test_decoded_cache_rejects_restored_mtime_replacement(tmp_path,monkeypatch):
    monkeypatch.setattr(checks,'TTFont',lambda value:Path(value).read_bytes())
    path=tmp_path/'value';path.write_bytes(b'first');stat=path.stat();first=checks.evidence_identity(path)
    assert checks.evidence_font(path)==b'first'
    other=tmp_path/'replacement';other.write_bytes(b'other');os.utime(other,ns=(stat.st_atime_ns,stat.st_mtime_ns));other.replace(path)
    assert checks.evidence_identity(path)!=first
    assert checks.evidence_font(path)==b'other'


def test_batch_dependency_work_does_not_scale_with_glyph_repetitions(marked_case,monkeypatch):
    root,base,marked,before,after=marked_case
    calls=0;original=checks.evidence_identity
    def identity(path):
        nonlocal calls
        calls+=1;return original(path)
    monkeypatch.setattr(checks,'evidence_identity',identity)
    with checks.catalog_evidence_batch():
        checks.assert_drawing_equal_or_optical(before,after,marked['file'],72)
        first=calls
        for _ in range(1000):checks.assert_drawing_equal_or_optical(before,after,marked['file'],72)
        assert calls==first,'Per-glyph checks must not rescan dependency identities'


def test_batch_rejects_optional_manifest_creation(tmp_path):
    path=tmp_path/'optional.json'
    with pytest.raises(AssertionError,match='Evidence changed'):
        with checks.catalog_evidence_batch():
            checks.watch_evidence(path,required=False)
            path.write_text('{}')


def test_batch_rejects_changed_live_kernel_settings(marked_case):
    import dense_native_adapter as dense
    root,base,marked,before,after=marked_case
    original=dense.SETTINGS['resolution']
    try:
        with pytest.raises(AssertionError,match='metadata changed'):
            with checks.catalog_evidence_batch():
                checks.assert_drawing_equal_or_optical(before,after,marked['file'],72)
                dense.SETTINGS['resolution']=original+1
    finally:dense.SETTINGS['resolution']=original


@pytest.mark.parametrize('field',['family','markSourceSha256'])
def test_batch_rejects_returned_marked_metadata_mutation(marked_case,field):
    root,base,marked,before,after=marked_case
    with pytest.raises(AssertionError,match='metadata changed'):
        with checks.catalog_evidence_batch():
            context=checks.marked_catalog_context(marked['file'],checks.catalog_bases())
            context[0][field]='tampered'


def test_batch_rejects_parsed_manifest_mutation(tmp_path):
    path=tmp_path/'manifest.js';path.write_text('export default {"fonts":[]};\n')
    with pytest.raises(AssertionError,match='metadata changed'):
        with checks.catalog_evidence_batch():checks.catalog_manifest(path)['fonts'].append({'fake':True})
