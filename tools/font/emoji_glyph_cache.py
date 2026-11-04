"""Disposable content-addressed prepared-glyph artifacts, never runtime fonts."""
import hashlib
import json
import os
from pathlib import Path
import tempfile


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


class GlyphCache:
    def __init__(self,directory):
        self.directory=Path(directory)
        self.hits=0;self.misses=0;self.keys=[]

    def prepare(self,inputs,compute):
        key=hashlib.sha256(canonical(inputs).encode()).hexdigest()
        self.keys.append(key)
        path=self.directory/key[:2]/(key+'.json')
        try:
            stored=json.loads(path.read_text())
            value=stored['glyph']
            if stored['inputs']!=inputs or stored['sha256']!=hashlib.sha256(canonical(value).encode()).hexdigest():
                raise ValueError('Invalid glyph cache')
            self.hits+=1
            return value
        except (OSError,ValueError,KeyError,TypeError):
            pass
        self.misses+=1
        # Hits and misses return exactly the same JSON-shaped representation.
        value=json.loads(canonical(compute()))
        stored=dict(inputs=inputs,glyph=value,sha256=hashlib.sha256(canonical(value).encode()).hexdigest())
        path.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(dir=path.parent,suffix='.tmp')
        try:
            with os.fdopen(fd,'w') as stream:stream.write(canonical(stored))
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp):os.unlink(tmp)
        return value
