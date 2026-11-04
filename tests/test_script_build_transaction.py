"""A failed source rebuild must not leave mixed browser font assets."""
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
import build_scripts


def test_failure_restores_font_shards_and_manifest(tmp_path,monkeypatch):
    fonts=tmp_path/'assets/fonts/scripts';fonts.mkdir(parents=True)
    manifest=tmp_path/'js/font-manifest.js';manifest.parent.mkdir()
    (fonts/'old.woff2').write_bytes(b'accepted original font');manifest.write_bytes(b'accepted manifest')
    monkeypatch.setattr(build_scripts,'ROOT',tmp_path);monkeypatch.setattr(build_scripts,'OUT',fonts);monkeypatch.setattr(build_scripts,'MANIFEST',manifest)
    def fail():
        (fonts/'old.woff2').write_bytes(b'incomplete replacement')
        (fonts/'new.woff2').write_bytes(b'incomplete new shard')
        manifest.write_bytes(b'incomplete manifest')
        raise ValueError('source failed')
    monkeypatch.setattr(build_scripts,'_build',fail)
    with pytest.raises(ValueError,match='source failed'):build_scripts.build()
    assert (fonts/'old.woff2').read_bytes()==b'accepted original font'
    assert not (fonts/'new.woff2').exists()
    assert manifest.read_bytes()==b'accepted manifest'
