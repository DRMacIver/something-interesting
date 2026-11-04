"""Warm dense glyph caches using isolated copies of the complete real builder.

Only assigned dense shards rebuild. Public assets and live regular-TT warmer
inputs remain untouched. Synthetic private cache recipes are NOT public build
recipes or claims that unassigned native shards received a dense finish.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
from fontTools.ttLib import TTFont
import build_scripts as builder
import supplemental_adapter as regular
import dense_native_adapter as dense

ROOT=dense.ROOT
PUBLIC=ROOT/'js/font-manifest.js'
DEFAULT=ROOT/'output/font-review/dense-warm'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def manifest():return json.loads(PUBLIC.read_text().split('export default ')[1].rstrip(';\n'))

def cmap_key(points):return hashlib.sha256(json.dumps(sorted(points),separators=(',',':')).encode()).hexdigest()


def synthetic_recipe(recipe):
    text=str(recipe);token=':supplemental-pressure:'+dense.recipe_hash()
    markers=(':source-optics:',':native-glyph-bounds:',':native-variations:',':uvs-mark-closure:')
    places=[text.index(marker) for marker in markers if marker in text]
    position=min(places,default=len(text))
    return text[:position]+token+text[position:]


def assert_public(plan):
    assert sha(PUBLIC)==plan['publicManifestSha256'],'Public manifest changed while private caches warmed'
    for file,expected in plan['publicAssets'].items():assert sha(ROOT/file)==expected,f'Public font changed: {file}'


def plan(output,workers):
    data=manifest();rows=[];applied=set();assets={}
    for entry in data['fonts']:
        path=ROOT/entry['file'];actual=sha(path);assert actual==entry['sha256']
        assets[entry['file']]=actual;name=Path(entry['source']).name
        if entry.get('supplementalTreatment'):
            assert name in regular.SOURCES
            assert entry['supplementalTreatment']['recipeSha256']==regular.recipe_hash(name)
            applied.add(name)
        if name not in dense.SOURCES:continue
        with TTFont(path,lazy=True) as font:
            count=font['maxp'].numGlyphs;signature=cmap_key(font.getBestCmap())
        rows.append({'family':entry['family'],'source':entry['source'],'sourceName':name,'file':entry['file'],'sha256':actual,'glyphs':count,'cmapKey':signature,'originalRecipe':entry['recipe']})
    assert len({(r['sourceName'],r['cmapKey']) for r in rows})==len(rows),'Ambiguous dense native cmap-to-family mapping'
    bins=[{'index':i,'glyphs':0,'shards':[]} for i in range(workers)]
    for row in sorted(rows,key=lambda r:r['glyphs'],reverse=True):
        group=min(bins,key=lambda b:b['glyphs']);group['shards'].append(row);group['glyphs']+=row['glyphs']
    output.mkdir(parents=True,exist_ok=True)
    record={'status':'private warm plan; public normal builder remains sole integration writer','publicManifestSha256':sha(PUBLIC),'publicAssets':assets,'builderSha256':sha(Path(builder.__file__)),'denseRecipeSha256':dense.recipe_hash(),'alreadyAppliedTT':sorted(applied),'denseShards':rows,'groups':bins,'sharedGlyphCache':str(dense.CACHE.relative_to(ROOT))}
    (output/'plan.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'denseShards':len(rows),'glyphs':sum(r['glyphs'] for r in rows),'alreadyAppliedTT':len(applied),'groups':[{'index':g['index'],'shards':len(g['shards']),'glyphs':g['glyphs']} for g in bins]},indent=2))


def run(output,index):
    record=json.loads((output/'plan.json').read_text());assert_public(record)
    assert sha(Path(builder.__file__))==record['builderSha256'],'Builder changed before worker snapshot'
    assert dense.recipe_hash()==record['denseRecipeSha256'],'Dense kernel changed before warm run'
    group=next(g for g in record['groups'] if g['index']==index)
    assigned={r['family']:r for r in group['shards']};all_dense={r['family']:r for r in record['denseShards']}
    key_to_family={(r['sourceName'],r['cmapKey']):r['family'] for r in record['denseShards']}
    work=output/f'group-{index}';fonts=work/'fonts';reports=work/'reports';fonts.mkdir(parents=True,exist_ok=True)
    data=manifest();kept=[]
    for entry in data['fonts']:
        target=fonts/Path(entry['file']).name;shutil.copyfile(ROOT/entry['file'],target)
        entry['file']=target.relative_to(ROOT).as_posix()
        if entry['family'] in assigned:continue  # Sole forced rebuild set.
        if entry['family'] in all_dense:
            entry['recipe']=synthetic_recipe(entry['recipe'])
            entry['denseWarmState']='unassigned original cache hit; not claimed dense treated'
        kept.append(entry)
    private=work/'manifest.js';private.write_text('export default '+json.dumps(data|{'fonts':kept},separators=(',',':'))+';\n')
    builder.OUT=fonts;builder.MANIFEST=private;builder.CUBIC_SOURCES={}
    applied=set(record['alreadyAppliedTT'])
    builder.SUPPLEMENTAL_SOURCES={name:regular.SOURCES[name] for name in applied}|{name:{'privateDenseWarm':True} for name in dense.SOURCES}
    original_hash=builder.supplemental_recipe_hash
    builder.supplemental_recipe_hash=lambda source:dense.recipe_hash(source) if Path(source).name in dense.SOURCES else original_hash(source)
    seen={}
    def selected_apply(font,source):
        name=Path(source).name
        if name not in dense.SOURCES:raise RuntimeError(f'Unexpected non-dense cache miss during private warm: {source}')
        key=(name,cmap_key(font.getBestCmap()));family=key_to_family.get(key)
        if family not in assigned:raise RuntimeError(f'Unexpected unassigned dense rebuild: {source}, {family}, {key[1]}')
        if dense.recipe_hash()!=record['denseRecipeSha256']:raise RuntimeError('Frozen dense kernel changed mid-run')
        print(f'dense warm group{index}: {family} {name}, {len(font.getGlyphOrder())} native glyphs',flush=True)
        result=dense.apply(font,source,cache_dir=dense.CACHE,report_dir=reports)
        if result is None:raise RuntimeError('Assigned dense source lacked a real treatment result')
        seen[family]=result
        (work/'progress.json').write_text(json.dumps({'completedFamilies':sorted(seen),'assignedFamilies':sorted(assigned),'latestFamily':family,'latestCounts':result['counts']},indent=2)+'\n')
        return result
    builder.apply_supplemental=selected_apply
    builder.build()
    built=json.loads(private.read_text().split('export default ')[1].rstrip(';\n'))
    assert set(seen)==set(assigned),'Assigned dense shards missing callbacks'
    for entry in built['fonts']:
        family=entry['family']
        if family in assigned:
            result=entry.pop('supplementalTreatment',None)
            assert result and result['method']=='native-normal-finer-pen-v1'
            assert result['recipeSha256']==record['denseRecipeSha256']
            entry['denseTreatment']=result;entry['denseWarmState']='assigned native dense glyph cache warmed; private artifact only'
        else:
            original=next(e for e in manifest()['fonts'] if e['family']==family)
            assert entry['sha256']==original['sha256'],f'Unassigned shard rebuilt/changed: {family}'
    private.write_text('export default '+json.dumps(built,separators=(',',':'))+';\n')
    assert_public(record)
    (work/'complete.json').write_text(json.dumps({'status':'private dense cache warm complete; public assets unchanged','index':index,'families':sorted(seen),'counts':{family:result['counts'] for family,result in seen.items()},'privateManifestSha256':sha(private),'denseRecipeSha256':record['denseRecipeSha256']},indent=2)+'\n')
    print(f'Dense warm group{index} complete: {len(seen)} shards; public assets unchanged',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['plan','run','verify']);parser.add_argument('--output',type=Path,default=DEFAULT);parser.add_argument('--workers',type=int,default=3);parser.add_argument('--index',type=int)
    args=parser.parse_args()
    if args.action=='plan':plan(args.output,args.workers)
    elif args.action=='run':
        if args.index is None:parser.error('--index required for run')
        run(args.output,args.index)
    else:
        record=json.loads((args.output/'plan.json').read_text());assert_public(record)
        for group in record['groups']:assert (args.output/f"group-{group['index']}"/'complete.json').exists(),'Worker not complete'
        print('All private dense workers complete; public manifest/assets unchanged. Final normal build still required.')

if __name__=='__main__':main()
