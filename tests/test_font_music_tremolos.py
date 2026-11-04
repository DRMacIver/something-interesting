"""Tremolo counts survive native reordering and low-form selection."""

from pathlib import Path
from font_baseline_checks import pinned_packaging_font
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import manifest, shape, ROOT
from test_font_cuneiform import outline


def file_path(entry):return ROOT/entry['file']

def native_font(entry):return pinned_packaging_font(entry)

def pair():
    e = next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoMusic-Regular.ttf'))
    return e, TTFont(file_path(e))


def test_tremolo_counts_survive_stems_flags_and_canonical_note_forms():
    e, f = pair(); p = file_path(e)
    for cp, count in [(0x1D25B, 4), (0x1D25C, 5)]:
        assert outline(f, cp)[2] == 0
        assert outline(f, cp)[1] == outline(f, 0x1D169)[1]
        for head in ['\U0001d158\U0001d165', '\U0001d15f', '\U0001d157\U0001d165']:
            for flag in ['', '\U0001d16e', '\U0001d172', '\U0001d250', '\U0001d252']:
                for before in [True, False]:
                    suffix = chr(cp) + flag if before else flag + chr(cp)
                    text = head + suffix
                    reference = head + suffix.replace(chr(cp), '\U0001d169')
                    actual, expected = shape(p, text, True), shape(p, reference, True)
                    assert len(actual) == len(expected)
                    changed = 0
                    for a, b in zip(actual, expected):
                        assert a[1:] == b[1:], (text, a, b)
                        if a[0] != b[0]:
                            g = f['glyf'][f.getGlyphName(a[0])]
                            assert g.numberOfContours == count
                            assert len(f['glyf'][f.getGlyphName(b[0])].getCoordinates(f['glyf'])[1]) == 3
                            changed += 1
                    assert changed == 1, text
                    assert all(g[0] for g in actual)


def test_strokes_are_separate_and_original_music_is_unchanged():
    from fontTools.pens.pointInsidePen import PointInsidePen
    from music_tremolos import add_marks
    e, f = pair(); p = file_path(e);native=native_font(e)
    import hashlib,json
    source=ROOT/e['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==e['sourceSha256']
    files=[ROOT/'tools/font/music_tremolos.py',ROOT/'tools/font/music_mark_rules.py']
    token=':music-tremolos:'+':'.join(hashlib.sha256(path.read_bytes()).hexdigest() for path in files)
    assert token in e['recipe']
    records=json.loads((ROOT/e['supplementalTreatment']['report']).read_text())['records']
    by_name={row['glyph']:row['gid'] for row in records}
    constructor=TTFont(source);add_marks(constructor)
    def boxes(font,cp):
        glyph=font['glyf'][font.getBestCmap()[cp]];points,ends,_=glyph.getCoordinates(font['glyf']);start=0;result=[]
        for end in ends:
            part=points[start:end+1];start=end+1
            result.append((min(x for x,y in part),min(y for x,y in part),max(x for x,y in part),max(y for x,y in part)))
        return sorted(result,key=lambda b:b[1])
    def slices(font,cp):
        gs=font.getGlyphSet();name=font.getBestCmap()[cp];values=[]
        for y in range(350,901):
            pen=PointInsidePen(gs,(199,y));gs[name].draw(pen)
            if pen.getResult():values.append(y)
        runs=[]
        for y in values:
            if not runs or y>runs[-1][1]+1:runs.append([y,y])
            else:runs[-1][1]=y
        return runs
    for cp,count in [(0x1D25B,4),(0x1D25C,5)]:
        for name in [f'u{cp:05X}',f'u{cp:05X}_low']:
            original_name=native.getGlyphName(by_name[name])
            assert native['glyf'][original_name].getCoordinates(native['glyf'])==constructor['glyf'][name].getCoordinates(constructor['glyf'])
            assert native['hmtx'][original_name]==constructor['hmtx'][name]
        original=native['glyf'][native.getBestCmap()[cp]]
        # The frozen constructor retains the exact straight native attachment
        # edges. Finished pressure may curve them, but not merge/count strokes.
        start=0;spans=[]
        for end in original.endPtsOfContours:
            points=original.coordinates[start:end+1];start=end+1
            ys=sorted(y for x,y in points if x==50)
            assert len(ys)==2 and ys[1]>ys[0]
            spans.append(ys)
        assert len(spans)==count and all(a[1]<b[0] for a,b in zip(spans,spans[1:]))
        old_boxes,new_boxes=boxes(native,cp),boxes(f,cp)
        assert len(old_boxes)==len(new_boxes)==count
        # Bound each finished bar within one percent of the native em
        # (10 units at this source's 1000 UPM), preserving attachment area.
        attachment_tolerance=.01*native['head'].unitsPerEm
        assert all(max(abs(a-b) for a,b in zip(old,new))<=attachment_tolerance for old,new in zip(old_boxes,new_boxes))
        old_slices,new_slices=slices(native,cp),slices(f,cp)
        assert len(old_slices)==len(new_slices)==count
        native_gap=min(b[0]-a[1] for a,b in zip(old_slices,old_slices[1:]))
        assert all(b[0]-a[1]>=native_gap/2 for a,b in zip(new_slices,new_slices[1:]))
    for text in ['\U0001d158\U0001d165\U0001d169', '\U0001d15f\U0001d172\U0001d169', '\U0001d15f\U0001d167']:
        assert shape(ROOT / e['source'], text) == shape(p, text)


def test_real_tremolo_fields_preserve_native_connections_and_counters(monkeypatch):
    import check_supplemental_fields as fields
    e,_=pair();native_font(e)
    native=ROOT/'output/font-review/supplemental-production-baselines'/Path(e['file']).name
    current=file_path(e);factory=fields.Font
    fonts={str(native):factory(native),str(current):factory(current)}
    monkeypatch.setattr(fields,'Font',lambda path:fonts[str(path)])
    head='\U0001d158\U0001d165'
    contexts=[head+chr(cp)+flag for cp in [0x1d25b,0x1d25c] for flag in ['', '\U0001d172','\U0001d250']]
    for text in [*contexts,' '.join(contexts)]:
        for size in [384,1024]:
            result=fields.check(native,current,text,size)
            assert result['status']=='pass',(text,size,result)
