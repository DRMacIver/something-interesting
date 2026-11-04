"""Qualification input reuse preserves the old parser, never prepared outputs."""
import hashlib
import os
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
import emoji_sequences as sequences


@pytest.fixture(autouse=True)
def empty_input_caches():
    sequences._qualification_input.cache_clear();sequences._qualification_index.cache_clear()
    yield
    sequences._qualification_input.cache_clear();sequences._qualification_index.cache_clear()


def source(root,text):
    path=root/'data/unicode/18.0.0/emoji/emoji-test.txt';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text);return path


def old_decoded_rows(path):
    # Decode exactly as the original function did, once for the entire pass.
    rows=[]
    for line in path.read_text().splitlines():
        fields=line.split('#')[0].strip().split(';')
        if len(fields)<2:continue
        rows.append(''.join(chr(int(cp,16)) for cp in fields[0].split()))
    return rows


def test_every_real_canonical_form_matches_original_filter_in_file_order():
    rows=old_decoded_rows(ROOT/'data/unicode/18.0.0/emoji/emoji-test.txt')
    for canonical in dict.fromkeys(rows):
        expected=[text for text in rows if text.replace('\ufe0f','')==canonical.replace('\ufe0f','')]
        assert sequences.qualified_forms(ROOT,canonical)==expected
    assert sequences._qualification_input.cache_info().misses==1
    assert sequences._qualification_index.cache_info().misses==1


def test_duplicate_order_and_qualification_statuses_are_preserved(tmp_path):
    source(tmp_path,'# comment\n263A FE0F ; fully-qualified # x\n263A ; unqualified # y\n263A FE0F ; duplicate # z\n')
    assert sequences.qualified_forms(tmp_path,'☺')==['☺️','☺','☺️']
    assert sequences.qualified_forms(tmp_path,'☺️')==['☺️','☺','☺️']
    with pytest.raises(AssertionError):sequences.qualified_forms(tmp_path,'☺\ufe0e')


def test_each_caller_gets_a_fresh_list_and_index_is_immutable(tmp_path):
    path=source(tmp_path,'0041 ; fully-qualified # A\n')
    value=sequences.qualified_forms(tmp_path,'A');value.append('poison');value.clear()
    assert sequences.qualified_forms(tmp_path,'A')==['A']
    raw=path.read_bytes();model=sequences._qualification_index(hashlib.sha256(raw).hexdigest(),raw)
    with pytest.raises(TypeError):model['A']=('poison',)
    assert model['A']==('A',)


def test_same_size_inplace_change_with_restored_mtime_invalidates(tmp_path):
    path=source(tmp_path,'0041 ; fully-qualified # A\n');before=path.stat()
    assert sequences.qualified_forms(tmp_path,'A')==['A']
    path.write_text('0042 ; fully-qualified # B\n');os.utime(path,ns=(before.st_atime_ns,before.st_mtime_ns))
    assert path.stat().st_size==before.st_size and path.stat().st_mtime_ns==before.st_mtime_ns
    assert sequences.qualified_forms(tmp_path,'B')==['B']
    with pytest.raises(AssertionError):sequences.qualified_forms(tmp_path,'A')
    assert sequences._qualification_input.cache_info().misses==2


def test_atomic_replacement_with_preserved_size_and_mtime_invalidates(tmp_path):
    path=source(tmp_path,'0041 ; fully-qualified # A\n');before=path.stat()
    assert sequences.qualified_forms(tmp_path,'A')==['A']
    replacement=tmp_path/'replacement';replacement.write_text('0042 ; fully-qualified # B\n');os.utime(replacement,ns=(before.st_atime_ns,before.st_mtime_ns));replacement.replace(path)
    assert path.stat().st_ino!=before.st_ino
    assert sequences.qualified_forms(tmp_path,'B')==['B']
    with pytest.raises(AssertionError):sequences.qualified_forms(tmp_path,'A')


def test_separate_input_roots_never_share_different_content(tmp_path):
    a,b=tmp_path/'a',tmp_path/'b';source(a,'0041 ; fully-qualified # A\n');source(b,'0042 ; fully-qualified # B\n')
    assert sequences.qualified_forms(a,'A')==['A'] and sequences.qualified_forms(b,'B')==['B']
    with pytest.raises(AssertionError):sequences.qualified_forms(b,'A')


def test_content_digest_is_part_of_decoded_index_identity():
    raw=b'0041 ; fully-qualified # A\n'
    with pytest.raises(AssertionError):sequences._qualification_index('0'*64,raw)


def test_file_change_during_input_read_is_rejected_then_reloaded(tmp_path,monkeypatch):
    path=source(tmp_path,'0041 ; fully-qualified # A\n').resolve();read=Path.read_bytes;changed=False
    def racing_read(candidate):
        nonlocal changed
        raw=read(candidate)
        if candidate==path and not changed:
            changed=True;candidate.write_text('0042 ; fully-qualified # B\n')
        return raw
    monkeypatch.setattr(Path,'read_bytes',racing_read)
    with pytest.raises(RuntimeError,match='changed while being read'):sequences.qualified_forms(tmp_path,'A')
    assert sequences.qualified_forms(tmp_path,'B')==['B']


def test_file_change_during_cached_lookup_is_rejected(tmp_path,monkeypatch):
    path=source(tmp_path,'0041 ; fully-qualified # A\n')
    assert sequences.qualified_forms(tmp_path,'A')==['A']
    lookup=sequences._qualification_index
    def racing_lookup(digest,raw):
        result=lookup(digest,raw)
        path.write_text('0042 ; fully-qualified # B\n')
        return result
    monkeypatch.setattr(sequences,'_qualification_index',racing_lookup)
    with pytest.raises(RuntimeError,match='changed during lookup'):
        sequences.qualified_forms(tmp_path,'A')
    monkeypatch.setattr(sequences,'_qualification_index',lookup)
    assert sequences.qualified_forms(tmp_path,'B')==['B']
