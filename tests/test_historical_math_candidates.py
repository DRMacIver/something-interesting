import hashlib
import sys

import pytest
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from test_font_scripts import ROOT,shape

sys.path.insert(0,str(ROOT/'tools/font'))
import prototype_historical_math_variants as builder


@pytest.fixture(scope='module')
def candidate(tmp_path_factory):
    directory=tmp_path_factory.mktemp('historical-math')
    report=builder.build(directory)
    return directory,report,TTFont(directory/'candidate.otf')


def test_nine_candidates_shape_as_positive_distinct_glyphs(candidate):
    directory,report,font=candidate
    assert report['candidateOnly'] and len(report['variants'])==9
    for entry in report['variants']:
        base=chr(entry['base']);variant=base+chr(entry['selector'])
        plain=shape(directory/'candidate.otf',base,True)
        actual=shape(directory/'candidate.otf',variant,True)
        assert len(actual)==len(plain)==1
        assert font.getGlyphName(actual[0][0])==entry['variantGlyph']
        assert actual[0][1]==plain[0][1]==entry['advance']>0
        gs=font.getGlyphSet();a=DecomposingRecordingPen(gs);b=DecomposingRecordingPen(gs)
        gs[entry['defaultGlyph']].draw(a);gs[entry['variantGlyph']].draw(b)
        assert a.value and b.value and a.value!=b.value
        adjacent=shape(directory/'candidate.otf',variant*3,True)
        assert len(adjacent)==3 and all(row==actual[0] for row in adjacent)


def test_native_defaults_and_relation_topology(candidate):
    _,report,font=candidate
    source=TTFont(ROOT/report['sources'][0]['path']);gs=font.getGlyphSet()
    for entry in report['variants']:
        cp=entry['base'];name=entry['variantGlyph']
        if entry['defaultSourceGlyph']:
            a=DecomposingRecordingPen(source.getGlyphSet());b=DecomposingRecordingPen(gs)
            source.getGlyphSet()[entry['defaultSourceGlyph']].draw(a);gs[entry['defaultGlyph']].draw(b)
            assert a.value==b.value
            assert font['hmtx'][entry['defaultGlyph']]==source['hmtx'][entry['defaultSourceGlyph']]
        if cp in {0x22dc,0x22dd}:
            pen=DecomposingRecordingPen(gs);gs[name].draw(pen)
            # Exactly two horizontal bars followed by one diagonal, with no
            # upper diagonal arm left over from the ordinary chevron drawing.
            contours=[];current=[]
            for op,points in pen.value:
                if op=='closePath':contours.append(current);current=[]
                else:current.extend(points)
            assert len(contours)==3
            for c in contours[:2]:
                assert max(x for x,y in c)-min(x for x,y in c)>600
                assert max(y for x,y in c)-min(y for x,y in c)<35
            dx=contours[2][1][0]-contours[2][0][0]
            assert (dx>0)==(cp==0x22dc)
        if cp==0x1db10:
            from fontTools.pens.boundsPen import BoundsPen
            a=BoundsPen(gs);b=BoundsPen(gs);gs[entry['defaultGlyph']].draw(a);gs[name].draw(b)
            assert a.bounds[1]>0 and b.bounds[1]<-150


def test_candidate_rebuild_and_notices(candidate):
    directory,report,font=candidate
    assert font['name'].getDebugName(0)
    for notice in report['licences']:assert (directory/notice.rsplit('/',1)[-1]).is_file()
    paths=[directory/n for n in ['candidate.otf','candidate.json','specimen.svg','specimen.png','README.txt']]
    before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    builder.build(directory)
    assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]


def test_kurrent_z_has_one_closed_descending_loop_and_its_exact_selector(tmp_path):
    from math_historical_variants import KURRENT
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.boundsPen import BoundsPen
    import pymupdf
    import numpy as np
    from scipy import ndimage
    builder.build(tmp_path,points=[KURRENT]);path=tmp_path/'candidate.otf';font=TTFont(path)
    name=f'u{KURRENT:X}.variant';gs=font.getGlyphSet()
    result=shape(path,chr(KURRENT)+'\ufe02',True)
    assert len(result)==1 and font.getGlyphName(result[0][0])==name
    assert font.getGlyphName(shape(path,chr(KURRENT)+'\ufe00',True)[0][0])==f'u{KURRENT:X}'
    bounds=BoundsPen(gs);gs[name].draw(bounds)
    assert bounds.bounds[1]<-150 and bounds.bounds[3]>500
    pen=SVGPathPen(gs);gs[name].draw(pen)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect width="200" height="200" fill="white"/><path d="{pen.getCommands()}" transform="translate(20,130) scale(.2,-.2)"/></svg>'
    doc=pymupdf.open(stream=svg.encode(),filetype='svg');pix=doc[0].get_pixmap()
    pixels=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)
    ink=pixels[:,:,:3].min(axis=2)<128
    holes=ndimage.binary_fill_holes(ink)&~ink
    labels,count=ndimage.label(holes)
    assert count==1
    ys,xs=np.where(labels==1)
    assert len(ys)>50 and ys.mean()>130
