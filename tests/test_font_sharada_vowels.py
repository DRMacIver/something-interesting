"""Shaping and geometry gates for native Sharada Kashmiri vowels."""

from font_baseline_checks import pinned_packaging_font
import sys
from pathlib import Path
import pytest
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import ROOT, shape, manifest
sys.path.insert(0,str(ROOT/'tools/font'))
from sharada_vowels import add_marks, REFERENCES, SELECTORS


@pytest.fixture(scope='module',params=['prototype','delivered'])
def prototype(tmp_path_factory,request):
    if request.param=='delivered':
        e=next(e for e in manifest()['fonts'] if e['source'].endswith('/NotoSansSharada-Regular.ttf'))
        path=ROOT/e['file'];return path,TTFont(path)
    path=tmp_path_factory.mktemp('sharada')/'prototype.ttf'
    font=TTFont(ROOT/'build/unicode-sources/noto/NotoSansSharada-Regular.ttf')
    donor=TTFont(ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf')
    add_marks(font,donor);font.save(path)
    return path,TTFont(path)


def test_all_bases_and_conjunct_prefixes_preserve_nonspacing_vowel_identity(prototype):
    path,font=prototype
    for base in range(0x11183,0x111b3):
        for prefix in ['',chr(0x111a2)+chr(0x111c0),chr(0x11191)+chr(0x111c0)]:
            for cp,ref in REFERENCES.items():
                text=prefix+chr(base)+chr(cp);rows=shape(path,text,True)
                names=[font.getGlyphName(g[0]) for g in rows]
                assert all(g[0] for g in rows),(text,names)
                marks=[g for g,n in zip(rows,names) if n.startswith('kashmiri')]
                assert len(marks)==1,(text,names)
                assert marks[0][1]==0,(text,marks)
                alias=prefix+chr(base)+chr(ref)+chr(SELECTORS[cp])
                alternate=shape(path,alias,True)
                # The selector may survive as an invisible zero-width space.
                alternate=[g for g in alternate if font.getGlyphName(g[0])!='space']
                assert rows==alternate,(text,rows,alternate)


def test_existing_sharada_shaping_is_unchanged(prototype):
    path,_=prototype;source=ROOT/'build/unicode-sources/noto/NotoSansSharada-Regular.ttf'
    for base in range(0x11183,0x111b3):
        for vowel in range(0x111b3,0x111c1):
            for prefix in ['',chr(0x111a2)+chr(0x111c0)]:
                text=prefix+chr(base)+chr(vowel)
                assert shape(source,text)==shape(path,text),text


def test_below_vowels_clear_descenders_and_keep_native_body(prototype):
    from hebrew_marks import bounds
    path,font=prototype
    for base in range(0x11183,0x111b3):
        for prefix in ['',chr(0x111a2)+chr(0x111c0),chr(0x11191)+chr(0x111c0)]:
            for cp in (0x11b62,0x11b63):
                text=prefix+chr(base)+chr(cp);rows=shape(path,text,True)
                advance=0;body=[];marks=[]
                for gid,ax,ay,dx,dy in rows:
                    name=font.getGlyphName(gid);b=bounds(font,name)
                    if b:
                        box=(b[0]+advance+dx,b[1]+dy,b[2]+advance+dx,b[3]+dy)
                        (marks if name.startswith('kashmiri') else body).append(box)
                    advance+=ax
                assert len(marks)==1,(text,marks)
                mark=marks[0]
                overlapping=[b for b in body if b[0]<mark[2] and mark[0]<b[2]]
                assert overlapping,(text,body,mark)
                assert all(b[1]-mark[3]>=49 for b in overlapping),(text,body,mark)


def test_right_vowels_preserve_native_aa_forms_and_uvs_identity(prototype):
    from sharada_vowels import COMPOSITES
    path,font=prototype;seen=set()
    stems={prefix+chr(base) for base in range(0x11183,0x111b3)
           for prefix in ['',chr(0x111a2)+chr(0x111c0),chr(0x11191)+chr(0x111c0)]}
    reverse={n:cp for cp,n in font.getBestCmap().items()}
    for lookup in font['GSUB'].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            if not hasattr(sub,'ligatures'):continue
            for head,items in sub.ligatures.items():
                for item in items:
                    seq=[head,*item.Component]
                    if seq[-1]=='AA' and all(n in reverse for n in seq):
                        stems.add(''.join(chr(reverse[n]) for n in seq[:-1]))
    for stem in sorted(stems):
        native=shape(path,stem+chr(0x111b3),True)
        for cp,selector in COMPOSITES.items():
            text=stem+chr(cp);rows=shape(path,text,True)
            alias=shape(path,stem+chr(0x111b3)+chr(selector),True)
            alias=[g for g in alias if font.getGlyphName(g[0])!='space']
            assert rows==alias,(text,rows,alias)
            normalized=[]
            for gid,*position in rows:
                name=font.getGlyphName(gid)
                if '.kashmiri' in name:
                    seen.add(name);name=name.split('.kashmiri')[0]
                elif name.startswith('kashmiri'):
                    seen.add(name);name='AA'
                normalized.append((font.getGlyphID(name),*position))
            assert normalized==native,(text,normalized,native)
    assert len(seen)>20

    from sharada_vowels import record
    entry=next((e for e in manifest()['fonts'] if (ROOT/e['file']).resolve()==Path(path).resolve()),None)
    native=pinned_packaging_font(entry) if entry is not None else font
    # The original constructor must copy native AA exactly; approved seeded
    # pressure is independently authenticated for every delivered glyph.
    for name in seen:
        if '.kashmiri' in name:
            original=record(native,name.split('.kashmiri')[0]).value
            assert record(native,name).value[:len(original)]==original,name
