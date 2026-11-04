"""Registered Egyptian rotations preserve geometry and logical sequence identity."""
import hashlib
import importlib.util
import json
import math
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from test_font_scripts import ROOT,shape

PATH=ROOT/'assets/fonts/dad-egyptian-variants.woff2'


def test_every_registered_rotation_shapes_to_its_own_affine_drawing():
    spec=importlib.util.spec_from_file_location('egyptian_rotation_builder',ROOT/'tools/font/build_egyptian_variants.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    review=json.loads((ROOT/'docs/egyptian-variant-review.json').read_text())
    source=TTFont(ROOT/review['source']);font=TTFont(PATH)
    gs=source.getGlyphSet();actuals=font.getGlyphSet()
    expected={(cp,vs,angle) for cp,vs,angle,_ in builder.variants()}
    assert len(expected)==142
    assert {(r['codepoint'],r['selector'],r['angle']) for r in review['variants']}==expected
    for row in review['variants']:
        cp,vs,angle=row['codepoint'],row['selector'],row['angle']
        original=gs[source.getBestCmap()[cp]];pen=DecomposingRecordingPen(gs);original.draw(pen)
        matrix=row['transform'];c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle))
        assert all(abs(a-b)<1e-10 for a,b in zip(matrix[:4],(c,-s,s,c)))
        wanted=BoundsPen(None);pen.replay(TransformPen(wanted,matrix))
        actual=BoundsPen(actuals);actuals[row['glyph']].draw(actual)
        assert all(abs(a-b)<2 for a,b in zip(wanted.bounds,actual.bounds)),row
        shaped=shape(PATH,chr(cp)+chr(vs),True)
        assert len(shaped)==1 and font.getGlyphName(shaped[0][0])==row['glyph'],row
        assert 0<shaped[0][1]<5000,row
        assert shaped!=shape(PATH,chr(cp),True),row


def test_egyptian_rotation_font_rebuild_is_deterministic():
    spec=importlib.util.spec_from_file_location('egyptian_rotation_builder',ROOT/'tools/font/build_egyptian_variants.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    paths=[PATH,ROOT/'js/egyptian-variant-manifest.js',ROOT/'docs/egyptian-variant-review.json']
    before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    builder.build()
    assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
