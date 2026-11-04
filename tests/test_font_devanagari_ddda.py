"""Alternate DDDA preserves implosive identity and native vowel attachment."""
import hashlib
from native_sfnt_loader import evidence_ttfont as TTFont
from font_baseline_checks import pinned_packaging_font
from test_font_scripts import manifest, shape, ROOT
from test_font_cuneiform import outline
from test_font_bengali_anusvara import boxes

ALT = '\U00011b0a'
DRAW = '\u097e\U000e0160'


def pair():
    e = next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoSansDevanagari-Regular.ttf'))
    return e, TTFont(ROOT / e['file'])


def normalized(font, path, text):
    new, old = font.getBestCmap()[0x11B0A], font.getBestCmap()[0x97E]
    result = []
    for gid, *pos in shape(path, text, True):
        name = font.getGlyphName(gid)
        result.append((old if name == new else name, *pos))
    return result


def test_alternate_ddda_is_distinct_from_da_and_old_ddda():
    e, f = pair(); p = ROOT / e['file']
    assert len({repr(outline(f, cp)[0]) for cp in [0x926, 0x97E, 0x11B0A]}) == 3
    assert outline(f, 0x11B0A)[2] == outline(f, 0x97E)[2] > 0
    assert shape(p, ALT, True) == shape(p, DRAW, True)
    # First prove the raw constructor/native identities, then authenticate
    # each independently seeded current glyph through the complete cache proof.
    from devanagari_alternate_ddda import add_letter
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.pens.boundsPen import BoundsPen
    source=ROOT/e['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==e['sourceSha256']
    for token,file in [('alternate-ddda','devanagari_alternate_ddda.py'),('indic-input-rules','indic_input_rules.py')]:
        assert ':'+token+':'+hashlib.sha256((ROOT/'tools/font'/file).read_bytes()).hexdigest() in e['recipe']
    constructor=TTFont(source);add_letter(constructor);native=pinned_packaging_font(e)
    for cp in [0x926,0x97e,0x11b0a]:
        assert outline(native,cp)==outline(constructor,cp)
        assert f['hmtx'][f.getBestCmap()[cp]]==native['hmtx'][native.getBestCmap()[cp]]
    def contours(recording):
        output=[];current=[]
        for command in recording:
            current.append(command)
            if command[0]=='closePath':output.append(current);current=[]
        assert not current
        return output
    new,old=contours(outline(native,0x11b0a)[0]),contours(outline(native,0x97e)[0])
    assert len(new)==len(old)==2
    assert new[1]==old[1] and new[0]!=old[0]
    def bounds(recording):
        pen=RecordingPen();pen.value=recording;box=BoundsPen(None);pen.replay(box);return box.bounds
    band=bounds(old[0]);stroke=bounds(old[1]);actual_bodies=[]
    for cp in [0x97e,0x11b0a]:
        parts=contours(outline(f,cp)[0]);assert len(parts)==2
        ordered=sorted(parts,key=lambda part:bounds(part)[3]);lower,body=map(bounds,ordered)
        # Both actual forms keep the separate implosive bar below the original
        # body band. The native band/frame/metrics remain exact, without a
        # coordinate or area tolerance for changed seeded outlines.
        assert lower[1]==stroke[1]
        assert band[0]<=lower[0]<lower[2]<=band[2]
        assert lower[3]<band[1]<=body[1]<body[3]==band[3]
        assert body[0]==band[0] and body[2]==band[2]
        actual_bodies.append(ordered[1])
    assert actual_bodies[0]!=actual_bodies[1]


def test_vowels_reph_and_consonant_contexts_keep_native_implosive_rules():
    e, f = pair(); p = ROOT / e['file']
    vowels = ['', 'ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'ॄ', 'े', 'ै', 'ो', 'ौ', 'ं', 'ः', 'ँ']
    for vowel in vowels:
        for before in ['', 'र्', 'क्']:
            assert normalized(f, p, before + DRAW + vowel) == normalized(f, p, before + 'ॾ' + vowel)
    for cp in range(0x915, 0x93A):
        if cp not in f.getBestCmap(): continue
        for pattern in ['{}्' + chr(cp), chr(cp) + '्{}']:
            assert normalized(f, p, pattern.replace('{}', DRAW)) == normalized(f, p, pattern.replace('{}', 'ॾ'))
    # Below-vowel signs may join the stroke but must stay below the DA body.
    for vowel in ['ु', 'ू', 'ृ', 'ॄ']:
        shaped = boxes(f, p, DRAW + vowel)
        assert len(shaped) == 2
        assert shaped[1][1][3] <= 70
        assert all(g[0] for g in shape(p, DRAW + vowel))


def test_existing_devanagari_shaping_and_complete_character_inventory():
    e, _ = pair()
    for text in ['देवनागरी', 'द दु दू दृ द्र द्य द्ध', 'ॻ ॼ ॾ ॿ ॾु ॾू', 'क्ष त्र ज्ञ']:
        assert shape(ROOT / e['source'], text) == shape(ROOT / e['file'], text)
    from test_unicode_inventory import audit
    scripts = audit.properties(audit.DATA / 'Scripts.txt')
    required = {cp for cp in audit.inventory() if scripts.get(cp) == 'Devanagari'}
    m = manifest(); covered = {cp for e in m['fonts'] for a, b in e['ranges'] for cp in range(a, b + 1)}
    covered.update(cp for a, b in m['baseRanges'] + m['behaviouralRanges'] for cp in range(a, b + 1))
    assert required <= covered
