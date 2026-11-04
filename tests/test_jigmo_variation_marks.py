from font_baseline_checks import authenticate_catalog_dense_parent, pinned_packaging_font
from pathlib import Path
import sys
import json

import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools import subset
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from test_font_scripts import ROOT,shape

sys.path.insert(0,str(ROOT/'tools/font'))
from jigmo_variation_marks import add_marks,POINTS

DONOR=ROOT/'build/unicode-sources/jigmo/extracted/Jigmo.ttf'


@pytest.mark.parametrize('source,base,selector',[
    ('Jigmo2.ttf',0x20000,0xe0100),
    ('Jigmo3.ttf',0x30654,0xe0101),
])
def test_native_marks_keep_supplementary_variants_and_native_cell_positions(tmp_path,source,base,selector):
    donor=TTFont(DONOR);original=ROOT/'build/unicode-sources/jigmo/extracted'/source
    font=TTFont(original);add_marks(font,donor)
    path=tmp_path/'augmented.ttf';font.save(path)
    native=shape(original,chr(base)+chr(selector),True)
    assert shape(path,chr(base)+chr(selector),True)==native
    # Fallback mark placement depends on the base's ink bounds. Build an
    # independent control by putting that exact base into the BMP donor,
    # rather than comparing against an unrelated BMP ideograph.
    reference_font=TTFont(DONOR);base_name=font.getGlyphName(native[0][0]);proxy='test.sameVariantBase'
    reference_order=list(reference_font.getGlyphOrder())
    outline=DecomposingRecordingPen(font.getGlyphSet());font.getGlyphSet()[base_name].draw(outline)
    pen=TTGlyphPen(None);outline.replay(pen)
    reference_font['glyf'][proxy]=pen.glyph()
    for tag in ['hmtx','vmtx']:reference_font[tag][proxy]=font[tag][base_name]
    reference_font['GDEF'].table.GlyphClassDef.classDefs[proxy]=font['GDEF'].table.GlyphClassDef.classDefs.get(base_name,0)
    reference_font.setGlyphOrder([*reference_order,proxy])
    for table in reference_font['cmap'].tables:
        if table.isUnicode() and table.format in {4,12}:table.cmap[0x3402]=proxy
    options=subset.Options();options.glyph_names=True
    sub=subset.Subsetter(options=options);sub.populate(unicodes={0x3402,*POINTS});sub.subset(reference_font)
    reference_path=tmp_path/'control.ttf';reference_font.save(reference_path)
    for cp in POINTS:
        name=font.getBestCmap()[cp];old=donor.getBestCmap()[cp]
        a=DecomposingRecordingPen(donor.getGlyphSet());b=DecomposingRecordingPen(font.getGlyphSet())
        donor.getGlyphSet()[old].draw(a);font.getGlyphSet()[name].draw(b)
        assert a.value==b.value
        assert font['hmtx'][name]==donor['hmtx'][old]
        assert font['vmtx'][name]==donor['vmtx'][old]
        assert font['glyf'][name].program.getBytecode()==donor['glyf'][old].program.getBytecode()
        text=chr(base)+chr(selector)+chr(cp)
        actual=shape(path,text,True)
        assert len(actual)==2 and actual[0]==native[0]
        reference=shape(reference_path,'㐂'+chr(cp),True)
        assert actual[1][1:]==reference[-1][1:]
        assert font.getGlyphName(actual[1][0])==name
        assert sum(g[1] for g in actual)==native[0][1]


def test_incompatible_hinting_and_existing_marks_are_rejected():
    donor=TTFont(DONOR);target=TTFont(ROOT/'build/unicode-sources/jigmo/extracted/Jigmo2.ttf')
    add_marks(target,donor)
    with pytest.raises(AssertionError,match='replace native'):add_marks(target,donor)
    target=TTFont(ROOT/'build/unicode-sources/jigmo/extracted/Jigmo2.ttf')
    target['prep'].program.fromBytecode(b'\x00')
    with pytest.raises(AssertionError,match='Incompatible donor hinting'):add_marks(target,donor)


def test_shipped_supplementary_ivs_and_borrowed_marks_keep_native_drawings():
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    donor=TTFont(DONOR);donor_glyphs=donor.getGlyphSet();checked=0;expected=0
    for filename in ['Jigmo2.ttf','Jigmo3.ttf']:
        source=TTFont(ROOT/'build/unicode-sources/jigmo/extracted'/filename);source_glyphs=source.getGlyphSet()
        native={(cp,s):n or source.getBestCmap()[cp] for t in source['cmap'].tables if t.format==14 for s,rows in t.uvsDict.items() for cp,n in rows}
        expected+=len(native)
        for entry in [e for e in manifest['fonts'] if e['source'].endswith('/'+filename)]:
            font=TTFont(ROOT/entry['file']);cmap=font.getBestCmap()
            if entry.get('denseTreatment'):
                # Complete base/native/cache proof is memoized only while all
                # raw, font, report and per-glyph cache dependencies are fixed.
                assert authenticate_catalog_dense_parent(entry)
                frozen=ROOT/'output/font-review/supplemental-production-baselines'/Path(entry['file']).name
                packaged_native=TTFont(frozen)
            else:packaged_native=pinned_packaging_font(entry)
            gs=packaged_native.getGlyphSet();native_cmap=packaged_native.getBestCmap()
            native_pairs={(cp,s):n or native_cmap[cp] for t in packaged_native['cmap'].tables if t.format==14 for s,rows in t.uvsDict.items() for cp,n in rows}
            pairs={(cp,s):n or cmap[cp] for t in font['cmap'].tables if t.format==14 for s,rows in t.uvsDict.items() for cp,n in rows}
            if pairs:
                assert POINTS<=cmap.keys()
                assert entry['additionalSources'][0]['source'].endswith('/Jigmo.ttf')
                for cp in POINTS:
                    name=cmap[cp];native_name=native_cmap[cp];old=donor.getBestCmap()[cp]
                    a=DecomposingRecordingPen(donor_glyphs);b=DecomposingRecordingPen(gs)
                    donor_glyphs[old].draw(a);gs[native_name].draw(b)
                    assert a.value==b.value
                    for tag in ['hmtx','vmtx']:assert font[tag][name]==packaged_native[tag][native_name]==donor[tag][old]
            else:assert not POINTS&cmap.keys()
            for pair,name in pairs.items():
                old=native[pair];native_name=native_pairs[pair];a=DecomposingRecordingPen(source_glyphs);b=DecomposingRecordingPen(gs)
                source_glyphs[old].draw(a);gs[native_name].draw(b)
                assert a.value==b.value,(entry['file'],pair)
                assert font['hmtx'][name]==packaged_native['hmtx'][native_name]==source['hmtx'][old]
                text=''.join(chr(c) for c in pair)
                actual=shape(ROOT/entry['file'],text,True)
                assert len(actual)==1 and font.getGlyphName(actual[0][0])==name
                assert actual[0][1:]==shape(ROOT/entry['source'],text,True)[0][1:]
                checked+=1
    assert checked==expected==2677
