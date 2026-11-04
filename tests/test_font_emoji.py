"""Custom glyph inventory, colour layers and presentation must agree."""
import json
from functools import lru_cache
import pytest
from pathlib import Path
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import shape

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT/'assets/fonts/dad-emoji.woff2'


@lru_cache(maxsize=2)
def _production_font(mtime_ns,size):
    # Tests inspect this model without mutating it. Rebuilds get a fresh model.
    return TTFont(PATH)


def production_font():
    stat=PATH.stat()
    return _production_font(stat.st_mtime_ns,stat.st_size)


def test_custom_emoji_have_real_outlines_and_valid_colour_layers():
    font = production_font()
    review = json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    assert set(font.getBestCmap()) - set(review['componentOnly']) == {int(g['codepoint'][2:],16) for g in review['glyphs'] if 'codepoint' in g}
    assert len(font.getBestCmap()) == 1459
    assert font['COLR'].version == 0
    for cp,glyph in font.getBestCmap().items():
        if cp in review['componentOnly']:
            assert font['glyf'][glyph].numberOfContours == 0
            continue
        assert font['glyf'][glyph].numberOfContours > 0
        painted=0
        for layer in font['COLR'].ColorLayers[glyph]:
            # Quantized palettes can retain unused colour buckets. They are
            # valid empty layers; the base and painted artwork must be real.
            count=font['glyf'][layer.name].numberOfContours
            assert count>=0
            painted+=count>0
            assert layer.colorID < len(font['CPAL'].palettes[0])
        assert painted>0
    palette = font['CPAL'].palettes[0]
    assert [(c.red,c.green,c.blue) for c in palette] == [tuple(c) for c in review['palette']]


def test_heart_text_and_emoji_presentation_are_distinct_glyphs():
    assert shape(PATH,'❤',True) == shape(PATH,'❤\ufe0e',True)
    assert shape(PATH,'❤\ufe0f',True) != shape(PATH,'❤\ufe0e',True)


def test_skin_tones_ligate_to_five_distinct_coloured_drawings_with_white_cuffs():
    font=production_font()
    shapes=[]
    for i in range(5):
        text='👍'+chr(0x1f3fb+i)
        shaped=shape(PATH,text,True)
        assert len(shaped)==1
        assert shaped[0][0]!=0
        name=font.getGlyphName(shaped[0][0]); shapes.append(name)
        layers=font['COLR'].ColorLayers[name]
        assert [layer.colorID for layer in layers]==[0,6+i,1]
        assert font['glyf'][layers[1].name].numberOfContours>0
        hand=font['glyf'][layers[1].name]
        whole=font['glyf'][layers[0].name]
        assert hand.xMin>whole.xMin+50  # The cuff to the left stays white.
    assert len(set(shapes))==5
    tones=font['CPAL'].palettes[0][6:11]
    brightness=[.2126*c.red+.7152*c.green+.0722*c.blue for c in tones]
    assert all(a-b>15 for a,b in zip(brightness,brightness[1:]))


def test_every_advertised_custom_sequence_shapes_as_one_real_coloured_glyph():
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    font=production_font()
    assert len(manifest['sequences'])==5533
    for text in manifest['sequences']:
        shaped=shape(PATH,text,True)
        assert len(shaped)==1,repr(text)
        assert shaped[0][0]!=0 and shaped[0][1]>0,repr(text)
        name=font.getGlyphName(shaped[0][0])
        assert font['glyf'][name].numberOfContours>0
        assert name in font['COLR'].ColorLayers
    assert not any(chr(cp) in manifest['sequences'] for cp in manifest['componentOnly'])


def test_neutral_astronaut_zwj_and_modifiers_keep_helmet_and_suit_white():
    font=production_font()
    glyphs=[]
    for tone in ['',*[chr(cp) for cp in range(0x1f3fb,0x1f400)]]:
        result=shape(PATH,'🧑'+tone+'‍🚀',True)
        assert len(result)==1 and result[0][0]!=0
        name=font.getGlyphName(result[0][0]);glyphs.append(name)
        if tone:
            layers=font['COLR'].ColorLayers[name]
            assert [layer.colorID for layer in layers]==[0,6+ord(tone)-0x1f3fb,1]
            face=font['glyf'][layers[1].name]; whole=font['glyf'][layers[0].name]
            assert face.yMin>whole.yMin+150
            assert face.xMin>whole.xMin and face.xMax<whole.xMax
    assert len(set(glyphs))==6


def test_emoji_font_and_manifest_rebuild_identically(tmp_path):
    import hashlib
    import importlib.util
    spec=importlib.util.spec_from_file_location('build_emoji',ROOT/'tools/font/build_emoji.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    manifest=ROOT/'js/emoji-manifest.js'
    products=[PATH,ROOT/'assets/fonts/dad-emoji-ink.woff2',manifest,ROOT/'output/imagegen/emoji-production/glyph-review.json']
    before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in products]
    module.build(output_root=tmp_path)
    rebuilt=[tmp_path/path.relative_to(ROOT) for path in products]
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in rebuilt]==before
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in products]==before


def test_keycaps_have_twelve_distinct_drawings_and_identical_qualification_forms():
    font=production_font();names=[];drawings=[]
    for char in '#*0123456789':
        plain=shape(PATH,char+'\u20e3',True)
        qualified=shape(PATH,char+'\ufe0f\u20e3',True)
        assert plain==qualified and len(plain)==1
        name=font.getGlyphName(plain[0][0]);names.append(name)
        drawings.append(tuple(font['glyf'][name].coordinates))
        assert name==f'key{ord(char):X}.cap'
        assert font['glyf'][name].numberOfContours>=3
        assert [layer.colorID for layer in font['COLR'].ColorLayers[name]]==[0,1]
    assert len(set(names))==12
    assert len(set(drawings))==12


def test_heart_colours_preserve_semantic_distinctions_and_custom_ink():
    font=production_font();palette=font['CPAL'].palettes[0]
    review=json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    colours=[]
    source=font['glyf']['u2764']
    for item in review['glyphs']:
        if item.get('sourceGlyph')!='u2764': continue
        cp=int(item['codepoint'][2:],16);name=font.getBestCmap()[cp]
        assert font['glyf'][name].coordinates==source.coordinates
        layers=font['COLR'].ColorLayers[name]
        assert [l.name for l in layers]==['u2764.layer0','u2764.layer1','u2764.layer2']
        assert layers[0].colorID==0 and layers[2].colorID==1
        c=palette[layers[1].colorID];rgb=(c.red,c.green,c.blue)
        assert rgb==tuple(item['rgb']);colours.append(rgb)
        shaped=shape(PATH,chr(cp),True)
        assert len(shaped)==1 and font.getGlyphName(shaped[0][0])==name
    assert len(colours)==len(set(colours))==11


def test_geometric_emoji_keep_size_colour_and_fill_distinctions():
    font=production_font();palette=font['CPAL'].palettes[0]
    review=json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    shapes=[g for g in review['glyphs'] if 'shape' in g]
    assert len(shapes)==24
    for item in shapes:
        cp=int(item['codepoint'][2:],16);name=font.getBestCmap()[cp]
        layers=font['COLR'].ColorLayers[name]
        c=palette[layers[0].colorID]
        assert (c.red,c.green,c.blue)==tuple(item['rgb'])
        assert layers[1].colorID==1
        glyph=font['glyf'][name]
        assert glyph.numberOfContours==(1 if item['colour']=='black' else 2)
        assert abs(glyph.xMax-glyph.xMin-item['size'])<8
        assert abs(glyph.yMax-glyph.yMin-item['size'])<8
    for group in [[0x25AA,0x25FE,0x25FC,0x2B1B],[0x25AB,0x25FD,0x25FB,0x2B1C]]:
        widths=[font['hmtx'][font.getBestCmap()[cp]][0] for cp in group]
        assert all(a<b for a,b in zip(widths,widths[1:]))
        for cp in group:
            assert shape(PATH,chr(cp),True)==shape(PATH,chr(cp)+'\ufe0e',True)==shape(PATH,chr(cp)+'\ufe0f',True)


def test_circle_emoji_are_circular_rather_than_rounded_squares():
    import math
    from fontTools.pens.recordingPen import RecordingPen
    font=production_font();gs=font.getGlyphSet()
    for cp,size in [(0x1F534,700),(0x26AA,550)]:
        pen=RecordingPen();gs[f'u{cp:X}.fill'].draw(pen)
        centre=(50+size/2,350);radius=size/2
        previous=None
        for op,points in pen.value:
            if op=='moveTo': previous=points[0]
            elif op=='qCurveTo':
                control,end=points
                for t in [0,.25,.5,.75,1]:
                    p=[(1-t)**2*previous[j]+2*(1-t)*t*control[j]+t*t*end[j] for j in (0,1)]
                    assert abs(math.dist(p,centre)/radius-1)<.02
                previous=end


def test_approved_faces_preserve_enclosed_white_interiors_and_distinct_ink():
    from fontTools.pens.areaPen import AreaPen
    from fontTools.pens.recordingPen import RecordingPen
    font = production_font()
    glyphs = font.getGlyphSet()
    drawings = []
    for cp in [0x1F60A, 0x1F606, 0x1F610, 0x1F634,
               0x1F601, 0x1F603, 0x1F604, 0x1F605, 0x1F609, 0x1F60B,
               0x1F60E, 0x1F611, 0x1F642, 0x1F641, 0x1F62E, 0x1F62F,
               0x1F61B, 0x1F61C, 0x1F61D, 0x1F92A, 0x1F928, 0x1F9D0,
               0x1F913, 0x1F910, 0x1F644, 0x1F60F, 0x1F612, 0x1F62C,
               0x1F615, 0x1F61F, 0x1F61E, 0x1F614, 0x1F616, 0x1F623,
               0x1F629, 0x1F62B, 0x1F624, 0x1F620, 0x1F643, 0x1F636,
               0x1F637, 0x1F912, 0x1F915, 0x1F927, 0x1F971, 0x1F62A,
               0x1F924, 0x1F635, 0x1F632, 0x1F626, 0x1F627, 0x1F622]:
        name = font.getBestCmap()[cp]
        layers = font['COLR'].ColorLayers[name]
        assert [layer.colorID for layer in layers] == [0, 1]
        areas = []
        for layer in layers:
            pen = AreaPen(glyphs)
            glyphs[layer.name].draw(pen)
            areas.append(abs(pen.value))
        # A broken contour must not reduce the white layer to the ink alone.
        assert areas[0] > areas[1] * 2
        pen = RecordingPen()
        glyphs[name].draw(pen)
        drawings.append(repr(pen.value))
        base = font['glyf'][layers[0].name]
        assert 0 < base.xMin < base.xMax < font['hmtx'][name][0]
        assert 750 <= max(base.yMax-base.yMin, base.xMax-base.xMin) <= 761
    assert len(set(drawings)) == 52


def test_mouthless_and_upside_down_faces_keep_their_defining_features():
    font = production_font()

    def interior_contours(cp):
        glyph = font['glyf'][font.getBestCmap()[cp]]
        coordinates, ends, _ = glyph.getCoordinates(font['glyf'])
        start = 0
        features = []
        for end in ends:
            points = coordinates[start:end+1]
            start = end+1
            xs, ys = zip(*points)
            bounds = min(xs), min(ys), max(xs), max(ys)
            # Exclude the outer and inner edges of the enclosing face outline.
            if bounds[2]-bounds[0] < (glyph.xMax-glyph.xMin)*.6:
                features.append(bounds)
        return features

    eyes = interior_contours(0x1F636)
    assert len(eyes) == 2  # No mouth, nose or eyebrow ink.
    assert all(x1-x0 < y1-y0 for x0, y0, x1, y1 in eyes)
    inverted = interior_contours(0x1F643)
    assert len(inverted) == 3
    mouth = max(inverted, key=lambda b: b[2]-b[0])
    assert all(mouth[1] > b[3] for b in inverted if b != mouth)


def test_licensed_music_preserves_note_groups_and_pinned_provenance():
    import hashlib
    font = production_font()
    review = json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    records = [r for r in review['glyphs'] if r.get('category') == 'music']
    assert {int(r['codepoint'][2:], 16) for r in records} == {ord(c) for c in '🥁🎷🎺🎸🎻🎹🎵🎶🎼🎤🎧📻'}
    for r in records:
        assert r['sourceWeight'] == 400
        assert r['penTreatment']['appliedStrength'] > 0
        assert not r['penTreatment']['fallback']
    for char, groups in [('🎵', 1), ('🎶', 3)]:
        name = font.getBestCmap()[ord(char)]
        assert font['glyf'][name].numberOfContours == groups
    source = json.loads((ROOT/'data/font-sources/noto-emoji.json').read_text())
    for entry in source['files']:
        assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest() == entry['sha256']
    assert source['files'][0]['build_target'] == 'emoji'
    assert 'SIL Open Font License' in font['name'].getDebugName(13)
    assert 'Google LLC' in font['name'].getDebugName(0)
    assert font['name'].getDebugName(1) == 'Dad Emoji'


def test_clock_hands_show_all_hours_and_half_hours_after_treatment(monkeypatch):
    import numpy as np
    from scipy.ndimage import map_coordinates
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    from fontTools.pens.recordingPen import RecordingPen
    font = production_font()
    glyphs = font.getGlyphSet()
    drawings = []
    for cp in range(0x1F550, 0x1F568):
        name = font.getBestCmap()[cp]
        ink = raster(glyphs, name).astype(float)
        hour = (cp-0x1F550) % 12 + 1
        half = cp >= 0x1F55C
        # Clockwise from twelve. Half-hour hands sit between hour marks.
        for angle, radii in [((hour*30+15*half)%360, np.arange(35, 54)),
                             (180 if half else 0, np.arange(35, 81))]:
            candidates = np.deg2rad(np.arange(angle-8, angle+9))[:, None]
            x = 191.5+np.sin(candidates)*radii
            y = 191.5-np.cos(candidates)*radii
            scores = map_coordinates(ink, [y, x], order=1).mean(axis=1)
            assert max(scores) > .75, (hex(cp), angle, max(scores))
        pen = RecordingPen(); glyphs[name].draw(pen)
        drawings.append(repr(pen.value))
        assert shape(PATH, chr(cp), True) == shape(PATH, chr(cp)+'\ufe0e', True)
        assert shape(PATH, chr(cp), True) == shape(PATH, chr(cp)+'\ufe0f', True)
    assert len(set(drawings)) == 24


@pytest.mark.parametrize('category,symbols', [
    ('household', '🚪🛗🪞🪟🛏🛋🪑🚽🪠🚿🛁🪒🧴🧷🧹🧺🧻🪣🧼🫧🪥🧽🛒🧳'),
    ('science', '⚗🧪🧫🧬🔬🔭📡🩺🩻🩼💊💉'),

    ('recreation', '🎯🪀🪁🎱🔮🪄🎮🕹🎰🎲🧩🧸🪅🪩🪆🃏🎴🎭🖼🎨🧵🪡🧶🪢🎪'),
    ('celebrations', '🎀🎁🎃🎄🎆🎇🧨🎈🎉🎊🎋🎍🎎🎏🎐🎑🎟🎫'),
    ('electronics', '📱📲☎📞📟📠🔋🪫🔌💻🖥🖨⌨🖱🖲💽💾💿📀🧮🎥🎞📽🎬📺📷📸📹📼🔍🔎🕯💡🔦🏮🪔'),
    ('clothing', '👑👒🎩🎓🧢🪖⛑🧣🧤🧥🧦👔👕👖👗👘🥻🩱🩲🩳👙👚👛👜👝🎒🩴👞👟🥾🥿👠👡🩰👢🥼🦺🥽'),
    ('produce', '🍇🍈🍉🍊🍋🍌🍍🥭🍐🍑🍒🍓🫐🥝🍅🫒🥥🥑🍆🥔🥕🌽🌶🫑🥒🥬🥦🧄🧅🥜🫘🌰🫚🫛'),
    ('timepieces', '⌚⏰⏱⏲🕰⌛⏳'),
    ('stationery', '✏✒🖋🖊🖌🖍📝💼📁📂🗂📅📆🗒🗓📇📋📌📍📎🖇📏📐✂🗃🗄🗑'),

    ('places', '🏔⛰🌋🗻🏕🏖🏜🏝🏞🏟🏛🏗🏘🏚🌁🌃🏙🌄🌅🌆🌇🌉♨🎠🎡🎢🗼🗽🗾🗺🌐🧭'),
    ('buildings', '🏠🏡🏢🏣🏤🏥🏦🏨🏩🏪🏫🏬🏭🏯🏰💒⛪🕌🛕🕍⛩🕋⛲🛖'),
    ('sky', '🌑🌒🌓🌔🌕🌖🌗🌘🌙🌚🌛🌜🌝🌞⭐🌟🌠🌌☀☁⛅⛈🌤🌥🌦🌧🌨🌩🌪🌫🌬🌀🌂☂☔⛱⚡❄☃⛄☄💧🌊'),
    ('dining', '🍦🍧🍨🍩🍪🎂🍰🧁🥧🍫🍬🍭🍮🍯🍼🥛☕🫖🍵🍶🍾🍷🍸🍹🍺🍻🥂🥃🫗🥤🧋🧃🧉🧊🥢🍽🍴🥄🔪🫙🏺'),
    ('food', '🍞🥐🥖🫓🥨🥯🥞🧇🧀🍖🍗🥩🥓🍔🍟🍕🌭🥪🌮🌯🫔🥙🧆🥚🍳🥘🍲🫕🥣🥗🍿🧈🧂🥫🍱🍘🍙🍚🍛🍜🍝🍠🍢🍣🍤🍥🥮🍡🥟🥠🥡'),
    ('sports', '⚽⚾🥎🏀🏐🏈🏉🎾🥏🎳🏏🏑🏒🥍🏓🏸🥊🥋🥅⛳⛸🎣🤿🎽🎿🛷🥌'),
    ('plants', '💐🌸💮🪷🏵🌹🥀🌺🌻🌼🌷🪻🌱🪴🌲🌳🌴🌵🌾🌿☘🍀🍁🍂🍃🪹🪺🍄'),
    ('birds', '🦃🐔🐓🐣🐤🐥🐦🐧🕊🦅🦆🦢🦉🦤🪶🦩🦚🦜🪽🪿'),
    ('wildlife', '🐸🐊🐢🦎🐍🐲🐉🦕🦖🐳🐋🐬🦭🐟🐠🐡🦈🐙🐚🪸🪼🦀🦞🦐🦑🦪🐌🦋🐛🐜🐝🪲🐞🦗🪳🕷🕸🦂🦟🪰🪱🦠'),
    ('transport_extra', '🚀🚁🚉🚊🚋🚏🚒🚓🚖🚞🚟🚠🚡🛴🛵🛫🛬🛝🛞🛟🛢'),
    ('transport', '🚗🚕🚙🚌🚎🚐🚚🚛🚜🛺🚂🚃🚄🚅🚆🚇🚈🚝🚢⛵🚤🛥🛶⛴'),
    ('tools', '🛠⚒🔨⛏🔧🪛🔩⚙🗜⚖🔗⛓🪝🧰🧲🪜🪚🪓🪤🧯🔑🗝🔒🔓'),
    ('expressions', '🤣🫠😇🥰😍🤩😘😗😚😙🥲🤑🤗🤭🫢🫣🤫🫡🫥🤥🫨😌🥴🤠🥳🥸🫤🥹😨😰😥😱😓😺😸😹😻😼😽🙀😿😾🙈🙉🙊'),
    ('mammals', '🐵🐒🦍🦧🐶🐕🦮🐩🐺🦊🦝🐱🐈🦁🐯🐅🐆🐴🫎🫏🐎🦄🦓🦌🦬🐮🐂🐃🐄🐷🐖🐗🐽🐏🐑🐐🐪🐫🦙🦒🐘🦣🦏🦛🐭🐁🐀🐹🐰🐇🐿🦫🦔🦇🐻🐨🐼🦥🦦🦨🦘🦡🐾'),
])
def test_licensed_objects_remain_distinct_with_guarded_ink_and_variants(category, symbols):
    from fontTools.pens.recordingPen import RecordingPen
    font = production_font(); glyphs = font.getGlyphSet()
    review = json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    # SVG accessories share semantic categories but have their own multi-layer
    # candidate comparisons. These invariants apply to the pinned font donor.
    records = [r for r in review['glyphs'] if r.get('category') == category
               and r.get('source') == 'build/unicode-sources/noto-emoji/NotoEmoji.ttf']
    expected = set(map(ord, symbols))
    assert {int(r['codepoint'][2:], 16) for r in records} == expected
    drawings = []
    for cp in sorted(expected):
        name = font.getBestCmap()[cp]
        pen = RecordingPen(); glyphs[name].draw(pen)
        drawings.append(repr(pen.value))
        assert font['hmtx'][name][0] > 0
        assert len(font['COLR'].ColorLayers[name]) == 2
    assert len(set(drawings)) == len(expected)
    for r in records:
        assert r['penTreatment']['appliedStrength'] > 0
        assert not r['penTreatment']['fallback']
        name = font.getBestCmap()[int(r['codepoint'][2:], 16)]
        expected_contours = r['penTreatment']['sourceComponents'] + r['penTreatment']['sourceHoles']
        assert font['glyf'][name].numberOfContours >= expected_contours, r['codepoint']
    variation_file = ROOT/'data/unicode/18.0.0/emoji/emoji-variation-sequences.txt'
    for line in variation_file.read_text().splitlines():
        fields = line.split('#')[0].strip().split(';')
        if len(fields) < 2:
            continue
        sequence = [int(s, 16) for s in fields[0].split()]
        if len(sequence) == 2 and sequence[0] in expected:
            assert shape(PATH, ''.join(map(chr, sequence)), True) == shape(PATH, chr(sequence[0]), True)


def test_padlock_shackle_is_closed_only_for_locked_symbol(monkeypatch):
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font = production_font()
    glyphs = font.getGlyphSet()
    # Check the compiled drawing, not just distinct glyph IDs: only the locked
    # shackle encloses a white region in the upper part of the icon.
    for cp, expected in [(0x1F512, True), (0x1F513, False)]:
        ink = raster(glyphs, font.getBestCmap()[cp])
        labels, count = ndimage.label(ndimage.binary_fill_holes(ink) & ~ink)
        upper_enclosures = [i for i in range(1, count+1)
                            if (labels == i).sum() > 100
                            and ndimage.center_of_mass(labels == i)[0] < len(ink)*.4]
        assert bool(upper_enclosures) == expected


def test_dotted_face_keeps_twelve_separate_dashes_and_three_features(monkeypatch):
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font = production_font()
    ink = raster(font.getGlyphSet(), font.getBestCmap()[0x1FAE5])
    # Filling or joining the dotted perimeter would change the symbol's meaning.
    labels, count = ndimage.label(ink)
    assert count == 15
    assert not (ndimage.binary_fill_holes(ink) & ~ink).any()
    centres = [ndimage.center_of_mass(labels == i) for i in range(1, count+1)]
    central = [(y, x) for y, x in centres if 120 < y < 260 and 120 < x < 260]
    assert len(central) == 3  # Two eyes and a mouth, surrounded by twelve dashes.


def test_compound_emoji_qualification_and_component_boundaries():
    font = production_font()
    review = json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    records = [r for r in review['glyphs'] if r.get('category') == 'compounds']
    assert {r['sequence'] for r in records} == {
        '😶‍🌫️','😮‍💨','😵‍💫','🙂‍↔️','🙂‍↕️','🐈‍⬛','🐕‍🦺','🐻‍❄️','⛓️‍💥','🐦‍⬛','🍋‍🟩','🍄‍🟫'}
    assert sum(len(r['qualificationForms']) for r in records) == 17
    identities = set()
    for record in records:
        canonical = shape(PATH, record['sequence'], True)
        assert len(canonical) == 1 and canonical[0][1] > 0
        name = font.getGlyphName(canonical[0][0])
        assert name == record['glyphName']
        identities.add(name)
        assert len(font['COLR'].ColorLayers[name]) == (3 if record['sequence'] in {'🍋‍🟩','🍄‍🟫'} else 2)
        treatment = record['penTreatment']
        assert treatment['appliedStrength'] > 0 and not treatment['fallback']
        assert font['glyf'][name].numberOfContours >= treatment['sourceComponents'] + treatment['sourceHoles']
        for form in record['qualificationForms']:
            assert shape(PATH, form, True) == canonical
            # Adjacent standalone characters must not accidentally form the
            # compound, and repeated compounds must not absorb one another.
            assert shape(PATH, form.replace('\u200d',''), True) != canonical
            assert shape(PATH, form+form, True) == canonical+canonical
    assert len(identities) == 12


def test_animal_base_and_compound_ink_distinctions_and_paw_toes(monkeypatch):
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font = production_font()
    glyphs = font.getGlyphSet()

    def ink(text):
        result = shape(PATH, text, True)
        assert len(result) == 1 and result[0][1] > 0
        return raster(glyphs, font.getGlyphName(result[0][0]))

    assert ink('🐈‍⬛').sum() > ink('🐈').sum()*1.5
    assert ink('🐻').sum() > ink('🐻‍❄️').sum()*2
    dog_ids = [shape(PATH, s, True)[0][0] for s in ['🐕','🦮','🐕‍🦺']]
    assert len(set(dog_ids)) == 3
    # Two isolated pads and eight isolated toes survive tracing.
    assert ndimage.label(ink('🐾'))[1] == 10


def test_black_bird_fill_and_spider_web_openings_survive_compilation(monkeypatch):
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font = production_font()
    glyphs = font.getGlyphSet()

    def ink(text):
        result = shape(PATH, text, True)
        assert len(result) == 1
        return raster(glyphs, font.getGlyphName(result[0][0]))

    assert ink('🐦‍⬛').sum() > ink('🐦').sum()*2
    web = ink('🕸')
    labels, count = ndimage.label(ndimage.binary_fill_holes(web) & ~web)
    # Two rings of six open sectors must not be filled or merged by tracing.
    assert sum((labels == i).sum() >= 4 for i in range(1,count+1)) == 12


def test_shamrock_and_four_leaf_clover_keep_their_leaf_counts(monkeypatch):
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font = production_font()
    for char, leaves in [('☘',3),('🍀',4)]:
        ink = raster(font.getGlyphSet(), font.getBestCmap()[ord(char)])
        interior = ndimage.binary_fill_holes(ink) & ~ink
        distance = ndimage.distance_transform_edt(interior)
        # Erode through the narrow joins to isolate the broad leaf interiors.
        # Two erosion depths guard against an accidental one-pixel split.
        for radius in [24,28]:
            labels, _ = ndimage.label(distance > radius)
            areas = np.bincount(labels.ravel())[1:]
            assert sum(areas > 100) == leaves, char


def test_nest_with_eggs_retains_two_enclosed_eggs_above_the_bowl(monkeypatch):
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font = production_font()
    for char, eggs in [('🪹',0),('🪺',2)]:
        ink = raster(font.getGlyphSet(), font.getBestCmap()[ord(char)])
        labels, count = ndimage.label(ndimage.binary_fill_holes(ink) & ~ink)
        upper_details = [i for i in range(1,count+1)
                         if 1000 < (labels == i).sum() < 10000
                         and ndimage.center_of_mass(labels == i)[0] < 190]
        assert len(upper_details) == eggs, char


def test_colour_face_underpaint_preserves_every_enclosed_white_detail(monkeypatch):
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_colour_faces import COLOURS, prepare_face
    source = TTFont(ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf')
    for cp in COLOURS:
        (white, fill, ink), report, _ = prepare_face(source, cp)
        labels, _ = ndimage.label(white & ~ink)
        sizes = np.bincount(labels.ravel()); sizes[0] = 0
        main = labels == sizes.argmax()
        details = (labels != 0) & ~main
        assert np.array_equal(fill & ~ink, main), hex(cp)
        assert not (fill & details).any(), hex(cp)
        assert not (ink & ~fill).any(), hex(cp)
        assert report['whiteDetailPixels'] == int(details.sum())


def test_colour_faces_keep_pdf_fills_inside_ink_and_preserve_white_details():
    import hashlib
    import numpy as np
    import pymupdf
    from PIL import Image
    from fontTools.pens.svgPathPen import SVGPathPen
    font = production_font()
    glyphs = font.getGlyphSet()
    review = json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    records = [r for r in review['glyphs'] if r.get('category') == 'colour-faces']
    expected = {0x1F621:'red',0x1F922:'green',0x1F975:'orange',0x1F976:'light blue'}
    assert {int(r['codepoint'][2:],16):r['colour'] for r in records} == expected
    palette_path = ROOT/'output/imagegen/emoji-production/colour-face-palette-source.json'
    palette = json.loads(palette_path.read_text())
    colours = {s['colour']:tuple(s['rgb']) for s in palette['samples']}

    def mask(name, advance):
        pen = SVGPathPen(glyphs); glyphs[name].draw(pen)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{advance}" height="1000"><rect width="100%" height="100%" fill="white"/><path transform="translate(0 850) scale(1 -1)" d="{pen.getCommands()}" fill="black"/></svg>'
        document = pymupdf.open(stream=svg.encode(),filetype='svg')
        pdf = pymupdf.open('pdf',document.convert_to_pdf())
        pix = pdf[0].get_pixmap(matrix=pymupdf.Matrix(.4,.4),alpha=False)
        return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128

    for record in records:
        cp = int(record['codepoint'][2:],16)
        name = font.getBestCmap()[cp]
        layers = font['COLR'].ColorLayers[name]
        assert len(layers) == 3 and layers[0].colorID == 0 and layers[-1].colorID == 1
        c = font['CPAL'].palettes[0][layers[1].colorID]
        assert (c.red,c.green,c.blue) == colours[record['colour']] == tuple(record['rgb'])
        assert record['paletteSha256'] == hashlib.sha256(palette_path.read_bytes()).hexdigest()
        assert record['penTreatment']['appliedStrength'] > 0 and not record['penTreatment']['fallback']
        advance = font['hmtx'][name][0]
        white, fill, ink = [mask(layer.name,advance) for layer in layers]
        assert not (fill & ~white).any()
        assert fill.sum() > white.sum()*.25
        # The colour must continue under the ink: abutting layers produce pale
        # seams after antialiasing. Allow raster/contour rounding at the rim.
        assert (fill & ink).sum() > ink.sum()*.98
        if cp in {0x1F975,0x1F976}:
            assert (white & ~fill & ~ink).sum() > white.sum()*.1
    assert colours['red'][0] > colours['red'][1]*2
    assert colours['green'][1] > max(colours['green'][0],colours['green'][2])
    assert colours['orange'][0] > colours['orange'][1] > colours['orange'][2]
    assert colours['light blue'][2] > colours['light blue'][1] > colours['light blue'][0]


def test_baseball_and_softball_keep_opposite_ink_polarities(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font = production_font()
    glyphs = font.getGlyphSet()
    baseball = raster(glyphs, font.getBestCmap()[ord('⚾')])
    softball = raster(glyphs, font.getBestCmap()[ord('🥎')])
    # The reviewed monochrome donor distinguishes the stitched balls with a
    # white baseball and dark softball. Preserve that distinction after tracing.
    assert softball.sum() > baseball.sum()*2


def test_moon_phases_keep_light_fraction_and_waxing_waning_direction(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font = production_font()
    glyphs = font.getGlyphSet()
    masks = {c:raster(glyphs, font.getBestCmap()[ord(c)]) for c in '🌑🌒🌓🌔🌕🌖🌗🌘'}
    # A new moon is dark, then the illuminated fraction increases to full.
    amounts = [int(masks[c].sum()) for c in '🌑🌒🌓🌔🌕']
    assert all(a-b > masks['🌑'].size*.025 for a,b in zip(amounts,amounts[1:]))
    # Waxing phases have their dark region on the left; waning on the right.
    # Require a clear imbalance without assuming a specific crescent width.
    for c in '🌒🌓🌔':
        mask = masks[c]; middle = mask.shape[1]//2
        assert int(mask[:,:middle].sum())-int(mask[:,middle:].sum()) > mask.sum()*.1, c
    for c in '🌖🌗🌘':
        mask = masks[c]; middle = mask.shape[1]//2
        assert int(mask[:,middle:].sum())-int(mask[:,:middle].sum()) > mask.sum()*.1, c


def test_solid_new_moon_remains_round_after_pen_pressure(monkeypatch):
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font = production_font()
    mask = raster(font.getGlyphSet(), font.getBestCmap()[0x1F311])
    center = ndimage.center_of_mass(mask)
    y,x = np.nonzero(mask & ~ndimage.binary_erosion(mask))
    radii = np.hypot(y-center[0],x-center[1])
    # Allow hand-drawn variation, but reject the lumpy silhouette produced by
    # treating the filled disk's radius as a narrow pen stroke's radius.
    assert radii.std()/radii.mean() < .06



def test_new_moon_face_is_dark_with_white_features(monkeypatch):
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font = production_font()
    glyphs = font.getGlyphSet()
    dark = raster(glyphs, font.getBestCmap()[0x1F31A])
    light = raster(glyphs, font.getBestCmap()[0x1F31D])
    assert dark.sum() > light.sum()*2
    labels, count = ndimage.label(ndimage.binary_fill_holes(dark) & ~dark)
    # Two eyes, nose, mouth and lower-lip accent remain as white features.
    assert sum((labels == i).sum() >= 4 for i in range(1,count+1)) == 5


def test_gesture_modifiers_preserve_ink_and_use_the_sampled_skin_palette(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_gestures import POINTS
    from fontTools.pens.recordingPen import RecordingPen
    font=production_font();glyphs=font.getGlyphSet()
    records=json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    standard=set()
    for line in (ROOT/'data/unicode/18.0.0/emoji/emoji-sequences.txt').read_text().splitlines():
        fields=line.split('#')[0].strip().split(';')
        if len(fields)>1 and fields[1].strip()=='RGI_Emoji_Modifier_Sequence':
            standard.add(''.join(chr(int(cp,16)) for cp in fields[0].split()))
    gestures=[r for r in records['glyphs'] if r.get('category')=='gestures']
    assert {int(r['codepoint'][2:],16) for r in gestures}==set(POINTS)
    for record in gestures:
        assert record['penTreatment']['appliedStrength']>0 and not record['penTreatment']['fallback']
    for cp in POINTS:
        base=font.getBestCmap()[cp];neutral=RecordingPen();glyphs[base].draw(neutral)
        for i in range(5):
            text=chr(cp)+chr(0x1F3FB+i)
            assert text in standard
            assert text in records['skinToneSequences']
            shaped=shape(PATH,text,True);assert len(shaped)==1 and shaped[0][0]
            name=font.getGlyphName(shaped[0][0]);pen=RecordingPen();glyphs[name].draw(pen)
            assert pen.value==neutral.value
            layers=font['COLR'].ColorLayers[name]
            assert [l.colorID for l in layers]==[0,6+i,1]
            assert font['hmtx'][name]==font['hmtx'][base]
            assert layers[-1].name==font['COLR'].ColorLayers[base][-1].name


def test_gesture_skin_masks_colour_fingers_but_leave_air_gaps(monkeypatch):
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_gestures import prepare
    from fontTools.pens.pointInsidePen import PointInsidePen
    donor=TTFont(ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf')
    compiled=production_font();glyphs=compiled.getGlyphSet()
    for cp,gaps in [(0x270A,0),(0x1F44E,0),(0x1F44C,1),(0x1F90C,1),(0x1F91E,1),(0x1FAF6,1),(0x1FAF7,0),(0x1FAF8,0),(0x1F64C,0)]:
        (white,skin,ink),report,_=prepare(donor,cp)
        assert not (skin&~white).any()
        assert ndimage.label(white&~ink&~skin)[1]==gaps
        assert skin.sum()>white.sum()*.25
        if not gaps:assert np.array_equal(skin,white)
        name=compiled.getGlyphName(shape(PATH,chr(cp)+'🏽',True)[0][0])
        skin_name=compiled['COLR'].ColorLayers[name][1].name
        ys,xs=np.nonzero(white);factor=760/max(xs.max()-xs.min()+1,ys.max()-ys.min()+1)
        for mask,inside in [(skin&~ink,True),(white&~ink&~skin,False)]:
            labels,count=ndimage.label(mask)
            for i in range(1,count+1):
                region=labels==i
                distance=ndimage.distance_transform_edt(region)
                if inside and distance.max()<2:continue  # Subpixel wrist-edge slivers.
                y,x=np.unravel_index(distance.argmax(),region.shape)
                point=((x-xs.min())*factor+50,760-(y-ys.min())*factor)
                pen=PointInsidePen(glyphs,point);glyphs[skin_name].draw(pen)
                assert pen.getResult()==inside,(hex(cp),i,inside)


def test_hourglass_sand_state_survives_compiled_pen_treatment(monkeypatch):
    import numpy as np
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    font=production_font();glyphs=font.getGlyphSet()
    for cp,has_upper_sand in [(0x231B,False),(0x23F3,True)]:
        ink=raster(glyphs,font.getBestCmap()[cp])
        ys,xs=np.where(ink)
        body=ink[ys.min():ys.max()+1,xs.min():xs.max()+1]
        h,w=body.shape
        # Sample the interior away from the glass rim: the completed hourglass
        # is empty above, while the running hourglass still contains sand.
        upper=body[int(.24*h):int(.38*h),int(.35*w):int(.65*w)].mean()
        lower=body[int(.7*h):int(.82*h),int(.35*w):int(.65*w)].mean()
        assert upper>.5 if has_upper_sand else upper<.05
        assert lower>.65


def test_apples_share_ink_but_keep_distinct_pdf_colour_and_underpaint(monkeypatch):
    import hashlib
    import numpy as np
    from fontTools.pens.recordingPen import RecordingPen
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_apples import prepare_apple
    source_record=json.loads((ROOT/'data/font-sources/noto-emoji.json').read_text())
    source=TTFont(ROOT/source_record['files'][0]['path'])
    (white,fill,ink),treatment,_=prepare_apple(source)
    assert not (fill & ~white).any()
    assert np.all(fill[ink])  # Underpaint avoids pale seams against the outline.
    assert (fill & ~ink).sum()>white.sum()*.5
    assert treatment['sourceComponents']==1 and treatment['sourceHoles']==1
    font=production_font();glyphs=font.getGlyphSet()
    palette_path=ROOT/'output/imagegen/emoji-production/apple-palette-source.json'
    palette=json.loads(palette_path.read_text())
    reused=palette['reusedPalette'];original=json.loads((ROOT/reused['path']).read_text())
    assert hashlib.sha256((ROOT/reused['path']).read_bytes()).hexdigest()==reused['sha256']
    assert all(s in original['samples'] for s in palette['samples'])
    review=json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    records=[r for r in review['glyphs'] if r.get('category')=='apples']
    assert {r['codepoint'] for r in records}=={'U+1F34E','U+1F34F'}
    expected={0x1F34E:(174,41,42),0x1F34F:(134,177,152)}
    drawings=[];advances=[]
    for record in records:
        cp=int(record['codepoint'][2:],16);name=font.getBestCmap()[cp]
        assert record['sourceCodepoint']=='U+1F34F'
        assert record['paletteSha256']==hashlib.sha256(palette_path.read_bytes()).hexdigest()
        layers=font['COLR'].ColorLayers[name]
        assert len(layers)==3 and layers[0].colorID==0 and layers[-1].colorID==1
        colour=font['CPAL'].palettes[0][layers[1].colorID]
        assert (colour.red,colour.green,colour.blue)==expected[cp]==tuple(record['rgb'])
        pen=RecordingPen();glyphs[layers[-1].name].draw(pen);drawings.append(pen.value)
        advances.append(font['hmtx'][name][0])
        assert len(shape(PATH,chr(cp),True))==1
    assert drawings[0]==drawings[1] and advances[0]==advances[1]


def test_coloured_produce_sequences_preserve_rind_flesh_and_mushroom_details(monkeypatch):
    import hashlib
    import numpy as np
    import uharfbuzz as hb
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_sequences import source_ligature
    from emoji_licensed import raster
    from emoji_sequence_colour import colour_masks
    from pen_translate import Settings,translate
    record=json.loads((ROOT/'data/font-sources/noto-emoji.json').read_text())
    path=ROOT/record['files'][0]['path'];source=TTFont(path)
    shaping=hb.Font(hb.Face(path.read_bytes()));shaping.set_variations({'wght':400})
    font=production_font()
    for sequence,colour in [('🍋‍🟩',(134,177,152)),('🍄‍🟫',(139,106,68))]:
        source_name=source_ligature(source,shaping,sequence)
        original=raster(source.getGlyphSet(location={'wght':400}),source_name)
        seed=int.from_bytes(hashlib.sha256(sequence.encode()).digest()[:4],'big')
        treated,_=translate(original,Settings(strength=1.7,seed=seed));ink=np.asarray(treated)<128
        (white,fill,final_ink),info=colour_masks(ink,sequence)
        assert not (fill & ~white).any()
        interiors,count=ndimage.label(white & ~ink)
        sizes=np.bincount(interiors.ravel());sizes[0]=0
        if sequence.startswith('🍋'):
            assert count==6 and np.array_equal(ink,final_ink)
            assert np.all(fill[ink])
            assert np.all(fill[interiors==sizes.argmax()])
            assert not fill[(interiors>0)&(interiors!=sizes.argmax())].any()
        else:
            stem=interiors==sizes.argmax();highlights=(interiors>0)&~stem
            assert count==3 and ndimage.label(highlights)[1]==2
            assert not fill[stem|highlights].any()
            assert not final_ink[stem|highlights].any()
            assert (fill & ~final_ink).sum()>white.sum()*.3
            assert np.array_equal(ink[info['stemTop']:],final_ink[info['stemTop']:])
        shaped=shape(PATH,sequence,True);assert len(shaped)==1
        name=font.getGlyphName(shaped[0][0]);layers=font['COLR'].ColorLayers[name]
        assert len(layers)==3 and [layers[0].colorID,layers[-1].colorID]==[0,1]
        c=font['CPAL'].palettes[0][layers[1].colorID]
        assert (c.red,c.green,c.blue)==colour
        assert font['glyf'][layers[1].name].numberOfContours>0
        assert font['glyf'][layers[-1].name].numberOfContours>0


def test_open_hand_wrists_close_colour_only_without_changing_ink(monkeypatch):
    import numpy as np
    from scipy import ndimage
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_gestures import prepare
    from emoji_licensed import raster
    from pen_translate import Settings,translate
    font=TTFont(ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf')
    for cp,closures in [(0x1FAF7,1),(0x1FAF8,1),(0x1F64C,2)]:
        (white,skin,ink),report,name=prepare(font,cp)
        original=raster(font.getGlyphSet(location={'wght':400}),name)
        treated,_=translate(original,Settings(strength=1.7,seed=cp))
        assert np.array_equal(ink,np.asarray(treated)<128)
        assert report['fillOnlyWristClosures']==closures
        assert np.array_equal(white,skin)
        # Both open palms must receive substantial fill, not merely coloured
        # antialiasing beneath ink or the already-enclosed narrow fingers.
        added=skin & ~ndimage.binary_fill_holes(ink)
        assert added.sum()>ink.sum()*.5
        labels,count=ndimage.label(added)
        areas=np.bincount(labels.ravel())[1:]
        assert sum(areas>1000)==closures


def test_mixed_handshakes_assign_both_tones_and_preserve_ink(monkeypatch):
    import numpy as np
    from scipy import ndimage
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.pens.pointInsidePen import PointInsidePen
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_gestures import prepare, mixed_handshakes, handshake_masks
    source=TTFont(ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf')
    (white,skin,ink),_,_=prepare(source,0x1F91D)
    first,second=handshake_masks(white,ink)
    # Reviewed anatomical probes: left wrist/main palm and lowest fingertip
    # belong to hand one; right wrist/thumb and four curled fingers to hand two.
    probes=[(123,200,False),(218,315,False),(326,182,True),
            (124,257,True),(150,275,True),(169,298,True),(195,303,True)]
    for x,y,belongs_to_second in probes:
        assert white[y,x] and not ink[y,x]
        assert bool(second[y,x])==belongs_to_second
    font=production_font();glyphs=font.getGlyphSet()
    neutral=RecordingPen();glyphs['u1F91D'].draw(neutral)
    ys,xs=np.nonzero(white);factor=760/max(xs.max()-xs.min()+1,ys.max()-ys.min()+1)
    forms=mixed_handshakes(ROOT);names=[]
    for text in forms:
        result=shape(PATH,text,True);assert len(result)==1 and result[0][0]
        name=font.getGlyphName(result[0][0]);names.append(name)
        pen=RecordingPen();glyphs[name].draw(pen);assert pen.value==neutral.value
        assert font['hmtx'][name]==font['hmtx']['u1F91D']
        layers=font['COLR'].ColorLayers[name]
        assert [l.colorID for l in layers]==[0,6+ord(text[1])-0x1F3FB,6+ord(text[4])-0x1F3FB,1]
        assert layers[-1].name=='u1F91D.ink'
        for x,y,belongs_to_second in probes:
            point=((x-xs.min())*factor+50,760-(y-ys.min())*factor)
            pen=PointInsidePen(glyphs,point);glyphs[layers[2].name].draw(pen)
            assert pen.getResult()==belongs_to_second
        # Consecutive ligatures must not consume neighbours or suppress advances.
        repeated=shape(PATH,text+text,True)
        assert repeated==result+result
    assert len(set(names))==20


def test_standalone_vest_promotion_preserves_service_dog_ligature():
    font=production_font()
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    assert 0x1F9BA not in manifest['componentOnly']
    vest=shape(PATH,'🦺',True);dog=shape(PATH,'🐕‍🦺',True)
    assert len(vest)==len(dog)==1 and vest!=dog
    for result in (vest,dog):
        name=font.getGlyphName(result[0][0])
        assert font['glyf'][name].numberOfContours>0 and result[0][1]>0
    assert shape(PATH,'🦺🐕‍🦺🦺',True)==vest+dog+vest
    assert font.getGlyphName(dog[0][0])=='seq.1F415.200D.1F9BA'


def test_licensed_compiler_rejects_unchanged_fallback_before_emitting_glyphs(monkeypatch):
    import numpy as np
    from PIL import Image
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    import emoji_licensed
    monkeypatch.setattr(emoji_licensed, 'POINTS', [0x1F6AA])
    def unchanged(ink, settings):
        return Image.fromarray(np.where(ink, 0, 255).astype('uint8')), {
            'appliedStrength': 0, 'fallback': True,
            'sourceComponents': 1, 'sourceHoles': 0,
        }
    monkeypatch.setattr(emoji_licensed, 'translate', unchanged)
    glyphs, metrics, cmap, layers, review = {}, {}, {}, {}, []
    with pytest.raises(AssertionError, match='No safe expressive treatment for U\\+1F6AA'):
        emoji_licensed.add_licensed(ROOT, glyphs, metrics, cmap, layers, review, None)
    assert not any((glyphs, metrics, cmap, layers, review))


@pytest.mark.parametrize('cp,probes', [
    (0x1F476, [(247,151,True),(195,165,False),(200,284,False),(128,219,False)]),
    (0x1F9D2, [(242,284,True)]),
    (0x1F466, [(166,92,False),(100,114,False),(249,127,False),(218,288,True)]),
    (0x1F467, [(74,152,False),(302,180,False),(229,281,True)]),
    (0x1F9D1, [(236,285,True)]),
    (0x1F468, [(226,280,True)]),
    (0x1F469, [(157,280,True)]),
    (0x1F9D3, [(120,111,False),(231,281,True)]),
    (0x1F474, [(174,84,False),(231,277,True)]),
    (0x1F475, [(153,79,False),(235,280,True)]),
    (0x1F9D4, [(192,158,True),(183,229,False),(143,305,True)]),
])
def test_people_tones_colour_skin_without_hair_hats_bows_teeth_or_blankets(cp, probes, monkeypatch):
    import numpy as np
    from fontTools.pens.pointInsidePen import PointInsidePen
    from fontTools.pens.recordingPen import RecordingPen
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_people import prepare
    source=TTFont(ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf')
    (white,skin,ink),report,_=prepare(source,cp)
    font=production_font();glyphs=font.getGlyphSet();name=font.getBestCmap()[cp]
    ys,xs=np.nonzero(white);scale=760/max(xs.max()-xs.min()+1,ys.max()-ys.min()+1)
    neutral=RecordingPen();glyphs[name].draw(neutral)
    assert report['appliedStrength']>0 and not report['fallback']
    assert font['glyf'][name].numberOfContours>=report['sourceComponents']+report['sourceHoles']
    for x,y,is_skin in probes:
        x+=report['padding'];y+=report['padding']
        assert white[y,x] and not ink[y,x]
        assert bool(skin[y,x])==is_skin
        point=((x-xs.min())*scale+50,760-(y-ys.min())*scale)
        pen=PointInsidePen(glyphs,point);glyphs[name+'.skin'].draw(pen)
        assert pen.getResult()==is_skin
    forms=[]
    for i in range(5):
        text=chr(cp)+chr(0x1F3FB+i);shaped=shape(PATH,text,True)
        assert len(shaped)==1 and shaped[0][0] and shaped[0][1]>0
        variant=font.getGlyphName(shaped[0][0]);forms.append(variant)
        assert font['hmtx'][variant]==font['hmtx'][name]
        layers=font['COLR'].ColorLayers[variant]
        assert [l.colorID for l in layers]==[0,6+i,1]
        assert [l.name for l in layers]==[name+'.white',name+'.skin',name+'.ink']
        pen=RecordingPen();glyphs[variant].draw(pen);assert pen.value==neutral.value
        assert shape(PATH,text+text,True)==shaped+shaped
    assert len(set(forms))==5


def test_person_promotion_keeps_astronaut_tone_ligatures_and_adjacent_people():
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    assert 0x1F9D1 not in manifest['componentOnly']
    font=production_font()
    for tone in ['',*[chr(cp) for cp in range(0x1F3FB,0x1F400)]]:
        person='🧑'+tone;astronaut=person+'‍🚀'
        p,a=shape(PATH,person,True),shape(PATH,astronaut,True)
        assert len(p)==len(a)==1 and p!=a
        assert font['glyf'][font.getGlyphName(p[0][0])].numberOfContours>0
        assert font.getGlyphName(a[0][0]).startswith('astronaut')
        assert shape(PATH,person+astronaut+person,True)==p+a+p


@pytest.mark.parametrize('canonical,probes', [('👱', [(116, 114, False), (234, 280, True)]), ('🧔\u200d♂️', [(193, 173, True), (189, 232, False), (244, 300, True)]), ('🧔\u200d♀️', [(188, 167, True), (192, 230, False), (152, 310, True)]), ('👨\u200d🦰', [(233, 281, True)]), ('👨\u200d🦱', [(156, 283, True)]), ('👨\u200d🦳', [(218, 123, False), (237, 287, True)]), ('👨\u200d🦲', [(229, 275, True)]), ('👩\u200d🦰', [(233, 284, True)]), ('🧑\u200d🦰', [(240, 284, True)]), ('👩\u200d🦱', [(231, 286, True)]), ('🧑\u200d🦱', [(239, 283, True)]), ('👩\u200d🦳', [(128, 86, False), (216, 292, True)]), ('🧑\u200d🦳', [(158, 88, False), (235, 282, True), (89, 144, False)]), ('👩\u200d🦲', [(225, 276, True)]), ('🧑\u200d🦲', [(158, 281, True)]), ('👱\u200d♀️', [(168, 96, False), (218, 287, True)]), ('👱\u200d♂️', [(187, 101, False), (235, 288, True)])])
def test_person_hair_gender_forms_keep_independent_skin_hair_and_qualification(canonical, probes, monkeypatch):
    import numpy as np
    import uharfbuzz as hb
    from scipy import ndimage
    from fontTools.pens.pointInsidePen import PointInsidePen
    from fontTools.pens.recordingPen import RecordingPen
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_person_forms import prepare, FORMS
    from emoji_sequences import qualified_forms
    source=ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf'
    donor=TTFont(source);shaper=hb.Font(hb.Face(source.read_bytes()));shaper.set_variations({'wght':400})
    (white,skin,hair,ink,original),report,_=prepare(donor,shaper,canonical)
    font=production_font();glyphs=font.getGlyphSet()
    result=shape(PATH,canonical,True);assert len(result)==1 and result[0][0]
    base=font.getGlyphName(result[0][0]);neutral=RecordingPen();glyphs[base].draw(neutral)
    ys,xs=np.nonzero(white);scale=760/max(xs.max()-xs.min()+1,ys.max()-ys.min()+1)
    for x,y,is_skin in probes:
        x+=report['padding'];y+=report['padding']
        assert white[y,x] and not original[y,x]
        assert bool(skin[y,x])==is_skin
        point=((x-xs.min())*scale+50,760-(y-ys.min())*scale)
        pen=PointInsidePen(glyphs,point);glyphs[base+'.skin'].draw(pen)
        assert pen.getResult()==is_skin
    colour=FORMS[canonical][2]
    if colour=='orange':
        # No colour in the chin/cheek border, eyes or mouth. Only the thick
        # connected hair shares the outer outline component in this donor.
        face_rows=np.where(skin)[0];cut=round(face_rows.min()+.7*np.ptp(face_rows))
        assert not hair[cut:].any()
        labels,count=ndimage.label(original);sizes=np.bincount(labels.ravel());sizes[0]=0
        features=(labels!=0)&(labels!=sizes.argmax())
        assert features.any() and np.array_equal(ink[features],original[features])
        assert not ((original & ~ink) & ~hair).any()
    if colour:
        distance=ndimage.distance_transform_edt(hair & ~ink)
        y,x=np.unravel_index(distance.argmax(),distance.shape)
        assert distance[y,x]>3 and not skin[y,x]
        point=((x-xs.min())*scale+50,760-(y-ys.min())*scale)
        pen=PointInsidePen(glyphs,point);glyphs[base+'.hair'].draw(pen);assert pen.getResult()
        pen=PointInsidePen(glyphs,point);glyphs[base+'.ink'].draw(pen);assert not pen.getResult()
    names=[]
    for i in range(6):
        text=canonical[:1]+(chr(0x1F3FA+i) if i else '')+canonical[1:]
        expected=shape(PATH,text,True);assert len(expected)==1 and expected[0][0] and expected[0][1]>0
        name=font.getGlyphName(expected[0][0]);names.append(name)
        assert font['hmtx'][name]==font['hmtx'][base]
        pen=RecordingPen();glyphs[name].draw(pen);assert pen.value==neutral.value
        layers=font['COLR'].ColorLayers[name]
        assert layers[0].name==base+'.white' and layers[-1].name==base+'.ink'
        skin_layers=[l for l in layers if l.name==base+'.skin']
        assert [l.colorID for l in skin_layers]==([5+i] if i else [])
        hair_layers=[l for l in layers if l.name==base+'.hair']
        assert len(hair_layers)==bool(colour)
        if colour:
            c=font['CPAL'].palettes[0][hair_layers[0].colorID]
            assert (c.red,c.green,c.blue)==({'orange':(174,104,29),'yellow':(180,157,60)}[colour])
        for form in qualified_forms(ROOT,text):assert shape(PATH,form,True)==expected
        assert shape(PATH,text+text,True)==expected+expected
        if len(canonical)>1:
            prefix=text[:2] if i else text[:1]
            assert shape(PATH,prefix+text+prefix,True)==shape(PATH,prefix,True)+expected+shape(PATH,prefix,True)
    assert len(set(names))==6


def test_every_fully_qualified_person_subgroup_form_is_now_exactly_custom():
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    custom=set(manifest['sequences']);required=set();subgroup=None
    for line in (ROOT/'data/unicode/18.0.0/emoji/emoji-test.txt').read_text().splitlines():
        if line.startswith('# subgroup: '):subgroup=line.partition(': ')[2]
        fields=line.partition('#')[0].strip().split(';')
        if subgroup=='person' and len(fields)==2 and fields[1].strip()=='fully-qualified':
            required.add(''.join(chr(int(cp,16)) for cp in fields[0].split()))
    assert len(required)==168 and required<=custom
    assert len(manifest['sequences'])==len(custom)


@pytest.mark.parametrize('canonical,probes', [('🧑\u200d⚕️', [(190, 104, True), (304, 189, False), (83, 187, False), (113, 235, False), (81, 229, False), (269, 306, False), (139, 325, False), (101, 334, False)]), ('👨\u200d⚕️', [(189, 103, True), (306, 190, False), (87, 189, False), (90, 212, False), (88, 231, False), (270, 286, False), (136, 326, False), (96, 333, False)]), ('👩\u200d⚕️', [(197, 104, True), (85, 184, False), (303, 191, False), (117, 238, False), (84, 226, False), (273, 302, False), (136, 321, False), (97, 328, False)]), ('🧑\u200d🎓', [(185, 78, False), (225, 131, False), (154, 281, True)]), ('👨\u200d🎓', [(189, 80, False), (191, 127, False), (143, 282, True)]), ('👩\u200d🎓', [(188, 76, False), (257, 144, False), (226, 278, True)]), ('🧑\u200d🏫', [(126, 100, True), (273, 116, False), (72, 153, True), (254, 143, False), (191, 156, True), (95, 264, True), (258, 249, False), (224, 200, False), (293, 285, False), (213, 281, False)]), ('👨\u200d🏫', [(126, 102, True), (262, 114, False), (249, 140, False), (70, 154, True), (185, 157, True), (145, 273, True), (261, 244, False), (219, 202, False), (288, 302, False), (207, 277, False)]), ('👩\u200d🏫', [(131, 105, True), (250, 113, False), (223, 140, False), (74, 154, True), (188, 157, True), (146, 274, True), (280, 217, False), (225, 201, False), (283, 303, False), (201, 274, False)]), ('🧑\u200d⚖️', [(151, 274, True), (269, 183, False), (298, 195, False), (330, 209, False), (259, 302, False)]), ('👨\u200d⚖️', [(158, 263, True), (262, 193, False), (292, 203, False), (325, 213, False), (264, 306, False)]), ('👩\u200d⚖️', [(157, 271, True), (264, 186, False), (293, 198, False), (330, 205, False), (267, 309, False)]), ('🧑\u200d🌾', [(157, 71, False), (162, 103, False), (199, 144, False), (283, 280, False), (215, 288, True)]), ('👨\u200d🌾', [(203, 70, False), (185, 101, False), (188, 142, False), (289, 275, False), (220, 281, True)]), ('👩\u200d🌾', [(155, 74, False), (157, 106, False), (169, 144, False), (286, 279, False), (218, 289, True)]), ('🧑\u200d🍳', [(128, 87, False), (185, 271, True), (314, 226, False), (295, 202, False), (262, 315, False)]), ('👨\u200d🍳', [(168, 132, False), (182, 270, True), (314, 228, False), (295, 204, False), (260, 315, False)]), ('👩\u200d🍳', [(274, 269, False), (222, 542, True), (628, 448, False), (596, 399, False), (517, 629, False)]), ('🧑\u200d🔧', [(131, 98, False), (290, 166, False), (168, 273, True)]), ('👨\u200d🔧', [(123, 94, False), (292, 171, False), (171, 273, True)]), ('👩\u200d🔧', [(134, 95, False), (289, 166, False), (169, 273, True)]), ('🧑\u200d🏭', [(102, 71, False), (82, 116, False), (181, 271, True), (321, 173, False), (267, 192, False)]), ('👨\u200d🏭', [(109, 71, False), (205, 120, False), (181, 274, True), (325, 174, False), (276, 179, False)]), ('👩\u200d🏭', [(109, 72, False), (204, 118, False), (181, 272, True), (325, 176, False), (277, 178, False)]), ('🧑\u200d💼', [(123, 114, True), (257, 197, False), (301, 236, False), (311, 292, False), (268, 260, False), (267, 278, False)]), ('👨\u200d💼', [(104, 262, True), (259, 199, False), (304, 238, False), (313, 295, False), (259, 263, False), (266, 280, False)]), ('👩\u200d💼', [(124, 119, True), (261, 192, False), (300, 230, False), (264, 258, False), (310, 290, False), (266, 275, False)]), ('🧑\u200d🔬', [(158, 94, True), (143, 165, False), (72, 169, False), (311, 166, False), (232, 175, False), (267, 266, False), (114, 279, True)]), ('👨\u200d🔬', [(157, 97, True), (149, 170, False), (313, 159, False), (75, 169, False), (241, 173, False), (266, 263, False), (111, 280, True)]), ('👩\u200d🔬', [(158, 96, True), (146, 170, False), (308, 159, False), (73, 172, False), (237, 169, False), (267, 261, False), (115, 284, True)]), ('🧑\u200d💻', [(124, 82, False), (184, 132, True), (202, 255, False), (156, 298, False)]), ('👨\u200d💻', [(125, 80, False), (182, 131, True), (110, 254, False), (156, 297, False)]), ('👩\u200d💻', [(321, 212, False), (178, 136, True), (115, 256, False), (156, 301, False)]), ('🧑\u200d🎤', [(257, 285, True), (178, 186, False), (145, 257, False), (125, 272, False), (86, 299, False)]), ('👨\u200d🎤', [(262, 280, True), (174, 185, False), (144, 259, False), (127, 278, False), (86, 306, False)]), ('👩\u200d🎤', [(261, 283, True), (178, 187, False), (146, 261, False), (125, 274, False), (85, 302, False)]), ('🧑\u200d🎨', [(192, 100, False), (308, 113, False), (299, 138, False), (227, 145, False), (142, 279, True), (280, 167, False), (262, 290, False), (268, 206, False), (307, 219, False), (239, 239, False)]), ('👨\u200d🎨', [(174, 99, False), (308, 115, False), (301, 138, False), (97, 147, False), (116, 271, True), (282, 169, False), (261, 291, False), (269, 209, False), (305, 221, False), (238, 240, False), (284, 260, False)]), ('👩\u200d🎨', [(190, 99, False), (313, 119, False), (300, 140, False), (206, 142, False), (118, 270, True), (281, 170, False), (262, 293, False), (305, 223, False), (237, 241, False), (284, 262, False)]), ('🧑\u200d✈️', [(238, 86, False), (192, 121, False), (141, 119, False), (223, 122, False), (160, 135, False), (217, 137, False), (237, 286, True)]), ('👨\u200d✈️', [(241, 84, False), (193, 124, False), (241, 122, False), (142, 124, False), (220, 139, False), (159, 140, False), (236, 286, True)]), ('👩\u200d✈️', [(144, 82, False), (188, 123, False), (137, 119, False), (242, 125, False), (152, 136, False), (214, 139, False), (238, 293, True)]), ('👨\u200d🚀', [(307, 62, False), (293, 233, False), (199, 114, False), (54, 214, False), (324, 215, False), (190, 185, True), (274, 305, False)]), ('👩\u200d🚀', [(300, 230, False), (302, 65, False), (196, 114, False), (61, 210, False), (330, 212, False), (194, 220, True), (275, 309, False)]), ('🧑\u200d🚒', [(321, 232, False), (238, 242, False), (526, 244, False), (382, 158, False), (358, 187, False), (318, 317, False), (495, 579, True), (171, 443, False), (596, 448, False)]), ('👨\u200d🚒', [(160, 113, False), (121, 120, False), (192, 80, False), (264, 122, False), (180, 94, False), (126, 161, False), (245, 290, True), (297, 219, False), (83, 219, False)]), ('👩\u200d🚒', [(222, 117, False), (265, 120, False), (191, 78, False), (120, 121, False), (203, 92, False), (180, 156, False), (243, 288, True), (297, 219, False), (84, 221, False)])])
def test_profession_skin_excludes_uniforms_and_equipment(canonical, probes, monkeypatch):
    import numpy as np
    import uharfbuzz as hb
    from fontTools.pens.pointInsidePen import PointInsidePen
    from fontTools.pens.recordingPen import RecordingPen
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_professions import prepare
    from emoji_sequences import qualified_forms
    source=ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf'
    donor=TTFont(source);shaper=hb.Font(hb.Face(source.read_bytes()));shaper.set_variations({'wght':400})
    (white,skin,ink),report,_=prepare(donor,shaper,canonical)
    assert report['settings']['strength']==1.7 and report['appliedStrength']>0 and not report['fallback']
    font=production_font();glyphs=font.getGlyphSet()
    result=shape(PATH,canonical,True);assert len(result)==1 and result[0][0]
    base=font.getGlyphName(result[0][0]);neutral=RecordingPen();glyphs[base].draw(neutral)
    assert base.startswith('profession.')
    assert font['glyf'][base].numberOfContours>=report['sourceComponents']+report['sourceHoles']
    ys,xs=np.nonzero(white);scale=760/max(xs.max()-xs.min()+1,ys.max()-ys.min()+1)
    for x,y,is_skin in probes:
        x+=report['padding'];y+=report['padding']
        assert white[y,x] and not ink[y,x]
        assert bool(skin[y,x])==is_skin
        point=((x-xs.min())*scale+50,760-(y-ys.min())*scale)
        pen=PointInsidePen(glyphs,point);glyphs[base+'.skin'].draw(pen)
        assert pen.getResult()==is_skin
    names=[]
    for i in range(6):
        text=canonical[:1]+(chr(0x1F3FA+i) if i else '')+canonical[1:]
        expected=shape(PATH,text,True);assert len(expected)==1 and expected[0][0] and expected[0][1]>0
        name=font.getGlyphName(expected[0][0]);names.append(name)
        assert font['hmtx'][name]==font['hmtx'][base]
        pen=RecordingPen();glyphs[name].draw(pen);assert pen.value==neutral.value
        layers=font['COLR'].ColorLayers[name]
        assert [(l.name,l.colorID) for l in layers]==[(base+'.white',0)]+([(base+'.skin',5+i)] if i else [])+[(base+'.ink',1)]
        for form in qualified_forms(ROOT,text):assert shape(PATH,form,True)==expected
        assert shape(PATH,text+text,True)==expected+expected
        prefix=text[:2] if i else text[:1]
        assert shape(PATH,prefix+text+prefix,True)==shape(PATH,prefix,True)+expected+shape(PATH,prefix,True)
    assert len(set(names))==6


@pytest.mark.parametrize('canonical,probes', [('👮', [(145, 81, False), (192, 118, False), (126, 154, False), (205, 166, False), (234, 287, True)]), ('👮\u200d♂️', [(231, 85, False), (186, 122, False), (156, 167, False), (189, 170, False), (152, 285, True)]), ('👮\u200d♀️', [(144, 82, False), (195, 117, False), (167, 164, False), (205, 164, False), (230, 285, True)]), ('🕵️', [(124, 81, False), (216, 129, False), (134, 285, True), (274, 222, False), (239, 299, True), (184, 321, False)]), ('🕵️\u200d♂️', [(131, 82, False), (128, 133, False), (125, 281, True), (274, 223, False), (240, 300, True), (218, 287, False)]), ('🕵️\u200d♀️', [(185, 83, False), (189, 134, False), (134, 287, True), (269, 219, False), (236, 304, True), (183, 322, False)]), ('💂', [(189, 241, True), (265, 295, False)]), ('💂\u200d♂️', [(184, 241, True), (261, 295, False)]), ('💂\u200d♀️', [(191, 234, True), (259, 294, False)]), ('🥷', [(211, 149, True), (71, 195, False), (84, 235, False)]), ('👷', [(190, 135, False), (249, 296, True)]), ('👷\u200d♂️', [(247, 140, False), (248, 291, True)]), ('👷\u200d♀️', [(192, 137, False), (253, 288, True)]), ('🫅', [(113, 121, False), (140, 153, False), (245, 285, True)]), ('🤴', [(156, 116, False), (134, 154, False), (250, 290, True)]), ('👸', [(218, 111, False), (185, 145, False), (245, 285, True)]), ('👳', [(133, 62, False), (154, 84, False), (276, 112, False), (283, 151, False), (227, 287, True)]), ('👳\u200d♂️', [(144, 72, False), (131, 107, False), (130, 141, False), (278, 143, False), (236, 283, True)]), ('👳\u200d♀️', [(132, 76, False), (109, 115, False), (267, 101, False), (273, 142, False), (236, 280, True)]), ('👲', [(188, 82, False), (120, 107, False), (253, 103, False), (186, 135, False), (240, 282, True)]), ('🧕', [(268, 299, False), (185, 154, True)]), ('🤵', [(189, 108, True), (160, 311, False)]), ('🤵\u200d♂️', [(190, 105, True), (157, 310, False)]), ('🤵\u200d♀️', [(192, 105, True), (158, 308, False)]), ('👰', [(201, 58, False), (95, 179, False), (288, 179, False), (237, 285, True)]), ('👰\u200d♂️', [(202, 56, False), (290, 180, False), (96, 180, False), (152, 283, True)]), ('👰\u200d♀️', [(177, 57, False), (95, 175, False), (289, 177, False), (239, 283, True), (293, 228, False)])])
def test_outlined_roles_keep_skin_out_of_headwear_and_equipment(canonical, probes, monkeypatch):
    import numpy as np
    import uharfbuzz as hb
    from fontTools.pens.pointInsidePen import PointInsidePen
    from fontTools.pens.recordingPen import RecordingPen
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_roles import prepare
    from emoji_sequences import qualified_forms
    source=ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf'
    donor=TTFont(source);shaper=hb.Font(hb.Face(source.read_bytes()));shaper.set_variations({'wght':400})
    (white,skin,ink),report,_=prepare(donor,shaper,canonical)
    assert report['settings']['strength']==1.7 and report['appliedStrength']>0 and not report['fallback']
    font=production_font();glyphs=font.getGlyphSet()
    result=shape(PATH,canonical,True);assert len(result)==1 and result[0][0]
    base=font.getGlyphName(result[0][0]);neutral=RecordingPen();glyphs[base].draw(neutral)
    assert base.startswith('role.')
    assert font['glyf'][base].numberOfContours>=report['sourceComponents']+report['sourceHoles']
    ys,xs=np.nonzero(white);scale=760/max(xs.max()-xs.min()+1,ys.max()-ys.min()+1)
    for x,y,is_skin in probes:
        x+=report['padding'];y+=report['padding']
        assert white[y,x] and not ink[y,x]
        assert bool(skin[y,x])==is_skin
        point=((x-xs.min())*scale+50,760-(y-ys.min())*scale)
        pen=PointInsidePen(glyphs,point);glyphs[base+'.skin'].draw(pen)
        assert pen.getResult()==is_skin
    names=[]
    for i in range(6):
        text=canonical[:1]+chr(0x1F3FA+i)+canonical[1:].removeprefix('\ufe0f') if i else canonical
        expected=shape(PATH,text,True);assert len(expected)==1 and expected[0][0] and expected[0][1]>0
        name=font.getGlyphName(expected[0][0]);names.append(name)
        assert font['hmtx'][name]==font['hmtx'][base]
        pen=RecordingPen();glyphs[name].draw(pen);assert pen.value==neutral.value
        layers=font['COLR'].ColorLayers[name]
        assert [(l.name,l.colorID) for l in layers]==[(base+'.white',0)]+([(base+'.skin',5+i)] if i else [])+[(base+'.ink',1)]
        for form in qualified_forms(ROOT,text):assert shape(PATH,form,True)==expected
        assert shape(PATH,text+text,True)==expected+expected
        prefix=text[:2] if i else text[:1]
        assert shape(PATH,prefix+text+prefix,True)==shape(PATH,prefix,True)+expected+shape(PATH,prefix,True)
    assert len(set(names))==6


@pytest.mark.parametrize('key,probes', [('1f469_200d_1f37c', [(385, 222, True), (269, 300, True), (380, 449, False), (446, 379, True), (327, 372, False), (277, 463, True), (514, 394, False), (475, 477, False), (409, 472, False), (437, 450, False), (559, 490, False), (284, 537, False), (162, 604, False), (489, 599, False), (547, 573, False), (393, 609, False), (443, 560, False), (293, 618, False), (609, 624, False), (410, 694, True), (357, 648, False), (263, 698, False)]), ('1f9d1_200d_1f37c', [(456, 276, True), (508, 230, True), (255, 284, True), (384, 441, False), (448, 371, True), (279, 459, True), (323, 365, False), (516, 387, False), (427, 424, False), (442, 441, False), (482, 460, False), (558, 482, False), (292, 535, False), (170, 608, False), (494, 590, False), (410, 564, False), (449, 551, False), (549, 564, False), (301, 622, False), (612, 616, False), (414, 690, True), (362, 645, False), (272, 704, False)]), ('1f931', [(386, 235, True), (271, 315, True), (514, 390, False), (333, 406, False), (467, 413, True), (570, 439, False), (475, 483, True), (328, 480, False), (527, 512, False), (605, 552, False), (279, 533, False), (241, 628, False), (413, 571, False), (450, 589, False), (530, 607, False), (500, 605, False), (395, 646, True), (549, 608, False), (660, 623, False), (585, 660, False), (267, 692, False), (181, 702, True), (345, 711, False), (309, 704, False)]), ('1f930', [(355, 291, True), (414, 324, True), (352, 385, False), (381, 496, False), (217, 534, True), (517, 586, True), (513, 692, False)]), ('1fac3', [(349, 248, True), (436, 300, True), (360, 373, False), (387, 486, False), (221, 535, True), (520, 568, True), (508, 685, False)]), ('1fac4', [(337, 260, True), (430, 309, True), (356, 391, False), (394, 502, False), (230, 537, True), (525, 575, True), (514, 698, False)]), ('1f468_200d_1f37c', [(456, 274, True), (506, 206, True), (261, 274, True), (380, 443, False), (322, 360, False), (447, 378, False), (270, 448, True), (518, 394, False), (411, 469, False), (438, 448, False), (480, 479, False), (574, 492, False), (280, 523, False), (157, 588, False), (496, 601, False), (404, 578, False), (448, 561, False), (554, 577, False), (293, 607, False), (614, 628, False), (415, 693, True), (362, 643, False), (265, 691, False)])])
def test_detailed_svg_people_keep_anatomical_skin_masks_and_real_sequences(key, probes, monkeypatch):
    import numpy as np
    from fontTools.pens.pointInsidePen import PointInsidePen
    from fontTools.pens.recordingPen import RecordingPen
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_svg import prepare
    from emoji_sequences import qualified_forms
    canonical=''.join(chr(int(c,16)) for c in key.split('_'))
    (white,skin,ink),report=prepare(key)
    assert report['settings']['strength']==1.7 and report['appliedStrength']>0 and not report['fallback']
    font=production_font();glyphs=font.getGlyphSet()
    result=shape(PATH,canonical,True);assert len(result)==1 and result[0][0]
    base=font.getGlyphName(result[0][0]);assert base=='detailed.'+key.replace('_','.')
    neutral=RecordingPen();glyphs[base].draw(neutral)
    assert font['glyf'][base].numberOfContours>=report['sourceComponents']+report['sourceHoles']
    ys,xs=np.nonzero(white);scale=760/max(xs.max()-xs.min()+1,ys.max()-ys.min()+1)
    for x,y,is_skin in probes:
        x+=report['padding'];y+=report['padding']
        assert white[y,x] and not ink[y,x]
        assert bool(skin[y,x])==is_skin
        point=((x-xs.min())*scale+50,760-(y-ys.min())*scale)
        pen=PointInsidePen(glyphs,point);glyphs[base+'.skin'].draw(pen)
        assert pen.getResult()==is_skin
    names=[]
    for i in range(6):
        text=canonical[:1]+(chr(0x1F3FA+i) if i else '')+canonical[1:]
        expected=shape(PATH,text,True);assert len(expected)==1 and expected[0][0] and expected[0][1]>0
        name=font.getGlyphName(expected[0][0]);names.append(name)
        assert font['hmtx'][name]==font['hmtx'][base]
        pen=RecordingPen();glyphs[name].draw(pen);assert pen.value==neutral.value
        layers=font['COLR'].ColorLayers[name]
        assert [(l.name,l.colorID) for l in layers]==[(base+'.white',0)]+([(base+'.skin',5+i)] if i else [])+[(base+'.ink',1)]
        for form in qualified_forms(ROOT,text):assert shape(PATH,form,True)==expected
        assert shape(PATH,text+text,True)==expected+expected
        if len(canonical)>1:
            prefix=text[:2] if i else text[:1]
            assert shape(PATH,prefix+text+prefix,True)==shape(PATH,prefix,True)+expected+shape(PATH,prefix,True)
    assert len(set(names))==6


def test_person_role_subgroup_is_exactly_covered_and_svg_sources_are_pinned():
    import hashlib
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    custom=set(manifest['sequences']);required=set();subgroup=None
    for line in (ROOT/'data/unicode/18.0.0/emoji/emoji-test.txt').read_text().splitlines():
        if line.startswith('# subgroup: '):subgroup=line.partition(': ')[2]
        fields=line.partition('#')[0].strip().split(';')
        if subgroup=='person-role' and len(fields)==2 and fields[1].strip()=='fully-qualified':
            required.add(''.join(chr(int(cp,16)) for cp in fields[0].split()))
    assert len(required)==492 and required<=custom
    spec=json.loads((ROOT/'data/font-sources/noto-emoji-svg.json').read_text())
    svg=[f for f in spec['files'] if f['path'].endswith('.svg')]
    assert len(svg)==7 and sum(len(f['include_sequences']) for f in svg)==42
    for entry in spec['files']:
        raw=(ROOT/entry['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==entry['sha256']
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['git_blob_sha1']
    assert all(set(f['include_sequences'])<=custom for f in svg)
    assert 'Apache License' in (ROOT/'assets/fonts/licenses/NotoEmoji-SVG-Apache-2.0.txt').read_text()
    assert 'Copyright 2013 Google' in (ROOT/'assets/fonts/licenses/NotoEmoji-SVG-NOTICE.txt').read_text()


def test_visible_rocket_keeps_all_astronaut_substitutions_and_boundaries():
    font=production_font()
    rocket=shape(PATH,'🚀',True)
    assert len(rocket)==1 and rocket[0][0]>0 and rocket[0][1]>0
    assert font.getGlyphName(rocket[0][0])=='rocket'
    assert font['glyf']['rocket'].numberOfContours==8
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    assert 0x1F680 not in manifest['componentOnly'] and '🚀' in manifest['sequences']
    for person in '🧑👨👩':
        for tone in ['',*[chr(cp) for cp in range(0x1F3FB,0x1F400)]]:
            text=person+tone+'\u200d🚀';astronaut=shape(PATH,text,True)
            assert len(astronaut)==1 and astronaut[0][0]!=rocket[0][0]
            assert shape(PATH,'🚀'+text+'🚀',True)==rocket+astronaut+rocket
            assert shape(PATH,text+text,True)==astronaut+astronaut
    assert shape(ROOT/'assets/fonts/dad-emoji-ink.woff2','🚀',True)==rocket


def test_transport_expansion_retains_reviewed_source_details():
    records=json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())['glyphs']
    records={int(r['codepoint'][2:],16):r for r in records if r.get('category')=='transport_extra'}
    expected={0x1F680:8,0x1F681:7,0x1F689:14,0x1F68A:9,0x1F68B:13,0x1F68F:16,0x1F692:22,0x1F693:17,0x1F696:13,0x1F69E:27,0x1F69F:25,0x1F6A0:6,0x1F6A1:5,0x1F6F4:7,0x1F6F5:6,0x1F6EB:15,0x1F6EC:13,0x1F6DD:10,0x1F6DE:16,0x1F6DF:10,0x1F6E2:5}
    assert set(records)==set(expected)
    source=TTFont(ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf');font=production_font()
    for cp,count in expected.items():
        record=records[cp];treatment=record['penTreatment']
        assert record['sourceGlyph']==source.getBestCmap()[cp]
        assert record['sourcePixels']==384
        assert record['sourceWeight']==(350 if cp==0x1F696 else 400)
        assert treatment['sourceComponents']+treatment['sourceHoles']==count
        assert font['glyf'][font.getBestCmap()[cp]].numberOfContours==count


def test_standalone_mobility_equipment_preserves_details_and_compound_boundaries(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'tools/font'))
    from emoji_licensed import raster
    from pen_translate import Settings, translate
    from build_emoji import outline
    import numpy as np
    from scipy import ndimage
    source=TTFont(ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf')
    source_glyphs=source.getGlyphSet(location={'wght':400});font=production_font()
    manifest=json.loads((ROOT/'js/emoji-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    expected={'🦯':(1,5),'🦼':(2,6),'🦽':(2,5)}
    for text,(components,holes) in expected.items():
        cp=ord(text);name=font.getBestCmap()[cp]
        assert cp not in manifest['componentOnly'] and text in manifest['sequences']
        mask=raster(source_glyphs,source.getBestCmap()[cp],384)
        image,report=translate(mask,Settings(strength=1.7,seed=cp))
        assert report['appliedStrength']>0 and not report['fallback']
        assert (report['sourceComponents'],report['sourceHoles'])==(components,holes)
        ink=np.asarray(image)<128;white=ndimage.binary_fill_holes(ink)
        ys,xs=np.nonzero(white);scale=760/max(np.ptp(xs)+1,np.ptp(ys)+1)
        rebuilt=outline(ink,(xs.min(),ys.min(),scale))
        assert tuple(rebuilt.coordinates)==tuple(font['glyf'][name].coordinates)
        assert rebuilt.numberOfContours==components+holes
        standalone=shape(PATH,text,True)
        assert len(standalone)==1 and standalone[0][0]>0 and standalone[0][1]>0
        for person in '🧑👨👩':
            for tone in ['',*'🏻🏼🏽🏾🏿']:
                for direction in ['', '\u200d➡️']:
                    compound=person+tone+'\u200d'+text+direction
                    shaped=shape(PATH,compound,True)
                    assert len(shaped)==1 and shaped[0][0]!=standalone[0][0]
                    assert shape(PATH,text+compound+text,True)==standalone+shaped+standalone


def test_body_part_drawings_preserve_reviewed_details_and_eye_presentation():
    records=json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())['glyphs']
    records={int(r['codepoint'][2:],16):r for r in records if r.get('category')=='body_parts'}
    expected={0x1F9E0:6,0x1F9B7:3,0x1F9B4:2,0x1F440:5,0x1F441:4,0x1F445:2,0x1F444:5,0x1FAE6:4,0x1FAC0:10,0x1FAC1:10,0x1F9BE:14,0x1F9BF:9}
    assert set(records)==set(expected)
    font=production_font();source=TTFont(ROOT/'build/unicode-sources/noto-emoji/NotoEmoji.ttf')
    drawings=[]
    for cp,count in expected.items():
        record=records[cp];treatment=record['penTreatment'];glyph=font['glyf'][font.getBestCmap()[cp]]
        assert record['sourceGlyph']==source.getBestCmap()[cp]
        assert record['sourcePixels']==384 and record['sourceWeight']==400
        assert treatment['appliedStrength']>0 and not treatment['fallback']
        assert treatment['sourceComponents']+treatment['sourceHoles']==glyph.numberOfContours==count
        drawings.append(tuple(glyph.coordinates))
        text=chr(cp);one=shape(PATH,text,True)
        assert len(one)==1 and one[0][1]>0
        assert shape(PATH,text+text,True)==one+one
    assert len(set(drawings))==12
    assert shape(PATH,'👁',True)==shape(PATH,'👁️',True)==shape(PATH,'👁︎',True)
