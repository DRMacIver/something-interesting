"""Authenticate complete regular TT warmers and their GID-range auxiliaries.

No geometry rerender or public writes. Verify assigned source/count coverage,
private manifest/font hashes, frozen native layout/frames, exact recipe/report
metadata and every cached adapted glyph. Partial fonts never become public.
"""
import argparse
from collections import Counter
import hashlib
import inspect
import json
from pathlib import Path
import re
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen,DecomposingRecordingPen
from fontTools.ttLib.tables._g_l_y_f import Glyph
import supplemental_adapter as adapter
from verify_supplemental_production import verify as verify_frames
from warm_supplemental import ROOT,DEFAULT,assert_public_unchanged,sha

sys.path.insert(0,str(ROOT/'tests'))
from font_baseline_checks import reviewed_supplemental_change,assert_retained_native_drawing

BASELINES=ROOT/'output/font-review/supplemental-production-baselines'


def manifest(path):return json.loads(path.read_text().split('export default ')[1].rstrip(';\n'))
def read(path):return json.loads(path.read_text())


def cache_lineage(entry,full_report,records,cache):
    """Use authoritative full-source names even when checking partial ranges."""
    path=ROOT/entry['file'];frozen=BASELINES/path.name
    native=TTFont(frozen,recalcTimestamp=False);native.setGlyphOrder([r['glyph'] for r in full_report['records']])
    actual=TTFont(path);gs=native.getGlyphSet();current=actual.getGlyphSet()
    recipe=adapter.recipe_hash(entry['source']);settings=adapter.SOURCES[Path(entry['source']).name]
    for position,row in enumerate(records,1):
        if position%1000==0:print(Path(entry['source']).name,f'cache lineage {position}/{len(records)}',flush=True)
        gid=row['gid'];name=row['glyph'];new_name=actual.getGlyphName(gid)
        assert full_report['records'][gid]['glyph']==name
        pen=SVGPathPen(gs);gs[name].draw(pen)
        key=hashlib.sha256(json.dumps([recipe,settings,native['head'].unitsPerEm,native['hmtx'][name],name,pen.getCommands()],sort_keys=True).encode()).hexdigest()
        if not row.get('sourcePolicy'):
            assert read(cache/(key+'.json'))=={k:v for k,v in row.items() if k!='gid'},(entry['source'],gid,'cache record')
        if row['status']=='adapted':
            expected=Glyph(data=(cache/(key+'.glyf')).read_bytes());p,q=RecordingPen(),RecordingPen()
            expected.draw(p,actual['glyf']);actual['glyf'][new_name].draw(q,actual['glyf'])
            assert p.value==q.value,(entry['source'],gid,'cache glyph')
        else:
            p,q=DecomposingRecordingPen(gs),DecomposingRecordingPen(current)
            gs[name].draw(p);current[new_name].draw(q)
            assert_retained_native_drawing(entry['source'],row,p.value,q.value)
    return len(records)


def raw_unpreserved_cache_stage(before,entry,report):
    """Authenticate the old private pressure cache, never its final acceptance.

    These warmers ran before the separately approved joining preservation fix.
    The shipped helper remains strict: final policy/token is still mandatory.
    """
    source=Path(entry['source']).name
    expected={'NotoSansDuployan-Regular.ttf':10240,'NotoSansCuneiform-Regular.ttf':1239}
    assert source in expected
    treatment=entry['supplementalTreatment']
    assert treatment.get('sourcePolicy') is None
    assert ':duployan-source-preservation:' not in entry['recipe']
    assert ':cuneiform-source-preservation:' not in entry['recipe']
    token=':supplemental-pressure:'+adapter.recipe_hash(entry['source'])
    assert entry['recipe'].count(token)==1 and entry['recipe'].replace(token,'')==str(before['recipe'])
    assert treatment['method']==adapter.RECIPES['method']
    assert treatment['settings']==adapter.SOURCES[Path(entry['source']).name]
    assert treatment['resolution']==adapter.RECIPES['resolution']
    assert entry['style']=='smooth native component-centred variable pressure; native layout retained; rejected geometry retained with explicit audit; specialist review provisional'
    changed={'sha256','bytes','recipe','supplementalTreatment','style'}
    old={k:v for k,v in before.items() if k not in changed};new={k:v for k,v in entry.items() if k not in changed}
    if 'nativeVariations' not in old and 'nativeVariations' in new:
        from native_variations import variation_ranges
        native=TTFont(BASELINES/Path(entry['file']).name);actual=TTFont(ROOT/entry['file'])
        assert new['nativeVariations']==variation_ranges(native)==variation_ranges(actual)
        new.pop('nativeVariations')
    assert old==new
    assert report['glyphs']==expected[source]
    return dict(scope='private pre-preservation pressure-cache stage only',source=source,finalSourcePreservationRequired=True,finalDuployanWrapperRequired=source=='NotoSansDuployan-Regular.ttf',finalCuneiformWrapperRequired=source=='NotoSansCuneiform-Regular.ttf',fieldStyleAcceptance=False,reason='Whole-field joins or component connectivity require the separately approved final native preservation wrapper')


def regular(output,plan):
    checked=[];sources={}
    for group in plan['groups']:
        work=output/f"group-{group['index']}";complete=read(work/'complete.json');path=work/'manifest.js'
        selected={s['name'] for s in group['sources']}
        assert complete['status']=='private warm complete; public assets unchanged'
        assert set(complete['selected'])==selected
        assert complete['manifestSha256']==sha(path)
        entries=[e for e in manifest(path)['fonts'] if Path(e['source']).name in selected]
        assert {Path(e['source']).name for e in entries}==selected
        for entry in entries:
            name=Path(entry['source']).name;t=entry['supplementalTreatment']
            assert not t.get('partialWarm')
            assert t['recipeSha256']==next(s['recipeSha256'] for s in group['sources'] if s['name']==name)==adapter.recipe_hash(name)
            report=read(ROOT/t['report'])
            assert {k:v for k,v in report.items() if k!='records'}=={k:v for k,v in t.items() if k!='report'}
            assert dict(Counter(r['status'] for r in report['records']))==report['counts']
            print(name,'checking native frames/layout and exact source metadata',flush=True)
            frame_result=verify_frames(entry,BASELINES)
            before=read(BASELINES/(Path(entry['file']).stem+'.json'));before['file']=entry['file']
            pending_policy=None
            if name in {'NotoSansDuployan-Regular.ttf','NotoSansCuneiform-Regular.ttf'} and not t.get('sourcePolicy'):
                pending_policy=raw_unpreserved_cache_stage(before,entry,report)
            else:assert reviewed_supplemental_change(before,entry)
            print(name,'checking exact cache glyph lineage',flush=True)
            cache_count=cache_lineage(entry,report,report['records'],work/'glyph-cache')
            assert cache_count==report['glyphs']
            assert name not in sources
            sources[name]=(entry,report,work/'glyph-cache')
            checked.append(dict(group=group['index'],source=name,file=entry['file'],sha256=entry['sha256'],glyphs=cache_count,counts=report['counts'],nativeFrameLayoutVerified=True,cacheLineageVerified=True,privatePrePolicyStage=pending_policy))
            print(name,cache_count,'glyphs authenticated',flush=True)
    assert set(sources)=={s['name'] for group in plan['groups'] for s in group['sources']}
    return sources,checked


def auxiliary_inventory(path,source):
    """Bind the current private manifest to all381 frozen public entries.

    Range completions never recorded a private manifest hash. Authenticate the
    actual inventory now; prove only the selected glyph range as painted output.
    """
    public=manifest(ROOT/'js/font-manifest.js')['fonts'];private=manifest(path)['fonts']
    old={e['family']:e for e in public};new={e['family']:e for e in private}
    assert len(old)==len(new)==len(public)==len(private)==381
    assert old.keys()==new.keys()
    selected=[];inventory=[]
    for family,entry in new.items():
        original=old[family];target=ROOT/entry['file']
        assert target.resolve()==(path.parent/'fonts'/Path(original['file']).name).resolve()
        assert sha(target)==entry['sha256'] and target.stat().st_size==entry['bytes']
        before=dict(original,file=entry['file'])
        if Path(entry['source']).name!=source:
            assert before==entry,(family,'unassigned inventory metadata')
            assert entry['sha256']==original['sha256']
        else:
            selected.append(entry)
            changed={'sha256','bytes','recipe','supplementalTreatment','style','nativeVariations'}
            assert {k:v for k,v in before.items() if k not in changed}=={k:v for k,v in entry.items() if k not in changed}
            token=':supplemental-pressure:'+adapter.recipe_hash(source)
            assert entry['recipe'].count(token)==1 and entry['recipe'].replace(token,'')==str(original['recipe'])
            assert entry['style']=='smooth native component-centred variable pressure; native layout retained; rejected geometry retained with explicit audit; specialist review provisional'
            from native_variations import variation_ranges
            native=TTFont(ROOT/original['file']);actual=TTFont(target)
            assert entry.get('nativeVariations',{})==variation_ranges(native)==variation_ranges(actual)
            assert len(native.getGlyphOrder())==len(actual.getGlyphOrder())
            assert native['head'].unitsPerEm==actual['head'].unitsPerEm
            assert {cp:native.getGlyphID(n) for cp,n in native.getBestCmap().items()}=={cp:actual.getGlyphID(n) for cp,n in actual.getBestCmap().items()}
            for tag in ('GPOS','GDEF','GSUB','hmtx','vmtx'):
                assert (tag in native)==(tag in actual)
                if tag in native:assert native.getTableData(tag)==actual.getTableData(tag)
        inventory.append((family,entry['file'],entry['sha256'],entry['bytes']))
    assert len(selected)==1
    return selected[0],hashlib.sha256(json.dumps(sorted(inventory),sort_keys=True).encode()).hexdigest()


def auxiliaries(output,plan,sources):
    checked=[]
    for relative in plan.get('auxiliaryCompletions',[]):
        directory=output/Path(relative).parent;done=read(directory/'complete.json')
        assert done['status']=='partial-cache-range-complete; public assets unchanged'
        assert done['publicManifestSha256']==plan['publicManifestSha256']
        name=done['source'];assert name in sources
        authoritative,full,expected_cache=sources[name]
        assert done['recipeSha256']==adapter.recipe_hash(name)
        assert Path(done['sharedCache']).resolve()==expected_cache.resolve()
        partial=done['partialWarm'];start,stop=partial['gidStart'],partial['gidStopExclusive']
        assert directory.name==f'aux-{Path(name).stem}-{start}-{stop}'
        assert partial['scope']=='glyph-cache-range-only' and partial['completeSourceCoverage'] is False
        assert partial['sourceProfile']==name and partial['nativeGlyphs']==full['glyphs']
        assert partial['selectedGlyphs']==stop-start and partial['enumerateCalls']==1
        assert 0<=start<stop<=full['glyphs']
        assert partial['applySourceSha256']==hashlib.sha256(inspect.getsource(adapter.apply).encode()).hexdigest()
        backend=partial.get('validationBackend')
        if backend:
            from fast_supplemental_validation import REFERENCE_SHA256
            assert backend['sha256']==sha(ROOT/backend['module'])
            assert backend['referenceSha256']==REFERENCE_SHA256
        path=ROOT/done['privateManifest'];assert path.resolve().is_relative_to(directory.resolve())
        inner=read(path.parent/'complete.json')
        assert inner==done,'Range wrapper repeats its actual completion schema at both levels'
        entry,inventory_hash=auxiliary_inventory(path,name)
        t=entry['supplementalTreatment'];assert t['partialWarm']==partial
        assert t['recipeSha256']==done['recipeSha256']
        assert t['method']==adapter.RECIPES['method'] and t['settings']==adapter.SOURCES[name]
        report=read(ROOT/t['report'])
        assert {k:v for k,v in report.items() if k!='records'}=={k:v for k,v in t.items() if k!='report'}
        assert report['glyphs']==stop-start
        assert [r['gid'] for r in report['records']]==list(range(start,stop))
        assert dict(Counter(r['status'] for r in report['records']))==report['counts']
        assert cache_lineage(entry,full,report['records'],expected_cache)==stop-start
        checked.append(dict(source=name,start=start,stop=stop,glyphs=stop-start,privateManifestSha256=sha(path),privateInventorySha256=inventory_hash,scope='selected-cache-range-only; unassigned381inventory-sha-authenticated',fontSha256=entry['sha256'],recipeSha256=t['recipeSha256'],completion=relative))
        print(name,start,stop,'auxiliary authenticated',flush=True)
    return checked


def prior_groups(output,plan,log):
    """Bind successful source proofs from a failed prior aggregate execution.

    This is explicitly bounded to groups0+1; the original process exited1 at
    source9. No terminal-success claim is made for that aggregate execution.
    """
    text=log.read_text();checked=[];sources={}
    assert 'ArchaicCuneiformNumerals.ttf checking native frames/layout' in text
    assert 'Traceback (most recent call last)' in text
    bindings=[]
    for group in plan['groups']:
        if group['index'] not in (0,1):continue
        work=output/f"group-{group['index']}";path=work/'manifest.js';complete=read(work/'complete.json')
        selected={s['name'] for s in group['sources']}
        assert complete['status']=='private warm complete; public assets unchanged'
        assert set(complete['selected'])==selected and complete['manifestSha256']==sha(path)
        entries=[e for e in manifest(path)['fonts'] if Path(e['source']).name in selected]
        assert {Path(e['source']).name for e in entries}==selected
        for entry in entries:
            name=Path(entry['source']).name;t=entry['supplementalTreatment'];report_path=ROOT/t['report'];report=read(report_path)
            assert t['recipeSha256']==adapter.recipe_hash(name)==next(s['recipeSha256'] for s in group['sources'] if s['name']==name)
            assert not t.get('partialWarm')
            assert {k:v for k,v in report.items() if k!='records'}=={k:v for k,v in t.items() if k!='report'}
            assert dict(Counter(r['status'] for r in report['records']))==report['counts']
            assert text.count(f"{name} {report['glyphs']} glyphs authenticated\n")==1
            target=ROOT/entry['file'];assert sha(target)==entry['sha256'] and target.stat().st_size==entry['bytes']
            assert sha(ROOT/entry['source'])==entry['sourceSha256']
            baseline=BASELINES/target.name;old=read(BASELINES/(target.stem+'.json'));assert sha(baseline)==old['sha256']
            sources[name]=(entry,report,work/'glyph-cache')
            pending=raw_unpreserved_cache_stage(dict(old,file=entry['file']),entry,report) if name=='NotoSansDuployan-Regular.ttf' else None
            checked.append(dict(group=group['index'],source=name,file=entry['file'],sha256=entry['sha256'],glyphs=report['glyphs'],counts=report['counts'],nativeFrameLayoutVerified=True,cacheLineageVerified=True,privatePrePolicyStage=pending,proof='prior successful per-source proof; current immutable artifact binding',reportSha256=sha(report_path)))
        cache_digest=hashlib.sha256()
        for cachefile in sorted((work/'glyph-cache').iterdir()):
            if cachefile.is_file():cache_digest.update((cachefile.name+':'+sha(cachefile)+'\n').encode())
        bindings.append(dict(group=group['index'],completeSha256=sha(work/'complete.json'),manifestSha256=sha(path),currentCacheInventorySha256=cache_digest.hexdigest()))
    assert len(checked)==65
    proof=dict(scope='prior successful65 source proofs only; original aggregate exited1 at source9',originalLog=str(log),originalLogSha256=sha(log),originalAggregateExitCode=1,currentBindings=bindings,recipeIdentity='current source-specific recipe hashes equal frozen worker plan and reports; pressure kernels unchanged',writers='all regular and range workers terminal; dense cache is separate')
    print('Bound65 prior successful source proofs to unchanged completed artifacts',flush=True)
    return sources,checked,proof


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=DEFAULT);p.add_argument('--resume-prior-log',type=Path);a=p.parse_args()
    plan=read(a.output/'plan.json');assert_public_unchanged(plan)
    prior=None
    if a.resume_prior_log:
        sources,rows,prior=prior_groups(a.output,plan,a.resume_prior_log)
        rest,more=regular(a.output,dict(plan,groups=[g for g in plan['groups'] if g['index']==2]))
        assert not (sources.keys() & rest.keys());sources.update(rest);rows.extend(more)
    else:sources,rows=regular(a.output,plan)
    aux=auxiliaries(a.output,plan,sources);assert_public_unchanged(plan)
    record=dict(status='All regular and auxiliary warmers authenticated; public assets unchanged',publicManifestSha256=plan['publicManifestSha256'],sources=len(rows),glyphs=sum(r['glyphs'] for r in rows),regular=rows,auxiliaries=aux,priorSuccessfulScope=prior)
    (a.output/'verified.json').write_text(json.dumps(record,indent=2));print(record['status'],flush=True)

if __name__=='__main__':main()
