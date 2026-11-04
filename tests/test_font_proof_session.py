"""Identical-state proof reuse retains complete dependency and runtime checks."""
import builtins
import copy
import io
import os
from pathlib import Path
import threading
import pytest
import font_baseline_checks as checks
import font_proof_session as session


@pytest.fixture
def proof_case(tmp_path,monkeypatch):
    monkeypatch.setattr(checks,'ROOT',tmp_path);session._PROOFS.clear()
    names=['font','raw','archive','report','cache','policy','docs/unicode-style-dispositions.json','output/font-review/supplemental-production-baselines/font','output/font-review/supplemental-production-baselines/font.json']
    for name in names:
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'good')
    before=dict(file='font',source='raw',sources=[dict(archive='archive')])
    after=dict(before,supplementalTreatment={'report':'report'},styleReview={'record':'test'})
    calls=[]
    @session.reuse_reviewed_proof
    def proof(a,b):
        calls.append(1)
        for name in names:assert (tmp_path/name).read_bytes()==b'good',name
        return True
    return tmp_path,names,before,after,calls,proof


def test_identical_proof_reuses_only_success_and_replays_batch_dependencies(proof_case):
    root,names,before,after,calls,proof=proof_case
    assert proof(before,after)
    with checks.catalog_evidence_batch():
        for _ in range(5):assert proof(before,after)
        deps=checks._BATCH.get()['dependencies']
        assert all((root/name).absolute() in deps for name in names)
    assert len(calls)==1


@pytest.mark.parametrize('name',['font','raw','archive','report','cache','policy','docs/unicode-style-dispositions.json','output/font-review/supplemental-production-baselines/font'])
def test_changed_dependency_never_reuses_success_even_with_restored_mtime(proof_case,name):
    root,names,before,after,calls,proof=proof_case;assert proof(before,after)
    path=root/name;stat=path.stat();path.write_bytes(b'baad');os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
    with pytest.raises(AssertionError):proof(before,after)
    assert len(calls)==2


def test_inode_replacement_and_identical_builder_rewrite_invalidate(proof_case):
    root,names,before,after,calls,proof=proof_case;assert proof(before,after)
    path=root/'font';stat=path.stat();other=root/'new';other.write_bytes(b'good');os.utime(other,ns=(stat.st_atime_ns,stat.st_mtime_ns));other.replace(path)
    assert proof(before,after) and len(calls)==2
    path.write_bytes(b'good');assert proof(before,after) and len(calls)==3


@pytest.mark.parametrize('module,name,value',[
    ('source_optics','SCALES',{'changed':1}),('dense_native_adapter','SETTINGS',{'changed':1}),
    ('dense_native_adapter','CACHE',Path('other-cache')),('source_preservation','POLICIES',{}),
    ('music_source_preservation','NAMED_GLYPHS',['changed']),('chemical_source_preservation','CODEPOINTS',[1]),
    ('chemical_source_preservation','REASON','changed'),('supplemental_adapter','ROOT',Path('other-root'))])
def test_live_runtime_constants_are_part_of_exact_proof_key(proof_case,monkeypatch,module,name,value):
    import importlib
    root,names,before,after,calls,proof=proof_case;assert proof(before,after)
    monkeypatch.setattr(importlib.import_module(module),name,value)
    assert proof(before,after) and len(calls)==2


def test_changed_arguments_and_missing_dependency_invalidate(proof_case):
    root,names,before,after,calls,proof=proof_case;assert proof(before,after)
    altered=dict(after,metadata='new');assert proof(before,altered) and len(calls)==2
    (root/'cache').unlink()
    with pytest.raises(FileNotFoundError):proof(before,altered)
    assert len(calls)==3


def test_failure_and_false_results_are_not_cached(proof_case):
    root,names,before,after,calls,proof=proof_case
    (root/'cache').write_bytes(b'baad')
    for _ in range(2):
        with pytest.raises(AssertionError):proof(before,after)
    assert len(calls)==2
    false_calls=[]
    @session.reuse_reviewed_proof
    def false(a,b):false_calls.append(1);return False
    assert false(before,after) is False and false(before,after) is False
    assert len(false_calls)==2


def test_read_recorder_restores_after_error_and_does_not_block_other_thread_writes(tmp_path):
    original_builtin,original_io=builtins.open,io.open
    with pytest.raises(AssertionError):
        with session.read_dependencies():
            with open(tmp_path/'forbidden','w'):pass
    assert builtins.open is original_builtin and io.open is original_io
    with session.read_dependencies() as deps:
        thread=threading.Thread(target=lambda:(tmp_path/'unrelated').write_text('allowed'));thread.start();thread.join()
        assert tmp_path/'unrelated' not in deps
    assert (tmp_path/'unrelated').read_text()=='allowed'


def test_mutation_after_cache_hit_is_still_rejected_by_enclosing_batch(proof_case):
    root,names,before,after,calls,proof=proof_case;assert proof(before,after)
    with pytest.raises(AssertionError,match='Evidence changed'):
        with checks.catalog_evidence_batch():
            assert proof(before,after)
            (root/'cache').write_bytes(b'good')


def test_nested_read_recorders_restore_and_proof_time_mutation_rejects(tmp_path):
    path=tmp_path/'read';path.write_bytes(b'good')
    with session.read_dependencies() as outer:
        with session.read_dependencies() as inner:
            assert path.read_bytes()==b'good'
        assert outer is inner and path.absolute() in outer


def test_proof_time_dependency_mutation_rejects_and_is_never_cached(proof_case):
    root,names,before,after,calls,proof=proof_case;path=root/'font'
    @session.reuse_reviewed_proof
    def changed(a,b):
        path.read_bytes();stat=path.stat();os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns+1));return True
    for _ in range(2):
        with pytest.raises(AssertionError,match='dependency changed'):changed(before,after)


def test_loaded_recipe_config_path_is_explicit_dependency(proof_case,monkeypatch):
    import supplemental_adapter as adapter
    root,names,before,after,calls,proof=proof_case;config=root/'recipe.json';config.write_text('{}')
    monkeypatch.setattr(adapter,'RECIPE_PATH',config)
    assert proof(before,after)
    config.write_text('{}')
    assert proof(before,after) and len(calls)==2


def test_proof_argument_mutation_rejects(proof_case):
    root,names,before,after,calls,proof=proof_case
    @session.reuse_reviewed_proof
    def changed(a,b):b['mutated']=True;return True
    with pytest.raises(AssertionError,match='arguments changed'):changed(before,after)


def test_mutation_between_hit_validation_and_dependency_replay_rejects(proof_case,monkeypatch):
    root,names,before,after,calls,proof=proof_case
    original=checks.watch_evidence;changed=False;active=False
    def watch(path,required=True):
        nonlocal changed
        if active and not changed and Path(path)==root/'font':
            changed=True;(root/'font').write_bytes(b'good')
        return original(path,required)
    monkeypatch.setattr(checks,'watch_evidence',watch)
    assert proof(before,after);active=True
    with pytest.raises(AssertionError,match='dependency changed during reuse'):proof(before,after)


def test_missing_explicit_loaded_recipe_config_rejects(proof_case,monkeypatch):
    import supplemental_adapter as adapter
    root,names,before,after,calls,proof=proof_case
    monkeypatch.setattr(adapter,'RECIPE_PATH',root/'missing-config.json')
    with pytest.raises(AssertionError,match='Missing native proof code/config'):proof(before,after)
    assert not calls


def test_dictionary_key_type_is_part_of_runtime_identity(proof_case,monkeypatch):
    import supplemental_cubic_adapter as adapter
    root,names,before,after,calls,proof=proof_case
    monkeypatch.setattr(adapter,'TYPED_KEYS',{1:'same'},raising=False)
    assert proof(before,after)
    adapter.TYPED_KEYS={'1':'same'}
    assert proof(before,after) and len(calls)==2


def test_delegated_callable_replacement_invalidates_proof(proof_case,monkeypatch):
    import dense_native_adapter as adapter
    root,names,before,after,calls,proof=proof_case
    assert proof(before,after)
    original=adapter.recipe_hash
    monkeypatch.setattr(adapter,'recipe_hash',lambda *args,**kwargs:original(*args,**kwargs))
    assert proof(before,after) and len(calls)==2
