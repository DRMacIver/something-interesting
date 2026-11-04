"""Pinned archive restoration must not admit corrupt or redirected sources."""
import hashlib
import importlib.util
import io
import tarfile
import zipfile
import stat
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('font_fetch', Path(__file__).resolve().parents[1] / 'tools/font/fetch_sources.py')
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)


@pytest.fixture(params=['tar','zip'])
def archive_source(tmp_path, monkeypatch, request):
    monkeypatch.setattr(fetch, 'ROOT', tmp_path)
    raw = b'known source glyph'
    path = tmp_path / ('build/unicode-sources/test/source.'+request.param)
    path.parent.mkdir(parents=True)
    if request.param == 'zip':
        with zipfile.ZipFile(path,'w') as archive:
            archive.writestr('upstream/glyph.svg',raw)
            link = zipfile.ZipInfo('upstream/link.svg')
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(link,'/outside')
    else:
        with tarfile.open(path, 'w') as archive:
            member = tarfile.TarInfo('upstream/glyph.svg')
            member.size = len(raw)
            archive.addfile(member, io.BytesIO(raw))
            link = tarfile.TarInfo('upstream/link.svg')
            link.type = tarfile.SYMTYPE
            link.linkname = '/outside'
            archive.addfile(link)
    entry = dict(path='build/unicode-sources/test/glyph.svg', archive_member='upstream/glyph.svg',
                 sha256=hashlib.sha256(raw).hexdigest(),
                 git_blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
    return dict(archive=dict(path=str(path.relative_to(tmp_path)),
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest()), files=[entry])


def test_restore_exact_verified_member(archive_source, tmp_path):
    fetch.restore_archive(archive_source)
    assert (tmp_path / archive_source['files'][0]['path']).read_bytes() == b'known source glyph'


def test_restore_bundled_licence(archive_source, tmp_path):
    archive_source['files'][0]['path']='assets/fonts/licenses/Test-OFL.txt'
    fetch.restore_archive(archive_source)
    assert (tmp_path / archive_source['files'][0]['path']).read_bytes() == b'known source glyph'


@pytest.mark.parametrize('mutation,error', [
    ({'sha256': '0'*64}, 'hash mismatch'),
    ({'git_blob_sha1': '0'*40}, 'hash mismatch'),
    ({'path': 'outside.svg'}, 'target path'),
    ({'archive_member': 'upstream/link.svg'}, 'regular source files'),
])
def test_reject_unverified_or_redirected_member(archive_source, tmp_path, mutation, error):
    archive_source['files'][0].update(mutation)
    with pytest.raises(ValueError, match=error):
        fetch.restore_archive(archive_source)
    assert not (tmp_path / archive_source['files'][0]['path']).exists()
