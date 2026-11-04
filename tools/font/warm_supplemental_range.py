"""Isolated, explicitly partial GID-range warming with unchanged pressure code.

Only the single enumerate(native.getGlyphOrder()) in the original apply function
is filtered. Native snapshot/compound freeze, recipes, metrics, cache keys and
geometry remain the complete ordinary builder flow. Never publish these fonts.
"""
import argparse
import ast
import builtins
import hashlib
import inspect
import json
import os
from pathlib import Path,PosixPath
import tempfile
import textwrap
import time
from types import FunctionType

import supplemental_adapter as adapter
import warm_supplemental as warmer
import build_scripts as builder

ROOT=adapter.ROOT
SIGNWRITING='NotoSansSignWriting-Regular.ttf'


class AtomicCachePath(PosixPath):
    """Auxiliary writes publish complete payloads before existing readers see them."""
    def write_bytes(self,data):
        self.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=self.parent,prefix='.range-cache-',delete=False) as stream:
            stream.write(data);temporary=stream.name
        os.replace(temporary,self)
        return len(data)

    def write_text(self,data,encoding=None,errors=None,newline=None):
        if newline not in {None,''}:data=data.replace('\n',newline)
        return self.write_bytes(data.encode(encoding or 'utf-8',errors or 'strict'))

    def read_text(self,encoding=None,errors=None):
        # A legacy worker can have created its JSON file before finishing the
        # write. Its glyph payload is already closed before JSON is published.
        # Retry only this bounded publication window; malformed cache is an error.
        deadline=time.monotonic()+5
        while True:
            try:
                data=super().read_text(encoding=encoding,errors=errors)
                if self.suffix=='.json':json.loads(data)
                return data
            except (json.JSONDecodeError,UnicodeDecodeError,FileNotFoundError):
                if time.monotonic()>=deadline:raise
                time.sleep(.01)


def enumeration_proof():
    source=textwrap.dedent(inspect.getsource(adapter.apply));tree=ast.parse(source)
    calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='enumerate']
    assert len(calls)==1,'Pressure apply enumerate structure changed; range wrapper requires review'
    call=calls[0]
    assert not call.keywords and len(call.args)==1
    arg=call.args[0]
    assert isinstance(arg,ast.Call) and not arg.args and not arg.keywords
    assert isinstance(arg.func,ast.Attribute) and arg.func.attr=='getGlyphOrder'
    assert isinstance(arg.func.value,ast.Name) and arg.func.value.id=='native'
    assert any(isinstance(n,ast.For) and n.iter is call for n in ast.walk(tree))
    return dict(enumerateCalls=1,selection='only enumerate(native.getGlyphOrder())',applySourceSha256=hashlib.sha256(source.encode()).hexdigest())


def isolated_apply(report_root,cache_dir,enumerate_override=None):
    """Clone code, never mutate the original function/module/code object."""
    report_root=Path(report_root);report_root.mkdir(parents=True,exist_ok=True)
    namespace=dict(adapter.apply.__globals__)
    namespace['ROOT']=report_root;namespace['CACHE']=AtomicCachePath(cache_dir)
    # Baseline IO also stays private. No private public-manifest path exists, so
    # this original baseline function returns without touching public snapshots.
    namespace['baseline']=FunctionType(adapter.baseline.__code__,namespace,'baseline',adapter.baseline.__defaults__,adapter.baseline.__closure__)
    if enumerate_override is not None:namespace['enumerate']=enumerate_override
    clone=FunctionType(adapter.apply.__code__,namespace,adapter.apply.__name__,adapter.apply.__defaults__,adapter.apply.__closure__)
    assert clone.__code__ is adapter.apply.__code__
    return clone


def range_apply(report_root,cache_dir,start,stop,source_name=SIGNWRITING,expected_glyphs=None,validation_backend=None):
    assert 0<=start<stop
    proof=enumeration_proof();selection={};calls=[]
    def assigned_enumerate(values,start_index=0):
        assert start_index==0
        values=list(values)
        if expected_glyphs is not None:assert len(values)==expected_glyphs
        assert stop<=len(values),'Assigned range exceeds actual complete native glyph order'
        selection.update(nativeGlyphs=len(values),gidStart=start,gidStopExclusive=stop,selectedGlyphs=stop-start)
        return ((gid,name) for gid,name in builtins.enumerate(values) if start<=gid<stop)
    clone=isolated_apply(report_root,cache_dir,assigned_enumerate)
    def apply(font,source):
        assert Path(source).name==source_name
        result=clone(font,source)
        assert result is not None and result['recipeSha256']==adapter.recipe_hash(source)
        local=Path(report_root)/result['report'];report=json.loads(local.read_text())
        assert [r['gid'] for r in report['records']]==list(range(start,stop))
        assert result['glyphs']==stop-start
        partial=dict(scope='glyph-cache-range-only',completeSourceCoverage=False,sourceProfile=source_name,**selection,**proof)
        if validation_backend is not None:partial['validationBackend']=validation_backend
        report['partialWarm']=partial
        AtomicCachePath(local).write_text(json.dumps(report,indent=2)+'\n')
        result={**result,'partialWarm':partial}
        try:result['report']=local.relative_to(ROOT).as_posix()
        except ValueError:result['report']=str(local)
        calls.append(partial)
        return result
    apply.selection=selection;apply.calls=calls;apply.code_object=clone.__code__
    return apply


def run(output,start,stop,shared_cache,source_name=SIGNWRITING,validation_backend=None):
    output=Path(output).resolve();base_plan=json.loads((output/'plan.json').read_text())
    warmer.assert_public_unchanged(base_plan)
    sources=[s for group in base_plan['groups'] for s in group['sources'] if s['name']==source_name]
    assert len(sources)==1
    source=sources[0]
    assert 0<=start<stop<=source['glyphs']
    assert source['recipeSha256']==adapter.recipe_hash(source_name)
    aux=output/f'aux-{Path(source_name).stem}-{start}-{stop}';aux.mkdir(parents=True,exist_ok=True)
    plan={**base_plan,'groups':[dict(index=0,glyphs=stop-start,sources=[source])],
          'partialCacheWarm':dict(sourceProfile=source_name,gidStart=start,gidStopExclusive=stop,completeSourceCoverage=False)}
    (aux/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    private_root=aux/'partial-reports'
    callback=range_apply(private_root,shared_cache,start,stop,source_name,source['glyphs'],validation_backend)
    builder.apply_supplemental=callback
    # Use the real complete381font source-priority/subset/repair/closure flow.
    warmer.run(aux,0)
    assert len(callback.calls)==1,'Expected exactly one native source shard for assigned GIDs'
    warmer.assert_public_unchanged(base_plan)
    record=dict(status='partial-cache-range-complete; public assets unchanged',source=source_name,
                recipeSha256=adapter.recipe_hash(source_name),sharedCache=str(Path(shared_cache).resolve()),
                partialWarm=callback.calls[0],publicManifestSha256=base_plan['publicManifestSha256'],
                privateManifest=str((aux/'group-0/manifest.js').relative_to(ROOT)))
    (aux/'complete.json').write_text(json.dumps(record,indent=2)+'\n')
    # Replace generic warmer wording: these outputs are intentionally incomplete.
    (aux/'group-0/complete.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=warmer.DEFAULT)
    parser.add_argument('--shared-cache',type=Path,required=True)
    parser.add_argument('--source',default=SIGNWRITING)
    parser.add_argument('--fast-validation',action='store_true')
    parser.add_argument('--start',type=int,required=True);parser.add_argument('--stop',type=int,required=True)
    args=parser.parse_args();backend=None
    if args.fast_validation:
        from fast_supplemental_validation import install
        backend=install();print('Exact fast validation backend '+json.dumps(backend,sort_keys=True),flush=True)
    run(args.output,args.start,args.stop,args.shared_cache,args.source,backend)

if __name__=='__main__':main()
