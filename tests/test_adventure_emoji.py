import hashlib
import io
import json
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

ROOT=Path(__file__).resolve().parents[1]


def test_selected_sources_and_font_hashes_are_current():
    review=json.loads((ROOT/'assets/emoji-concepts/production-review.json').read_text())
    assert len(review['drawings'])==16
    assert {d['emoji'] for d in review['drawings']}==set('☃⛄🦖🦕🚀🛸👽👾🪐☄📦💣🐅🐯🐉💀')
    for d in review['drawings']:
        assert hashlib.sha256((ROOT/d['source']).read_bytes()).hexdigest()==d['sourceSha256']
    entry=review['font']
    for f in [entry,*entry['companions']]:
        assert hashlib.sha256((ROOT/f['file']).read_bytes()).hexdigest()==f['sha256']
    assert review['recipeSha256']==hashlib.sha256((ROOT/'tools/font/build_adventure_emoji.py').read_bytes()).hexdigest()
    selected={d['emoji']:d['source'] for d in review['drawings']}
    assert selected['🐯'].endswith('face-cli.png')
    assert selected['🐅'].endswith('hobbes-upside-down-v2.png')
    assert selected['📦'].endswith('box-cli-v1.png')
    assert selected['⛄'].endswith('snow-goon-and-box-v2.png')


def test_colour_and_ink_glyphs_align_and_variants_shape_to_same_drawing():
    review=json.loads((ROOT/'assets/emoji-concepts/production-review.json').read_text());entry=review['font']
    points={int(r['codepoint'][2:],16) for r in review['drawings']}
    font=TTFont(ROOT/entry['file'],recalcBBoxes=False);ink=TTFont(ROOT/entry['companions'][0]['file'],recalcBBoxes=False)
    assert 'COLR' in font and 'CPAL' in font and 'COLR' not in ink
    font.flavor=None;stream=io.BytesIO();font.save(stream);shaper=hb.Font(hb.Face(stream.getvalue()))
    def shape(text):
        b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(shaper,b)
        return [(g.codepoint,p.x_advance,p.x_offset,p.y_offset) for g,p in zip(b.glyph_infos,b.glyph_positions)]
    for text in entry['sequences']:
        if ord(text[0]) not in points or len(text)>2 or len(text)==2 and ord(text[-1]) not in {0xfe0e,0xfe0f}:continue
        assert shape(text)==shape(text[0])
        assert len(shape(text))==1 and shape(text)[0][0]
    names=set()
    for cp,name in font.getBestCmap().items():
        if cp not in points:continue
        names.add(name);names.update(layer.name for layer in font['COLR'].ColorLayers[name])
        assert name in font['COLR'].ColorLayers
        assert font['hmtx'][name]==ink['hmtx'][name]
        a,b=RecordingPen(),RecordingPen()
        font.getGlyphSet()[name].draw(a);ink.getGlyphSet()[name].draw(b)
        assert a.value==b.value
    for name in names:
        glyph=font['glyf'][name]
        if glyph.numberOfContours:
            assert font['hmtx'][name][1]==glyph.xMin
            assert glyph.xMin>=0 and glyph.xMax<=font['hmtx'][name][0]
            assert -5<=glyph.yMin<=glyph.yMax<=765


def test_hobbes_uses_full_source_resolution_and_true_curves():
    review=json.loads((ROOT/'assets/emoji-concepts/production-review.json').read_text())
    records={row['emoji']:row for row in review['drawings']}
    font=TTFont(ROOT/review['font']['file'],recalcBBoxes=False)
    for text in ['🐅','🐯']:
        assert records[text]['resolution']==1024 and records[text]['curves']
        glyph=font['glyf'][font.getBestCmap()[ord(text)]]
        assert sum(not(flag&1) for flag in glyph.flags)>100


def test_curved_tracing_retains_counter_winding():
    import numpy as np
    from tools.font.build_adventure_emoji import outline
    y,x=np.mgrid[:96,:96];radius=(x-48)**2+(y-48)**2
    ring=(radius<32**2)&(radius>14**2)
    glyph=outline(ring,5,curves=True)
    assert glyph.numberOfContours==2
    assert any(not(flag&1) for flag in glyph.flags)
    areas=[];start=0
    for end in glyph.endPtsOfContours:
        points=list(glyph.coordinates[start:end+1]);start=end+1
        areas.append(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])))
    assert areas[0]*areas[1]<0,'inner counter must remain a hole'
