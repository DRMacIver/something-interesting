"""Parallel, isolated warming of accepted pressure glyph caches.

Every worker retains the complete production source order, cmap novelty,
variation inventory, native repairs and layout closure computations. It copies
all current browser shards/manifest into a private output and enables only its
assigned new source recipes plus previously integrated pressure recipes.
Private glyph caches merge only after all workers terminate successfully.
The ordinary builder remains the sole writer of public browser assets.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from fontTools.ttLib import TTFont
import build_scripts as builder
import supplemental_adapter as adapter

ROOT=adapter.ROOT
PUBLIC_MANIFEST=ROOT/'js/font-manifest.js'
DEFAULT=ROOT/'output/font-review/supplemental-warm'


def load_manifest():
    return json.loads(PUBLIC_MANIFEST.read_text().split('export default ')[1].rstrip(';\n'))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def plan(output,workers=3):
    manifest=load_manifest();applied=set();source_rows={}
    for entry in manifest['fonts']:
        name=Path(entry['source']).name
        if name not in adapter.SOURCES:continue
        source_rows.setdefault(name,[]).append(entry)
        if entry.get('supplementalTreatment'):
            assert entry['supplementalTreatment']['recipeSha256']==adapter.recipe_hash(name),'Integrated recipe kernel changed before warm plan'
            applied.add(name)
    todo=[]
    for name,entries in source_rows.items():
        if name in applied:continue
        glyphs=sum(len(TTFont(ROOT/e['file']).getGlyphOrder()) for e in entries)
        todo.append(dict(name=name,glyphs=glyphs,recipeSha256=adapter.recipe_hash(name)))
    bins=[dict(index=i,glyphs=0,sources=[]) for i in range(workers)]
    for source in sorted(todo,key=lambda x:x['glyphs'],reverse=True):
        target=min(bins,key=lambda b:b['glyphs']);target['sources'].append(source);target['glyphs']+=source['glyphs']
    output.mkdir(parents=True,exist_ok=True)
    record=dict(publicManifestSha256=sha(PUBLIC_MANIFEST),alreadyApplied=sorted(applied),groups=bins,allSources=len(source_rows),newSources=len(todo),publicAssets={e['file']:e['sha256'] for e in manifest['fonts']})
    (output/'plan.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(dict(newSources=len(todo),groups=[dict(index=b['index'],glyphs=b['glyphs'],sources=len(b['sources'])) for b in bins]),indent=2))


def assert_public_unchanged(plan):
    assert sha(PUBLIC_MANIFEST)==plan['publicManifestSha256'],'Public manifest changed during isolated warming'
    for file,expected in plan['publicAssets'].items():assert sha(ROOT/file)==expected,f'Public font asset changed: {file}'


def run(output,index):
    if not hasattr(builder,'MANIFEST'):raise RuntimeError('Builder requires configurable MANIFEST entry point before isolated warming')
    plan=json.loads((output/'plan.json').read_text());assert_public_unchanged(plan)
    group=next(g for g in plan['groups'] if g['index']==index);selected={s['name'] for s in group['sources']};already=set(plan['alreadyApplied'])
    for source in group['sources']:assert source['recipeSha256']==adapter.recipe_hash(source['name']),'Frozen source recipe changed'
    work=output/f'group-{index}';fonts=work/'fonts';fonts.mkdir(parents=True,exist_ok=True)
    manifest=load_manifest()
    for entry in manifest['fonts']:
        destination=fonts/Path(entry['file']).name;shutil.copyfile(ROOT/entry['file'],destination)
        entry['file']=destination.relative_to(ROOT).as_posix()
    private_manifest=work/'manifest.js';private_manifest.write_text('export default '+json.dumps(manifest,separators=(',',':'))+';\n')
    # Full verify_sources/priority/covered/variation/subset flow remains intact.
    # Only the enabled adaptation set and file destinations are process-local.
    builder.OUT=fonts;builder.MANIFEST=private_manifest
    # Cubic and dense kernels have independent stages/caches. Their existing
    # public native recipes remain cached during these regular TT warmers.
    builder.CUBIC_SOURCES={}
    builder.SUPPLEMENTAL_SOURCES={name:adapter.SOURCES[name] for name in selected|already}
    original_apply=builder.apply_supplemental
    def selected_apply(font,source):
        name=Path(source).name
        if name in already and name not in selected:
            raise RuntimeError(f'Previously integrated recipe unexpectedly missed its private cache: {name}')
        return original_apply(font,source) if name in selected else None
    builder.apply_supplemental=selected_apply
    adapter.CACHE=work/'glyph-cache'
    builder.build()
    built=json.loads(private_manifest.read_text().split('export default ')[1].rstrip(';\n'))
    for entry in built['fonts']:
        name=Path(entry['source']).name
        if name in selected|already:
            assert entry.get('supplementalTreatment'),'Enabled source lacks real pressure evidence'
            assert entry['supplementalTreatment']['recipeSha256']==adapter.recipe_hash(name)
    assert_public_unchanged(plan)
    (work/'complete.json').write_text(json.dumps(dict(status='private warm complete; public assets unchanged',selected=sorted(selected),manifestSha256=sha(private_manifest)),indent=2))


def merge(output):
    plan=json.loads((output/'plan.json').read_text());assert_public_unchanged(plan);copied=0;duplicate=0
    for completion in plan.get('auxiliaryCompletions',[]):
        assert (output/completion).exists(),f'Auxiliary warmer has not completed: {completion}'
    for group in plan['groups']:
        work=output/f"group-{group['index']}";assert (work/'complete.json').exists(),'A warmer has not completed'
        for path in (work/'glyph-cache').glob('*'):
            if path.suffix not in {'.json','.glyf'}:continue
            target=adapter.CACHE/path.name
            if target.exists():
                assert sha(path)==sha(target),f'Cache collision differs: {path.name}'
                duplicate+=1
            else:
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target);copied+=1
    (output/'merge.json').write_text(json.dumps(dict(status='all private caches merged; public normal build still required',copiedFiles=copied,identicalDuplicates=duplicate),indent=2));print(copied,'cache files copied;',duplicate,'identical duplicates')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['plan','run','merge']);p.add_argument('--output',type=Path,default=DEFAULT);p.add_argument('--workers',type=int,default=3);p.add_argument('--index',type=int);a=p.parse_args()
    if a.action=='plan':plan(a.output,a.workers)
    elif a.action=='run':
        if a.index is None:p.error('--index required for run')
        run(a.output,a.index)
    else:merge(a.output)

if __name__=='__main__':main()
