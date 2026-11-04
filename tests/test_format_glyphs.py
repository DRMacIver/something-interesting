"""Format behaviour and visible font requirements are overlapping sets."""

from font_baseline_checks import pinned_packaging_font
import json
import subprocess
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from test_font_scripts import ROOT,shape
from test_outline_audit import routed_points,drawn_glyph
from test_unicode_inventory import module


def test_font_dependent_formats_belong_to_drawing_and_behaviour_requirements():
    audit=module('audit');points=audit.font_dependent_formats()
    assert len(points)==13
    assert {0x600,0x6dd,0x70f,0x890,0x8e2,0x110bd,0x110cd}<=points
    chars=audit.inventory()
    assert all(chars[cp]=='Cf' for cp in points)
    report=json.loads((ROOT/'docs/unicode-coverage.json').read_text())
    assert report['drawing_and_behaviour_characters']==len(points)
    assert report['visible_characters']+report['behavioural_characters']-len(points)==len(chars)
    # The browser table is generated from this same pinned property, not ICU.
    assert (ROOT/'js/unicode-data.js').read_text()==module('build_tables').build()


def test_all_format_signs_paint_their_native_nonempty_source_and_keep_number_shaping():
    points=module('audit').font_dependent_formats();report=routed_points(points)
    entries=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))['fonts']
    assert report['gaps']==[]
    cache={}
    for cp,indexes in report['routes']:
        assert len(indexes)==1
        file=report['files'][indexes[0]];entry=next(e for e in entries if e['file']==file)
        if file not in cache:cache[file]=TTFont(ROOT/file),TTFont(ROOT/entry['source']),pinned_packaging_font(entry)
        font,source,native=cache[file];name=font.getBestCmap()[cp];original=source.getBestCmap()[cp]
        assert drawn_glyph(font,name),hex(cp)
        a,b=DecomposingRecordingPen(native.getGlyphSet()),DecomposingRecordingPen(source.getGlyphSet())
        native.getGlyphSet()[native.getBestCmap()[cp]].draw(a);source.getGlyphSet()[original].draw(b)
        assert a.value==b.value,hex(cp)
        contexts=[digits for digits in ['123','١٢٣','१२३','ܒܓܕ'] if all(ord(c) in source.getBestCmap() for c in digits)]
        assert contexts,hex(cp)
        for text in [chr(cp),*[chr(cp)+digits for digits in contexts]]:
            assert shape(ROOT/file,text)==shape(ROOT/entry['source'],text),(hex(cp),text)
        outputs=shape(ROOT/file,chr(cp),True)
        assert outputs and all(row[0]>0 for row in outputs)
        assert any(drawn_glyph(font,font.getGlyphName(row[0])) for row in outputs),hex(cp)


def test_actual_context_runs_keep_source_number_and_abbreviation_substitution():
    # Exercise the real loader, font-run boundary and painted CSS stack. Merely
    # proving that a source font can shape this text missed fallback splitting.
    script=r'''
      import {fontRuns} from './js/emoji-routing.js';
      import {requiredFonts} from './js/fonts.js';
      import {makeFontString} from './js/comic.js';
      const texts=['\u0600123','\u06012026','\u06dd123','\u06dd١٢٣','\u06dd۱۲۳',
        '\u0890123','\u0891456','\u08e2١٢٣','\u070fܒܓܕ','ܒ\u070fܓܕ',
        '\u{110bd}१२३','\u{110cd}१२३'];
      console.log(JSON.stringify(texts.map(text=>{
        const fonts=requiredFonts([text]).fonts,runs=fontRuns(text);
        return {text,runs:runs.map(run=>({...run,font:fonts.find(f=>f.family===run.fontFamily),
          css:makeFontString(20,fonts.map(f=>f.family),run.emojiPolicy,run.fontFamily)}))};
      })));
    '''
    rows=json.loads(subprocess.check_output(['node','--input-type=module','-e',script],cwd=ROOT,text=True))
    for row in rows:
        assert len(row['runs'])==1,row
        run=row['runs'][0];font=run['font'];text=row['text']
        assert run['text']==text
        assert run['css'].split('"')[1]==font['family']
        assert shape(ROOT/font['file'],text)==shape(ROOT/font['source'],text)
        shaped=shape(ROOT/font['file'],text,True)
        assert shaped and all(g[0]>0 for g in shaped)
        if ord(text[0]) in {0x600,0x601,0x6dd,0x890,0x891,0x8e2}:
            # Native GSUB/GPOS actually incorporates the digits into the sign:
            # zero-advance positioned digits are stronger than cmap coverage.
            assert any(g[1]==0 and (g[3]!=0 or g[4]!=0) for g in shaped),text
