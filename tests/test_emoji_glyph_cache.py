import json
import shutil
import sys
from pathlib import Path

from PIL import Image
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from emoji_glyph_cache import GlyphCache
import build_adventure_emoji as drawings
from build_emoji import build,prepared_font


def test_source_recipe_invalidation_and_corruption_recovery(tmp_path):
    cache=GlyphCache(tmp_path);calls=[]
    def compute():calls.append(1);return {'outlines':[1,2],'layers':[],'advance':700}
    a={'source':'first','recipe':'v1'}
    assert cache.prepare(a,compute)==cache.prepare(a,compute)
    assert (cache.hits,cache.misses)==(1,1)
    cache.prepare(dict(a,source='changed'),compute)
    cache.prepare(dict(a,recipe='v2'),compute)
    assert len(calls)==3
    key=cache.keys[0];(tmp_path/key[:2]/(key+'.json')).write_text('{"corrupt":true}')
    cache.prepare(a,compute);assert len(calls)==4


def test_editing_one_atlas_cell_reprepares_only_that_glyph(tmp_path,monkeypatch):
    original=drawings.ART;art=tmp_path/'assets/emoji-concepts';art.mkdir(parents=True)
    for name in {'sprite-sheet-v1.png',*[v[0] for v in drawings.REPLACEMENTS.values()]}:
        target=art/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original/name,target)
    monkeypatch.setattr(drawings,'ROOT',tmp_path);monkeypatch.setattr(drawings,'ART',art)
    cache=GlyphCache(tmp_path/'cache')
    before=[drawings.prepare_glyph(i,cp,cache)[0] for i,cp in enumerate(drawings.POINTS)]
    assert cache.misses==16
    for i,cp in enumerate(drawings.POINTS):drawings.prepare_glyph(i,cp,cache)
    assert (cache.hits,cache.misses)==(16,16)
    path=art/'sprite-sheet-v1.png';im=Image.open(path).convert('RGBA')
    im.putpixel((100,100),(0,0,0,255));im.save(path)
    after=[drawings.prepare_glyph(i,cp,cache)[0] for i,cp in enumerate(drawings.POINTS)]
    assert (cache.hits,cache.misses)==(31,17)
    assert before[1:]==after[1:]


def test_cold_and_warm_main_assembly_are_identical(tmp_path):
    cache=tmp_path/'cache';a=tmp_path/'cold';b=tmp_path/'warm'
    cold=build(a,cache);warm=build(b,cache)
    assert (cold['cacheHits'],cold['cacheMisses'])==(0,16)
    assert (warm['cacheHits'],warm['cacheMisses'])==(16,0)
    for name in ['assets/fonts/dad-emoji.woff2','assets/fonts/dad-emoji-ink.woff2','js/emoji-manifest.js']:
        assert (a/name).read_bytes()==(b/name).read_bytes(),name


def test_unmodified_legacy_glyphs_and_shaping_are_preserved():
    source=json.loads((ROOT/'data/font-sources/dad-emoji-prepared.json').read_text())
    old=prepared_font(source)
    new=TTFont(ROOT/'assets/fonts/dad-emoji.woff2',recalcBBoxes=False)
    old_order=old.getGlyphOrder()
    assert new.getGlyphOrder()[:len(old_order)]==old_order
    assert old.getTableData('GSUB')==new.getTableData('GSUB')
    assert old.getBestCmap()==new.getBestCmap()
    changed={old.getBestCmap()[cp] for cp in drawings.POINTS}
    for table in old['cmap'].tables:
        if table.format==14:
            changed.update(name for pairs in table.uvsDict.values() for cp,name in pairs if cp in drawings.POINTS and name)
    old_glyf,new_glyf=old['glyf'],new['glyf']
    for name in old_order:
        if name in changed:continue
        assert old_glyf.glyphs[name].compile(old_glyf,recalcBBoxes=False)==new_glyf.glyphs[name].compile(new_glyf,recalcBBoxes=False),name
        assert old['hmtx'][name]==new['hmtx'][name],name
        if name in old['COLR'].ColorLayers:
            a=[(l.name,l.colorID) for l in old['COLR'].ColorLayers[name]]
            b=[(l.name,l.colorID) for l in new['COLR'].ColorLayers[name]]
            assert a==b,name
    for a,b in zip(old['CPAL'].palettes,new['CPAL'].palettes):
        assert a==b[:len(a)]
