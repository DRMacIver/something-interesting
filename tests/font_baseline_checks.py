"""Keep historical unchanged-source checks strict across reviewed later recipes."""
import hashlib
import sys
from functools import lru_cache, wraps
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/font'))
from source_optics import SCALES
from font_proof_session import record_evidence, reuse_reviewed_proof


_BATCH=ContextVar('catalog_evidence_batch',default=None)


def evidence_identity(path):
    """ctime/inode also reject replacement or same-size restored-mtime edits."""
    try:stat=Path(path).stat()
    except FileNotFoundError:return None
    return (stat.st_dev,stat.st_ino,stat.st_ctime_ns,stat.st_mtime_ns,stat.st_size)


def watch_evidence(path,required=True):
    path=Path(path).absolute();record_evidence(path);state=_BATCH.get()
    if state is not None and path not in state['dependencies']:
        state['dependencies'][path]=evidence_identity(path)
    if required:
        identity=state['dependencies'][path] if state is not None else evidence_identity(path)
        assert identity is not None,('Missing evidence',str(path))
    return path


@contextmanager
def catalog_evidence_batch():
    """Authenticate immutable dependencies once; still compare every glyph.

    A nested comparison shares its parent's scope. Every dependency is checked
    again even when a glyph assertion raises; no evidence survives the batch.
    """
    if _BATCH.get() is not None:
        yield
        return
    state={'dependencies':{},'memo':{},'objects':{}};token=_BATCH.set(state)
    try:
        yield
    finally:
        try:
            import json
            for value,serialized in state['objects'].values():
                assert json.dumps(value,sort_keys=True)==serialized,'Evidence metadata changed during catalog comparison'
            for path,identity in state['dependencies'].items():
                assert evidence_identity(path)==identity,('Evidence changed during catalog comparison',str(path))
        finally:_BATCH.reset(token)


def batch_memo(function):
    @wraps(function)
    def wrapped(*args,**kwargs):
        import json
        state=_BATCH.get()
        if state is None:return function(*args,**kwargs)
        if function.__name__=='marked_catalog_context':
            bases=args[1];identity=id(bases)
            if identity not in state['objects']:state['objects'][identity]=(bases,json.dumps(bases,sort_keys=True))
            key=(function.__name__,args[0],identity)
        else:key=(function.__name__,json.dumps([args,kwargs],sort_keys=True,default=str))
        if key not in state['memo']:
            value=function(*args,**kwargs);state['memo'][key]=value
            if function.__name__ in {'catalog_manifest','catalog_bases','marked_catalog_context','font_variation_evidence'}:
                state['objects'][id(value)]=(value,json.dumps(value,sort_keys=True))
        return state['memo'][key]
    return wrapped


def catalog_batch(function):
    @wraps(function)
    def wrapped(*args,**kwargs):
        with catalog_evidence_batch():return function(*args,**kwargs)
    return wrapped


@batch_memo
def catalog_manifest(path):
    import json
    return json.loads(watch_evidence(path).read_text().split('export default ',1)[1].rstrip(';\n'))


@batch_memo
def catalog_bases():
    bases=list(catalog_manifest(ROOT/'js/font-manifest.js')['fonts'])
    standalone=watch_evidence(ROOT/'js/cjk-variant-manifest.js',required=False)
    if standalone.exists():bases.append(catalog_manifest(standalone))
    return bases


@lru_cache(maxsize=32)
def _decoded_evidence_font(path,identity):
    # FontTools decoding is expensive for dense adapted WOFF2. Rebuilds change
    # this key; live checks never reuse evidence across a changed file.
    return TTFont(path)


def evidence_font(path):
    path=watch_evidence(path)
    state=_BATCH.get()
    if state is not None:
        key=('font',str(path))
        if key not in state['memo']:state['memo'][key]=_decoded_evidence_font(str(path),state['dependencies'][path])
        return state['memo'][key]
    return _decoded_evidence_font(str(path),evidence_identity(path))


@batch_memo
def evidence_glyphset(path):
    return evidence_font(path).getGlyphSet()


@lru_cache(maxsize=8192)
def _native_evidence_drawing(path,identity,glyph):
    from build_combining_outlines import native_drawing
    font=evidence_font(path)
    return native_drawing(evidence_glyphset(path),glyph,1/font['head'].unitsPerEm)


def evidence_drawing(path,glyph):
    path=watch_evidence(path)
    identity=_BATCH.get()['dependencies'][path] if _BATCH.get() is not None else evidence_identity(path)
    return _native_evidence_drawing(str(path),identity,glyph)


def authenticated_review_metadata(before,after):
    """Authenticate a later sampled decision independently of font geometry."""
    if 'styleReview' not in after:return before,after
    from style_review import review_for_source
    assert after['styleReview']==review_for_source(after['source'])
    reviewed_style='sampled source style disposition: '+after['styleReview']['disposition']+'; native identities and guarded exceptions retained'
    if 'styleReview' not in before:
        after={k:v for k,v in after.items() if k!='styleReview'}
    pending=any(marker in before.get('style','') for marker in ('custom visual review pending','specialist/style review pending'))
    if pending and after.get('style')==reviewed_style:
        after=dict(after,style=before['style'])
    return before,after


@reuse_reviewed_proof
def reviewed_later_change(before, after):
    """Return true only for an exact, independently verifiable optical recipe.

    Arbitrary metadata is not an exemption from a historical baseline. Unknown
    changes continue to fail until their own provenance/invariants are checked.
    """
    original_after=after
    before,after=authenticated_review_metadata(before,after)
    if before==after and original_after is not after:
        assert hashlib.sha256((ROOT/after['file']).read_bytes()).hexdigest()==after['sha256']
        return True
    if after.get('denseTreatment'):
        return reviewed_dense_change(before,after)
    if after.get('supplementalTreatment'):
        if after['supplementalTreatment'].get('method') == 'native-centred-cubic-pressure-v1':
            return reviewed_cubic_change(before,after)
        return reviewed_supplemental_change(before,after)
    optical = after.get('opticalSize')
    if not optical or Path(before['source']).name not in SCALES:
        return False
    unchanged = {key:value for key,value in after.items() if key not in {'sha256','bytes','recipe','opticalSize'}}
    baseline = {key:value for key,value in before.items() if key not in {'sha256','bytes','recipe'}}
    # Older cached shards predate explicit empty UVS metadata.
    if 'nativeVariations' not in baseline and unchanged.get('nativeVariations') == {}:
        unchanged.pop('nativeVariations')
    assert unchanged == baseline, before['family']
    token = ':source-optics:' + hashlib.sha256((ROOT/'tools/font/source_optics.py').read_bytes()).hexdigest()
    assert after['recipe'].count(token) == 1
    assert after['recipe'].replace(token,'') == str(before['recipe'])
    assert after['bytes'] == (ROOT/after['file']).stat().st_size
    assert hashlib.sha256((ROOT/after['file']).read_bytes()).hexdigest() == after['sha256']
    with TTFont(ROOT/before['source']) as original, TTFont(ROOT/after['file']) as actual:
        source_em = original['head'].unitsPerEm
        assert optical['method'] == 'optical-em'
        assert optical['originalUnitsPerEm'] == source_em
        expected = round(source_em/SCALES[Path(before['source']).name])
        assert optical['unitsPerEm'] == actual['head'].unitsPerEm == expected
        assert optical['scale'] == source_em/expected
        native, packaged = original.getGlyphSet(), actual.getGlyphSet()
        for cp,name in actual.getBestCmap().items():
            source_name = original.getBestCmap()[cp]
            a,b = DecomposingRecordingPen(native), DecomposingRecordingPen(packaged)
            native[source_name].draw(a); packaged[name].draw(b)
            assert a.value == b.value, (before['family'],cp)
            assert original['hmtx'][source_name] == actual['hmtx'][name]
    return True


def enclosure_evidence(path, glyph, codepoint):
    """Recompute exact catalog ring/counter metadata from one source glyph."""
    from build_combining_outlines import enclosure_contours
    allowed={0x1abe,0x20dd,0x20de,0x20df,0x20e0,0x20e2,0x20e3,0x20e4}
    if codepoint not in allowed:return {}
    font=evidence_font(path)
    assert font.getBestCmap().get(codepoint)==glyph,'Enclosure source glyph identity changed'
    contours=enclosure_contours(font.getGlyphSet(),glyph,1/font['head'].unitsPerEm)
    if len(contours)==2 and contours[0]['area']*contours[1]['area']<0:
        outer,inner=sorted(contours,key=lambda part:abs(part['area']),reverse=True)
        return {'ring':dict(outer=outer,inner=inner)}
    if codepoint in {0x20e0,0x20e3}:
        outer=max(contours,key=lambda part:abs(part['area']))
        holes=[part for part in contours if part['area']*outer['area']<0]
        assert holes
        bounds=max(holes,key=lambda part:abs(part['area']))['bounds'] if codepoint==0x20e3 else [min(part['bounds'][0] for part in holes),min(part['bounds'][1] for part in holes),max(part['bounds'][2] for part in holes),max(part['bounds'][3] for part in holes)]
        return {'contentBounds':bounds}
    return {}


@lru_cache(maxsize=128)
def _authenticate_catalog_dense_parent(serialized_entry, evidence_identity):
    """Reuse complete native/cache proof only while every evidence file is fixed."""
    import json
    entry=json.loads(serialized_entry)
    frozen=ROOT/'output/font-review/supplemental-production-baselines'/Path(entry['file']).name
    before=json.loads(frozen.with_suffix('.json').read_text())
    assert reviewed_later_change(before,entry)
    return True


@batch_memo
def authenticate_catalog_dense_parent(entry):
    import json
    import dense_native_adapter as dense
    assert entry.get('denseTreatment'), 'Changed marked native ink requires an approved dense base'
    import style_review,source_optics
    for path in (Path(__file__),Path(style_review.__file__),Path(source_optics.__file__)):
        watch_evidence(path)
    if 'styleReview' in entry:watch_evidence(ROOT/style_review.RECORD)
    state=_BATCH.get()
    if state is not None and id(dense.SETTINGS) not in state['objects']:
        state['objects'][id(dense.SETTINGS)]=(dense.SETTINGS,json.dumps(dense.SETTINGS,sort_keys=True))
    frozen=ROOT/'output/font-review/supplemental-production-baselines'/Path(entry['file']).name
    report=ROOT/entry['denseTreatment']['report']
    files=[ROOT/entry['file'],frozen,frozen.with_suffix('.json'),report]
    for path in files:watch_evidence(path)
    for name in ('dense_native_adapter.py','dense_geometry_guards.py','dense_display_raster.py','native_contrast_pen.py','native_contour_pressure.py','supplemental_adapter.py'):watch_evidence(Path(dense.__file__).with_name(name))
    if entry.get('source'):
        source=watch_evidence(ROOT/entry['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==entry['sourceSha256']
        files.append(source)
    else:
        import zipfile
        for source in entry['sources']:
            archive=watch_evidence(ROOT/source['archive']);assert hashlib.sha256(archive.read_bytes()).hexdigest()==source['archiveSha256']
            with zipfile.ZipFile(archive) as packed:assert hashlib.sha256(packed.read(source['member'])).hexdigest()==source['sha256']
            files.append(archive)
    for row in json.loads(report.read_text())['records']:
        key=row['cacheKey'];files.append(dense.CACHE/key[:2]/(key+'.json'))
        if row['status'] in {'dense-native-pen','guarded-native-flex'}:files.append(dense.CACHE/key[:2]/(key+'.glyf'))
    identity=hashlib.sha256(dense.recipe_hash(entry['denseTreatment']['sourceProfile']).encode())
    identity.update(json.dumps(dense.SETTINGS,sort_keys=True).encode())
    for path in files:
        watch_evidence(path);identity.update(f'{path.absolute()}:{evidence_identity(path)}\n'.encode())
    return _authenticate_catalog_dense_parent(json.dumps(entry,sort_keys=True),identity.hexdigest())


@batch_memo
def marked_catalog_context(source_file,bases):
    """Authenticate a marked derivative and its complete reviewed dense base."""
    import json
    from native_variations import variation_ranges
    from build_marked_cjk_variants import __file__ as marked_builder_file
    path=ROOT/'js/marked-cjk-variant-manifest.js';assert path.exists()
    marked_entries=catalog_manifest(path)['fonts']
    candidates=[entry for entry in marked_entries if entry['file']==source_file];assert len(candidates)==1
    marked=candidates[0]
    candidates=[entry for entry in bases if entry['file']==marked['source']];assert len(candidates)==1
    base=candidates[0];treatment=base.get('denseTreatment');assert treatment
    assert marked['baseVariantFamily']==base['family'] and marked['sourceSha256']==base['sha256']
    identity=hashlib.sha256(base['family'].encode()).hexdigest()[:12]
    assert marked['family']=='Dad Marked CJK '+identity
    assert marked['file']=='assets/fonts/scripts/marked-cjk-'+identity+'.woff2'
    assert marked['inheritedDenseTreatment']==dict(method=treatment['method'],recipeSha256=treatment['recipeSha256'],sourceFile=base['file'],sourceSha256=base['sha256'])
    for entry in (base,marked):
        target=watch_evidence(ROOT/entry['file']);assert hashlib.sha256(target.read_bytes()).hexdigest()==entry['sha256']
        assert target.stat().st_size==entry['bytes']
    donor=watch_evidence(ROOT/'assets/fonts/dad-lettering-unicode.woff2')
    assert marked['markSource']==donor.relative_to(ROOT).as_posix()
    assert hashlib.sha256(donor.read_bytes()).hexdigest()==marked['markSourceSha256']
    builder=Path(marked_builder_file)
    expected_recipe=':'.join(hashlib.sha256(watch_evidence(p).read_bytes()).hexdigest() for p in (builder,builder.with_name('math_unicode_marks.py'),donor))
    assert marked['recipe']==expected_recipe
    assert authenticate_catalog_dense_parent(base)
    return marked,base


@batch_memo
def font_variation_evidence(path):
    from native_variations import variation_ranges
    font=evidence_font(path)
    uvs={selector:sorted((cp,font.getGlyphID(name) if name is not None else None) for cp,name in mappings) for table in font['cmap'].tables if table.format==14 for selector,mappings in table.uvsDict.items()}
    return uvs,variation_ranges(font)


def assert_marked_native_catalog_drawing(before,after,source_file,codepoint,bases,context=None):
    """Follow native ink to its base; unchanged borrowed ink stays exact."""
    from native_variations import variation_ranges
    assert isinstance(codepoint,int),'Native marked glyph requires explicit codepoint'
    marked,base=context if context is not None else marked_catalog_context(source_file,bases)
    assert marked['file']==source_file
    frozen=ROOT/'output/font-review/supplemental-production-baselines'/Path(base['file']).name
    native,current,finished=[evidence_font(p) for p in (frozen,ROOT/base['file'],ROOT/marked['file'])]
    assert codepoint in finished.getBestCmap()
    if codepoint not in native.getBestCmap():
        assert codepoint not in current.getBestCmap()
        assert before==after,'Borrowed Dad mark drawing changed'
        assert any(a<=codepoint<=b for a,b in marked['addedMarks'])
        assert codepoint in evidence_font(ROOT/marked['markSource']).getBestCmap()
        name=finished.getBestCmap()[codepoint];assert after['glyph']==name
        assert {k:after[k] for k in ('path','bounds')}==evidence_drawing(ROOT/marked['file'],name)
        return
    assert codepoint in current.getBestCmap()
    names=[font.getBestCmap()[codepoint] for font in (native,current,finished)]
    assert before['glyph']==names[0] and after['glyph']==names[2]
    assert native.getGlyphID(names[0])==current.getGlyphID(names[1])==finished.getGlyphID(names[2])
    assert current['hmtx'][names[1]]==finished['hmtx'][names[2]]
    current_uvs,current_ranges=font_variation_evidence(ROOT/base['file'])
    finished_uvs,finished_ranges=font_variation_evidence(ROOT/marked['file'])
    assert current_uvs==finished_uvs
    assert marked['nativeVariations']==current_ranges==finished_ranges
    assert {k:v for k,v in before.items() if k not in {'path','bounds'}}=={k:v for k,v in after.items() if k not in {'path','bounds'}}
    assert {k:before[k] for k in ('path','bounds')}==evidence_drawing(frozen,names[0])
    expected=evidence_drawing(ROOT/base['file'],names[1])
    assert {k:after[k] for k in ('path','bounds')}==expected==evidence_drawing(ROOT/marked['file'],names[2])
    current_gs,finished_gs=evidence_glyphset(ROOT/base['file']),evidence_glyphset(ROOT/marked['file'])
    a,b=DecomposingRecordingPen(current_gs),DecomposingRecordingPen(finished_gs)
    current_gs[names[1]].draw(a);finished_gs[names[2]].draw(b)
    assert a.value==b.value,'Marked derivative changed copied native ink'


def assert_drawing_equal_or_optical(before, after, source_file, codepoint=None, marked_context=None):
    """Authenticate frozen/current drawings and their source-derived geometry."""
    if before == after and marked_context is None:
        return
    import json
    from fontTools.svgLib.path import parse_path
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.pens.transformPen import TransformPen
    bases=catalog_bases()
    entry = next((e for e in bases if e['file'] == source_file),None)
    if entry is None:
        assert_marked_native_catalog_drawing(before,after,source_file,codepoint,bases,marked_context)
        return
    if entry.get('supplementalTreatment') or entry.get('denseTreatment'):
        from build_combining_outlines import native_drawing
        frozen = ROOT/'output/font-review/supplemental-production-baselines'/Path(entry['file']).name
        derived={'ring','contentBounds'}
        has_derived=bool((before.keys()|after.keys())&derived)
        if has_derived:assert isinstance(codepoint,int),'Enclosure codepoint required for source classification'
        assert {k:v for k,v in before.items() if k not in {'path','bounds'}|derived} == {k:v for k,v in after.items() if k not in {'path','bounds'}|derived}
        glyph = before['glyph']
        for row,path in [(before,frozen),(after,ROOT/entry['file'])]:
            expected = evidence_drawing(path,glyph)
            assert row['path'] == expected['path'] and row['bounds'] == expected['bounds']
            if has_derived:
                assert {k:v for k,v in row.items() if k in derived} == enclosure_evidence(path,glyph,codepoint),'Source-derived enclosure geometry changed'
        return
    optical = entry['opticalSize']
    assert Path(entry['source']).name in SCALES
    assert optical['method'] == 'optical-em'
    assert optical['unitsPerEm'] == round(optical['originalUnitsPerEm']/SCALES[Path(entry['source']).name])
    assert {k:v for k,v in before.items() if k not in {'path','bounds'}} == {k:v for k,v in after.items() if k not in {'path','bounds'}}
    scale = optical['scale']
    a,b = RecordingPen(), RecordingPen()
    parse_path(before['path'],TransformPen(a,(scale,0,0,scale,0,0)))
    parse_path(after['path'],b)
    assert len(a.value) == len(b.value)
    for (op,points),(new_op,new_points) in zip(a.value,b.value):
        assert op == new_op and len(points) == len(new_points)
        for old_point,new_point in zip(points,new_points):
            assert all(abs(x-y)<.000002 for x,y in zip(old_point,new_point))
    assert all(abs(x*scale-y)<.000002 for x,y in zip(before['bounds'],after['bounds']))


@catalog_batch
def assert_catalog_equal_or_optical(before, after):
    """Authenticate catalog geometry for recorded optics and native treatments."""
    import copy,json
    expected = copy.deepcopy(before)
    bases=catalog_bases()
    optics = {e['file']:e for e in bases if e.get('opticalSize') or e.get('supplementalTreatment') or e.get('denseTreatment')}
    marked_path=watch_evidence(ROOT/'js/marked-cjk-variant-manifest.js',required=False)
    marked={e['file']:e for e in catalog_manifest(marked_path)['fonts']} if marked_path.exists() else {}
    contexts={}
    for source in expected['sources']:
        if source['file'] in optics:
            source['sha256'] = optics[source['file']]['sha256']
        elif source['file'] in marked and marked[source['file']].get('inheritedDenseTreatment'):
            contexts[source['file']]=marked_catalog_context(source['file'],bases)
            source['sha256']=marked[source['file']]['sha256']
    for cp,old in expected['marks'].items():
        new = after['marks'][cp]
        source_file = expected['sources'][old['source']]['file']
        assert_drawing_equal_or_optical(old,new,source_file,int(cp),contexts.get(source_file))
        expected['marks'][cp] = new
    assert_added_native_variant_families(before,after)
    for family,old in expected['variationMarks'].items():
        new = after['variationMarks'][family]
        assert old.keys() == new.keys() and old['source'] == new['source']
        assert old['marks'].keys() == new['marks'].keys()
        source_file = expected['sources'][old['source']]['file']
        for cp,row in old['marks'].items():
            other = new['marks'][cp]
            assert row['glyph'] == other['glyph']
            a = dict(expected['variantDrawings'][row['drawing']],glyph=row['glyph'])
            b = dict(after['variantDrawings'][other['drawing']],glyph=other['glyph'])
            assert_drawing_equal_or_optical(a,b,source_file,int(cp),contexts.get(source_file))
    expected['variationMarks'] = after['variationMarks']
    expected['variantDrawings'] = after['variantDrawings']
    assert expected == after, 'only authenticated optical or approved native source/drawing changes may follow the frozen catalog'


def assert_retained_native_drawing(source,row,before,after):
    """Authenticate only source9's proven empty-contour flattening delta."""
    gid=row['gid']
    if Path(source).name!='ArchaicCuneiformNumerals.ttf' or gid not in range(131,139):
        assert before==after
        return
    assert row['glyph']==f'u{0x125d2+gid-131:X}'
    assert row['status']=='native-retained-guard' and not row.get('sourcePolicy',False)
    def split_empty(commands):
        kept=[];empty=0;i=0
        while i<len(commands):
            if i+1<len(commands) and commands[i][0]=='moveTo' and len(commands[i][1])==1 and commands[i+1]==('closePath',()):
                empty+=1;i+=2
            else:kept.append(commands[i]);i+=1
        return kept,empty
    old,old_count=split_empty(before);new,new_count=split_empty(after)
    assert old_count==gid-129 and new_count==0
    assert old==new


def reviewed_supplemental_change(before, after, isolated_file=None):
    """Allow only the reviewed source recipe with frozen native layout evidence."""
    before,after=authenticated_review_metadata(before,after)
    import json
    from supplemental_adapter import RECIPES, SOURCES, recipe_hash
    source_name = Path(before['source']).name
    assert source_name in SOURCES
    treatment = after['supplementalTreatment']
    assert treatment['method'] == RECIPES['method'] == 'native-centred-distance-pressure-v1'
    assert treatment['recipeSha256'] == recipe_hash(source_name)
    assert treatment['settings'] == SOURCES[source_name]
    assert treatment['resolution'] == RECIPES['resolution']
    from source_preservation import POLICIES, policy_hash
    source_policy = treatment.get('sourcePolicy')
    recipe = after['recipe']
    if source_name in POLICIES:
        assert source_policy is not None
        assert source_policy['module'] == 'tools/font/source_preservation.py'
        assert source_policy['sha256'] == policy_hash()
        assert source_policy['codepoints'] == POLICIES[source_name] == [0x1262d]
        policy_token = ':source-preservation:' + policy_hash()
        import re
        policy_report = ROOT/treatment['report']
        assert policy_report.parent == ROOT/'output/font-review/supplemental-production'
        assert re.fullmatch('[0-9a-f]{64}-'+recipe_hash(source_name)+'-preserve-'+policy_hash()+r'\.json',policy_report.name)
        assert recipe.count(policy_token) == 1
        recipe = recipe.replace(policy_token,'')
    elif source_name=='NotoSansDuployan-Regular.ttf':
        import duployan_source_preservation as duployan
        assert source_policy is not None
        assert source_policy['module']=='tools/font/duployan_source_preservation.py'
        assert source_policy['sha256']==duployan.policy_hash()
        assert source_policy['codepoints']==duployan.CODEPOINTS==[0x1bc63]
        assert source_policy['namedGlyphs']==duployan.NAMED_GLYPHS==['dupl.Dot.rel1']
        assert source_policy['reason']==duployan.REASON
        policy_token=':duployan-source-preservation:'+duployan.policy_hash()
        import re
        policy_report=ROOT/treatment['report']
        expected_parent=ROOT/'output/font-review/supplemental-production' if isolated_file is None else Path(isolated_file).resolve().parent
        assert policy_report.resolve().parent==expected_parent.resolve()
        assert re.fullmatch('[0-9a-f]{64}-'+recipe_hash(source_name)+'-duployan-preserve-'+duployan.policy_hash()+r'\.json',policy_report.name)
        assert recipe.count(policy_token)==1
        recipe=recipe.replace(policy_token,'')
    elif source_name=='NotoSansCuneiform-Regular.ttf':
        import cuneiform_source_preservation as cuneiform
        assert source_policy is not None
        assert source_policy['module']=='tools/font/cuneiform_source_preservation.py'
        assert source_policy['sha256']==cuneiform.policy_hash()
        assert source_policy['codepoints']==cuneiform.CODEPOINTS==[0x12493]
        assert source_policy['namedGlyphs']==cuneiform.NAMED_GLYPHS==[]
        assert source_policy['reason']==cuneiform.REASON
        policy_token=':cuneiform-source-preservation:'+cuneiform.policy_hash()
        import re
        policy_report=ROOT/treatment['report']
        expected_parent=ROOT/'output/font-review/supplemental-production' if isolated_file is None else Path(isolated_file).resolve().parent
        assert policy_report.resolve().parent==expected_parent.resolve()
        assert re.fullmatch('[0-9a-f]{64}-'+recipe_hash(source_name)+'-cuneiform-preserve-'+cuneiform.policy_hash()+r'\.json',policy_report.name)
        assert recipe.count(policy_token)==1
        recipe=recipe.replace(policy_token,'')
    elif source_name=='NotoMusic-Regular.ttf':
        import music_source_preservation as music
        assert source_policy is not None
        assert source_policy['module']=='tools/font/music_source_preservation.py'
        assert source_policy['sha256']==music.policy_hash()
        assert source_policy['codepoints']==music.CODEPOINTS==[]
        assert source_policy['namedGlyphs']==music.NAMED_GLYPHS==['u1D25B_low']
        assert source_policy['reason']==music.REASON
        assert source_policy['sourceConstruction']==music.construction(before['source'])
        construction=source_policy['sourceConstruction']
        constructor_token=':music-tremolos:'+construction['sha256']+':'+construction['rulesSha256']
        assert str(before['recipe']).count(constructor_token)==1
        assert recipe.count(constructor_token)==1
        policy_token=':music-source-preservation:'+music.policy_hash()
        import re
        policy_report=ROOT/treatment['report']
        expected_parent=ROOT/'output/font-review/supplemental-production' if isolated_file is None else Path(isolated_file).resolve().parent
        assert policy_report.resolve().parent==expected_parent.resolve()
        assert re.fullmatch('[0-9a-f]{64}-'+recipe_hash(source_name)+'-music-preserve-'+music.policy_hash()+r'\.json',policy_report.name)
        assert recipe.count(policy_token)==1
        recipe=recipe.replace(policy_token,'')
    elif source_name=='UnicodiaFunky.ttf':
        import chemical_source_preservation as chemical
        assert source_policy is not None
        assert source_policy['module']=='tools/font/chemical_source_preservation.py'
        assert source_policy['sha256']==chemical.policy_hash()
        assert source_policy['codepoints']==chemical.CODEPOINTS==[0x1cee0,0x1cee1,0x1cee2,0x1cee3,0x1cee4,0x1cee5,0x1cee8,0x1cee9,0x1ceea,0x1ceeb,0x1ceec,0x1ceed,0x1ceee,0x1ceef,0x1f8d1]
        assert source_policy['namedGlyphs']==chemical.NAMED_GLYPHS==[]
        assert source_policy['reason']==chemical.REASON
        assert source_policy['sourceConstruction']==chemical.construction(before['source'])
        construction=source_policy['sourceConstruction']
        ink_token=':alphabet-ink:'+json.dumps(construction['scope'],separators=(',',':'))+':'+construction['sha256']
        repair_token=':chemical-repair:'+construction['chemicalSha256']
        assert str(before['recipe']).count(ink_token)==recipe.count(ink_token)==1
        assert str(before['recipe']).count(repair_token)==recipe.count(repair_token)==1
        policy_token=':chemical-source-preservation:'+chemical.policy_hash()
        import re
        policy_report=ROOT/treatment['report']
        expected_parent=ROOT/'output/font-review/supplemental-production' if isolated_file is None else Path(isolated_file).resolve().parent
        assert policy_report.resolve().parent==expected_parent.resolve()
        assert re.fullmatch('[0-9a-f]{64}-'+recipe_hash(source_name)+'-chemical-preserve-'+chemical.policy_hash()+r'\.json',policy_report.name)
        assert recipe.count(policy_token)==1
        recipe=recipe.replace(policy_token,'')
    else:
        assert source_policy is None
        assert ':source-preservation:' not in recipe
        assert ':duployan-source-preservation:' not in recipe
        assert ':cuneiform-source-preservation:' not in recipe
        assert ':music-source-preservation:' not in recipe
        assert ':chemical-source-preservation:' not in recipe
    token = ':supplemental-pressure:' + recipe_hash(source_name)
    assert recipe.count(token) == 1
    assert recipe.replace(token,'') == str(before['recipe'])
    frozen = ROOT/'output/font-review/supplemental-production-baselines'/Path(before['file']).name
    assert hashlib.sha256(frozen.read_bytes()).hexdigest() == before['sha256']
    assert hashlib.sha256((ROOT/after['file']).read_bytes()).hexdigest() == after['sha256']
    assert (ROOT/after['file']).stat().st_size == after['bytes']
    changed = {'sha256','bytes','recipe','supplementalTreatment','style'}
    if isolated_file is not None:
        assert (ROOT/after['file']).resolve()==Path(isolated_file).resolve()
        changed.add('file')
    old_meta = {k:v for k,v in before.items() if k not in changed}
    new_meta = {k:v for k,v in after.items() if k not in changed}
    if 'nativeVariations' not in old_meta and 'nativeVariations' in new_meta:
        # Cached pre-treatment entries sometimes omitted existing UVS metadata.
        # Permit its disclosure only when both frozen and rebuilt native cmap14
        # tables prove exactly the advertised repertoire, not a new sequence.
        from native_variations import variation_ranges
        with TTFont(frozen) as original, TTFont(ROOT/after['file']) as current:
            assert new_meta['nativeVariations'] == variation_ranges(original) == variation_ranges(current)
        new_meta.pop('nativeVariations')
    assert old_meta == new_meta
    assert after['style'] == 'smooth native component-centred variable pressure; native layout retained; rejected geometry retained with explicit audit; specialist review provisional'
    report = json.loads(watch_evidence(ROOT/treatment['report']).read_text())
    assert {k:v for k,v in report.items() if k != 'records'} == {k:v for k,v in treatment.items() if k != 'report'}
    from collections import Counter
    assert dict(Counter(row['status'] for row in report['records'])) == report['counts']
    assert sum(report['counts'].values()) == report['glyphs']
    assert treatment['nativeBoundsPreserved'] is True
    assert set(report['counts']) <= {'adapted','native-blank','native-retained-guard'}
    with TTFont(frozen) as native, TTFont(ROOT/after['file']) as actual:
        assert len(native.getGlyphOrder()) == len(actual.getGlyphOrder())
        assert {cp:native.getGlyphID(name) for cp,name in native.getBestCmap().items()} == {cp:actual.getGlyphID(name) for cp,name in actual.getBestCmap().items()}
        assert treatment['nativeEmUnchanged'] == native['head'].unitsPerEm == actual['head'].unitsPerEm
        for tag in ('GPOS','GDEF','GSUB','hmtx','vmtx'):
            assert (tag in native) == (tag in actual)
            if tag in native: assert native.getTableData(tag) == actual.getTableData(tag),tag
        assert [r['gid'] for r in report['records']] == list(range(len(native.getGlyphOrder())))
        policy_gids = set()
        if source_policy:
            policy_gids = source_policy_closure(native,source_policy,[r['glyph'] for r in report['records']])
            records = {row['gid']:row for row in report['records']}
            if source_name in {'NotoSansDuployan-Regular.ttf','NotoSansCuneiform-Regular.ttf','NotoMusic-Regular.ttf','UnicodiaFunky.ttf','ArchaicCuneiformNumerals.ttf'}:
                raw_path=ROOT/before['source']
                assert hashlib.sha256(raw_path.read_bytes()).hexdigest()==before['sourceSha256']
                with TTFont(raw_path) as raw:
                    if source_name=='NotoMusic-Regular.ttf':
                        from music_tremolos import add_marks as construct_native_tremolos
                        construct_native_tremolos(raw)
                    elif source_name=='UnicodiaFunky.ttf':
                        from chemical_symbols import repair_isolobal
                        from alphabet_ink import adapt as construct_alphabet_ink
                        repair_isolobal(raw)
                        construct_alphabet_ink(raw,{cp for a,b in source_policy['sourceConstruction']['scope'] for cp in range(a,b+1)})
                    raw_gs=raw.getGlyphSet();native_gs=native.getGlyphSet()
                    for cp in source_policy['codepoints']:
                        assert records[native.getGlyphID(native.getBestCmap()[cp])]['glyph']==raw.getBestCmap()[cp]
                    for gid in policy_gids:
                        original_name=records[gid]['glyph'];assert original_name in raw_gs
                        p,q=DecomposingRecordingPen(raw_gs),DecomposingRecordingPen(native_gs)
                        raw_gs[original_name].draw(p);native_gs[native.getGlyphName(gid)].draw(q)
                        assert p.value==q.value
                        assert raw['hmtx'][original_name]==native['hmtx'][native.getGlyphName(gid)]
            for gid in policy_gids:
                name = native.getGlyphName(gid)
                if native['glyf'][name].numberOfContours:
                    assert records[gid]['status'] == 'native-retained-guard'
                    assert records[gid]['sourcePolicy'] is True
                    assert records[gid]['reason'] == source_policy['reason']
        n,a = native.getGlyphSet(),actual.getGlyphSet()
        for row in report['records']:
            if row['status'] == 'adapted':
                assert row['vectorChecks'] and row['changedPixels'] > 0
            else:
                p,q = DecomposingRecordingPen(n),DecomposingRecordingPen(a)
                n[native.getGlyphName(row['gid'])].draw(p);a[actual.getGlyphName(row['gid'])].draw(q)
                assert_retained_native_drawing(before['source'],row,p.value,q.value)
    return True


def assert_cubic_charstring_advance(charstring,advance):
    """Decode Type2 nominal/default-width semantics independently of hmtx."""
    from fontTools.pens.basePen import NullPen
    charstring.draw(NullPen())
    assert charstring.width==advance


CUBIC_NATIVE_WIDTH_REPAIRS={1210:0x1d253,1211:0x1d254,1212:0x1d255,1245:0x1d279,1248:0x1d27c}


def assert_cubic_retained_charstring(native,current,advance,row):
    """Only five proven legacy width operands may change in retained CFF."""
    import copy
    from fontTools.misc.psCharStrings import T2CharString
    from fontTools.pens.recordingPen import RecordingPen
    old=copy.deepcopy(native);new=copy.deepcopy(current)
    assert_cubic_charstring_advance(new,advance)
    repair=row.get('widthRepair')
    if repair:
        gid=row['gid'];assert gid in CUBIC_NATIVE_WIDTH_REPAIRS
        assert row['glyph']==f'u{CUBIC_NATIVE_WIDTH_REPAIRS[gid]:X}'
        assert row['status']=='native-retained-guard' and not row.get('sourcePolicy',False)
        p,q=RecordingPen(),RecordingPen();old.draw(p);new.draw(q)
        assert p.value==q.value
        assert old.width!=advance
        old.decompile();assert old.program[0]==advance
        nominal=old.private.nominalWidthX;default=old.private.defaultWidthX
        assert nominal==1046 and default==200
        encoded=None if advance==default else advance-nominal
        assert repair==dict(method='explicit-type2-width-operand-only',nativeDecodedAdvance=old.width,hmtxAdvance=advance,encodedOperandBefore=old.program[0],encodedOperandAfter=encoded,nominalWidthX=nominal,defaultWidthX=default)
        program=old.program[1:] if encoded is None else [encoded,*old.program[1:]]
        expected=T2CharString(program=program,private=old.private,globalSubrs=old.globalSubrs)
        expected.compile();new.compile();assert expected.bytecode==new.bytecode
    else:
        old.compile();new.compile();assert old.bytecode==new.bytecode


def authenticate_cubic_native_sfnt_hash(native,expected_hash):
    """Match exact SFNT bytes, allowing only packaged WOFF2 bit11 removal.

    FontTools sets head.flags bit11 on WOFF2 serialization. The reviewed
    pre-WOFF2 UFS adapter stage has that one bit clear; all other native table
    bytes and head fields must still produce the exact declared input SHA.
    """
    import copy,io
    original_flags=native['head'].flags
    choices=[original_flags]
    if original_flags & 0x800:choices.append(original_flags & ~0x800)
    for flags in choices:
        snapshot=copy.deepcopy(native);snapshot.flavor=None;snapshot.recalcTimestamp=False
        snapshot['head'].flags=flags
        data=io.BytesIO();snapshot.save(data)
        if hashlib.sha256(data.getvalue()).hexdigest()==expected_hash:return flags
    raise AssertionError('Native cubic SFNT SHA does not match exact native or approved WOFF2 bit11 state')


def reviewed_cubic_change(before, after, isolated_file=None):
    """CFF pressure retains native output, glyphs/layout and exact rejected ink."""
    before,after=authenticated_review_metadata(before,after)
    import copy,json,re
    from collections import Counter
    from supplemental_cubic_adapter import METHOD,SOURCES,RESOLUTION,BOUNDS_TOLERANCE,recipe_hash,bounds
    source_name = Path(before['source']).name
    assert source_name == 'UFSZeroExt.otf' and source_name in SOURCES
    treatment = after['supplementalTreatment']
    assert treatment['method'] == METHOD == 'native-centred-cubic-pressure-v1'
    assert treatment['recipeSha256'] == recipe_hash(source_name)
    assert treatment['settings'] == SOURCES[source_name]
    assert treatment['resolution'] == RESOLUTION == 1024
    assert treatment['nativeBoundsPreserved'] is True
    assert treatment['nativeBoundsTolerance'] == BOUNDS_TOLERANCE == .01
    import cubic_source_preservation as policy_module
    policy=treatment.get('sourcePolicy');recipe=after['recipe']
    if policy:
        assert policy['module']=='tools/font/cubic_source_preservation.py'
        assert policy['sha256']==policy_module.policy_hash()
        assert policy['codepoints']==policy_module.POLICIES[source_name]==[0x18f6c]
        assert policy['reason']==policy_module.REASON
        policy_token=':cubic-source-preservation:'+policy_module.policy_hash()
        assert recipe.count(policy_token)==1
        recipe=recipe.replace(policy_token,'')
    else:assert ':cubic-source-preservation:' not in recipe
    token = ':supplemental-cubic-pressure:' + recipe_hash(source_name)
    assert recipe.count(token) == 1
    assert recipe.replace(token,'') == str(before['recipe'])
    frozen = ROOT/'output/font-review/supplemental-production-baselines'/Path(before['file']).name
    assert hashlib.sha256(frozen.read_bytes()).hexdigest() == before['sha256']
    output = ROOT/after['file']
    assert hashlib.sha256(output.read_bytes()).hexdigest() == after['sha256']
    assert output.stat().st_size == after['bytes']
    changed = {'sha256','bytes','recipe','supplementalTreatment','style'}
    if isolated_file is not None:
        assert output.resolve()==Path(isolated_file).resolve()
        changed.add('file')
    old_meta = {k:v for k,v in before.items() if k not in changed}
    new_meta = {k:v for k,v in after.items() if k not in changed}
    if 'nativeVariations' not in old_meta and new_meta.get('nativeVariations') == {}:
        new_meta.pop('nativeVariations')
    assert old_meta == new_meta
    assert after['style'] == before['style'] or after['style'] == 'smooth native cubic variable pressure; native CFF/layout retained; rejected drawings retained with explicit audit; specialist review provisional'
    assert treatment['charstringAdvancesMatchHmtx'] is True
    native_hash = treatment['nativeInputSha256']
    assert re.fullmatch('[0-9a-f]{64}',native_hash)
    expected_name = f"{native_hash}-{recipe_hash(source_name)}"
    if policy:expected_name += '-cubic-preserve-'+policy_module.policy_hash()
    expected_name += '.json'
    report_path = ROOT/treatment['report']
    assert report_path.parent == ROOT/'output/font-review/supplemental-cubic-production'
    assert report_path.name == expected_name
    report = json.loads(report_path.read_text())
    assert {k:v for k,v in report.items() if k != 'records'} == {k:v for k,v in treatment.items() if k != 'report'}
    assert dict(Counter(row['status'] for row in report['records'])) == report['counts']
    assert sum(report['counts'].values()) == report['glyphs']
    assert set(report['counts']) <= {'adapted','native-blank','native-retained-guard'}
    with TTFont(frozen) as native, TTFont(output) as actual:
        assert 'CFF ' in native and 'CFF ' in actual
        assert 'glyf' not in native and 'glyf' not in actual
        assert len(native.getGlyphOrder()) == len(actual.getGlyphOrder()) == report['glyphs']
        assert {cp:native.getGlyphID(name) for cp,name in native.getBestCmap().items()} == {cp:actual.getGlyphID(name) for cp,name in actual.getBestCmap().items()}
        assert treatment['nativeEmUnchanged'] == native['head'].unitsPerEm == actual['head'].unitsPerEm
        tags = [tag for tag in ('GPOS','GDEF','GSUB','hmtx','vmtx') if tag in native]
        assert sorted(tags) == treatment['layoutTablesUnchanged']
        assert native.getTableData('cmap')==actual.getTableData('cmap')
        for tag in ('GPOS','GDEF','GSUB','hmtx','vmtx'):
            assert (tag in native) == (tag in actual)
            if tag in native:assert native.getTableData(tag) == actual.getTableData(tag),tag
        assert [row['gid'] for row in report['records']] == list(range(report['glyphs']))
        from fontTools.misc.psCharStrings import T2CharString
        authenticate_cubic_native_sfnt_hash(native,native_hash)
        old_cs = native['CFF '].cff.topDictIndex[0].CharStrings
        new_cs = actual['CFF '].cff.topDictIndex[0].CharStrings
        if 0x18f6c in native.getBestCmap():assert policy is not None
        if policy:
            expected=[native.getGlyphID(native.getBestCmap()[cp]) for cp in policy['codepoints']]
            assert [row['gid'] for row in policy['glyphs']]==sorted(set(expected))
            for row in policy['glyphs']:
                gid=row['gid'];old_name,new_name=native.getGlyphName(gid),actual.getGlyphName(gid)
                assert row['glyph']==old_name
                assert row['charstringSha256']==hashlib.sha256(policy_module.charstring_bytes(old_cs[old_name])).hexdigest()
                record=report['records'][gid]
                assert record['status']=='native-retained-guard' and record['sourcePolicy'] is True
                assert record['reason']==policy_module.REASON
                assert evidence_drawing(frozen,old_name)==evidence_drawing(output,new_name)
        assert treatment['widthOnlyRepairGids']==sorted(row['gid'] for row in report['records'] if row.get('widthRepair'))
        if 0x18f6c in native.getBestCmap():
            assert treatment['widthOnlyRepairGids']==sorted(CUBIC_NATIVE_WIDTH_REPAIRS)
            assert all(native.getGlyphID(native.getBestCmap()[cp])==gid for gid,cp in CUBIC_NATIVE_WIDTH_REPAIRS.items())
        else:assert treatment['widthOnlyRepairGids']==[]
        for row in report['records']:
            old_name,new_name = native.getGlyphName(row['gid']),actual.getGlyphName(row['gid'])
            advance=native['hmtx'][old_name][0]
            assert actual['hmtx'][new_name][0]==advance
            assert_cubic_charstring_advance(new_cs[new_name],advance)
            old_box,new_box = bounds(native,old_name),bounds(actual,new_name)
            if old_box is None:assert new_box is None
            else:
                assert new_box is not None
                assert all(abs(a-b) <= BOUNDS_TOLERANCE for a,b in zip(old_box,new_box))
            if row['status'] == 'adapted':
                key=hashlib.sha256(json.dumps([treatment['recipeSha256'],native_hash,old_name,native['hmtx'][old_name]],sort_keys=True).encode()).hexdigest()
                cached=json.loads((ROOT/'build/font-cache/cubic-pressure'/(key+'.json')).read_text())
                assert cached['record']==row
                expected=T2CharString(program=cached['program'],private=old_cs[old_name].private,globalSubrs=old_cs[old_name].globalSubrs)
                # Compile the approved quantized program using the same Type2
                # encoder; serialized relative-coordinate bytes must be exact.
                expected.compile();observed=copy.deepcopy(new_cs[new_name]);observed.compile()
                assert expected.bytecode==observed.bytecode,(source_name,row['gid'])
                assert row['changedPixels'] > 0 and row['vectorChecks']['changedPixels'] > 0
                assert row['scale384Checks'] and row['nativeBoundsMaxError'] <= BOUNDS_TOLERANCE
            else:
                if row.get('widthRepair'):
                    key=hashlib.sha256(json.dumps([treatment['recipeSha256'],native_hash,old_name,native['hmtx'][old_name]],sort_keys=True).encode()).hexdigest()
                    cached=json.loads((ROOT/'build/font-cache/cubic-pressure'/(key+'.json')).read_text())
                    assert cached['record']=={k:v for k,v in row.items() if k!='widthRepair'}
                    assert cached['program'] is None
                assert_cubic_retained_charstring(old_cs[old_name],new_cs[new_name],advance,row)
    return True


def source_policy_closure(native,policy,original_names=None):
    """Metadata must name exactly the approved original component closure."""
    from source_preservation import POLICIES,policy_hash
    if policy['module']=='tools/font/duployan_source_preservation.py':
        import duployan_source_preservation as duployan
        assert policy['sha256']==duployan.policy_hash()
        assert policy['codepoints']==duployan.CODEPOINTS==[0x1bc63]
        assert policy['namedGlyphs']==duployan.NAMED_GLYPHS==['dupl.Dot.rel1']
        assert policy['reason']==duployan.REASON
        assert original_names is not None and len(original_names)==len(native.getGlyphOrder())
        extra=[native.getGlyphName(original_names.index(name)) for name in duployan.NAMED_GLYPHS]
    elif policy['module']=='tools/font/cuneiform_source_preservation.py':
        import cuneiform_source_preservation as cuneiform
        assert policy['sha256']==cuneiform.policy_hash()
        assert policy['codepoints']==cuneiform.CODEPOINTS==[0x12493]
        assert policy['namedGlyphs']==cuneiform.NAMED_GLYPHS==[]
        assert policy['reason']==cuneiform.REASON
        assert original_names is not None and len(original_names)==len(native.getGlyphOrder())
        extra=[native.getGlyphName(original_names.index(name)) for name in cuneiform.NAMED_GLYPHS]
    elif policy['module']=='tools/font/music_source_preservation.py':
        import music_source_preservation as music
        assert policy['sha256']==music.policy_hash()
        assert policy['codepoints']==music.CODEPOINTS==[]
        assert policy['namedGlyphs']==music.NAMED_GLYPHS==['u1D25B_low']
        assert policy['reason']==music.REASON
        construction=policy['sourceConstruction']
        assert construction==music.construction(construction['sourceFile'])
        assert Path(construction['sourceFile']).name==music.SOURCE
        assert construction['sourceCodepoint']==0x1d169
        assert original_names is not None and len(original_names)==len(native.getGlyphOrder())
        extra=[native.getGlyphName(original_names.index(name)) for name in music.NAMED_GLYPHS]
    elif policy['module']=='tools/font/chemical_source_preservation.py':
        import chemical_source_preservation as chemical
        assert policy['sha256']==chemical.policy_hash()
        assert policy['codepoints']==chemical.CODEPOINTS==[0x1cee0,0x1cee1,0x1cee2,0x1cee3,0x1cee4,0x1cee5,0x1cee8,0x1cee9,0x1ceea,0x1ceeb,0x1ceec,0x1ceed,0x1ceee,0x1ceef,0x1f8d1]
        assert policy['namedGlyphs']==chemical.NAMED_GLYPHS==[]
        assert policy['reason']==chemical.REASON
        construction=policy['sourceConstruction']
        assert construction==chemical.construction(construction['sourceFile'])
        assert Path(construction['sourceFile']).name==chemical.SOURCE
        assert original_names is not None and len(original_names)==len(native.getGlyphOrder())
        extra=[native.getGlyphName(original_names.index(name)) for name in chemical.NAMED_GLYPHS]
    else:
        assert policy['module']=='tools/font/source_preservation.py'
        assert policy['sha256']==policy_hash()
        assert policy['codepoints']==POLICIES['ArchaicCuneiformNumerals.ttf']==[0x1262d]
        extra=[]
    names=set()
    def visit(name):
        if name in names:return
        names.add(name)
        for child in native['glyf'][name].getComponentNames(native['glyf']):visit(child)
    for cp in policy['codepoints']:visit(native.getBestCmap()[cp])
    for name in extra:visit(name)
    gids={native.getGlyphID(name) for name in names}
    assert [row['gid'] for row in policy['glyphs']] == sorted(gids)
    if original_names is not None:
        assert all(row['glyph']==original_names[row['gid']] for row in policy['glyphs'])
    return gids


def assert_added_native_variant_families(before,after):
    """Only disclose UVS families that existed in frozen native cmap14 tables."""
    import json
    from native_variations import variation_ranges
    old_families=set(before['variationMarks']);new_families=set(after['variationMarks'])
    assert old_families <= new_families
    manifest=catalog_manifest(ROOT/'js/font-manifest.js')
    by_family={entry['family']:entry for entry in manifest['fonts']}
    for family in new_families-old_families:
        entry=by_family[family]
        assert entry.get('supplementalTreatment'),family
        frozen=ROOT/'output/font-review/supplemental-production-baselines'/Path(entry['file']).name
        baseline=json.loads(watch_evidence(frozen.with_suffix('.json')).read_text())
        assert 'nativeVariations' not in baseline
        assert reviewed_later_change(baseline,entry)
        native,actual=evidence_font(frozen),evidence_font(ROOT/entry['file'])
        assert entry['nativeVariations'] == variation_ranges(native) == variation_ranges(actual)
        assert entry['nativeVariations']
        row=after['variationMarks'][family]
        assert after['sources'][row['source']]['file'] == entry['file']
        wanted={int(cp) for cp in after['marks']}&actual.getBestCmap().keys()
        assert {int(cp) for cp in row['marks']} == wanted
        for cp,mark in row['marks'].items():
            assert mark['glyph'] == actual.getBestCmap()[int(cp)]
            assert after['variantDrawings'][mark['drawing']] == evidence_drawing(ROOT/entry['file'],mark['glyph'])


def assert_cached_glyf_drawing(data,actual,glyf_table,identity):
    """Exact bytes imply equal drawing under this same component table.

    Different serialization (including hints/bounds) keeps the original exact
    RecordingPen geometry comparison. No surrounding provenance guard changes.
    """
    from fontTools.ttLib.tables._g_l_y_f import Glyph
    from fontTools.pens.recordingPen import RecordingPen
    if data==actual.compile(glyf_table,recalcBBoxes=False):return
    expected=Glyph(data=data);expected.expand(glyf_table)
    a,b=RecordingPen(),RecordingPen()
    expected.draw(a,glyf_table);actual.draw(b,glyf_table)
    assert a.value==b.value,identity


def reviewed_dense_change(before,after,isolated_root=None):
    """Prove frozen-native -> reviewed dense cache -> actual painted output."""
    before,after=authenticated_review_metadata(before,after)
    import json,re
    from collections import Counter
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.ttLib.tables._g_l_y_f import Glyph
    import dense_native_adapter as dense
    treatment=after['denseTreatment'];profile=treatment['sourceProfile']
    kernel_hash=dense.recipe_hash(profile)
    assert profile in dense.SOURCES
    assert treatment['method'] == 'native-normal-finer-pen-v1'
    assert treatment['recipeSha256'] == kernel_hash
    assert treatment['settings'] == dense.SETTINGS
    assert treatment['nativeBoundsPreserved'] is True
    assert Path(treatment['source']).name == profile
    mixed=after.get('mixedNativeInput')
    if mixed:
        assert before['family'] == after['family'] == 'Dad CJK Variants'
        assert profile == 'Jigmo.ttf'
        frozen=ROOT/'output/font-review/supplemental-production-baselines/dad-cjk-variants.woff2'
        assert mixed == dict(file=frozen.relative_to(ROOT).as_posix(),sha256=before['sha256'],sources=before['sources'])
        assert after['sources'] == before['sources']
    else:
        assert Path(before['source']).name == profile
        assert treatment['source'] in {before['source'],profile}
        frozen=ROOT/'output/font-review/supplemental-production-baselines'/Path(before['file']).name
    assert hashlib.sha256(frozen.read_bytes()).hexdigest() == before['sha256']
    assert hashlib.sha256((ROOT/after['file']).read_bytes()).hexdigest() == after['sha256']
    assert after['bytes'] == (ROOT/after['file']).stat().st_size
    token=':dense-native-pen:'+kernel_hash
    assert after['recipe'].count(token) == 1
    assert after['recipe'].replace(token,'') == str(before.get('recipe','native-compatibility' if mixed else 1))
    changed={'sha256','bytes','recipe','denseTreatment','mixedNativeInput','style'}
    if isolated_root is not None:
        assert (ROOT/after['file']).resolve() == (Path(isolated_root)/before['file']).resolve()
        changed.add('file')
    old_meta={k:v for k,v in before.items() if k not in changed}
    new_meta={k:v for k,v in after.items() if k not in changed}
    if 'nativeVariations' not in old_meta and 'nativeVariations' in new_meta:
        from native_variations import variation_ranges
        assert new_meta['nativeVariations'] == variation_ranges(evidence_font(frozen)) == variation_ranges(evidence_font(ROOT/after['file']))
        new_meta.pop('nativeVariations')
    assert old_meta == new_meta
    native_hash=treatment['nativeInputSha256']
    assert re.fullmatch('[0-9a-f]{64}',native_hash)
    report_path=ROOT/treatment['report']
    assert report_path.parent == ROOT/'output/font-review/dense-production'
    assert report_path.name == native_hash+'-'+kernel_hash+'.json'
    report=json.loads(report_path.read_text())
    assert {k:v for k,v in report.items() if k!='records'} == {k:v for k,v in treatment.items() if k!='report'}
    assert not {'cacheHits','seconds'}&report.keys()
    assert dict(Counter(r['status'] for r in report['records'])) == report['counts']
    assert sum(report['counts'].values()) == report['glyphs']
    assert set(report['counts']) <= {'dense-native-pen','guarded-native-flex','native-retained-guard','native-blank'}
    with TTFont(frozen,recalcTimestamp=False) as original,TTFont(ROOT/after['file']) as actual:
        assert 'glyf' in original and 'glyf' in actual
        assert len(original.getGlyphOrder()) == len(actual.getGlyphOrder()) == report['glyphs']
        assert [r['gid'] for r in report['records']] == list(range(report['glyphs']))
        assert treatment['nativeEmUnchanged'] == original['head'].unitsPerEm == actual['head'].unitsPerEm
        for tag in ('cmap','GSUB','GPOS','GDEF','hmtx','vmtx'):
            assert (tag in original) == (tag in actual)
            if tag in original:assert original.getTableData(tag)==actual.getTableData(tag),tag
        assert sorted(t for t in ('GSUB','GPOS','GDEF','hmtx') if t in original)==treatment['layoutTablesUnchanged']
        # The adapter seeds from pre-post3 names. Restore those names before
        # decoding any native table, preserving source glyph IDs exactly.
        with TTFont(frozen,recalcTimestamp=False) as native:
            native.setGlyphOrder([r['glyph'] for r in report['records']])
            gs=native.getGlyphSet();actual_gs=actual.getGlyphSet()
            for row in report['records']:
                gid,name=row['gid'],row['glyph'];current=actual.getGlyphName(gid)
                source_glyph=native['glyf'][name];actual_glyph=actual['glyf'][current]
                frame=[getattr(source_glyph,a,0) for a in ('xMin','yMin','xMax','yMax')]
                assert frame == [getattr(actual_glyph,a,0) for a in ('xMin','yMin','xMax','yMax')]
                pen=SVGPathPen(gs);gs[name].draw(pen)
                key=hashlib.sha256(json.dumps([kernel_hash,native['head'].unitsPerEm,name,native['hmtx'][name],frame,pen.getCommands()],sort_keys=True).encode()).hexdigest()
                assert row['cacheKey'] == key
                meta=dense.CACHE/key[:2]/(key+'.json')
                cached=json.loads(meta.read_text())
                assert {k:v for k,v in row.items() if k not in {'gid','glyph','cacheKey'}} == cached
                if row['status'] in {'dense-native-pen','guarded-native-flex'}:
                    assert row['nativeBoundsPreserved'] is True
                    expected_count=len(source_glyph.getCoordinates(native['glyf'])[1])
                    assert len(actual_glyph.getCoordinates(actual['glyf'])[1]) == expected_count
                    phases={'1024','384','384@0,0.5','384@0.5,0','384@0.5,0.5'}
                    assert row['vectorGuards'].keys() == phases
                    for guard in row['vectorGuards'].values():
                        assert guard['minComponentAreaRatio'] >= .75
                        assert guard['maxComponentAreaRatio'] <= 1.2
                        assert guard['minCounterOverlap'] >= .75
                    data=watch_evidence(dense.CACHE/key[:2]/(key+'.glyf')).read_bytes()
                    assert_cached_glyf_drawing(data,actual_glyph,actual['glyf'],(profile,gid))
                else:
                    a,b=DecomposingRecordingPen(gs),DecomposingRecordingPen(actual_gs)
                    gs[name].draw(a);actual_gs[current].draw(b)
                    assert a.value == b.value,(profile,gid)
    return True


def assert_pressure_glyph_lineage(entry,codepoints=None):
    """Trace selected finished glyphs to exact frozen-native pressure inputs.

    Two native glyph names can share an isolated drawing but receive different
    seeded pressure. Preserve their native identity proof, then verify each
    finished drawing against its own exact source-derived cache artifact.
    """
    import json
    from fontTools.pens.recordingPen import RecordingPen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.ttLib.tables._g_l_y_f import Glyph
    import supplemental_adapter as pressure
    frozen=ROOT/'output/font-review/supplemental-production-baselines'/Path(entry['file']).name
    before=json.loads(frozen.with_suffix('.json').read_text())
    assert reviewed_later_change(before,entry)
    treatment=entry['supplementalTreatment']
    assert treatment['method']=='native-centred-distance-pressure-v1'
    report=json.loads(watch_evidence(ROOT/treatment['report']).read_text())
    with TTFont(frozen) as original,TTFont(ROOT/entry['file']) as actual,TTFont(frozen) as native:
        native.setGlyphOrder([row['glyph'] for row in report['records']])
        gs=native.getGlyphSet();current_gs=actual.getGlyphSet()
        selected=[(cp,original.getGlyphID(original.getBestCmap()[cp])) for cp in codepoints] if codepoints is not None else [(None,gid) for gid in range(len(original.getGlyphOrder()))]
        for cp,gid in selected:
            if cp is not None: assert actual.getGlyphID(actual.getBestCmap()[cp])==gid
            row=report['records'][gid];assert row['gid']==gid
            name=row['glyph'];current=actual.getGlyphName(gid)
            pen=SVGPathPen(gs);gs[name].draw(pen)
            key=hashlib.sha256(json.dumps([treatment['recipeSha256'],treatment['settings'],native['head'].unitsPerEm,native['hmtx'][name],name,pen.getCommands()],sort_keys=True).encode()).hexdigest()
            if row['status']=='adapted':
                cached=json.loads(watch_evidence(pressure.CACHE/(key+'.json')).read_text())
                assert {k:v for k,v in row.items() if k!='gid'}==cached
                data=watch_evidence(pressure.CACHE/(key+'.glyf')).read_bytes()
                assert_cached_glyf_drawing(data,actual['glyf'][current],actual['glyf'],(entry['family'],gid))
            else:
                a,b=DecomposingRecordingPen(gs),DecomposingRecordingPen(current_gs)
                gs[name].draw(a);current_gs[current].draw(b)
                assert_retained_native_drawing(entry['source'],row,a.value,b.value)


@reuse_reviewed_proof
def _complete_pressure_lineage(before,after):
    """Only complete successful all-GID proofs may share immutable evidence."""
    assert_pressure_glyph_lineage(after)
    return True


def pinned_packaging_font(entry):
    """Return native packaging evidence only after proving its complete finish lineage.

    Callers must compare pinned raw inputs against this font, and continue to
    check semantic behaviour and metrics against the actual current output.
    """
    import json
    if not (entry.get('supplementalTreatment') or entry.get('denseTreatment')):
        return TTFont(ROOT/entry['file'])
    frozen=ROOT/'output/font-review/supplemental-production-baselines'/Path(entry['file']).name
    before=json.loads(frozen.with_suffix('.json').read_text())
    assert before['source']==entry['source']
    assert reviewed_later_change(before,entry)
    if entry.get('supplementalTreatment',{}).get('method')=='native-centred-distance-pressure-v1':
        assert _complete_pressure_lineage(before,entry)
    return TTFont(frozen)
