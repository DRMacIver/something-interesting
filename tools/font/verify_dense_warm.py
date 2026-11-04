"""Authenticate dense private warm completion before the public build stage.
No glyph geometry is regenerated. Public/native mapping, layout, private font
hashes, report coverage and actual shared-cache payloads are authenticated.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from fontTools.ttLib import TTFont
import dense_native_adapter as adapter

ROOT=adapter.ROOT
PUBLIC=ROOT/'js/font-manifest.js'


def require(condition,message):
    if not condition:raise ValueError(message)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def manifest(path):return json.loads(Path(path).read_text().split('export default ')[1].rstrip(';\n'))
def cmap_key(points):return hashlib.sha256(json.dumps(sorted(points),separators=(',',':')).encode()).hexdigest()

def synthetic_recipe(recipe,kernel):
    text=str(recipe);markers=(':source-optics:',':native-glyph-bounds:',':native-variations:',':uvs-mark-closure:')
    position=min([text.index(m) for m in markers if m in text],default=len(text))
    return text[:position]+':supplemental-pressure:'+kernel+text[position:]


def authenticate_complete(complete,group,kernel,private):
    families=[r['family'] for r in group['shards']]
    require(complete.get('status')=='private dense cache warm complete; public assets unchanged','Unexpected completion status')
    require(complete.get('index')==group['index'],'Completion worker index differs')
    require(complete.get('denseRecipeSha256')==kernel,'Completion recipe differs')
    require(len(complete.get('families',[]))==len(families) and set(complete['families'])==set(families),'Completion assigned family set differs')
    require(set(complete.get('counts',{}))==set(families),'Completion count family coverage differs')
    require(complete.get('privateManifestSha256')==sha(private),'Completed private manifest changed')


def verify_plan(output,cache_memo=None):
    output=Path(output);plan=read(output/'plan.json');kernel=adapter.recipe_hash();public=manifest(PUBLIC)
    require(plan['denseRecipeSha256']==kernel,'Frozen dense kernel differs from plan')
    require(sha(PUBLIC)==plan['publicManifestSha256'],'Public manifest changed')
    public_by_family={e['family']:e for e in public['fonts']}
    require(len(public_by_family)==len(public['fonts']),'Duplicate public families')
    require(set(plan['publicAssets'])=={e['file'] for e in public['fonts']},'Public asset inventory differs')
    for file,digest in plan['publicAssets'].items():require(sha(ROOT/file)==digest,f'Public font changed: {file}')
    dense_expected={e['family'] for e in public['fonts'] if Path(e['source']).name in adapter.SOURCES}
    all_rows=plan['denseShards'];all_by_family={r['family']:r for r in all_rows}
    require(len(all_by_family)==len(all_rows) and set(all_by_family)==dense_expected,'Full dense native family inventory differs')
    union=[r['family'] for g in plan['groups'] for r in g['shards']]
    expected=set(plan.get('selectedFamilies',dense_expected))
    require(len(union)==len(set(union)) and set(union)==expected,'Assigned unique dense family union differs')
    require(expected<=dense_expected,'Assigned unknown dense families')
    if plan.get('auxiliary'):
        require('selectedFamilies' in plan and len(expected)<len(dense_expected),'Auxiliary subset not explicit')
        require(sha(ROOT/plan['basePlan'])==plan['basePlanSha256'],'Auxiliary parent plan changed')
    else:require(expected==dense_expected,'Primary plan does not cover all dense shards')
    cache=ROOT/plan['sharedGlyphCache'];memo={} if cache_memo is None else cache_memo
    inventory=hashlib.sha256();results={};statuses=Counter();encoded_retained=0
    for group in plan['groups']:
        work=output/f"group-{group['index']}";private=work/'manifest.js';complete=read(work/'complete.json')
        authenticate_complete(complete,group,kernel,private)
        built=manifest(private);by_family={e['family']:e for e in built['fonts']};assigned={r['family']:r for r in group['shards']}
        require(len(by_family)==len(built['fonts']) and set(by_family)==set(public_by_family),'Private font family inventory differs')
        for family,entry in by_family.items():
            font_path=ROOT/entry['file'];expected_path=work/'fonts'/Path(public_by_family[family]['file']).name
            require(font_path.resolve()==expected_path.resolve(),'Private entry does not reference its private font copy')
            require(sha(font_path)==entry['sha256'] and font_path.stat().st_size==entry['bytes'],f'Private font SHA/size differs: {family}')
            if family not in assigned:
                require(entry['sha256']==public_by_family[family]['sha256'],f'Unassigned font changed: {family}')
                if family in dense_expected:require('denseTreatment' not in entry,'Unassigned native font falsely claims a dense treatment')
                continue
            row=assigned[family];require(row==all_by_family[family],'Worker assignment diverges from full native inventory')
            require(entry['source']==row['source'],'Private native source identity differs')
            require(entry['recipe']==synthetic_recipe(row['originalRecipe'],kernel),'Private synthetic warm recipe differs')
            treatment=entry.get('denseTreatment');require(isinstance(treatment,dict),'Assigned dense treatment absent')
            require(treatment.get('recipeSha256')==kernel and treatment.get('method')=='native-normal-finer-pen-v1','Dense treatment identity differs')
            report_path=ROOT/treatment['report'];require(report_path.resolve().is_relative_to((work/'reports').resolve()),'Dense report lies outside its private report directory')
            report=read(report_path);require(report_path.name==report['nativeInputSha256']+'-'+kernel+'.json','Dense report content-addressed name differs')
            require(treatment=={k:v for k,v in report.items() if k!='records'}|{'report':treatment['report']},'Manifest treatment differs from detailed report')
            require(report['source']==row['source'] and report['sourceProfile']==row['sourceName'],'Report source/profile differs')
            require(report['settings']==adapter.SETTINGS and report['nativeBoundsPreserved'] is True,'Report guard/frame recipe differs')
            records=report['records'];n=row['glyphs']
            require(report['glyphs']==n and len(records)==n,'Report does not cover every actual native glyph')
            require({r['gid'] for r in records}==set(range(n)) and len({r['glyph'] for r in records})==n,'Dense original glyph ID/name coverage differs')
            counts=dict(Counter(r['status'] for r in records));require(counts==report['counts']==complete['counts'][family],'Dense status totals differ')
            require(set(counts)<={'dense-native-pen','guarded-native-flex','native-retained-guard','native-blank'},'Unknown dense glyph disposition')
            with TTFont(ROOT/row['file']) as native, TTFont(font_path) as derived:
                require(native['maxp'].numGlyphs==derived['maxp'].numGlyphs==n,'Actual maxp count differs')
                require(cmap_key(native.getBestCmap())==row['cmapKey'],'Planned native cmap identity differs')
                require(native['head'].unitsPerEm==derived['head'].unitsPerEm==report['nativeEmUnchanged'],'Native em differs')
                for tag in ('cmap','hmtx','GSUB','GPOS','GDEF'):
                    require((tag in native)==(tag in derived),f'Native {tag} presence differs')
                    if tag in native:require(native.getTableData(tag)==derived.getTableData(tag),f'Native {tag} bytes differ')
                expected_layout=sorted(t for t in ('hmtx','GSUB','GPOS','GDEF') if t in native)
                require(report['layoutTablesUnchanged']==expected_layout,'Reported native layout coverage differs')
                encoded={derived.getGlyphID(name) for name in derived.getBestCmap().values()}
                encoded_retained+=sum(r['gid'] in encoded and r['status']=='native-retained-guard' for r in records)
            for record in records:
                key=record['cacheKey'];require(len(key)==64 and all(c in '0123456789abcdef' for c in key),'Malformed dense cache key')
                cached_path=cache/key[:2]/(key+'.json');glyph_path=cache/key[:2]/(key+'.glyf')
                if key not in memo:
                    cached=read(cached_path);drawing=sha(glyph_path) if cached['status'] in {'dense-native-pen','guarded-native-flex'} else None
                    if drawing:require(glyph_path.stat().st_size>0,'Empty adapted dense cache drawing')
                    memo[key]=(cached,sha(cached_path),drawing)
                cached,meta_sha,drawing_sha=memo[key]
                require(cached=={k:v for k,v in record.items() if k not in {'glyph','gid','cacheKey'}},'Detailed glyph report differs from actual cache disposition')
                inventory.update((key+meta_sha+(drawing_sha or '')).encode())
            statuses.update(counts);results[family]={'fontSha256':entry['sha256'],'reportSha256':sha(report_path),'report':treatment['report'],'glyphs':n,'counts':counts}
        print(f"Authenticated dense group{group['index']}: {len(assigned)} assigned shards; all private/public font hashes intact",flush=True)
    require(set(results)==expected,'Authenticated dense result union differs')
    return {'status':'authenticated private dense warm complete; final public build still required','plan':str(output/'plan.json'),'denseRecipeSha256':kernel,'publicManifestSha256':plan['publicManifestSha256'],'publicAssets':len(plan['publicAssets']),'expectedDenseFamilies':len(dense_expected),'verifiedFamilies':len(results),'verifiedGlyphs':sum(r['glyphs'] for r in results.values()),'counts':dict(statuses),'encodedNativeRetained':encoded_retained,'cacheInventorySha256':inventory.hexdigest(),'families':results}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'output/font-review/dense-warm');parser.add_argument('--ahead',type=Path);args=parser.parse_args()
    memo={};primary=verify_plan(args.output,memo);(args.output/'verified.json').write_text(json.dumps(primary,indent=2)+'\n')
    if args.ahead:
        ahead=verify_plan(args.ahead,memo)
        require(set(ahead['families'])<=set(primary['families']),'Ahead verification includes unknown original families')
        for family,row in ahead['families'].items():
            expected=primary['families'][family]
            require({k:v for k,v in row.items() if k!='report'}=={k:v for k,v in expected.items() if k!='report'},'Repeated ahead/native warm result differs')
        (args.ahead/'verified.json').write_text(json.dumps(ahead,indent=2)+'\n')
    print('AUTHENTICATED: assigned family unions, completion manifests, font/report/cache coverage and frozen public assets; final normal public integration remains required.')

if __name__=='__main__':main()
