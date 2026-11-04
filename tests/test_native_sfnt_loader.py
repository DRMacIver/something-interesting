"""Native WOFF2 decoding keeps every original table and fresh font object."""
import copy
import io
import os
from pathlib import Path
import pytest
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables.ttProgram import Program
import native_sfnt_loader as loader
from test_dense_skeleton import fixture_font


@pytest.mark.parametrize('case',['simple','composite','instructions','overlap','long-loca','blank-tail'])
def test_native_decoder_tables_glyphs_hints_and_frame_exact(tmp_path,case):
    f=TTFont(io.BytesIO(fixture_font()),recalcTimestamp=False)
    if case=='composite':
        pen=TTGlyphPen(f.getGlyphSet());pen.addComponent('H',(1,0,0,1,30,0));g=pen.glyph();f['glyf']['part']=copy.deepcopy(f['glyf']['H']);g.components[0].glyphName='part';f['glyf']['H']=g
        f.setGlyphOrder(['.notdef','H','part']);f['hmtx']['part']=(500,50)
    elif case=='instructions':f['glyf']['H'].program=Program();f['glyf']['H'].program.fromBytecode(b'\xb0\x00')
    elif case=='overlap':f['glyf']['H'].flags[0]|=0x40
    elif case=='long-loca':
        # Large coordinates create a long loca representation without changing
        # the decoder's on/offcurve or hint semantics.
        for _ in range(12):
            pen=TTGlyphPen(None)
            for i in range(4000):
                x=i*7%30000;y=i*13%30000;pen.moveTo((x,y));pen.lineTo((x+3,y));pen.lineTo((x,y+3));pen.closePath()
            f['glyf']['H']=pen.glyph()
            break
    elif case=='blank-tail':f.setGlyphOrder(['H','.notdef'])
    path=tmp_path/(case+'.woff2');f.flavor='woff2';f.save(path)
    old=TTFont(path);new=loader.evidence_ttfont(path)
    assert type(new.reader).__name__=='SFNTReader','Qualifying controls must actually use native backend'
    assert set(old.reader.keys())==set(new.reader.keys())
    for tag in old.reader.keys():assert old.reader[tag]==new.reader[tag],(case,tag)
    assert old.getGlyphOrder()==new.getGlyphOrder()
    for name in old.getGlyphOrder():
        a,b=old['glyf'][name],new['glyf'][name]
        assert a.numberOfContours==b.numberOfContours
        assert a.getCoordinates(old['glyf'])==b.getCoordinates(new['glyf'])
        assert tuple(getattr(a,k,0) for k in ('xMin','yMin','xMax','yMax'))==tuple(getattr(b,k,0) for k in ('xMin','yMin','xMax','yMax'))
        if hasattr(a,'program'):assert a.program.getBytecode()==b.program.getBytecode()
    assert loader.evidence_ttfont(path) is not new


def test_actual_dense_670_all_tables_exact_and_fresh():
    root=Path(__file__).resolve().parents[1];path=root/'assets/fonts/scripts/9ede16589680.woff2'
    old=TTFont(path);new=loader.evidence_ttfont(path)
    for tag in old.reader.keys():assert old.reader[tag]==new.reader[tag],tag
    again=loader.evidence_ttfont(path);assert again is not new
    new['head'].unitsPerEm=999
    assert again['head'].unitsPerEm==old['head'].unitsPerEm


def test_changed_library_falls_back_to_reference_decoder(tmp_path,monkeypatch):
    path=tmp_path/'fixture.woff2';f=TTFont(io.BytesIO(fixture_font()));f.flavor='woff2';f.save(path)
    monkeypatch.setattr(loader,'_INITIAL_LIBRARY_ID',('different',))
    result=loader.evidence_ttfont(path)
    assert result.flavor=='woff2'


def test_raw_fonts_and_streams_keep_reference_loader():
    result=loader.evidence_ttfont(io.BytesIO(fixture_font()))
    assert result.flavor is None


def test_same_size_changed_source_with_restored_mtime_uses_its_new_sha(tmp_path):
    def encoded(units):
        font=TTFont(io.BytesIO(fixture_font()),recalcTimestamp=False);font['head'].unitsPerEm=units;font.flavor='woff2';stream=io.BytesIO();font.save(stream);return stream.getvalue()
    old=encoded(1000);variants=[(units,encoded(units)) for units in range(1001,1033)]
    units,new=next((units,data) for units,data in variants if len(data)==len(old))
    path=tmp_path/'changed.woff2';path.write_bytes(old);stat=path.stat();first=loader.evidence_ttfont(path)
    path.write_bytes(new);os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns));second=loader.evidence_ttfont(path)
    assert first['head'].unitsPerEm==1000 and second['head'].unitsPerEm==units
    assert type(second.reader).__name__=='SFNTReader'


def test_same_bytes_restored_mtime_and_inode_replacement_refresh_decoded_objects(tmp_path):
    import font_baseline_checks as checks
    font=TTFont(io.BytesIO(fixture_font()));font.flavor='woff2';path=tmp_path/'fixture.woff2';font.save(path)
    raw=path.read_bytes();stat=path.stat();first=checks.evidence_font(path);first['head'].unitsPerEm=777
    path.write_bytes(raw);os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns));second=checks.evidence_font(path)
    assert second is not first and second['head'].unitsPerEm==1000
    replacement=tmp_path/'replacement';replacement.write_bytes(raw);os.utime(replacement,ns=(stat.st_atime_ns,stat.st_mtime_ns));replacement.replace(path)
    third=checks.evidence_font(path);assert third is not second and third['head'].unitsPerEm==1000


def test_input_read_race_rejects_even_same_size_restored_mtime(tmp_path,monkeypatch):
    font=TTFont(io.BytesIO(fixture_font()));font.flavor='woff2';path=tmp_path/'race.woff2';font.save(path)
    original=Path.read_bytes
    def read(p):
        data=original(p)
        if p==path:
            stat=p.stat();p.write_bytes(data);os.utime(p,ns=(stat.st_atime_ns,stat.st_mtime_ns))
        return data
    monkeypatch.setattr(Path,'read_bytes',read)
    with pytest.raises(AssertionError,match='Font changed during decode read'):loader.evidence_ttfont(path)


def test_canonical_cache_hit_race_rejects(tmp_path,monkeypatch):
    font=TTFont(io.BytesIO(fixture_font()));font.flavor='woff2';path=tmp_path/'race.woff2';font.save(path)
    loader.evidence_ttfont(path);original=loader._canonical_sfnt
    def canonical(*args):
        value=original(*args);stat=path.stat();path.write_bytes(args[0]);os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns));return value
    monkeypatch.setattr(loader,'_canonical_sfnt',canonical)
    with pytest.raises(AssertionError,match='Font/native library changed'):loader.evidence_ttfont(path)
