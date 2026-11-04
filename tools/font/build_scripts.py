"""Build licensed, shape-preserving browser shards from pinned sources.

These are provisional native forms, not a claim of completed comic styling.
Source hashes are verified first. Subsetting retains all OpenType features and
renames each derivative to avoid reserved font names.
"""
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont
from source_inventory import verify_sources
from canonical_composition import compose_kirat, compose_tulu
from ideograph_metrics import repair_ufs_metrics
from native_variations import variation_bases, retain_selectors, variation_ranges
from sibe_quotes import add_horizontal_sibe_quotes, derivations as sibe_derivations
from fullwidth_zero import add_fullwidth_zero, derivations as zero_derivations
from variation_marks import additional_marks
from jigmo_variation_marks import add_marks as add_jigmo_marks,POINTS as JIGMO_MARKS
from alphabet_ink import adapt as adapt_alphabet
from source_optics import apply as apply_source_optics, SCALES as OPTICAL_SCALES
from supplemental_adapter import apply as apply_supplemental, SOURCES as SUPPLEMENTAL_SOURCES, recipe_hash as supplemental_recipe_hash
from source_preservation import apply as apply_source_preservation, POLICIES as SOURCE_POLICIES, policy_hash as source_policy_hash
from supplemental_cubic_adapter import apply as apply_supplemental_cubic, SOURCES as CUBIC_SOURCES, recipe_hash as cubic_recipe_hash
from cuneiform_source_preservation import apply as apply_cuneiform_preservation, SOURCE as CUNEIFORM_POLICY_SOURCE, policy_hash as cuneiform_policy_hash
from duployan_source_preservation import apply as apply_duployan_preservation, SOURCE as DUPLOYAN_POLICY_SOURCE, policy_hash as duployan_policy_hash
from cubic_source_preservation import apply as apply_cubic_preservation, POLICIES as CUBIC_POLICIES, policy_hash as cubic_policy_hash
from dense_native_adapter import apply as apply_dense, SOURCES as DENSE_SOURCES, recipe_hash as dense_recipe_hash
from style_review import review_for_source
from music_source_preservation import apply as apply_music_preservation, SOURCE as MUSIC_POLICY_SOURCE, policy_hash as music_policy_hash
from chemical_source_preservation import apply as apply_chemical_preservation, SOURCE as CHEMICAL_POLICY_SOURCE, policy_hash as chemical_policy_hash
from cyrillic_mark import add_mark
from chemical_symbols import repair_isolobal
from yangqin_signs import add_signs as add_yangqin_signs, POINTS as YANGQIN_SIGNS
from vietnamese_marks import add_marks as add_vietnamese_marks, POINTS as VIETNAMESE_MARKS
from sharada_vowels import add_marks as add_sharada_vowels, POINTS as SHARADA_VOWELS
from kawi_nukta import add_mark as add_kawi_nukta, POINT as KAWI_NUKTA
from glagolitic_caudate import add_letters as add_glagolitic_caudate, POINTS as GLAGOLITIC_CAUDATE
from music_stems import add_stems as add_music_stems, POINTS as MUSIC_STEMS
from music_tremolos import add_marks as add_music_tremolos, POINTS as MUSIC_TREMOLOS
from music_articulations import add_marks as add_music_articulations, POINTS as MUSIC_ARTICULATIONS
from devanagari_alternate_ddda import add_letter as add_devanagari_ddda, POINT as DEVANAGARI_DDDA, SELECTOR as DEVANAGARI_DDDA_SELECTOR
from bengali_anusvara import add_mark as add_bengali_anusvara, POINT as BENGALI_ANUSVARA, SELECTOR as BENGALI_ANUSVARA_SELECTOR
from bengali_alternate_ba import add_letter as add_bengali_ba, POINT as BENGALI_BA, SELECTOR as BENGALI_BA_SELECTOR
from odia_marks import add_marks as add_odia_marks, POINTS as ODIA_MARKS
from hebrew_marks import add_marks as add_hebrew_marks, POINTS as HEBREW_MARKS
from arabic_marks import add_marks as add_arabic_marks, POINTS as ARABIC_MARKS
from arabic_crowns import add_crowns, POINTS as ARABIC_CROWNS
from audit import inventory, records, code_range, DATA

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/fonts/scripts'
MANIFEST = ROOT / 'js/font-manifest.js'
# Increment after changes to subsetting or naming rules.
RECIPE = 1


def ranges(points):
    result = []
    for cp in sorted(points):
        if result and cp == result[-1][1] + 1:
            result[-1][1] = cp
        else:
            result.append([cp, cp])
    return result


def priority(path):
    name = path.name
    if name == 'EastSyriacMalankara.ttf':
        return (6.5, name)  # Supplemental repertoire; preserve existing Syriac default.
    if name == 'NotoSerifDivesAkuru-Regular.ttf' and 'unicodia' in path.parts:
        return (5.5, name)  # Complete native repertoire before earlier partial source.
    if name == 'eot.ttf':
        return (4.5, name)  # Core Egyptian composition before coverage-only sources.
    for i, key in enumerate(['ArefRuqaa', 'Kalam', 'Gaegu', 'KleeOne', 'LXGWWenKai', 'UniHieroglyphica']):
        if key in name:
            return (i, name)
    return (7 if 'Jigmo' in name else 6, name)


def treatment_recipe(recipe, path):
    """Only enabled profiles add treatment or preservation recipe tokens."""
    if path.name in SUPPLEMENTAL_SOURCES:
        recipe = str(recipe) + ':supplemental-pressure:' + supplemental_recipe_hash(path)
        if path.name in SOURCE_POLICIES:
            recipe += ':source-preservation:' + source_policy_hash()
        if path.name == CUNEIFORM_POLICY_SOURCE:
            recipe += ':cuneiform-source-preservation:' + cuneiform_policy_hash()
        if path.name == DUPLOYAN_POLICY_SOURCE:
            recipe += ':duployan-source-preservation:' + duployan_policy_hash()
        if path.name == MUSIC_POLICY_SOURCE:
            recipe += ':music-source-preservation:' + music_policy_hash()
        if path.name == CHEMICAL_POLICY_SOURCE:
            recipe += ':chemical-source-preservation:' + chemical_policy_hash()
    if path.name in DENSE_SOURCES:
        recipe = str(recipe) + ':dense-native-pen:' + dense_recipe_hash(path)
    if path.name in CUBIC_SOURCES:
        recipe = str(recipe) + ':supplemental-cubic-pressure:' + cubic_recipe_hash(path)
        if path.name in CUBIC_POLICIES:
            recipe += ':cubic-source-preservation:' + cubic_policy_hash()
    return recipe


def apply_native_treatments(font, path):
    """Apply native TrueType treatments before names and optical scaling."""
    if path.name in DENSE_SOURCES:
        assert path.name not in SUPPLEMENTAL_SOURCES
        return None, apply_dense(font, path, report_dir=ROOT/'output/font-review/dense-production')
    if path.name not in SUPPLEMENTAL_SOURCES:
        return None, None
    if path.name == CUNEIFORM_POLICY_SOURCE:
        return apply_cuneiform_preservation(font, path, apply_supplemental), None
    if path.name == DUPLOYAN_POLICY_SOURCE:
        return apply_duployan_preservation(font, path, apply_supplemental), None
    if path.name == MUSIC_POLICY_SOURCE:
        return apply_music_preservation(font, path, apply_supplemental), None
    if path.name == CHEMICAL_POLICY_SOURCE:
        return apply_chemical_preservation(font, path, apply_supplemental), None
    return apply_source_preservation(font, path, apply_supplemental), None


def attach_style_review(entry):
    """Attach the authenticated sampled decision without changing font bytes."""
    review = review_for_source(entry['source'])
    entry['styleReview'] = review
    if any(marker in entry.get('style', '') for marker in ('custom visual review pending', 'specialist/style review pending')):
        entry['style'] = 'sampled source style disposition: ' + review['disposition'] + '; native identities and guarded exceptions retained'


def _build():
    OUT.mkdir(parents=True, exist_ok=True)
    grid_sources = {e['path'] for file in (ROOT/'data/font-sources').glob('*.json')
                    for e in json.loads(file.read_text()).get('files',[]) if e.get('build_target') in {'grid', 'emoji'}}
    paths = sorted((p for p in verify_sources() if p.relative_to(ROOT).as_posix() not in grid_sources if not any(tag in p.name for tag in ('Rotated', 'Vertical', 'Unjoined', 'UI-'))), key=priority)
    manifest_path = MANIFEST
    cached = {}
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text().split('export default ', 1)[1].rstrip(';\n'))
        cached = {e['family']: e for e in previous['fonts']}
    scopes = {entry['path']: entry['include_ranges']
              for file in (ROOT / 'data/font-sources').glob('*.json')
              for entry in json.loads(file.read_text()).get('files', [])
              if 'include_ranges' in entry}
    native_bounds = {entry['path'] for file in (ROOT/'data/font-sources').glob('*.json')
                     for entry in json.loads(file.read_text()).get('files',[])
                     if entry.get('preserve_native_bounds')}
    excludes = {entry['path']: entry['script_exclude_ranges']
                for file in (ROOT/'data/font-sources').glob('*.json')
                for entry in json.loads(file.read_text()).get('files',[])
                if 'script_exclude_ranges' in entry}
    ink_scopes = {entry['path']: entry['ink_ranges']
                  for file in (ROOT/'data/font-sources').glob('*.json')
                  for entry in json.loads(file.read_text()).get('files',[])
                  if 'ink_ranges' in entry}
    base = TTFont(ROOT / 'assets/fonts/dad-lettering-unicode.woff2')
    covered = set(base.getBestCmap())
    covered_variations = {(cp, selector) for selector, bases in variation_bases(base).items() for cp in bases}
    entries = []
    mark_points={cp for cp,category in inventory().items() if category.startswith('M')}
    for path in paths:
        source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        original = TTFont(path)
        if path.name == 'LXGWWenKai-Regular.ttf':
            add_horizontal_sibe_quotes(original)
        if path.name == 'NotoSansMath-Regular.ttf':
            zero_mark_repair=add_fullwidth_zero(original)
        borrowed_marks=JIGMO_MARKS if path.name in {'Jigmo2.ttf','Jigmo3.ttf'} else set()
        if borrowed_marks:
            mark_donor_path=path.parent/'Jigmo.ttf'
            mark_donor=TTFont(mark_donor_path)
            mark_donor_hash=hashlib.sha256(mark_donor_path.read_bytes()).hexdigest()
        cmap = set(original.getBestCmap())
        recipe = RECIPE
        scope = scopes.get(path.relative_to(ROOT).as_posix())
        if scope is not None:
            cmap &= {cp for a, b in scope for cp in range(a, b + 1)}
            recipe = str(RECIPE) + ':scope:' + json.dumps(scope, separators=(',', ':'))
        excluded = excludes.get(path.relative_to(ROOT).as_posix(), [])
        if excluded:
            cmap -= {cp for a,b in excluded for cp in range(a,b+1)}
            recipe = str(recipe) + ':exclude:' + json.dumps(excluded, separators=(',', ':'))
        if 0x16D68 in cmap:
            recipe = str(RECIPE) + ':kirat-ccmp:' + hashlib.sha256((ROOT/'tools/font/canonical_composition.py').read_bytes()).hexdigest()
        if path.name == 'UnicodiaDaarage.otf':
            recipe = str(recipe) + ':tulu-ccmp:' + hashlib.sha256((ROOT/'tools/font/canonical_composition.py').read_bytes()).hexdigest()
        if path.name == 'LXGWWenKai-Regular.ttf':
            cmap.update(YANGQIN_SIGNS | VIETNAMESE_MARKS)
            recipe = str(recipe)+':yangqin-signs:'+hashlib.sha256((ROOT/'tools/font/yangqin_signs.py').read_bytes()).hexdigest()
            recipe += ':vietnamese-marks:'+hashlib.sha256((ROOT/'tools/font/vietnamese_marks.py').read_bytes()).hexdigest()
        if path.name == 'UnicodiaFunky.ttf':
            recipe = str(recipe)+':chemical-repair:'+hashlib.sha256((ROOT/'tools/font/chemical_symbols.py').read_bytes()).hexdigest()
        if path.name == 'UFSZeroExt.otf':
            recipe = str(recipe) + ':ideograph-metrics:' + hashlib.sha256((ROOT/'tools/font/ideograph_metrics.py').read_bytes()).hexdigest()
        ink_scope = ink_scopes.get(path.relative_to(ROOT).as_posix(), [])
        if ink_scope:
            recipe = str(recipe) + ':alphabet-ink:' + json.dumps(ink_scope,separators=(',',':')) + ':' + hashlib.sha256((ROOT/'tools/font/alphabet_ink.py').read_bytes()).hexdigest()
        if path.name == 'NotoSansSharada-Regular.ttf':
            cmap.update(SHARADA_VOWELS)
            recipe=str(recipe)+':sharada-named:'+hashlib.sha256((ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf').read_bytes()).hexdigest()+':' +':'.join(hashlib.sha256((ROOT/'tools/font'/name).read_bytes()).hexdigest() for name in ['sharada_vowels.py','music_mark_rules.py','indic_input_rules.py'])
        if path.name == 'NotoSansKawi-Regular.ttf':
            cmap.add(KAWI_NUKTA)
            recipe = str(recipe)+':kawi-nukta:'+hashlib.sha256((ROOT/'tools/font/kawi_nukta.py').read_bytes()).hexdigest()+':'+hashlib.sha256((ROOT/'tools/font/music_mark_rules.py').read_bytes()).hexdigest()+':'+hashlib.sha256((ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf').read_bytes()).hexdigest()
        if path.name == 'NotoSansGlagolitic-Regular.ttf':
            cmap.update(GLAGOLITIC_CAUDATE)
            recipe = str(recipe)+':caudate-chrivi-uvs:'+hashlib.sha256((ROOT/'tools/font/glagolitic_caudate.py').read_bytes()).hexdigest()+':'+hashlib.sha256((ROOT/'build/unicode-sources/shafarik/Shafarik-Regular.ttf').read_bytes()).hexdigest()
        if path.name == 'NotoMusic-Regular.ttf':
            cmap.update(MUSIC_ARTICULATIONS | MUSIC_TREMOLOS.keys() | MUSIC_STEMS)
            recipe = str(recipe)+':music-stems:'+hashlib.sha256((ROOT/'tools/font/music_stems.py').read_bytes()).hexdigest()
            recipe = str(recipe)+':music-tremolos:'+hashlib.sha256((ROOT/'tools/font/music_tremolos.py').read_bytes()).hexdigest()+':'+hashlib.sha256((ROOT/'tools/font/music_mark_rules.py').read_bytes()).hexdigest()
            recipe = str(recipe)+':music-articulations:'+hashlib.sha256((ROOT/'tools/font/music_articulations.py').read_bytes()).hexdigest()+':'+hashlib.sha256((ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf').read_bytes()).hexdigest()
        if path.name == 'NotoSans-Regular.ttf':
            cmap.add(0x1E08F)
            recipe = str(recipe) + ':cyrillic-mark:' + hashlib.sha256((ROOT/'tools/font/cyrillic_mark.py').read_bytes()).hexdigest() + ':' + hashlib.sha256((ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf').read_bytes()).hexdigest()
        if path.name in ('NotoSansBengali-Regular.ttf', 'NotoSansDevanagari-Regular.ttf'):
            recipe = str(recipe)+':indic-input-rules:'+hashlib.sha256((ROOT/'tools/font/indic_input_rules.py').read_bytes()).hexdigest()
        if path.name == 'NotoSansDevanagari-Regular.ttf':
            cmap.add(DEVANAGARI_DDDA)
            recipe = str(recipe)+':alternate-ddda:'+hashlib.sha256((ROOT/'tools/font/devanagari_alternate_ddda.py').read_bytes()).hexdigest()
        if path.name == 'NotoSansBengali-Regular.ttf':
            cmap.update((BENGALI_BA, BENGALI_ANUSVARA))
            recipe = str(recipe)+':bengali-anusvara:'+hashlib.sha256((ROOT/'tools/font/bengali_anusvara.py').read_bytes()).hexdigest()+':'+hashlib.sha256((ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf').read_bytes()).hexdigest()
            recipe = str(recipe)+':alternate-ba:'+hashlib.sha256((ROOT/'tools/font/bengali_alternate_ba.py').read_bytes()).hexdigest()
        if path.name == 'NotoSansOriya-Regular.ttf':
            cmap.update(ODIA_MARKS)
            recipe = str(recipe)+':odia-marks:'+hashlib.sha256((ROOT/'tools/font/odia_marks.py').read_bytes()).hexdigest()+':'+hashlib.sha256((ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf').read_bytes()).hexdigest()
        if path.name == 'NotoRashiHebrew-Regular.ttf':
            cmap.update(HEBREW_MARKS)
            recipe = str(recipe)+':hebrew-marks:'+hashlib.sha256((ROOT/'tools/font/hebrew_marks.py').read_bytes()).hexdigest()+':'+hashlib.sha256((ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf').read_bytes()).hexdigest()
        if path.name == 'ScheherazadeNew-Regular.ttf':
            cmap.update(ARABIC_MARKS | ARABIC_CROWNS)
            recipe = str(recipe) + ':arabic-crowns:' + hashlib.sha256((ROOT/'tools/font/arabic_crowns.py').read_bytes()).hexdigest() + ':arabic-marks:' + hashlib.sha256((ROOT/'tools/font/arabic_marks.py').read_bytes()).hexdigest() + ':' + hashlib.sha256((ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf').read_bytes()).hexdigest()
        if path.name == 'LXGWWenKai-Regular.ttf':
            recipe = str(recipe)+':horizontal-sibe:'+hashlib.sha256((ROOT/'tools/font/sibe_quotes.py').read_bytes()).hexdigest()
        if path.name == 'NotoSansMath-Regular.ttf':
            recipe = str(recipe)+':fullwidth-zero:'+hashlib.sha256((ROOT/'tools/font/fullwidth_zero.py').read_bytes()).hexdigest()
            recipe += ':unicode-math-marks:'+hashlib.sha256((ROOT/'tools/font/math_unicode_marks.py').read_bytes()).hexdigest()
        recipe = treatment_recipe(recipe, path)
        if path.name in OPTICAL_SCALES:
            recipe = str(recipe) + ':source-optics:' + hashlib.sha256((ROOT/'tools/font/source_optics.py').read_bytes()).hexdigest()
        if path.relative_to(ROOT).as_posix() in native_bounds:
            recipe=str(recipe)+':native-glyph-bounds:1'
        if variation_bases(original):
            recipe = str(recipe) + ':native-variations:' + hashlib.sha256((ROOT/'tools/font/native_variations.py').read_bytes()).hexdigest()
        novel = cmap - covered
        variation_points = {cp for selector, bases in variation_bases(original).items()
                            for cp in bases if cp in cmap and (cp, selector) not in covered_variations}
        if not novel and not variation_points:
            continue
        # Keep complete script repertoires together for contextual shaping.
        # Large ideograph fonts are split; layout closure preserves substitutions.
        ideographs = any(key in path.name for key in ('Jigmo', 'LXGWWenKai', 'KleeOne', 'Tangut', 'DadSealSource'))
        chunks = [cmap] if len(cmap) <= 4096 or not ideographs else [set(sorted(cmap)[i:i+1024]) for i in range(0, len(cmap), 1024)]
        first_entry = len(entries)
        for index, points in enumerate(chunks):
            if not points & novel and not points & variation_points:
                continue
            extra_marks=additional_marks(original,points,(cmap&mark_points)|borrowed_marks)
            borrowed_for_chunk=extra_marks&borrowed_marks
            chunk_recipe=recipe
            if extra_marks:
                chunk_recipe=str(recipe)+':uvs-mark-closure:'+hashlib.sha256((ROOT/'tools/font/variation_marks.py').read_bytes()).hexdigest()+':'+json.dumps(sorted(extra_marks),separators=(',',':'))
            if borrowed_for_chunk:
                chunk_recipe+=':jigmo-native-marks:'+mark_donor_hash+':'+hashlib.sha256((ROOT/'tools/font/jigmo_variation_marks.py').read_bytes()).hexdigest()
            identity = hashlib.sha256((str(path.relative_to(ROOT)) + ':' + str(index)).encode()).hexdigest()[:12]
            family = 'Dad Script ' + identity
            target = OUT / (identity + '.woff2')
            old = cached.get(family)
            if old and old.get('sourceSha256') == source_hash and old.get('recipe') == chunk_recipe and target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == old['sha256']:
                entries.append(old)
                continue
            font = TTFont(path, recalcTimestamp=False,
                          recalcBBoxes=path.relative_to(ROOT).as_posix() not in native_bounds)
            if borrowed_for_chunk:
                add_jigmo_marks(font,mark_donor,borrowed_for_chunk)
            if path.name == 'NotoSansMath-Regular.ttf':
                add_fullwidth_zero(font)
            if path.name == 'LXGWWenKai-Regular.ttf':
                add_horizontal_sibe_quotes(font)
                add_yangqin_signs(font)
                add_vietnamese_marks(font)
            if path.name == 'NotoSansSharada-Regular.ttf':
                add_sharada_vowels(font,TTFont(ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf'))
            if path.name == 'NotoSansKawi-Regular.ttf':
                add_kawi_nukta(font,TTFont(ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf'))
            if path.name == 'NotoSansGlagolitic-Regular.ttf':
                add_glagolitic_caudate(font,TTFont(ROOT/'build/unicode-sources/shafarik/Shafarik-Regular.ttf'))
            if path.name == 'NotoMusic-Regular.ttf':
                add_music_articulations(font,TTFont(ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf'))
                add_music_tremolos(font)
                add_music_stems(font,TTFont(ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf'))
            if path.name == 'NotoSans-Regular.ttf':
                add_mark(font, TTFont(ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf'))
            if path.name == 'NotoSansDevanagari-Regular.ttf':
                add_devanagari_ddda(font)
            if path.name == 'NotoSansBengali-Regular.ttf':
                add_bengali_ba(font)
                add_bengali_anusvara(font, TTFont(ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf'))
            if path.name == 'NotoSansOriya-Regular.ttf':
                add_odia_marks(font,TTFont(ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf'))
            if path.name == 'NotoRashiHebrew-Regular.ttf':
                add_hebrew_marks(font,TTFont(ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf'))
            if path.name == 'ScheherazadeNew-Regular.ttf':
                add_arabic_marks(font, TTFont(ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf'))
                add_crowns(font, TTFont(ROOT/'build/unicode-sources/ufs/UFSZeroExt.otf'))
            options = subset.Options()
            options.layout_features = ['*']
            if path.name == 'NotoSansSharada-Regular.ttf':
                options.glyph_names = True
            options.name_IDs = ['*']
            options.name_legacy = True
            options.name_languages = ['*']
            sub = subset.Subsetter(options=options)
            subset_points = set(points)|extra_marks
            if path.name == 'ScheherazadeNew-Regular.ttf':
                subset_points.update(range(0xE0100, 0xE010F))
                subset_points.update(range(0xE0120, 0xE0136))
            if path.name == 'NotoSansOriya-Regular.ttf':
                subset_points.update((0xE0140, 0xE0141))
            if path.name == 'NotoSansBengali-Regular.ttf':
                subset_points.update((BENGALI_BA_SELECTOR, BENGALI_ANUSVARA_SELECTOR, BENGALI_ANUSVARA_SELECTOR + 1))
            if path.name == 'NotoSansDevanagari-Regular.ttf':
                subset_points.add(DEVANAGARI_DDDA_SELECTOR)
            if path.name == 'NotoSansGlagolitic-Regular.ttf':
                subset_points.update(range(0xE0170, 0xE0173))
            if path.name == 'NotoSansSharada-Regular.ttf':
                subset_points.update(range(0xe0180,0xe0188))
            sub.populate(unicodes=retain_selectors(font, subset_points))
            sub.subset(font)
            if 0x16D68 in cmap:
                compose_kirat(font)
            if path.name == 'UnicodiaDaarage.otf':
                compose_tulu(font)
            if path.name == 'UnicodiaFunky.ttf':
                repair_isolobal(font)
            if ink_scope:
                adapt_alphabet(font, {cp for a,b in ink_scope for cp in range(a,b+1)})
            supplemental_treatment, dense_treatment = apply_native_treatments(font, path)
            optical_size = apply_source_optics(font, path)
            for record in font['name'].names:
                if record.nameID in {1, 2, 3, 4, 6, 16, 17}:
                    value = 'Regular' if record.nameID in {2, 17} else family.replace(' ', '') if record.nameID == 6 else family
                    record.string = value.encode(record.getEncoding(), errors='replace')
            if path.name == 'UFSZeroExt.otf':
                repair_ufs_metrics(font)
            if 'CFF ' in font:
                cff = font['CFF '].cff
                cff.fontNames = [family.replace(' ', '')]
                for top in cff.topDictIndex:
                    top.FamilyName = family
                    top.FullName = family
            if path.name in CUBIC_SOURCES:
                supplemental_treatment = apply_cubic_preservation(font, path, apply_supplemental_cubic)
            font.flavor = 'woff2'
            target = OUT / (identity + '.woff2')
            font.save(target)
            raw = target.read_bytes()
            entries.append({'family': family, 'file': target.relative_to(ROOT).as_posix(),
                            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
                            'sourceSha256': source_hash, 'recipe': chunk_recipe,
                            'ranges': ranges(font.getBestCmap()), 'source': path.relative_to(ROOT).as_posix(),
                            'nativeVariations': variation_ranges(font),
                            **({'opticalSize': optical_size} if optical_size else {}),
                            **({'supplementalTreatment': supplemental_treatment} if supplemental_treatment else {}),
                            **({'denseTreatment': dense_treatment} if dense_treatment else {}),
                            **({'variationDerivations':sibe_derivations(font.getBestCmap())} if path.name=='LXGWWenKai-Regular.ttf' else {}),
                            **({'variationDerivations':zero_derivations()} if path.name=='NotoSansMath-Regular.ttf' else {}),
                            **({'markAttachmentRepair':zero_mark_repair} if path.name=='NotoSansMath-Regular.ttf' else {}),
                            **({'additionalSources':[{'source':mark_donor_path.relative_to(ROOT).as_posix(),'sourceSha256':mark_donor_hash,'ranges':ranges(borrowed_for_chunk),'licence':'assets/fonts/licenses/Jigmo-CC0.txt','adaptation':'native same-family CJK marks, metrics, classes and compatible hinting retained with supplementary variation bases'}]} if borrowed_for_chunk else {}),
                            'style': 'light pen adaptation of supplemental outlines; specialist/style review pending' if ink_scope else 'provisional licensed source; custom visual review pending'})
        for entry in entries[first_entry:]:
            covered_variations.update((cp, int(selector))
                for selector, spans in entry.get('nativeVariations', {}).items()
                for a, b in spans for cp in range(a, b+1))
        covered.update(cmap)
        print(path.name, len(entries), flush=True)
    for entry in entries:
        if entry['source'].endswith('/DadSealSans-Regular.otf'):
            entry['licence']='assets/fonts/licenses/SealSans-AGPL-3.0.txt'
            entry['correspondingSource']='assets/fonts/sources/DadSealSans-source.zip'
            entry['correspondingSourceSha256']=hashlib.sha256((ROOT/entry['correspondingSource']).read_bytes()).hexdigest()
            entry['notices']=['assets/fonts/licenses/README-DadSealSans.txt',entry['licence']]
            entry['additionalSources']=[{'source':'build/unicode-sources/seal-sans/SealSans-Regular_v1.otf','licence':entry['licence'],'adaptation':'139 native cubic drawings translated +340 y; unchanged horizontal geometry and advances; unrelated tone UVS excluded'}]
            entry['style']='native curves; reference topology compared for all 139 characters; comic style and specialist review provisional'
        if entry['source'].endswith('/DadTaiYo.ttf'):
            entry['style']='guarded horizontal stroke reconstruction; body anchors and adjacent marks reviewed; specialist review provisional'
            entry['additionalSources']=[{'source':'build/unicode-sources/unifont/unifont_upper-18.0.01.otf','licence':'assets/fonts/licenses/Unifont-OFL.txt','adaptation':'55 guarded outlines; body-specific mark anchors; horizontal mkmk; preserved spacing letters and explicit KVO'}]
        if entry['source'].endswith('/DadGaray.ttf'):
            entry['style']='guarded stroke reconstruction; case and RTL mark geometry reviewed; specialist review provisional'
            entry['additionalSources']=[{'source':'build/unicode-sources/unifont/unifont_upper-18.0.01.otf','licence':'assets/fonts/licenses/Unifont-OFL.txt','adaptation':'69 guarded outlines; native mark/mkmk; nonjoining RTL forms and preserved case'}]
        if entry['source'].endswith('/DadTolong.ttf'):
            entry['style']='guarded stroke reconstruction; 54 bases visually reviewed; donor marks and specialist review provisional'
            entry['additionalSources']=[{'source':'build/unicode-sources/unifont/unifont_upper-18.0.01.otf','licence':'assets/fonts/licenses/Unifont-OFL.txt','adaptation':'pixel stroke reconstruction preserving components and counters'}, {'source':'build/unicode-sources/noto/NotoSans-Regular.ttf','licence':'assets/fonts/licenses/Noto-OFL.txt','adaptation':'nine combining marks with native mark and mkmk attachment'}]
        if entry['source'].endswith('/NotoSansSharada-Regular.ttf'):
            entry['additionalSources']=[{'source':'build/unicode-sources/unicodia/UnicodiaFunky.ttf','ranges':ranges(SHARADA_VOWELS),'licence':'assets/fonts/licenses/Unicodia-LICENSE-Funky.txt','adaptation':'native mark classes; separate below-arc clearance; preserved AA conjunct bodies; zero advance for Mn signs; UVS compatibility'}]
        if entry['source'] in ink_scopes:
            entry['style']='light pen adaptation of supplemental outlines; specialist/style review pending'
        if entry.get('supplementalTreatment'):
            if entry['supplementalTreatment']['method'] == 'native-centred-cubic-pressure-v1':
                entry['style']='smooth native cubic variable pressure; native CFF/layout retained; rejected drawings retained with explicit audit; specialist review provisional'
            else:
                entry['style']='smooth native component-centred variable pressure; native layout retained; rejected geometry retained with explicit audit; specialist review provisional'
        if entry.get('denseTreatment'):
            entry['style']='finer native strokes with smooth contour variation; native layout retained; guarded original glyphs retained; specialist review provisional'
    for entry in entries:
        if entry['source'].endswith('/NotoSans-Regular.ttf'):
            entry['additionalSources'] = [{'source': 'build/unicode-sources/unicodia/UnicodiaFunky.ttf',
                'ranges': [[0x1E08F, 0x1E08F]], 'licence': 'assets/fonts/licenses/Unicodia-LICENSE-Funky.txt',
                'adaptation': 'native Cyrillic mark anchors and mark filtering sets'}]
    for entry in entries:
        if entry['source'].endswith('/NotoSansKawi-Regular.ttf'):
            entry['additionalSources']=[{'source':'build/unicode-sources/unicodia/UnicodiaFunky.ttf','ranges':[[KAWI_NUKTA,KAWI_NUKTA]],'licence':'assets/fonts/licenses/Unicodia-LICENSE-Funky.txt','adaptation':'three-dot outline; four-dot anusvara combination; native above-form attachment and preserved syllable bodies'}]
        if entry['source'].endswith('/NotoSansGlagolitic-Regular.ttf'):
            entry['additionalSources']=[{'source':'build/unicode-sources/shafarik/Shafarik-Regular.ttf','ranges':ranges(GLAGOLITIC_CAUDATE),'licence':'assets/fonts/licenses/Shafarik-OFL.txt','adaptation':'native capital/lowercase heights; retained descenders; native centered mark anchors'}]
        if entry['source'].endswith('/NotoMusic-Regular.ttf'):
            entry['additionalSources']=[{'source':'build/unicode-sources/ufs/UFSZeroExt.otf','ranges':ranges(MUSIC_ARTICULATIONS | MUSIC_STEMS),'licence':'assets/fonts/licenses/UFSZeroExt-OFL.txt','adaptation':'native musical articulation and flag attachment; contextual positioning; zero advance; uninverted articulations; special ornaments retained through native stem variants'}]
        if entry['source'].endswith('/NotoSansBengali-Regular.ttf'):
            entry['additionalSources']=[{'source':'build/unicode-sources/ufs/UFSZeroExt.otf','ranges':[[BENGALI_ANUSVARA,BENGALI_ANUSVARA]],'licence':'assets/fonts/licenses/UFSZeroExt-OFL.txt','adaptation':'native above-mark attachment and filtering sets; zero advance; UVS browser compatibility'}]
        if entry['source'].endswith('/NotoSansOriya-Regular.ttf'):
            entry['additionalSources']=[{'source':'build/unicode-sources/ufs/UFSZeroExt.otf','ranges':[[0xb53,0xb54]],'licence':'assets/fonts/licenses/UFSZeroExt-OFL.txt','adaptation':'native Odia overline classes; supplemental vowel anchors; zero advance; cubic-to-quadratic conversion; UVS browser compatibility'}]
        if entry['source'].endswith('/NotoRashiHebrew-Regular.ttf'):
            entry['additionalSources']=[{'source':'build/unicode-sources/ufs/UFSZeroExt.otf','ranges':[[0x5c8,0x5c9]],'licence':'assets/fonts/licenses/UFSZeroExt-OFL.txt','adaptation':'native sheva/dagesh anchor classes; zero advance; cubic-to-quadratic conversion'}]
        if entry['source'].endswith('/ScheherazadeNew-Regular.ttf'):
            entry['additionalSources'] = [{'source': 'build/unicode-sources/ufs/UFSZeroExt.otf', 'ranges': ranges(ARABIC_MARKS | ARABIC_CROWNS), 'licence': 'assets/fonts/licenses/UFSZeroExt-OFL.txt', 'adaptation': 'scaled cubic outlines; native mark anchors; aligned left-only crown joins; UVS browser compatibility'}]
    for entry in entries:
        attach_style_review(entry)
    ignorable = {cp for fields in records(DATA / 'DerivedCoreProperties.txt') if fields[1] == 'Default_Ignorable_Code_Point' for cp in code_range(fields[0])}
    behavioural = {cp for cp, cat in inventory().items() if cat in {'Cc', 'Cf', 'Zs', 'Zl', 'Zp'} or cp in ignorable}
    manifest = {'unicode': '18.0.0', 'behaviouralRanges': ranges(behavioural), 'baseRanges': ranges(base.getBestCmap()), 'fonts': entries}
    manifest_path.write_text('// Generated by tools/font/build_scripts.py; see font source manifests for licences.\nexport default ' + json.dumps(manifest, separators=(',', ':')) + ';\n')
    active = {e['file'] for e in entries}
    for old in cached.values():
        if old['file'] not in active:
            (ROOT / old['file']).unlink(missing_ok=True)
    print(f'{len(entries)} shards, {sum(e["bytes"] for e in entries):,} bytes')


def build():
    """Roll back browser shards and manifest if any source build fails.

    Per-glyph caches and isolated provenance reports survive for resumability.
    """
    OUT.mkdir(parents=True,exist_ok=True)
    manifest=MANIFEST
    original_manifest=manifest.read_bytes() if manifest.exists() else None
    originals={p.name for p in OUT.glob('*.woff2')}
    with tempfile.TemporaryDirectory(prefix='dad-script-build-') as temporary:
        backup=Path(temporary)
        for name in originals:shutil.copyfile(OUT/name,backup/name)
        try:_build()
        except BaseException:
            for path in OUT.glob('*.woff2'):
                if path.name not in originals:path.unlink()
            for name in originals:shutil.copyfile(backup/name,OUT/name)
            if original_manifest is None:manifest.unlink(missing_ok=True)
            else:manifest.write_bytes(original_manifest)
            print('Script build failed; browser font shards and manifest restored.',flush=True)
            raise


if __name__ == '__main__':
    build()
