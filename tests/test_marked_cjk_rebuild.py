"""Rebuild both CJK companion kinds without a cache or production writes."""
import json
import sys

from test_font_scripts import ROOT


def test_marked_cjk_fresh_builds_reproduce_both_source_kinds(tmp_path,monkeypatch):
    sys.path.insert(0,str(ROOT/'tools/font'))
    import build_marked_cjk_variants as builder
    entries=builder.read_manifest(ROOT/'js/marked-cjk-variant-manifest.js')['fonts']
    chosen=[next(e for e in entries if e['baseVariantFamily']==family)
            for family in ['Dad CJK Variants','Dad Script 8df1be125651']]
    def link(relative):
        target=tmp_path/relative;target.parent.mkdir(parents=True,exist_ok=True)
        target.symlink_to(ROOT/relative)
    for path in ['js/font-manifest.js','js/cjk-variant-manifest.js','assets/fonts/dad-lettering-unicode.woff2','tools/font/math_unicode_marks.py']:
        link(path)
    for entry in chosen:link(entry['source'])
    link('data/unicode')
    (tmp_path/'output/font-review').mkdir(parents=True)
    monkeypatch.setattr(builder,'ROOT',tmp_path)
    monkeypatch.setattr(builder,'DONOR',tmp_path/'assets/fonts/dad-lettering-unicode.woff2')
    monkeypatch.setattr(builder,'MANIFEST',tmp_path/'js/no-cache.js')
    for expected in chosen:
        [actual]=builder.build(only=expected['baseVariantFamily'])
        assert actual==expected
        assert (tmp_path/actual['file']).read_bytes()==(ROOT/expected['file']).read_bytes()
