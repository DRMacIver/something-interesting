"""CJK accent companions must retain real variants, not only mark coverage."""
import hashlib
import json
import sys

from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

from test_font_scripts import ROOT,shape
from math_mark_checks import positioned_ink


def entries():
    return json.loads((ROOT/'js/marked-cjk-variant-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))['fonts']


def copied_glyf_prefix_is_exact(source,target):
    """Equal closed glyph programs imply equal decomposed design-unit ink.

    This proves only the native prefix. Different table serialization and
    variable outlines keep the original per-glyph drawing comparison.
    """
    if any(tag in font for font in (source,target) for tag in ('fvar','gvar','VARC','CFF ','CFF2')):return False
    if any('glyf' not in font or 'loca' not in font for font in (source,target)):return False
    order=source.getGlyphOrder();n=len(order)
    if len(target.getGlyphOrder())<n:return False
    original=source.reader['glyf'];finished=target.reader['glyf']
    before=list(source['loca'].locations);after=list(target['loca'].locations)
    if len(before)!=n+1 or after[:n+1]!=before:return False
    if before[-1]!=len(original) or finished[:before[-1]]!=original:return False
    if len(set(order))!=n:raise AssertionError('Ambiguous source glyph IDs')
    ids={name:gid for gid,name in enumerate(order)};table=source['glyf'];graph=[]
    for name in order:
        try:children=table[name].getComponentNames(table)
        except (IndexError,KeyError) as error:raise AssertionError('Source component outside copied prefix') from error
        if any(child not in ids for child in children):raise AssertionError('Source component outside copied prefix')
        graph.append([ids[child] for child in children])
    # Both fonts use the same encoded component GIDs under equal byte/loca
    # prefixes; no target component can reach an appended accent glyph.
    states=[0]*n
    for root in range(n):
        stack=[(root,False)]
        while stack:
            gid,leaving=stack.pop()
            if leaving:states[gid]=2;continue
            if states[gid]==2:continue
            if states[gid]==1:raise AssertionError('Cyclic copied component graph')
            states[gid]=1;stack.append((gid,True))
            stack.extend((child,False) for child in reversed(graph[gid]))
    return True


def assert_native_companion_pair(entry,painted):
    variants=0;glyphs=0
    # A companion must copy the current painted base, including its reviewed
    # dense finish. Original donor->derived-base lineage is checked by the
    # strict source/cache tests; this step must not redraw that finish.
    assert entry['source']==painted['file']
    assert entry['sourceSha256']==painted['sha256']
    if painted.get('denseTreatment'):
        assert entry['inheritedDenseTreatment']==dict(method=painted['denseTreatment']['method'],recipeSha256=painted['denseTreatment']['recipeSha256'],sourceFile=painted['file'],sourceSha256=painted['sha256'])
    else:
        assert not entry.get('inheritedDenseTreatment')
    a,b=TTFont(ROOT/entry['source']),TTFont(ROOT/entry['file'])
    assert hashlib.sha256((ROOT/entry['source']).read_bytes()).hexdigest()==entry['sourceSha256']
    assert hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest()==entry['sha256']
    exact_prefix=copied_glyf_prefix_is_exact(a,b)
    ag,bg=a.getGlyphSet(),b.getGlyphSet()
    before=a.getGlyphOrder();after=b.getGlyphOrder()
    assert len(after)==len(before)+257
    for gid,name in enumerate(before):
        target=after[gid]
        if not exact_prefix:
            pa,pb=DecomposingRecordingPen(ag),DecomposingRecordingPen(bg)
            ag[name].draw(pa);bg[target].draw(pb)
            assert pa.value==pb.value,(entry['family'],name)
        # Drawing formerly expanded these objects. Keep all declared frame
        # and instruction checks live even when equal raw programs suffice.
        a['glyf'][name].expand(a['glyf']);b['glyf'][target].expand(b['glyf'])
        assert a['hmtx'][name]==b['hmtx'][target]
        if 'vmtx' in a:assert a['vmtx'][name]==b['vmtx'][target]
        for field in ['xMin','yMin','xMax','yMax']:
            assert getattr(a['glyf'][name],field,None)==getattr(b['glyf'][target],field,None)
        if hasattr(a['glyf'][name],'program'):
            assert a['glyf'][name].program.getBytecode()==b['glyf'][target].program.getBytecode()
        glyphs+=1
    for tag in ['fpgm','prep','cvt ']:
        if tag in a:assert a.getTableData(tag)==b.getTableData(tag)
    for table in a['cmap'].tables:
        if table.format!=14:continue
        for selector,pairs in table.uvsDict.items():
            for cp,name in pairs:
                text=chr(cp)+chr(selector)
                assert shape(ROOT/entry['source'],text,True)==shape(ROOT/entry['file'],text,True),(entry['family'],text)
                variants+=1
    assert entry['variationOnly']
    assert b['name'].getDebugName(1)==entry['family']
    assert 'Noto' in b['name'].getDebugName(0)
    assert 'SIL Open Font License' in b['name'].getDebugName(13)
    return variants,glyphs,exact_prefix


def test_every_native_glyph_and_variation_remain_exact_in_accent_companions():
    rows=entries()
    assert len(rows)==92 and len({e['baseVariantFamily'] for e in rows})==92
    variants=0;glyphs=0
    script_manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    standalone=json.loads((ROOT/'js/cjk-variant-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    bases={e['family']:e for e in [standalone,*script_manifest['fonts']]}
    for entry in rows:
        pair_variants,pair_glyphs,_=assert_native_companion_pair(entry,bases[entry['baseVariantFamily']])
        variants+=pair_variants;glyphs+=pair_glyphs
    assert variants>=30637 and glyphs>90000


def test_cjk_variant_accents_keep_the_base_and_stack_on_the_correct_side():
    rows=entries()
    for sequence in ['㐂\U000e0101','\U00020000\U000e0100','\U00030654\U000e0101','豈\ufe00']:
        base,selector=map(ord,sequence)
        entry=next(e for e in rows if any(a<=base<=b for a,b in e['nativeVariations'].get(str(selector),[])))
        font=TTFont(ROOT/entry['file'])
        plain=shape(ROOT/entry['file'],sequence,True)
        for suffix in ['\u0301','\u0323','\u0302\u0307','\u0323\u0302\u0307','\u0302\u0323\u0307']:
            shaped=shape(ROOT/entry['file'],sequence+suffix,True)
            assert shaped[0]==plain[0],(sequence,suffix)
            assert all(gid>0 for gid,*_ in shaped)
            assert all(g[1]==0 for g in shaped[1:])
            ink=positioned_ink(font,ROOT/entry['file'],sequence+suffix)
            _,base_box,_=ink[0]
            previous_top=base_box[3]
            for name,box,_ in ink[1:]:
                if name==font.getBestCmap()[0x323]:
                    assert box[3]<base_box[1]
                else:
                    assert box[1]>previous_top
                    previous_top=box[3]


def test_native_cjk_single_mark_positions_survive_gpos_and_foreign_accents():
    rows=entries()
    for sequence in ['㐂\U000e0101','\U00020000\U000e0100','\U00030654\U000e0101']:
        base,selector=map(ord,sequence)
        entry=next(e for e in rows if any(a<=base<=b for a,b in e['nativeVariations'].get(str(selector),[])))
        for cp in [*range(0x302a,0x3030),0x3099,0x309a]:
            text=sequence+chr(cp)
            original=shape(ROOT/entry['source'],text,True)
            assert shape(ROOT/entry['file'],text,True)==original,(sequence,hex(cp))
            extra=shape(ROOT/entry['file'],text+'\u0301',True)
            # Canonical mark ordering can put the acute before a native tone.
            retained=[g for g in extra if g[0] in {original[0][0],original[1][0]}]
            assert retained==original and all(g[0]>0 for g in extra),(sequence,hex(cp))
