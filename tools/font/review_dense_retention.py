"""Report real dense retentions and render bounded encoded cases for review.
Requires authenticated primary warm results. This never grants blanket visual
approval: nominal encodings, actual HarfBuzz selection and layout-only glyphs
are distinguished, and every retained source reason remains in the JSON.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from fontTools.ttLib import TTFont
from render_specimen import Font,render
from source_inventory import inventory,DATA
from audit import records

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())

def standard_pairs():
    return {tuple(int(v,16) for v in fields[0].split()) for fields in records(DATA/'StandardizedVariants.txt')}


def add_case(cache_cases,case):
    alias={'family':case['family'],'gid':case['gid'],'codepoints':case['assignedCodepoints'],'variationPairs':case['variationPairs'],'baseline':case['baseline'],'derived':case['derived']}
    existing=cache_cases.get(case['cacheKey'])
    if existing is None:
        cache_cases[case['cacheKey']]=case|{'aliases':[alias]}
    else:
        aliases=existing['aliases'];aliases.append(alias)
        if not (existing['assignedCodepoints'] or existing['variationPairs']) and (case['assignedCodepoints'] or case['variationPairs']):
            cache_cases[case['cacheKey']]=case|{'aliases':aliases}


def collect(output,plan_dir):
    output=Path(output).resolve();plan_dir=Path(plan_dir).resolve()
    plan=read(plan_dir/'plan.json');verified=read(plan_dir/'verified.json')
    if not verified['status'].startswith('authenticated'):raise ValueError('Dense warm results have not been authenticated')
    rows={r['family']:r for r in plan['denseShards']};groups={r['family']:g['index'] for g in plan['groups'] for r in g['shards']}
    if set(verified['families'])!=set(rows):raise ValueError('Authenticated primary dense union is incomplete')
    assigned=inventory();pairs=standard_pairs();retentions=[];counts=Counter();per_source={};cache_cases={}
    for family,evidence in verified['families'].items():
        report_path=ROOT/evidence['report']
        if sha(report_path)!=evidence['reportSha256']:raise ValueError('Authenticated dense report changed')
        report=read(report_path);row=rows[family];work=plan_dir/f"group-{groups[family]}"
        derived=work/'fonts'/Path(row['file']).name
        if sha(derived)!=evidence['fontSha256']:raise ValueError('Authenticated dense font changed')
        baseline=ROOT/'output/font-review/supplemental-production-baselines'/Path(row['file']).name
        if not baseline.exists():baseline=ROOT/row['file']
        if sha(baseline)!=row['sha256']:raise ValueError('Pinned native dense baseline changed or is unavailable')
        counts.update(report['counts']);profile=report['sourceProfile'];source=per_source.setdefault(profile,Counter());source.update(report['counts'])
        with TTFont(baseline) as native,TTFont(derived) as actual:
            cmap=actual.getBestCmap();encoded={}
            for cp,name in cmap.items():
                if cp in assigned:encoded.setdefault(actual.getGlyphID(name),[]).append(cp)
            variations={}
            for table in actual['cmap'].tables:
                if table.format!=14:continue
                for selector,entries in table.uvsDict.items():
                    for base,name in entries:
                        if base not in assigned or selector not in assigned:continue
                        target=name or cmap.get(base)
                        if target is None:continue
                        variations.setdefault(actual.getGlyphID(target),[]).append({'base':base,'selector':selector,'standardized':(base,selector) in pairs})
            order=native.getGlyphOrder();em=native['head'].unitsPerEm
            for entry in report['records']:
                if entry['status'] not in {'native-retained-guard','guarded-native-flex'}:continue
                gid=entry['gid'];glyph=native['glyf'][order[gid]]
                bounds=[getattr(glyph,a,0) for a in ('xMin','yMin','xMax','yMax')]
                points=sorted(encoded.get(gid,[]));selectors=variations.get(gid,[])
                case={'family':family,'profile':profile,'gid':gid,'originalGlyphName':entry['glyph'],'status':entry['status'],'reason':entry.get('reason',entry.get('penRejection')),'cacheKey':entry['cacheKey'],'baseline':str(baseline.relative_to(ROOT)),'derived':str(derived.relative_to(ROOT)),'nativeBounds':bounds,'nativeEm':em,'inkBoxAreaEm2':max(0,bounds[2]-bounds[0])*max(0,bounds[3]-bounds[1])/em**2,'assignedCodepoints':points,'variationPairs':selectors,'encodingRole':'nominal public/variation encoding' if points or selectors else 'unencoded layout closure; contextual reachability not established here','visualDisposition':'review pending; no automatic style approval'}
                retentions.append(case)
                add_case(cache_cases,case)
    ranked=sorted((r for r in cache_cases.values() if r['assignedCodepoints'] or r['variationPairs']),key=lambda r:r['inkBoxAreaEm2'],reverse=True)
    summary={'status':'Actual report-derived retention inventory; local visual triage pending','unicode':'18.0.0','nativeRecipeSha256':verified['denseRecipeSha256'],'fonts':len(rows),'glyphCounts':dict(counts),'bySource':{name:dict(value) for name,value in per_source.items()},'retainedCases':len(retentions),'uniqueRetainedArtwork':len(cache_cases),'uniqueEncodedCandidates':len(ranked),'unchangedNativeCases':sum(r['status']=='native-retained-guard' for r in retentions),'guardedNativeFlexCases':sum(r['status']=='guarded-native-flex' for r in retentions),'cases':retentions,'rankedEncoded':ranked,'limitations':['Direct cmap membership is a nominal encoding, not proof that native GSUB paints that glyph in a standalone field.','UVS entries distinguish standardized pairs from application/native transport pairs.','Unencoded layout closure is preserved in the inventory but not treated as a standalone encoded drawing.','All statuses/reasons come from authenticated build reports; fine-detail retention is not blanket native-reader/style approval.']}
    output.mkdir(parents=True,exist_ok=True);(output/'retained-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary


def specimens(summary,output,limit):
    cache={};chosen=[];deferred=[]
    def font(path):
        if path not in cache:cache[path]=Font(path)
        return cache[path]
    for case in summary['rankedEncoded']:
        selected=None
        # Each alias keeps its own font paths and GID. Never merge nominal
        # codepoints from another shard into this representative's font.
        for alias in case['aliases']:
            candidates=[chr(cp) for cp in alias['codepoints']]
            candidates += [chr(p['base'])+chr(p['selector']) for p in alias['variationPairs']]
            for candidate in candidates:
                try:source=font(alias['baseline']).shape(candidate,22);derived=font(alias['derived']).shape(candidate,22)
                except ValueError:continue
                source_ids=[g['gid'] for g in source['glyphs']];derived_ids=[g['gid'] for g in derived['glyphs']]
                if alias['gid'] in source_ids and source_ids==derived_ids:
                    selected=case|{'family':alias['family'],'gid':alias['gid'],'baseline':alias['baseline'],'derived':alias['derived'],'assignedCodepoints':alias['codepoints'],'variationPairs':alias['variationPairs'],'reviewText':candidate,'sourceGlyphIds':source_ids,'derivedGlyphIds':derived_ids};break
            if selected is not None:break
        if selected is None:
            deferred.append(case|{'reasonForNoStandaloneSpecimen':'Native shaping does not select retained nominal glyph with available standalone encoding; needs a genuine contextual field.'});continue
        chosen.append(selected)
        if len(chosen)>=limit:break
    for index in range(0,len(chosen),6):
        samples=[]
        for row in chosen[index:index+6]:
            identity=' '.join(f'{ord(c):X}' for c in row['reviewText'])
            for label,path in [('NATIVE BASELINE',row['baseline']),(row['status'].upper().replace('-',' '),row['derived'])]:
                samples.append({'label':f"{row['profile'].split('.')[0]} GID {row['gid']} CP {identity} {label}",'font':path,'text':row['reviewText']})
        render(samples,output/f'encoded-retentions-{index//6+1:02d}')
    (output/'encoded-review-corpus.json').write_text(json.dumps({'status':'Offline22/44px specimens generated; visual review and dispositions still required','selected':chosen,'needsContext':deferred},ensure_ascii=False,indent=2)+'\n')
    print(f'{len(chosen)} actual-shaped encoded cases rendered; {len(deferred)} nominal cases deferred for context; no blanket approvals')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--plan',type=Path,default=ROOT/'output/font-review/dense-warm');parser.add_argument('--output',type=Path,default=ROOT/'output/font-review/dense-retention-review');parser.add_argument('--top',type=int,default=24);args=parser.parse_args()
    output=args.output.resolve();summary=collect(output,args.plan.resolve());specimens(summary,output,args.top)

if __name__=='__main__':main()
