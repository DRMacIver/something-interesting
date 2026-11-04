"""GSUB-driven variants need real context, not a format14 presence count."""
import json
from functools import lru_cache
from pathlib import Path

import pytest
from fontTools.pens.recordingPen import DecomposingRecordingPen
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import ROOT, shape
from font_baseline_checks import pinned_packaging_font


@lru_cache(maxsize=2048)
def drawing(path, gid):
    font = loaded(path)
    glyphs = font.getGlyphSet()
    pen = DecomposingRecordingPen(glyphs)
    glyphs[font.getGlyphName(gid)].draw(pen)
    return pen.value


@lru_cache(maxsize=6)
def loaded(path):
    return TTFont(path)


def pinned_context_native(entry):
    """Authenticate the finished font cache before using its frozen native font."""
    native=pinned_packaging_font(entry)
    path=ROOT/entry['file']
    if entry.get('supplementalTreatment') or entry.get('denseTreatment'):
        path=ROOT/'output/font-review/supplemental-production-baselines'/Path(entry['file']).name
    return native,path


def assert_context_identity(native,finished):
    """Subset GIDs, advances and attachment offsets must remain exactly equal."""
    assert native and all(g[0]>0 for g in native)
    assert finished and all(g[0]>0 for g in finished)
    assert native==finished,'Contextual selector GIDs or positioning changed'


def assert_raw_native_context(original,native,text):
    """Allow source subsetting to renumber GIDs, preserving every native drawing."""
    source,frozen=shape(original,text,True),shape(native,text,True)
    assert source and len(source)==len(frozen),(text,original)
    for raw,pinned in zip(source,frozen):
        assert raw[0]>0 and pinned[0]>0,(text,original)
        assert raw[1:]==pinned[1:],(text,original)
        assert drawing(original,raw[0])==drawing(native,pinned[0]),(text,original)
    return source,frozen


@pytest.mark.parametrize('source,start,end,neighbour,count', [
    ('NotoSansMongolian-Regular.ttf',0x1800,0x18af,'ᠠ',117),
    ('NotoSansPhagsPa-Regular.ttf',0xa840,0xa87f,'ꡀ',6),
    ('NotoSansManichaean-Regular.ttf',0x10ac0,0x10aff,'𐫀',5),
])
def test_standardized_contextual_variants_keep_source_glyphs_in_all_word_positions(source,start,end,neighbour,count):
    manifest = json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    entry = next(e for e in manifest['fonts'] if e['source'].endswith('/'+source))
    original, packaged = ROOT/entry['source'], ROOT/entry['file']
    native_font,native = pinned_context_native(entry)
    assert native_font.getGlyphOrder()==loaded(native).getGlyphOrder()
    rows = []
    for line in (ROOT/'data/unicode/18.0.0/StandardizedVariants.txt').read_text().splitlines():
        body = line.split('#')[0].strip()
        if not body:
            continue
        cp, selector = (int(v,16) for v in body.split(';')[0].split())
        if start <= cp <= end:
            rows.append((cp,selector))
    assert len(rows) == count
    changed = set()
    for cp, selector in rows:
        sequence = chr(cp)+chr(selector)
        for left,right in [('', ''), ('', neighbour), (neighbour, ''), (neighbour, neighbour)]:
            text = left+sequence+right
            a,frozen = assert_raw_native_context(original,native,text)
            b = shape(packaged,text,True)
            assert_context_identity(frozen,b)
            plain_text=left+chr(cp)+right
            plain,ordinary_native = assert_raw_native_context(original,native,plain_text)
            assert_context_identity(ordinary_native,shape(packaged,plain_text,True))
            # Ignore empty selector carriers when comparing actual drawings.
            actual = [drawing(original,g[0]) for g in a if drawing(original,g[0])]
            ordinary = [drawing(original,g[0]) for g in plain if drawing(original,g[0])]
            if actual != ordinary:
                changed.add((cp,selector))
    assert changed == set(rows), ('Source did not demonstrate every variant in any tested position',set(rows)-changed)


@pytest.mark.parametrize('mutation',['selector_gid','context_order','x_advance','y_advance','x_offset','y_offset','missing_glyph','dropped_carrier'])
def test_context_identity_rejects_selector_and_joining_mutations(mutation):
    native=[(12,500,0,0,0),(27,300,0,-20,10),(9,0,0,0,0)]
    changed=list(native)
    if mutation=='selector_gid':changed[1]=(28,*changed[1][1:])
    elif mutation=='context_order':changed[0],changed[1]=changed[1],changed[0]
    elif mutation=='missing_glyph':changed[1]=(0,*changed[1][1:])
    elif mutation=='dropped_carrier':changed.pop()
    else:
        index={'x_advance':1,'y_advance':2,'x_offset':3,'y_offset':4}[mutation]
        row=list(changed[1]);row[index]+=1;changed[1]=tuple(row)
    with pytest.raises(AssertionError):assert_context_identity(native,changed)
