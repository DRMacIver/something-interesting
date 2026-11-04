"""Copied GLYF programs prove ink only with exact offsets and a valid graph."""
import copy,io,hashlib
from pathlib import Path
import struct
import pytest
from fontTools.ttLib import TTFont,newTable
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.pens.recordingPen import DecomposingRecordingPen
from test_dense_skeleton import fixture_font
import test_font_marked_cjk as marked


def saved(font):
    out=io.BytesIO();font.flavor=None;font.recalcTimestamp=False;font.save(out);return out.getvalue()


def pair():
    font=TTFont(io.BytesIO(fixture_font()));pen=TTGlyphPen(font.getGlyphSet());pen.addComponent('H',(1,0,0,1,20,0));font['glyf']['comp']=pen.glyph();font['hmtx']['comp']=(500,50);font.setGlyphOrder(['.notdef','H','comp'])
    font['glyf']['H'].program=Program();font['glyf']['H'].program.fromBytecode(b'\xb0\x00')
    font['name'].setName('Noto fixture',0,3,1,0x409);font['name'].setName('SIL Open Font License',13,3,1,0x409)
    source=TTFont(io.BytesIO(saved(font)));target=copy.deepcopy(source)
    for i in range(257):
        name='mark'+str(i);target['glyf'][name]=TTGlyphPen(None).glyph();target['hmtx'][name]=(0,0)
    target.setGlyphOrder(source.getGlyphOrder()+['mark'+str(i) for i in range(257)]);target['name'].setName('Dad Marked Fixture',1,3,1,0x409)
    return source,TTFont(io.BytesIO(saved(target)))


def corrupt_component(font,gid):
    raw=bytearray(saved(font));reader=TTFont(io.BytesIO(raw));offset=reader.reader.tables['glyf'].offset+reader['loca'].locations[2]
    struct.pack_into('>H',raw,offset+12,gid)
    return TTFont(io.BytesIO(raw))


@pytest.mark.parametrize('case',['exact','geometry','hints','cycle','missing','variable','loca'])
def test_prefix_exactness_and_graph_guards(case):
    a,b=pair()
    if case=='geometry':b['glyf']['H'].coordinates[0]=(51,0);b=TTFont(io.BytesIO(saved(b)))
    elif case=='hints':b['glyf']['H'].program.fromBytecode(b'\xb0\x01');b=TTFont(io.BytesIO(saved(b)))
    elif case in {'cycle','missing'}:
        gid=2 if case=='cycle' else 3;a=corrupt_component(a,gid);b=corrupt_component(b,gid)
    elif case=='variable':a['fvar']=newTable('fvar')
    elif case=='loca':b['loca'].locations[1]+=2
    if case in {'cycle','missing'}:
        with pytest.raises(AssertionError,match='Cyclic|outside'):marked.copied_glyf_prefix_is_exact(a,b)
    else:
        assert marked.copied_glyf_prefix_is_exact(a,b)==(case=='exact')
        if case=='exact':
            ag,bg=a.getGlyphSet(),b.getGlyphSet()
            for gid,name in enumerate(a.getGlyphOrder()):
                x,y=DecomposingRecordingPen(ag),DecomposingRecordingPen(bg);ag[name].draw(x);bg[b.getGlyphName(gid)].draw(y);assert x.value==y.value


def test_pair_keeps_hint_assertions_and_original_fallback(tmp_path,monkeypatch):
    a,b=pair();source=tmp_path/'source.ttf';target=tmp_path/'marked.ttf';source.write_bytes(saved(a));target.write_bytes(saved(b));monkeypatch.setattr(marked,'ROOT',tmp_path)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    painted={'file':'source.ttf','sha256':sha(source)};entry={'source':'source.ttf','sourceSha256':sha(source),'file':'marked.ttf','sha256':sha(target),'family':'Dad Marked Fixture','variationOnly':True}
    variants,glyphs,fast=marked.assert_native_companion_pair(entry,painted);assert (variants,glyphs,fast)==(0,3,True)
    # Equal geometry with different instructions must fall back to drawing and
    # still fail the retained instruction-byte assertion, never silently skip it.
    b['glyf']['H'].program.fromBytecode(b'\xb0\x01');target.write_bytes(saved(b));entry['sha256']=sha(target)
    calls=[];original=marked.DecomposingRecordingPen
    def pen(*args,**kwargs):calls.append(1);return original(*args,**kwargs)
    monkeypatch.setattr(marked,'DecomposingRecordingPen',pen)
    with pytest.raises(AssertionError):marked.assert_native_companion_pair(entry,painted)
    assert calls,'Raw mismatch must execute original drawing fallback'
