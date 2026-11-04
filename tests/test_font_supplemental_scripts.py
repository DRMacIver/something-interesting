"""Supplemental native drawings preserve modifier, kana and punctuation forms."""
import json
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from test_font_scripts import manifest,shape,ROOT
from test_font_cuneiform import outline
from test_unicode_inventory import audit
from font_baseline_checks import pinned_packaging_font


def sources():
    for name in ['ufs.json','unicodia.json']:
        for record in json.loads((ROOT/'data/font-sources'/name).read_text())['files']:
            if 'supplemental_script_ranges' in record:
                entry=next(e for e in manifest()['fonts'] if e['source']==record['path'])
                points={cp for a,b in record['supplemental_script_ranges'] for cp in range(a,b+1)}
                yield entry,points


def test_all_new_drawings_and_advances_match_the_pinned_source():
    total=0
    for e,points in sources():
        source,font=TTFont(ROOT/e['source']),TTFont(ROOT/e['file'])
        native=pinned_packaging_font(e)
        for cp in points:
            actual=outline(font,cp)
            native_drawing=outline(native,cp)
            assert actual[0] and actual[1] is not None and actual[2]>0,hex(cp)
            original=outline(source,cp)
            if cp==0x18cff:
                # The source declares xMin=63 while its first point is x=64.
                # FontTools corrects that box on save: tolerate that single-unit
                # translation, but require identical contours and advance.
                dx=native_drawing[1][0]-original[1][0]
                assert abs(dx)<=1 and actual[2]==original[2]
                recording=RecordingPen();recording.value=original[0]
                translated=RecordingPen();recording.replay(TransformPen(translated,(1,0,0,1,dx,0)))
                assert native_drawing[0]==translated.value
            else:
                assert native_drawing==original,hex(cp)
            assert actual[2]==native_drawing[2]
            assert all(abs(a-b)<=.01 for a,b in zip(actual[1],native_drawing[1])),hex(cp)
        # Spaces are supplied by the base font, outside these scoped shards.
        text=''.join(map(chr,sorted(points)))
        assert shape(ROOT/e['source'],text)==shape(ROOT/e['file'],text)
        total+=len(points)
    assert total==21


def test_modifier_letters_remain_raised_and_kana_shapes_remain_distinct():
    e=next(e for e,points in sources() if 0x558 in points);font=TTFont(ROOT/e['file'])
    for cp in [0x558,0x58b,0x58c,0x1dff3,0x1dff4]:
        box=outline(font,cp)[1]
        assert 0<box[1]<box[3]<1000
    kana=[0x1b123,0x1b124,0x1b125,0x1b126,0x1b127,0x1b128,0x1b168]
    assert len({repr(outline(font,cp)[0]) for cp in kana})==7


def test_all_assigned_characters_in_these_script_groups_are_bundled():
    scripts=audit.properties(audit.DATA/'Scripts.txt')
    groups={'Armenian','Greek','Hiragana','Katakana','Khitan_Small_Script','Balinese'}
    required={cp for cp in audit.inventory() if scripts.get(cp) in groups}
    m=manifest();points={cp for e in m['fonts'] for a,b in e['ranges'] for cp in range(a,b+1)}
    points.update(cp for a,b in m['baseRanges']+m['behaviouralRanges'] for cp in range(a,b+1))
    assert required<=points
