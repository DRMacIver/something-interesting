"""Reuse successful read-only native proofs only for identical complete inputs.

This caches assertions, never builder outputs. Each reuse revalidates every
observed dependency and replays it into any enclosing immutable catalog batch.
"""
import builtins
from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import importlib
import io
import json
import os
import sys
import types
from pathlib import Path
from threading import RLock

_READS=ContextVar('native_proof_reads',default=None)
_LOCK=RLock()
_PROOFS=OrderedDict()
_MODULES=('native_sfnt_loader','source_optics','style_review','supplemental_adapter','supplemental_pressure','supplemental_cubic_adapter','dense_native_adapter','source_preservation','cubic_source_preservation','duployan_source_preservation','cuneiform_source_preservation','music_source_preservation','chemical_source_preservation','music_tremolos','music_mark_rules','chemical_symbols','alphabet_ink','build_cjk_variants','math_unicode_marks','build_marked_cjk_variants')
_UNSUPPORTED=object()


def _json_value(value):
    if isinstance(value,Path):return {'$path':str(value)}
    if value is None or isinstance(value,(bool,int,float,str)):return value
    if isinstance(value,(tuple,list,set,frozenset)):
        values=[_json_value(v) for v in value]
        if any(v is _UNSUPPORTED for v in values):return _UNSUPPORTED
        if isinstance(value,(set,frozenset)):values.sort(key=lambda v:json.dumps(v,sort_keys=True))
        return {'$'+type(value).__name__:values}
    if isinstance(value,dict):
        pairs=[]
        for key,item in value.items():
            encoded_key,encoded_item=_json_value(key),_json_value(item)
            if encoded_key is _UNSUPPORTED or encoded_item is _UNSUPPORTED:return _UNSUPPORTED
            pairs.append({'keyType':type(key).__module__+'.'+type(key).__qualname__,'key':encoded_key,'value':encoded_item})
        pairs.sort(key=lambda pair:json.dumps([pair['keyType'],pair['key']],sort_keys=True))
        return {'$dict':pairs}
    return _UNSUPPORTED


def runtime_inputs():
    # Eager imports stabilize the relevant runtime namespace before a proof.
    import font_baseline_checks as checks
    modules=[checks]+[importlib.import_module(name) for name in _MODULES]
    project=Path(__file__).resolve().parents[1]/'tools/font'
    seen={module.__name__ for module in modules}
    for module in modules:
        for value in vars(module).values():
            child=value if isinstance(value,types.ModuleType) else sys.modules.get(getattr(value,'__module__',None)) if isinstance(value,(types.FunctionType,type)) else None
            if child is None or child.__name__ in seen or not getattr(child,'__file__',None):continue
            try:Path(child.__file__).absolute().relative_to(project)
            except ValueError:continue
            seen.add(child.__name__);modules.append(child)
    values={};files=[]
    for module in modules:
        files.append(Path(module.__file__))
        if module.__name__=='native_sfnt_loader':files.extend(module.LIBRARY_DEPENDENCIES)
        # Loaded recipe dictionaries can avoid reopening their config file.
        for name,value in vars(module).items():
            if name.isupper() and not name.startswith('_') and isinstance(value,Path) and (value.is_file() or name.endswith(('_PATH','_FILE'))):files.append(value)
        constants={}
        for name,value in vars(module).items():
            if name.isupper() and not name.startswith('_'):
                converted=_json_value(value)
                if converted is not _UNSUPPORTED:constants[name]=converted
        constants['$callables']={name:[type(value).__name__,id(value)] for name,value in vars(module).items() if not name.startswith('__') and callable(value)}
        values[module.__name__]=constants
    return values,files


def record_evidence(path):
    state=_READS.get()
    if state is None or isinstance(path,int):return
    try:path=Path(os.fsdecode(path)).absolute()
    except TypeError:return
    if path not in state:
        import font_baseline_checks as checks
        state[path]=checks.evidence_identity(path)


@contextmanager
def read_dependencies():
    existing=_READS.get()
    if existing is not None:
        yield existing
        return
    # Unrelated threads retain normal open behavior: their ContextVar is empty.
    # RLock serializes nested/parallel proof recorder installation, not all I/O.
    with _LOCK:
        dependencies={};token=_READS.set(dependencies)
        original_builtin,original_io=builtins.open,io.open
        def recorder(original):
            @wraps(original)
            def opened(file,mode='r',*args,**kwargs):
                if _READS.get() is not None:
                    if any(flag in mode for flag in ('w','a','x','+')):
                        raise AssertionError('Native proof must remain read-only')
                    record_evidence(file)
                return original(file,mode,*args,**kwargs)
            return opened
        try:
            builtins.open=recorder(original_builtin);io.open=recorder(original_io)
            yield dependencies
        finally:
            builtins.open=original_builtin;io.open=original_io;_READS.reset(token)


def _explicit_dependencies(before,after,modules):
    import font_baseline_checks as checks
    root=checks.ROOT
    for path in [Path(__file__),*modules]:
        record_evidence(path)
        assert checks.evidence_identity(path) is not None,('Missing native proof code/config input',str(path))
    for entry in (before,after):
        for key in ('file','source'):
            if entry.get(key):record_evidence(root/entry[key])
        for source in entry.get('sources',[]):
            if source.get('archive'):record_evidence(root/source['archive'])
        if 'styleReview' in entry:record_evidence(root/'docs/unicode-style-dispositions.json')
        if entry.get('denseTreatment') or entry.get('supplementalTreatment'):
            frozen=root/'output/font-review/supplemental-production-baselines'/Path(entry['file']).name
            record_evidence(frozen);record_evidence(frozen.with_suffix('.json'))
        for key in ('denseTreatment','supplementalTreatment'):
            if entry.get(key,{}).get('report'):record_evidence(root/entry[key]['report'])


def reuse_reviewed_proof(function):
    @wraps(function)
    def wrapped(before,after):
        import font_baseline_checks as checks
        settings,modules=runtime_inputs()
        arguments=json.dumps([function.__module__,function.__qualname__,id(function),str(checks.ROOT.absolute()),before,after,settings],sort_keys=True)
        saved=_PROOFS.get(arguments)
        if saved is not None:
            dependencies=saved
            if all(checks.evidence_identity(path)==identity for path,identity in dependencies.items()):
                for path in dependencies:
                    record_evidence(path);checks.watch_evidence(path,required=False)
                for path,identity in dependencies.items():
                    assert checks.evidence_identity(path)==identity,('Native proof dependency changed during reuse',str(path))
                _PROOFS.move_to_end(arguments)
                return True
            del _PROOFS[arguments]
        with read_dependencies() as dependencies:
            _explicit_dependencies(before,after,modules)
            result=function(before,after)
            final_settings,_=runtime_inputs()
            assert final_settings==settings,'Native proof runtime constants changed during validation'
            assert json.dumps([function.__module__,function.__qualname__,id(function),str(checks.ROOT.absolute()),before,after,settings],sort_keys=True)==arguments,'Native proof arguments changed during validation'
            for path,identity in dependencies.items():
                assert checks.evidence_identity(path)==identity,('Native proof dependency changed',str(path))
                checks.watch_evidence(path,required=False)
            if result is True:
                _PROOFS[arguments]=dict(dependencies)
                _PROOFS.move_to_end(arguments)
                while len(_PROOFS)>1024:_PROOFS.popitem(last=False)
            return result
    return wrapped
