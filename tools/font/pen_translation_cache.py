"""Disposable, content-addressed cache for deterministic pen translation."""
from dataclasses import asdict
from functools import wraps
import hashlib
from importlib.metadata import version
import inspect
import io
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile
import zlib

import numpy as np
from PIL import Image


# This is one reviewed, mathematically equivalent hole-counting optimization.
# Future pen source hashes receive no legacy migration permission.
LEGACY_EQUIVALENT = {
    'b11d76528cfac8b913e1f914d06c3501a0a870034260d6a5b0b0eff937310d72': ('5ab1805998fc1178e6cb0f79f54a0ffb415a3962d1ec38011938df97e8e1c081', 'e320addae5a5613260d8a0859c6f2dce8ed08a99194dafab943c64d0db912c7d'),
}


def _read_validated(path, settings):
    raw=path.read_bytes()
    with np.load(io.BytesIO(raw),allow_pickle=False) as stored:
        pixels=stored['pixels'];report_text=str(stored['report'].item())
        digest=hashlib.sha256(pixels.tobytes()+report_text.encode()).hexdigest()
        if pixels.dtype!=np.uint8 or pixels.ndim!=2 or digest!=str(stored['digest'].item()):
            raise ValueError('Corrupt pen cache')
        report=json.loads(report_text)
        if not isinstance(report,dict) or report.get('settings')!=asdict(settings):
            raise ValueError('Mismatched pen cache report')
    return pixels,report,raw


_MIGRATION_RECEIPTS = {}


def migration_receipts():
    """Return isolated evidence for an explicit build-driver publication step."""
    return copy.deepcopy(_MIGRATION_RECEIPTS)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def cached_translation(compute,source_path,cache_dir=None):
    """Cache pixels and the original report; never add cache state to provenance."""
    root=Path(__file__).resolve().parents[2]
    directory=Path(cache_dir) if cache_dir is not None else root/'build/font-cache/pen'
    environment=dict(
        source=hashlib.sha256(Path(source_path).read_bytes()).hexdigest(),
        cache=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        python=sys.version,platform=sys.platform,
        libraries={name:version(name) for name in ('numpy','scipy','scikit-image','Pillow')},
    )
    namespace=canonical(environment).encode()
    legacy=LEGACY_EQUIVALENT.get(environment['source'])
    legacy_namespace=None
    if legacy is not None:
        legacy_environment=dict(environment,source=legacy[0],cache=legacy[1])
        legacy_namespace=canonical(legacy_environment).encode()
    default=inspect.signature(compute).parameters['settings'].default

    @wraps(compute)
    def wrapped(mask,settings=default):
        if os.environ.get('DAD_DISABLE_PEN_CACHE')=='1':return compute(mask,settings)
        source=np.asarray(mask,dtype=bool)
        if source.ndim!=2 or not source.any():return compute(mask,settings)
        try:
            parameters=canonical(dict(shape=source.shape,settings=asdict(settings))).encode()
        except (TypeError,ValueError):
            return compute(mask,settings)
        key=hashlib.sha256(namespace+b'\0'+parameters+b'\0'+np.packbits(source).tobytes()).hexdigest()
        path=directory/key[:2]/(key+'.npz')
        try:
            pixels,report,_=_read_validated(path,settings)
            return Image.fromarray(pixels),report
        except (OSError,ValueError,KeyError,EOFError,zipfile.BadZipFile,zlib.error):
            pass
        if legacy_namespace is not None:
            legacy_key=hashlib.sha256(legacy_namespace+b'\0'+parameters+b'\0'+np.packbits(source).tobytes()).hexdigest()
            legacy_path=directory/legacy_key[:2]/(legacy_key+'.npz')
            try:
                pixels,report,raw=_read_validated(legacy_path,settings)
                # Read through only: no file writes or extra cache paths on a hit.
                # Drivers may publish an isolated copy of this receipt later.
                receipt=dict(method='exact-cropped-holes-read-through-v1',
                    oldKey=legacy_key,newKey=key,
                    oldSourceSha256=legacy[0],newSourceSha256=environment['source'],
                    oldCacheModuleSha256=legacy[1],newCacheModuleSha256=environment['cache'],
                    npzSha256=hashlib.sha256(raw).hexdigest(),
                    environment={k:v for k,v in environment.items() if k not in ('source','cache')})
                _MIGRATION_RECEIPTS[key]=receipt
                return Image.fromarray(pixels),report
            except (OSError,ValueError,KeyError,EOFError,zipfile.BadZipFile,zlib.error):
                pass
        image,report=compute(mask,settings)
        # An interrupted write cannot publish a partial entry. Cache failures
        # must never prevent the uncached font build from completing.
        temporary=None
        try:
            pixels=np.asarray(image,dtype=np.uint8)
            report_text=canonical(report)
            digest=hashlib.sha256(pixels.tobytes()+report_text.encode()).hexdigest()
            path.parent.mkdir(parents=True,exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent,suffix='.tmp',delete=False) as output:
                temporary=Path(output.name)
                np.savez_compressed(output,pixels=pixels,report=report_text,digest=digest)
            os.replace(temporary,path)
        except (OSError,TypeError,ValueError):
            pass
        finally:
            if temporary is not None:
                try:temporary.unlink(missing_ok=True)
                except OSError:pass
        return image,report
    return wrapped
