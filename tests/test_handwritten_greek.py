import hashlib
import io
import json
from pathlib import Path
import unicodedata

import pytest
import uharfbuzz as hb
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def greek():
    path = ROOT/'assets/fonts/dad-greek.woff2'
    font = TTFont(path)
    font.flavor = None
    stream = io.BytesIO()
    font.save(stream)
    shaper = hb.Font(hb.Face(stream.getvalue()))
    return font, shaper


def shape(shaper, text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(shaper, buf)
    return [(g.codepoint, p.x_advance, p.x_offset, p.y_offset)
            for g, p in zip(buf.glyph_infos, buf.glyph_positions)]


def test_every_extended_greek_canonical_form_matches_its_decomposition(greek):
    font, shaper = greek
    checked = 0
    for cp in font.getBestCmap():
        if 0x1f00 <= cp <= 0x1fff:
            text = chr(cp)
            composed = shape(shaper, text)
            assert composed and all(row[0] for row in composed), hex(cp)
            assert composed == shape(shaper, unicodedata.normalize('NFD', text)), hex(cp)
            checked += 1
    assert checked == 233


def test_existing_handwritten_greek_outlines_and_advances_are_retained(greek):
    font, _ = greek
    before = TTFont(ROOT/'assets/fonts/scripts/ee2777fce4d7.woff2')
    old, new = before.getGlyphSet(), font.getGlyphSet()
    oldmap, newmap = before.getBestCmap(), font.getBestCmap()
    for cp, name in oldmap.items():
        if not 0x370 <= cp <= 0x3ff or cp == 0x39a:
            continue
        a, b = DecomposingRecordingPen(old), DecomposingRecordingPen(new)
        old[name].draw(a)
        new[newmap[cp]].draw(b)
        assert a.value == b.value, hex(cp)
        assert before['hmtx'][name] == font['hmtx'][newmap[cp]], hex(cp)


def test_capital_kappa_uses_the_reference_ink_and_keeps_its_native_advance(greek):
    font, _ = greek
    manifest=json.loads((ROOT/'js/greek-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    assert 'assets/fonts/dad-lettering-unicode.woff2' in manifest['sourceHashes']
    before=TTFont(ROOT/'assets/fonts/scripts/ee2777fce4d7.woff2')
    old=before.getBestCmap()[0x39a];new=font.getBestCmap()[0x39a]
    assert before['hmtx'][old][0]==font['hmtx'][new][0]
    a,b=DecomposingRecordingPen(before.getGlyphSet()),DecomposingRecordingPen(font.getGlyphSet())
    before.getGlyphSet()[old].draw(a);font.getGlyphSet()[new].draw(b)
    assert a.value!=b.value


def test_manifest_hash_sources_and_licences_are_current():
    entry = json.loads((ROOT/'js/greek-manifest.js').read_text().split('export default ', 1)[1].rstrip(';\n'))
    assert hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest() == entry['sha256']
    for path, expected in entry['sourceHashes'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected
    assert len(entry['licences']) == 2 and all((ROOT/p).is_file() for p in entry['licences'])
