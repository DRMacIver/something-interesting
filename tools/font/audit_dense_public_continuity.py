"""Read-only public dense continuity audit after the sole normal build exits.
Uses accepted byte-identical private candidates instead of repeating geometry tests.
"""
import argparse,json,hashlib
from pathlib import Path
from collections import Counter
from fontTools.ttLib import TTFont
from verify_dense_warm import manifest,read,sha,require,synthetic_recipe,ROOT
import dense_native_adapter as adapter


def diagnostic(before,after):
    with TTFont(before) as a,TTFont(after) as b:
        tags=set(a.keys())|set(b.keys());tags.discard('GlyphOrder')
        changed=sorted(t for t in tags if (t in a)!=(t in b) or a.getTableData(t)!=b.getTableData(t))
        geometry={'glyf','loca','CFF ','CFF2','hmtx','vmtx','cmap','GSUB','GPOS','GDEF','maxp'}
        return {'changedTables':changed,'metadataOnlyCandidate':not bool(set(changed)&geometry),'nativeEmEqual':a['head'].unitsPerEm==b['head'].unitsPerEm,'interpretation':'Diagnostic only; byte continuity has failed and is not claimed.'}


def audit(plan_dir,output):
    plan=read(plan_dir/'plan.json');proof=read(plan_dir/'verified.json');require(proof['status'].startswith('authenticated'),'Private proof unavailable')
    expected={r['family']:r for r in plan['denseShards']};require(len(expected)==123 and set(expected)==set(proof['families']),'Accepted123family union incomplete')
    public=manifest(ROOT/'js/font-manifest.js');entries={e['family']:e for e in public['fonts']};selected={e['family']:e for e in public['fonts'] if Path(e['source']).name in adapter.SOURCES}
    require(set(selected)==set(expected),'Public dense family/source inventory differs');require({Path(e['source']).name for e in selected.values()}==set(adapter.SOURCES),'Public five dense source set differs')
    groups={r['family']:g['index'] for g in plan['groups'] for r in g['shards']};records=[];errors=[];counts=Counter()
    for family,row in expected.items():
        e=entries[family];accepted=proof['families'][family];path=ROOT/e['file'];private=plan_dir/f"group-{groups[family]}"/'fonts'/Path(row['file']).name
        require(sha(private)==accepted['fontSha256'],'Accepted private font changed');require(e['file']==row['file'] and e['source']==row['source'],'Public source or shard path changed')
        actualsha=sha(path);require(actualsha==e['sha256'] and path.stat().st_size==e['bytes'],'Public manifest fontSHA/size mismatch')
        kernel=adapter.recipe_hash(e['source']);require(kernel==proof['denseRecipeSha256'],'Accepted kernel differs')
        expected_recipe=synthetic_recipe(row['originalRecipe'],kernel).replace(':supplemental-pressure:'+kernel,':dense-native-pen:'+kernel)
        require(e['recipe']==expected_recipe,'Public dense recipe token differs')
        treatment=e.get('denseTreatment');require(isinstance(treatment,dict),'Missing denseTreatment')
        report_path=ROOT/treatment['report'];require(report_path.resolve().is_relative_to((ROOT/'output/font-review/dense-production').resolve()),'Public report outside canonical directory')
        report=read(report_path);reportsha=sha(report_path);require(reportsha==accepted['reportSha256'],'Public stable detailed report differs from accepted exact report')
        require(treatment=={k:v for k,v in report.items() if k!='records'}|{'report':treatment['report']},'Public treatment differs from stable report')
        require(report['method']=='native-normal-finer-pen-v1' and report['recipeSha256']==kernel,'Public dense method/hash differs')
        require(report_path.name==report['nativeInputSha256']+'-'+kernel+'.json','Public content-addressed report differs')
        require(report['source']==e['source'] and report['sourceProfile']==Path(e['source']).name,'Public report source differs')
        require(report['settings']==adapter.SETTINGS and report['nativeBoundsPreserved'] is True,'Public settings/frame differ')
        require(report['glyphs']==accepted['glyphs'] and report['counts']==accepted['counts'],'Public coverage/counts differ');counts.update(report['counts'])
        result={'family':family,'source':e['source'],'file':e['file'],'publicFontSha256':actualsha,'acceptedPrivateFontSha256':accepted['fontSha256'],'byteIdentical':actualsha==accepted['fontSha256'],'report':treatment['report'],'reportSha256':reportsha,'acceptedReportSha256':accepted['reportSha256'],'method':report['method'],'recipeSha256':kernel,'glyphs':report['glyphs'],'counts':report['counts']}
        if not result['byteIdentical']:result['difference']=diagnostic(private,path);errors.append(family)
        records.append(result)
    result={'status':'PASS: all123public dense fonts and stable reports byte-identical to accepted authenticated private candidates' if not errors else 'FAIL: public dense font byte continuity differs; inspect diagnostics','publicManifestSha256':sha(ROOT/'js/font-manifest.js'),'acceptedPrimaryProof':str((plan_dir/'verified.json').relative_to(ROOT)),'acceptedPrimaryProofSha256':sha(plan_dir/'verified.json'),'denseRecipeSha256':proof['denseRecipeSha256'],'fonts':len(records),'glyphs':sum(r['glyphs'] for r in records),'counts':dict(counts),'sourceSet':sorted(adapter.SOURCES),'byteIdentityFailures':errors,'basis':'Exact public font and stable detailed-report SHA identity carries prior1024/four384phase native guards, layout/metrics/frame proof and actual22/44seven-field review; no repeated geometry build. Final overall suite is separate.','records':records}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n');require(not errors,'Public fonts differ from accepted private candidates; diagnostics saved');return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,default=ROOT/'output/font-review/dense-warm');p.add_argument('--output',type=Path,default=ROOT/'output/font-review/dense-production/public-continuity.json');a=p.parse_args();r=audit(a.plan.resolve(),a.output.resolve());print(r['status']);print(r['fonts'],'fonts;',r['glyphs'],'glyphs;',r['counts'])

if __name__=='__main__':main()
