"""Every asset URL the pages use carries a hash of the file's contents, so
that browsers fetch a file again exactly when it has changed."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

import version_assets  # noqa: E402


def test_asset_urls_are_versioned_with_current_hashes():
    # If this fails, run: uv run tools/version_assets.py
    assert version_assets.stale() == []


def test_a_changed_file_gets_a_new_version(tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("one")
    first = version_assets.digest(path)
    path.write_text("two")
    assert version_assets.digest(path) != first


def test_versioning_replaces_an_old_version():
    text = 'href="style.css?v=0123456789"'
    assert version_assets.versioned(text, "style.css", "abcdef1234") == 'href="style.css?v=abcdef1234"'
    assert version_assets.versioned('href="style.css"', "style.css", "abcdef1234") == 'href="style.css?v=abcdef1234"'
