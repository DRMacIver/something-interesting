"""Changed marked catalog ink follows an exact reviewed native base lineage."""
import copy
import hashlib
import json
from pathlib import Path
import shutil

import pytest
from fontTools.ttLib import TTFont

import font_baseline_checks as checks
import dense_native_adapter as dense
from build_combining_outlines import native_drawing
from test_dense_baseline_checks import dense_fixture

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save_manifest(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text('export default '+json.dumps(value)+';\n')


@pytest.fixture
def marked_case(dense_fixture,monkeypatch):
    root,before,base=dense_fixture;base=copy.deepcopy(base)
    monkeypatch.setattr(checks,'ROOT',root);monkeypatch.setattr(dense,'CACHE',root/'cache')
    frozen=root/'output/font-review/supplemental-production-baselines'/Path(base['file']).name
    frozen.with_suffix('.json').write_text(json.dumps(before))
    identity=hashlib.sha256(base['family'].encode()).hexdigest()[:12]
    relative='assets/fonts/scripts/marked-cjk-'+identity+'.woff2';target=root/relative
    shutil.copyfile(root/base['file'],target)
    donor=root/'assets/fonts/dad-lettering-unicode.woff2';shutil.copyfile(ROOT/'assets/fonts/dad-lettering-unicode.woff2',donor)
    from build_marked_cjk_variants import __file__ as builder_file
    builder=Path(builder_file);recipe=':'.join(sha(p) for p in (builder,builder.with_name('math_unicode_marks.py'),donor))
    t=base['denseTreatment']
    marked=dict(family='Dad Marked CJK '+identity,baseVariantFamily=base['family'],file=relative,sha256=sha(target),bytes=target.stat().st_size,source=base['file'],sourceSha256=base['sha256'],markSource=donor.relative_to(root).as_posix(),markSourceSha256=sha(donor),recipe=recipe,nativeVariations={},inheritedDenseTreatment=dict(method=t['method'],recipeSha256=t['recipeSha256'],sourceFile=base['file'],sourceSha256=base['sha256']))
    save_manifest(root/'js/font-manifest.js',{'fonts':[base]});save_manifest(root/'js/marked-cjk-variant-manifest.js',{'fonts':[marked]})
    rows=[]
    for path in (frozen,target):
        f=TTFont(path);name=f.getBestCmap()[72];rows.append(dict(**native_drawing(f.getGlyphSet(),name,1/f['head'].unitsPerEm),glyph=name))
    assert rows[0]!=rows[1]
    return root,base,marked,rows[0],rows[1]


def invoke(case):
    root,base,marked,before,after=case
    checks.assert_drawing_equal_or_optical(before,after,marked['file'],72)


def test_marked_catalog_authenticates_complete_base_cache_and_exact_copy(marked_case):invoke(marked_case)


@pytest.mark.parametrize('mutation',['parent_sha','source','inherited_method','inherited_recipe','inherited_source_sha','recipe','path','donor_sha','family','base_family','base_recipe','old_path','new_path','copy','metric','uvs'])
def test_marked_catalog_rejects_unproven_parent_or_copy(marked_case,mutation):
    root,base,marked,before,after=copy.deepcopy(marked_case);target=root/marked['file']
    if mutation=='parent_sha':marked['sourceSha256']='0'*64
    elif mutation=='source':marked['source']='assets/fonts/scripts/unreviewed.woff2'
    elif mutation=='inherited_method':marked['inheritedDenseTreatment']['method']='unreviewed'
    elif mutation=='inherited_recipe':marked['inheritedDenseTreatment']['recipeSha256']='0'*64
    elif mutation=='inherited_source_sha':marked['inheritedDenseTreatment']['sourceSha256']='0'*64
    elif mutation=='recipe':marked['recipe']='unreviewed'
    elif mutation=='path':marked['file']='assets/fonts/scripts/unreviewed.woff2'
    elif mutation=='donor_sha':marked['markSourceSha256']='0'*64
    elif mutation=='family':marked['family']='unreviewed'
    elif mutation=='base_family':marked['baseVariantFamily']='unreviewed'
    elif mutation=='base_recipe':base['recipe']='unreviewed'
    elif mutation=='old_path':before['path']+='M0 0L1 1Z'
    elif mutation=='new_path':after['path']+='M0 0L1 1Z'
    else:
        f=TTFont(target,recalcTimestamp=False);name=f.getBestCmap()[72]
        if mutation=='copy':
            g=f['glyf'][name];x,y=g.coordinates[0];g.coordinates[0]=(x+1,y)
        elif mutation=='metric':advance,lsb=f['hmtx'][name];f['hmtx'][name]=(advance+1,lsb)
        else:
            from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
            table=CmapSubtable.newSubtable(14);table.platformID=0;table.platEncID=5;table.language=0;table.cmap={};table.uvsDict={0xfe00:[(72,None)]};f['cmap'].tables.append(table)
        f.save(target);marked.update(sha256=sha(target),bytes=target.stat().st_size)
        after.update(native_drawing(f.getGlyphSet(),name,1/f['head'].unitsPerEm))
    save_manifest(root/'js/font-manifest.js',{'fonts':[base]});save_manifest(root/'js/marked-cjk-variant-manifest.js',{'fonts':[marked]})
    with pytest.raises(AssertionError):invoke((root,base,marked,before,after))


def test_cached_parent_proof_invalidates_after_cache_record_mutation(marked_case):
    invoke(marked_case)
    root,base,marked,before,after=marked_case
    report=json.loads((root/base['denseTreatment']['report']).read_text());row=next(r for r in report['records'] if r['status']=='dense-native-pen')
    key=row['cacheKey'];path=dense.CACHE/key[:2]/(key+'.json');original=path.read_bytes()
    try:
        changed=json.loads(original);changed['nativeBoundsPreserved']=False;path.write_text(json.dumps(changed))
        with pytest.raises(AssertionError):invoke(marked_case)
    finally:path.write_bytes(original)


def test_cached_parent_proof_rejects_changed_kernel_settings(marked_case,monkeypatch):
    invoke(marked_case)
    monkeypatch.setitem(dense.SETTINGS,'amounts',[.5])
    with pytest.raises(AssertionError):invoke(marked_case)


def test_cached_parent_proof_rejects_changed_pinned_raw_source(marked_case):
    invoke(marked_case)
    root,base,marked,before,after=marked_case;source=root/base['source'];original=source.read_bytes()
    try:
        source.write_bytes(original+b'unreviewed source mutation')
        with pytest.raises(AssertionError):invoke(marked_case)
    finally:source.write_bytes(original)


def test_unchanged_borrowed_catalog_ink_requires_actual_marked_copy(marked_case):
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    root,base,marked,before,after=copy.deepcopy(marked_case);target=root/marked['file']
    font=TTFont(target,recalcTimestamp=False);pen=TTGlyphPen(None)
    pen.moveTo((0,0));pen.lineTo((100,200));pen.lineTo((200,0));pen.closePath()
    name='borrowed';font['glyf'][name]=pen.glyph();font['hmtx'][name]=(0,0);font.setGlyphOrder(list(font['glyf'].glyphs))
    for table in font['cmap'].tables:
        if table.isUnicode() and table.format!=14:table.cmap[0x301]=name
    font.save(target);marked.update(sha256=sha(target),bytes=target.stat().st_size,addedMarks=[[0x301,0x301]])
    save_manifest(root/'js/marked-cjk-variant-manifest.js',{'fonts':[marked]})
    decoded=TTFont(target);glyph=decoded.getBestCmap()[0x301]
    row=dict(**native_drawing(decoded.getGlyphSet(),glyph,1/decoded['head'].unitsPerEm),glyph=glyph)
    context=checks.marked_catalog_context(marked['file'],[base])
    checks.assert_drawing_equal_or_optical(row,row,marked['file'],0x301,context)
    wrong=copy.deepcopy(row);wrong['path']+='M0 0L1 1Z'
    with pytest.raises(AssertionError):checks.assert_drawing_equal_or_optical(row,wrong,marked['file'],0x301,context)
    missing=copy.deepcopy(marked);missing['addedMarks']=[]
    with pytest.raises(AssertionError):checks.assert_drawing_equal_or_optical(row,row,marked['file'],0x301,(missing,base))
