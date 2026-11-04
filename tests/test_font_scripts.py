"""Actual shaping must survive packaging, not merely retain table names."""
import io
from functools import lru_cache
import json
from pathlib import Path
import pytest
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from native_sfnt_loader import evidence_ttfont

ROOT = Path(__file__).resolve().parents[1]


def manifest():
    text = (ROOT / 'js/font-manifest.js').read_text()
    return json.loads(text.split('export default ', 1)[1].rstrip(';\n'))


@lru_cache(maxsize=16)
def _shaping_face(path, mtime_ns, size):
    # Reuse immutable font data across shaping cases; a rebuilt file invalidates
    # this cache. Each shape still uses a fresh Font and Buffer.
    font = evidence_ttfont(path)
    font.flavor = None
    stream = io.BytesIO()
    font.save(stream)
    return hb.Face(stream.getvalue())


def shape(path, text, identities=False):
    path = Path(path)
    stat = path.stat()
    shaping_font = hb.Font(_shaping_face(path, stat.st_mtime_ns, stat.st_size))
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(shaping_font, buffer)
    return [(info.codepoint if identities else bool(info.codepoint), pos.x_advance, pos.y_advance, pos.x_offset, pos.y_offset)
            for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions)]


@pytest.mark.parametrize('source,text', [
    ('tai-yo/DadTaiYo', '\U0001e6cd\U0001e6ee \U0001e6d5\U0001e6ef \U0001e6c5\U0001e6ee\U0001e6ee \U0001e6dc\U0001e6ee\U0001e6ef'),
    ('garay/DadGaray', '\U00010d73\U00010d69\U00010d4d \U00010d74\U00010d69\U00010d4d\U00010d4d'),
    ('tolong/DadTolong', '\U00011db4\u0324\u0303\U00011dd9 \U00011dca\u0324 \U00011dd4\u0308'),
    ('UnicodiaDaarage', '\U00011392\U000113d0\U00011392\U000113c7'),
    ('UnicodiaFunky', '\U00010940\U00010941\U00010942'),
    ('ArefRuqaa', 'مَرْحَبًا بالعالم'),
    ('Kalam', 'नमस्ते दुनिया'),
    ('Gaegu', '안녕하세요'),
    ('KleeOne', 'こんにちは'),
    ('Kedebideri', '\U00016ea0\U00016ea1\U00016ea2'),
    ('Kanchenjunga', '\U00016d44\U00016d45\U00016d67'),
    ('NotoSansGurungKhema', '\U00016101\U0001611e\U0001612d'),
    ('NotoSerifOlOnal', '\U0001e5d0\U0001e5d1\U0001e5ee'),
    ('egyptian-text/eot.ttf', '𓀀\U00013430𓀁'),
    ('egyptian-text/eot.ttf', '𓀀\U00013431𓀁'),
    ('egyptian-text/eot.ttf', '\U00013437𓀀\U00013430𓀁\U00013438\U00013431𓂀'),
    ('egyptian-text/eot.ttf', '𓅓\ufe00'),
])
def test_script_packaging_preserves_shaped_positions(source, text):
    candidates = [e for e in manifest()['fonts'] if source in e['source']]
    # These sentences must reside together in a shard; whole-script shaping
    # should not be broken by arbitrary divisions of joining scripts.
    required = {ord(c) for c in text}
    entry = next(e for e in candidates if all(any(a <= cp <= b for a,b in e['ranges']) for cp in required))
    original = shape(ROOT / entry['source'], text)
    packaged = shape(ROOT / entry['file'], text)
    assert all(g[0] for g in packaged)
    assert packaged == original


def test_shard_manifest_matches_assets_and_derivatives_are_renamed():
    import hashlib
    for entry in manifest()['fonts']:
        path = ROOT / entry['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
        with TTFont(path) as font:
            family = {n.toUnicode() for n in font['name'].names if n.nameID in {1, 16}}
            assert family == {entry['family']}
            recorded = {cp for a,b in entry['ranges'] for cp in range(a,b+1)}
            assert recorded == set(font.getBestCmap())


def test_egyptian_joiners_produce_distinct_compact_compositions():
    entry = next(e for e in manifest()['fonts'] if 'egyptian-text/eot.ttf' in e['source'])
    path = ROOT / entry['file']
    plain = shape(path, '𓀀𓀁', True)
    vertical = shape(path, '𓀀\U00013430𓀁', True)
    horizontal = shape(path, '𓀀\U00013431𓀁', True)
    assert vertical != horizontal != plain
    assert sum(g[1] for g in vertical) < sum(g[1] for g in horizontal) < sum(g[1] for g in plain)
    assert len({g[4] for g in vertical}) > 1


@pytest.mark.parametrize('source,base,prefix', [
    ('UnicodiaDaarage', 0x11392, 'TULU-TIGALARI'),
    ('NotoSansGurungKhema', 0x16101, 'GURUNG KHEMA'),
    ('Kanchenjunga', 0x16D44, 'KIRAT RAI'),
])
def test_new_script_canonical_sequences_shape_identically(source, base, prefix):
    import unicodedata2
    entry = next(e for e in manifest()['fonts'] if source in e['source'])
    checked = 0
    for row in (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines():
        fields = row.split(';')
        if not fields[1].startswith(prefix) or not fields[5] or fields[5].startswith('<'):
            continue
        text = chr(base) + chr(int(fields[0], 16))
        assert shape(ROOT/entry['file'], text, True) == shape(ROOT/entry['file'], unicodedata2.normalize('NFD',text), True)
        direct = chr(base) + ''.join(chr(int(cp,16)) for cp in fields[5].split())
        assert shape(ROOT/entry['file'], text, True) == shape(ROOT/entry['file'], direct, True)
        checked += 1
    assert checked > 0


def test_new_sources_have_real_outlines_and_respect_licensed_scope():
    from fontTools.pens.boundsPen import BoundsPen
    for source, first, last, expected in [('UnicodiaFunky', 0x10940, 0x10959, 26),
                                          ('UnicodiaDaarage', 0x11380, 0x113ff, 80)]:
        entry = next(e for e in manifest()['fonts'] if source in e['source'])
        font = TTFont(ROOT/entry['file'])
        cmap = font.getBestCmap()
        points = {cp for cp in cmap if first <= cp <= last}
        assert len(points) == expected
        if source == 'UnicodiaFunky':
            source_data=json.loads((ROOT/'data/font-sources/unicodia.json').read_text())
            scope=next(e for e in source_data['files'] if e['path']==entry['source'])
            permitted={cp for a,b in scope['include_ranges'] for cp in range(a,b+1)}
            excluded={cp for a,b in scope['script_exclude_ranges'] for cp in range(a,b+1)}
            assert set(cmap)==permitted-excluded
        glyphs = font.getGlyphSet()
        for cp in points:
            pen = BoundsPen(glyphs)
            glyphs[cmap[cp]].draw(pen)
            assert pen.bounds is not None, hex(cp)
        if 'CFF ' in font:
            assert font['CFF '].cff.fontNames == [entry['family'].replace(' ', '')]
            assert font['CFF '].cff.topDictIndex[0].FamilyName == entry['family']


def test_tulu_conjoiner_forms_a_ligature_and_vowel_is_reordered():
    entry = next(e for e in manifest()['fonts'] if 'UnicodiaDaarage' in e['source'])
    path = ROOT/entry['file']
    ka = '\U00011392'
    plain = shape(path, ka+ka, True)
    joined = shape(path, ka+'\U000113d0'+ka, True)
    assert len(joined) == 1 and joined[0][0] != plain[0][0]
    assert joined[0][1] < sum(g[1] for g in plain)
    vowel = shape(path, ka+'\U000113c7', True)
    assert len(vowel) == 3 and vowel[1][0] == plain[0][0]
