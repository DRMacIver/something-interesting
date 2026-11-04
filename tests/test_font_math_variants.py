import hashlib
import json
import sys

from fontTools.pens.recordingPen import DecomposingRecordingPen
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import ROOT,shape
from math_mark_checks import assert_accent_geometry

sys.path.insert(0,str(ROOT/'tools/font'))
import build_math_variants as builder

PATH=ROOT/'assets/fonts/dad-math-variants.woff2'


def test_explicit_variants_keep_source_drawings_and_base_metrics():
    report=json.loads((ROOT/'docs/math-variant-review.json').read_text())
    assert len(report['variants'])==27
    original=ROOT/report['source'];source=TTFont(original);font=TTFont(PATH)
    gs,actual=source.getGlyphSet(),font.getGlyphSet()
    for entry in report['variants']:
        name=entry['sourceGlyph']
        a,b=DecomposingRecordingPen(gs),DecomposingRecordingPen(actual)
        gs[name].draw(a);actual[name].draw(b)
        assert a.value==b.value,entry
        assert source['hmtx'][name]==font['hmtx'][name]
        base=chr(entry['base']);text=base+chr(entry['selector'])
        before,after=shape(original,text,True),shape(PATH,text,True)
        assert len(before)==len(after)
        for x,y in zip(before,after):
            assert x[1:]==y[1:],entry
            assert source.getGlyphName(x[0])==font.getGlyphName(y[0]),entry
        shaped=shape(PATH,text,True)
        assert len(shaped)==1 and font.getGlyphName(shaped[0][0])==name
        assert shaped[0][1]>0
        assert shaped!=shape(PATH,base,True),entry


def test_math_variant_accents_have_zero_advance_and_clear_stacking():
    report=json.loads((ROOT/'docs/math-variant-review.json').read_text())
    font=TTFont(PATH);source=TTFont(ROOT/report['source'])
    for entry in report['variants']+report['derivedVariants']:
        base=chr(entry['base'])
        for text in [base,base+chr(entry['selector'])]:
            assert_accent_geometry(font,PATH,text)
    # Normalize Unicode combining advances without altering their donor curves.
    categories=builder.unicode_categories(ROOT)
    for cp,name in font.getBestCmap().items():
        if categories.get(cp,('',0))[0] not in {'Mn','Me'}:continue
        a=DecomposingRecordingPen(source.getGlyphSet());b=DecomposingRecordingPen(font.getGlyphSet())
        source.getGlyphSet()[name].draw(a);font.getGlyphSet()[name].draw(b)
        assert a.value==b.value
        assert font['hmtx'][name]==(0,source['hmtx'][name][1])


def test_exact_inventory_rename_notices_and_reproduction():
    manifest=ROOT/'js/math-variant-manifest.js';review=ROOT/'docs/math-variant-review.json'
    entry=json.loads(manifest.read_text().split('export default ',1)[1].rstrip(';\n'))
    assert entry['variationOnly'] and len(entry['variationSequences'])==37
    font=TTFont(PATH)
    assert font['name'].getDebugName(1)=='Dad Math Variants'
    assert font['CFF '].cff.fontNames==['DadMathVariants']
    assert 'Modified subset' in font['name'].getDebugName(10)
    assert all((ROOT/p).is_file() for p in entry['notices'])
    native={(cp,s) for t in font['cmap'].tables if t.format==14 for s,rows in t.uvsDict.items() for cp,_ in rows}
    assert native=={tuple(map(ord,t)) for t in entry['variationSequences']}
    paths=[PATH,manifest,review];before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    builder.build()
    assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]


def test_previous_math_variant_shapes_and_accent_positions_are_preserved():
    font=TTFont(PATH)
    for folder,count in [('pre-historical-math-integration',216),('pre-kurrent-math-integration',288)]:
        baseline=ROOT/'output/font-review'/folder/'shaping.json'
        record=json.loads(baseline.read_text())
        assert len(record['cases'])==count
        for case in record['cases']:
            actual=[[font.getGlyphName(gid),*positions] for gid,*positions in shape(PATH,case['text'],True)]
            assert actual==case['glyphs'],case['text']


def test_production_historical_variants_match_reviewed_candidates():
    from prototype_historical_math_variants import build as candidate_build
    from math_historical_variants import POINTS,KURRENT
    import tempfile
    report=json.loads((ROOT/'docs/math-variant-review.json').read_text());font=TTFont(PATH)
    assert len(report['derivedVariants'])==10
    with tempfile.TemporaryDirectory() as folder:
        candidate_build(folder,points=[*POINTS,KURRENT]);candidate=TTFont(str(folder)+'/candidate.otf')
        for entry in report['derivedVariants']:
            cp=entry['base'];name=entry['glyph'];text=chr(cp)+chr(entry['selector'])
            a=DecomposingRecordingPen(candidate.getGlyphSet());b=DecomposingRecordingPen(font.getGlyphSet())
            candidate.getGlyphSet()[f'u{cp:X}.variant'].draw(a);font.getGlyphSet()[name].draw(b)
            assert a.value==b.value,entry
            assert font['hmtx'][name]==candidate['hmtx'][f'u{cp:X}.variant']
            assert shape(PATH,text,True)==[(font.getGlyphID(name),font['hmtx'][name][0],0,0,0)]
