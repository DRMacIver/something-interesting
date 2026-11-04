"""Dense provenance checks prove source geometry, cache recipe and output ink."""
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil

import pytest
from fontTools.ttLib import TTFont

import font_baseline_checks as checks
import dense_native_adapter as dense
from test_dense_skeleton import fixture_font


@pytest.fixture(scope='module',params=[False,True],ids=['named','post3-native-aliases'])
def dense_fixture(tmp_path_factory,request):
    root=tmp_path_factory.mktemp('dense-baseline')
    source=root/'native/Jigmo.ttf';source.parent.mkdir(parents=True);source.write_bytes(fixture_font())
    font=TTFont(io.BytesIO(source.read_bytes()),recalcTimestamp=False)
    if request.param:
        # A private closure glyph keeps its live source name before serialization,
        # while post3 gives the frozen/output files generic names by glyph ID.
        font['glyf']['original.native.part']=copy.deepcopy(font['glyf']['H'])
        font['hmtx']['original.native.part']=font['hmtx']['H']
        font.setGlyphOrder(list(font['glyf'].glyphs))
        font['post'].formatType=3
        font.save(source)
    path=root/'assets/fonts/scripts/fixture.woff2';path.parent.mkdir(parents=True)
    font.flavor='woff2';font.save(path)
    frozen=root/'output/font-review/supplemental-production-baselines'/path.name
    frozen.parent.mkdir(parents=True);shutil.copyfile(path,frozen)
    before=dict(family='DenseTest',file=str(path.relative_to(root)),source=str(source.relative_to(root)),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,recipe=1,ranges=[[72,72]],nativeVariations={},style='native fixture')
    with pytest.MonkeyPatch.context() as monkey:
        monkey.setattr(dense,'ROOT',root)
        result=dense.apply(font,source,cache_dir=root/'cache',report_dir=root/'output/font-review/dense-production')
    font.flavor='woff2';font.save(path)
    after=dict(before,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,recipe='1:dense-native-pen:'+dense.recipe_hash(source),denseTreatment=result)
    return root,before,after


def test_dense_baseline_proves_source_cache_and_actual_output(dense_fixture,monkeypatch):
    root,before,after=dense_fixture
    monkeypatch.setattr(checks,'ROOT',root);monkeypatch.setattr(dense,'CACHE',root/'cache')
    assert checks.reviewed_later_change(before,after)


def test_dense_baseline_rejects_stale_kernel_and_unreviewed_source(dense_fixture,monkeypatch):
    root,before,after=dense_fixture
    monkeypatch.setattr(checks,'ROOT',root);monkeypatch.setattr(dense,'CACHE',root/'cache')
    stale=copy.deepcopy(after);stale['denseTreatment']['recipeSha256']='0'*64
    with pytest.raises(AssertionError):checks.reviewed_later_change(before,stale)
    unknown=copy.deepcopy(after);unknown['denseTreatment']['sourceProfile']='Unreviewed.ttf'
    with pytest.raises(AssertionError):checks.reviewed_later_change(before,unknown)
