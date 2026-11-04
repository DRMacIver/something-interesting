"""Trace the approved-direction imagegen atlas into a selective-colour font.

This is font compilation, not a replacement raster illustration. Keep the
original imagegen source and prompt intact for review and reproducibility.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.measure import find_contours, approximate_polygon
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from emoji_keycaps import add_keycaps, KEYS
from emoji_standalone_component_compiler import add_standalone_components, COMPONENT_NAMES
from emoji_hearts import add_hearts
from emoji_shapes import add_shapes
from emoji_apples import add_apples
from emoji_faces import add_faces
from emoji_licensed import add_licensed
from emoji_sequences import add_sequences
from emoji_colour_faces import add_colour_faces
from emoji_gestures import add_gestures
from emoji_people import add_people
from emoji_person_forms import add_person_forms
from emoji_professions import add_professions
from emoji_roles import add_roles
from emoji_detailed_people import add_detailed_people
from emoji_gesture_people import add_gesture_people
from emoji_activity_people import add_activity_people
from emoji_fantasy_beings import add_fantasy_beings
from emoji_symbol_tiles import add_symbol_tiles
from emoji_signs import add_signs
from emoji_expressions import add_expressions
from emoji_geometric import add_geometric
from emoji_hand_props import add_hand_props
from emoji_person_symbols import add_person_symbols
from emoji_game_medical import add_game_medical
from emoji_sound_controls import add_sound_controls
from emoji_awards_events import add_awards_events
from emoji_holding_hands import add_holding_hands
from emoji_family_tiles import add_family_tiles
from emoji_couples import add_couples
from emoji_flags import add_flags
from emoji_book_mail import add_book_mail
from emoji_money_clothing import add_money_clothing
from emoji_final_objects import add_final_objects,PROMOTABLE_COMPONENTS
from emoji_clothed_sport import add_clothed_sport
from build_emoji_ink import build_ink
from emoji_new_svg import add_new_svg

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'output/imagegen/emoji-production/atlas-v2.png'
PALETTE = [(255,255,255), (17,17,17), (138,30,43), (132,22,97), (187,116,36), (178,156,62)]
POINTS = [0x1F600,0x1F602,0x1F97A,0x1F914,0x1F62D,0x1F92F,0x1F608,0x1F480,0x2764,0x1F525,0x1F44D]


def outline(mask, transform):
    pen = TTGlyphPen(None)
    x0,y0,factor = transform
    for contour in find_contours(np.pad(mask.astype(float),1),0.5):
        contour = approximate_polygon(contour, tolerance=0.65)
        if len(contour) < 4:
            continue
        points = [(round((x-1-x0)*factor+50), round(760-(y-1-y0)*factor)) for y,x in contour]
        pen.moveTo(points[0])
        for point in points[1:-1]: pen.lineTo(point)
        pen.closePath()
    return pen.glyph()


def build(output_root=None):
    output_root=ROOT if output_root is None else Path(output_root)
    atlas = np.asarray(Image.open(SOURCE).convert('RGBA'))
    h,w = atlas.shape[:2]
    assert h % 3 == 0 and w % 4 == 0
    cellw,cellh = w//4,h//3
    glyphs = {'.notdef': TTGlyphPen(None).glyph()}
    metrics = {'.notdef': (860,0)}
    skin_record = json.loads((ROOT/'output/imagegen/emoji-production/skin-palette-source.json').read_text())
    assert hashlib.sha256((ROOT/skin_record['pdf']).read_bytes()).hexdigest() == skin_record['pdfSha256']
    palette = PALETTE + [tuple(rgb) for rgb in skin_record['skinTones']]
    cmap = {}; layers = {}; review = []
    for index,cp in enumerate(POINTS+[None]):
        row,col = divmod(index,4)
        cell = atlas[row*cellh:(row+1)*cellh,col*cellw:(col+1)*cellw]
        opaque = cell[:,:,3] >= 128
        labels,count = ndimage.label(opaque)
        sizes = np.bincount(labels.ravel())
        opaque &= sizes[labels] >= 12
        yy,xx = np.nonzero(opaque)
        x0,y0,x1,y1 = int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())
        assert x0 > 2 and y0 > 2 and x1 < cellw-3 and y1 < cellh-3, f'Clipped icon {cp:X}'
        factor = 760/max(x1-x0+1,y1-y0+1)
        transform = (x0,y0,factor)
        rgb = cell[:,:,:3].astype(float)
        ink = opaque & (rgb.max(axis=2) < 100)
        saturated = opaque & ~ink & (rgb.max(axis=2)-rgb.min(axis=2) > 40)
        name = f'u{cp:X}' if cp is not None else 'astronaut'
        advance = round((x1-x0+1)*factor)+100
        masks = [(opaque,0)]
        if cp == 0x2764: masks.append((saturated,2))
        if cp == 0x1F608: masks.append((saturated,3))
        if cp == 0x1F525:
            yellow = saturated & (rgb[:,:,1] > rgb[:,:,0]*0.55)
            masks.extend([(saturated & ~yellow,4),(yellow,5)])
        masks.append((ink,1))
        glyphs[name] = outline(ink,transform)  # Monochrome fallback remains drawn.
        metrics[name] = (advance,50)
        layers[name] = []
        for i,(mask,palette_index) in enumerate(masks):
            layer = f'{name}.layer{i}'
            glyphs[layer] = outline(mask,transform)
            metrics[layer] = (advance,50)
            layers[name].append((layer,palette_index))
        if cp in (0x1F44D, None):
            # The black seam separates the cuff from the hand. Colour only
            # the largest white interior component, retaining the white cuff.
            interiors, count = ndimage.label(opaque & (rgb.min(axis=2) > 100))
            areas = np.bincount(interiors.ravel()); areas[0] = 0
            hand = interiors == areas.argmax()
            assert areas.max() > 10000, 'Review skin interior segmentation'
            if cp == 0x1F44D: assert count == 2, 'Review hand/cuff segmentation'
            else: assert np.nonzero(hand)[0].max() < cellh*0.6, 'Face colour must not reach the suit'
            skin = name+'.skin'
            glyphs[skin] = outline(hand,transform); metrics[skin] = (advance,50)
            for i in range(5):
                variant = name+f'.tone{i+1}'
                glyphs[variant] = outline(ink,transform); metrics[variant] = (advance,50)
                layers[variant] = [(name+'.layer0',0),(skin,len(PALETTE)+i),(name+f'.layer{len(masks)-1}',1)]
        if cp is not None: cmap[cp] = name
        if cp == 0x2764:
            text_name = name+'.text'
            glyphs[text_name] = outline(ink,transform)
            metrics[text_name] = (advance,50)
            layers[text_name] = [(name+'.layer0',0),(name+f'.layer{len(masks)-1}',1)]
            cmap[cp] = text_name  # U+2764 defaults to text presentation.
        identity = {'codepoint':f'U+{cp:04X}'} if cp is not None else {'sequence':'🧑‍🚀'}
        review.append(dict(**identity,cell=index,bounds=[x0,y0,x1,y1],advance=advance))
    print('Building faces',flush=True)
    face_review = add_faces(ROOT,glyphs,metrics,cmap,layers,review,outline)
    tone_points = list(range(0x1F3FB,0x1F400))
    components = sorted(tone_points+[0x200D,0x1F9D1,0x1F680])
    for i,cp in enumerate(tone_points):
        name = f'tone{i+1}'
        glyphs[name] = TTGlyphPen(None).glyph(); metrics[name] = (0,0); cmap[cp] = name
    for cp,name in [(0x200D,'joiner'),(0x1F9D1,'person'),(0x1F680,'rocket')]:
        glyphs[name] = TTGlyphPen(None).glyph(); metrics[name] = (0,0); cmap[cp] = name
    astronaut_sequences = ['🧑‍🚀'] + ['🧑'+chr(cp)+'‍🚀' for cp in tone_points]
    print('Building hearts',flush=True)
    heart_review = add_hearts(ROOT,glyphs,metrics,cmap,layers,palette,review)
    print('Building shapes',flush=True)
    shape_variants = add_shapes(ROOT,glyphs,metrics,cmap,layers,palette,review,heart_review)
    shape_variants += add_licensed(ROOT,glyphs,metrics,cmap,layers,review,outline)
    components.remove(0x1F680)
    add_apples(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    add_colour_faces(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    print('Building gestures',flush=True)
    gesture_sequences, gesture_rules, gesture_variants = add_gestures(ROOT,glyphs,metrics,cmap,layers,review,outline)
    shape_variants += gesture_variants
    print('Building people',flush=True)
    people_sequences, people_rules = add_people(ROOT,glyphs,metrics,cmap,layers,review,outline)
    components.remove(0x1F9D1)
    print('Building person forms',flush=True)
    person_form_sequences, person_form_components, person_form_rules, person_form_variations, person_form_tones = add_person_forms(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components += person_form_components
    print('Building professions',flush=True)
    profession_sequences, profession_components, profession_rules, profession_variations, profession_tones = add_professions(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components += profession_components
    print('Building roles',flush=True)
    role_sequences, role_components, role_rules, role_variations, role_tones = add_roles(ROOT,glyphs,metrics,cmap,layers,review,outline)
    components += role_components
    print('Building detailed people',flush=True)
    detailed_sequences, detailed_components, detailed_rules, detailed_tones = add_detailed_people(ROOT,glyphs,metrics,cmap,layers,review,outline)
    components += detailed_components
    print('Building gesture people',flush=True)
    gesture_person_sequences, gesture_person_components, gesture_person_rules, gesture_person_tones = add_gesture_people(ROOT,glyphs,metrics,cmap,layers,review,outline)
    components += gesture_person_components
    # Mixed wrestling sequences use the visible fight-cloud glyph as a component.
    print('Building new svg',flush=True)
    new_svg_sequences,new_svg_rules = add_new_svg(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)

    print('Building activity people',flush=True)
    activity_sequences, activity_components, activity_rules, activity_tones = add_activity_people(ROOT,glyphs,metrics,cmap,layers,review,outline)
    components += activity_components
    print('Building fantasy beings',flush=True)
    fantasy_sequences, fantasy_components, fantasy_rules = add_fantasy_beings(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components += fantasy_components

    print('Building clothed sport',flush=True)
    clothed_sequences,clothed_rules = add_clothed_sport(ROOT,glyphs,metrics,cmap,layers,review,outline)

    print('Building keycaps',flush=True)
    keycap_sequences, keycap_components, keycap_rules, keycap_review = add_keycaps(ROOT,glyphs,metrics,cmap,layers)
    components = sorted(components + keycap_components)
    print('Building sequences',flush=True)
    compound_sequences, compound_components, compound_rules, compound_variations = add_sequences(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components = sorted(components + compound_components)
    print('Building symbol tiles',flush=True)
    tile_sequences, tile_variations, promoted_components = add_symbol_tiles(ROOT,glyphs,metrics,cmap,layers,review,outline)
    components = [cp for cp in components if cp not in promoted_components]
    print('Building signs',flush=True)
    sign_sequences, sign_variations, promoted_signs = add_signs(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components = [cp for cp in components if cp not in promoted_signs]
    print('Building expressions',flush=True)
    expression_sequences, expression_variations, promoted_expressions, expression_rules, expression_components = add_expressions(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components = [cp for cp in components if cp not in promoted_expressions] + expression_components
    print('Building geometric',flush=True)
    geometric_sequences, geometric_variations, promoted_geometric = add_geometric(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components = [cp for cp in components if cp not in promoted_geometric]
    print('Building hand props',flush=True)
    hand_prop_sequences, hand_prop_variations, hand_prop_rules, hand_prop_tones = add_hand_props(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    print('Building person symbols',flush=True)
    person_symbol_sequences, person_symbol_variations, person_symbol_rules = add_person_symbols(ROOT,glyphs,metrics,cmap,layers,review,outline)
    print('Building game medical',flush=True)
    game_medical_sequences, game_medical_variations, promoted_game_medical = add_game_medical(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components = [cp for cp in components if cp not in promoted_game_medical]
    print('Building sound controls',flush=True)
    sound_control_sequences, sound_control_variations, promoted_sound_controls = add_sound_controls(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    assert not promoted_sound_controls
    print('Building awards events',flush=True)
    award_event_sequences, award_event_variations, promoted_awards_events = add_awards_events(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    assert not promoted_awards_events
    print('Building holding hands',flush=True)
    holding_sequences, holding_rules = add_holding_hands(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    print('Building family tiles',flush=True)
    family_tile_sequences, family_tile_variations, family_tile_rules = add_family_tiles(ROOT,glyphs,metrics,cmap,layers,review,outline)
    assert not family_tile_variations
    print('Building couples',flush=True)
    couple_sequences, couple_rules = add_couples(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    print('Building flags',flush=True)
    flag_sequences, flag_variations, flag_rules, flag_components = add_flags(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components = sorted(components + flag_components)
    print('Building book mail',flush=True)
    book_mail_sequences, book_mail_variations = add_book_mail(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    print('Building money clothing',flush=True)
    money_clothing_sequences, money_clothing_variations = add_money_clothing(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    assert set(PROMOTABLE_COMPONENTS)<=set(components)
    print('Building final objects',flush=True)
    final_object_sequences, final_object_variations, final_object_rules = add_final_objects(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components=[cp for cp in components if cp not in PROMOTABLE_COMPONENTS]
    assert set(COMPONENT_NAMES)<=set(components)
    print('Building standalone components',flush=True)
    promoted_components=add_standalone_components(ROOT,glyphs,metrics,cmap,layers,palette,review,outline)
    components=[cp for cp in components if cp not in promoted_components]
    fb = FontBuilder(1000,isTTF=True)
    fb.setupGlyphOrder(list(glyphs))
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    # TT glyph drawings preserve the ink's actual bearing, including layers
    # with outlines that start further inside the common cell.
    for name,glyph in glyphs.items():
        glyph.recalcBounds(fb.font['glyf'])
        metrics[name] = (metrics[name][0],getattr(glyph,'xMin',0))
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=850,descent=-150)
    fb.setupOS2(sTypoAscender=850,sTypoDescender=-150,usWinAscent=850,usWinDescent=150)
    fb.setupNameTable(dict(familyName='Dad Emoji',styleName='Regular',uniqueFontIdentifier='DadEmoji-001',fullName='Dad Emoji',psName='DadEmoji',version='Version 0.001',copyright='Contains Noto Emoji outlines and modified SVG artwork: Copyright 2013 Google LLC. Modified as Dad Emoji.',licenseDescription='This Font Software is licensed under the SIL Open Font License, Version 1.1. See NotoEmoji-OFL.txt. Includes modified Apache-2.0 Noto SVG artwork; see NotoEmoji-SVG-Apache-2.0.txt and NotoEmoji-SVG-NOTICE.txt.',licenseInfoURL='https://openfontlicense.org/'))
    fb.setupPost();fb.setupMaxp()
    fb.font['COLR'] = buildCOLR(layers,version=0)
    fb.font['CPAL'] = buildCPAL([[tuple(c/255 for c in rgb)+(1.0,) for rgb in palette]])
    uvs = CmapSubtable.newSubtable(14);uvs.platformID=0;uvs.platEncID=5;uvs.language=0;uvs.cmap={}
    uvs.uvsDict = {0xFE0E:[(0x2764,None),(0x1F44D,None)],0xFE0F:[(0x2764,'u2764'),(0x1F44D,None)]}
    uvs.uvsDict[0xFE0F].extend((ord(c),None) for c in KEYS)
    for cp,vs in shape_variants: uvs.uvsDict.setdefault(vs,[]).append((cp,None))
    for cp,vs in compound_variations + person_form_variations + profession_variations + role_variations + tile_variations + sign_variations + expression_variations + geometric_variations + hand_prop_variations + person_symbol_variations + game_medical_variations + sound_control_variations + award_event_variations + flag_variations + book_mail_variations + money_clothing_variations + final_object_variations:
        if not any(base == cp for base,_ in uvs.uvsDict.get(vs,[])):
            uvs.uvsDict.setdefault(vs,[]).append((cp,None))
    # Browsers use cmap variation support when selecting an emoji font,
    # before GSUB gets the chance to consume the directional arrow.
    for sequence in activity_sequences + clothed_sequences + fantasy_sequences:
        for base,selector in zip(sequence,sequence[1:]):
            if ord(selector) not in (0xFE0E,0xFE0F): continue
            pairs=uvs.uvsDict.setdefault(ord(selector),[])
            if not any(cp==ord(base) for cp,_ in pairs): pairs.append((ord(base),None))
    fb.font['cmap'].tables.append(uvs)
    rules = flag_rules + '\n' + couple_rules + '\n' + family_tile_rules + '\n' + holding_rules + '\n' + '\n'.join(f'sub u1F44D tone{i+1} by u1F44D.tone{i+1};' for i in range(5))
    rules += '\nsub person joiner rocket by astronaut;\n'
    rules += '\n'.join(f'sub person tone{i+1} joiner rocket by astronaut.tone{i+1};' for i in range(5))
    rules += '\n' + keycap_rules
    rules += '\n' + final_object_rules
    rules += '\n' + compound_rules
    rules += '\n' + activity_rules
    rules += '\n' + fantasy_rules
    rules += '\n' + clothed_rules
    rules += '\n' + gesture_person_rules
    rules += '\n' + detailed_rules
    rules += '\n' + role_rules
    rules += '\n' + profession_rules
    rules += '\n' + person_form_rules
    rules += '\n' + gesture_rules
    rules += '\n' + people_rules
    rules += '\n' + new_svg_rules
    rules += '\n' + expression_rules
    rules += '\n' + hand_prop_rules
    rules += '\n' + person_symbol_rules
    addOpenTypeFeaturesFromString(fb.font,'feature ccmp {\n'+rules+'\n} ccmp;')
    fb.font['head'].created=fb.font['head'].modified=2082844800
    fb.font.recalcTimestamp = False
    fb.font.flavor='woff2'
    path=output_root/'assets/fonts/dad-emoji.woff2';path.parent.mkdir(parents=True,exist_ok=True);fb.save(path)
    entry=dict(family='Dad Emoji',file=str(path.relative_to(output_root)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,
               sequences=[chr(cp) for cp in sorted(cmap) if cp not in components] + [chr(cp)+chr(vs) for cp in (0x2764,0x1F44D) for vs in (0xFE0E,0xFE0F)] + [chr(0x1F44D)+chr(cp) for cp in tone_points] + astronaut_sequences + keycap_sequences + compound_sequences + gesture_sequences + people_sequences + person_form_sequences + profession_sequences + role_sequences + detailed_sequences + gesture_person_sequences + activity_sequences + fantasy_sequences + tile_sequences + sign_sequences + expression_sequences + geometric_sequences + hand_prop_sequences + person_symbol_sequences + game_medical_sequences + sound_control_sequences + award_event_sequences + holding_sequences + family_tile_sequences + couple_sequences + flag_sequences + book_mail_sequences + money_clothing_sequences + final_object_sequences + clothed_sequences + new_svg_sequences + [chr(cp)+chr(vs) for cp,vs in shape_variants],
               componentOnly=components,
               ranges=[[cp,cp] for cp in sorted(cmap)],overrideBase=True,style='custom imagegen and reviewed OFL outlines; expressive procedural ink; selective PDF palette; colour-semantic hearts and geometric shapes; original keycap borders and comic lettering')
    entry['companions']=[build_ink(output_root)]
    manifest_path=output_root/'js/emoji-manifest.js';manifest_path.parent.mkdir(parents=True,exist_ok=True)
    manifest_path.write_text('// Generated by tools/font/build_emoji.py\nexport default '+json.dumps(entry,separators=(',',':'))+';\n')
    review_path=output_root/'output/imagegen/emoji-production/glyph-review.json';review_path.parent.mkdir(parents=True,exist_ok=True)
    review_path.write_text(json.dumps(dict(sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),palette=palette,glyphs=review,componentOnly=components,skinToneSequences=[chr(0x1F44D)+chr(cp) for cp in tone_points]+gesture_sequences+people_sequences+person_form_tones+profession_tones+role_tones+detailed_tones+gesture_person_tones+activity_tones+hand_prop_tones+new_svg_sequences,astronautSequences=astronaut_sequences,keycapSequences=keycap_sequences,keycaps=keycap_review,heartPalette=heart_review,faces=face_review,notYetEncoded=[]),indent=2)+'\n')
    print(f'{len(cmap)-len(components)} base emoji, {len(entry["sequences"])} explicit sequences, {len(components)} shaping components; {path.stat().st_size} bytes')


if __name__ == '__main__': build()
