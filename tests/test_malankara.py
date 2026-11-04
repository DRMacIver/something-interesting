"""Syriac Supplement needs joining forms and real vowel anchors, not just cmap."""
import io
from pathlib import Path
from functools import lru_cache
import uharfbuzz as hb
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from test_font_scripts import manifest

ROOT = Path(__file__).resolve().parents[1]
POINTS = range(0x860,0x86B)


@lru_cache
def faces(path):
    font = TTFont(path); font.flavor = None
    stream = io.BytesIO(); font.save(stream)
    return font, hb.Face(stream.getvalue())


def shaped(path,text):
    font,face = faces(path); hf = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(hf,buf)
    return font,list(zip(buf.glyph_infos,buf.glyph_positions))


def signature(path,text):
    font,run = shaped(path,text); glyphs=font.getGlyphSet(); result=[]
    for info,pos in run:
        assert info.codepoint != 0
        pen = DecomposingRecordingPen(glyphs)
        glyphs[font.getGlyphName(info.codepoint)].draw(pen)
        result.append((pen.value,pos.x_advance,pos.y_advance,pos.x_offset,pos.y_offset))
    return result


def test_malankara_packaging_preserves_all_contexts_and_vowel_positions():
    e=next(e for e in manifest()['fonts'] if e['source'].endswith('/EastSyriacMalankara.ttf'))
    for cp in POINTS:
        c=chr(cp)
        for text in [c,'ܒ'+c,c+'ܒ','ܒ'+c+'ܒ',c+'ܲ',c+'ܼ','ܒ'+c+'ܲܒ']:
            packaged=signature(ROOT/e['file'],text)
            original=signature(ROOT/e['source'],text)
            assert len(packaged)==len(original)
            for a,b in zip(packaged,original):
                assert a[1:]==b[1:],text  # Every advance and GPOS offset.
                assert len(a[0])==len(b[0])
                for (op,points),(source_op,source_points) in zip(a[0],b[0]):
                    assert op==source_op and len(points)==len(source_points)
                    for point,source_point in zip(points,source_points):
                        if point is None or source_point is None:
                            assert point is source_point
                        else:
                            # WOFF2 reconstructs xMin from the source bearing;
                            # this donor has a one-unit bound discrepancy.
                            assert all(abs(x-y)<=1 for x,y in zip(point,source_point))


def test_malankara_joining_types_and_zero_advance_vowels():
    e=next(e for e in manifest()['fonts'] if e['source'].endswith('/EastSyriacMalankara.ttf'))
    path=ROOT/e['file']
    for cp in POINTS:
        c=chr(cp)
        def identity(text,index):
            _,run=shaped(path,text)
            return next(i.codepoint for i,p in run if i.cluster==index)
        isolated=identity(c,0)
        final=identity('ܒ'+c,1)
        initial=identity(c+'ܒ',0)
        if cp in (0x861,0x866):
            assert isolated==final==initial  # Unicode nonjoining letters.
        else:
            assert final!=isolated
            if cp in (0x867,0x869,0x86A):
                assert initial==isolated  # Unicode right-joining letters.
            elif cp!=0x868:  # Native LLA shares its isolated/initial drawing.
                assert initial!=isolated
        _,run=shaped(path,c+'ܼ')
        marks=[p for i,p in run if p.x_advance==0]
        assert marks and all(p.y_offset!=0 for p in marks)
