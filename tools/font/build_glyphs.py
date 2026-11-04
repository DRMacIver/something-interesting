"""Compile verified OFL Glyphs sources without executing upstream build scripts."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from importlib.metadata import version
from fontTools.ttLib import TTFont
from glyphsLib import GSFont

ROOT = Path(__file__).resolve().parents[2]


def build(source):
    path = ROOT / source['build_input']
    out = path.with_suffix('.ttf')
    cache = path.with_suffix('.built.json')
    key = hashlib.sha256(json.dumps(source,sort_keys=True).encode() + Path(__file__).read_bytes()
                         + version('fontmake').encode() + version('fonttools').encode()).hexdigest()
    if out.exists() and cache.exists():
        saved = json.loads(cache.read_text())
        if saved['input'] == key and saved['output'] == hashlib.sha256(out.read_bytes()).hexdigest():
            return out
    glyphs = GSFont(path)
    # These pinned sources use only declarative OpenType features, not plug-ins.
    for owner in [glyphs, *glyphs.masters, *glyphs.instances]:
        if any('filter' in p.name.lower() for p in owner.customParameters):
            raise ValueError('Source filters need explicit review before compilation')
    work = path.parent / 'compiler'
    work.mkdir(exist_ok=True)
    log = work / 'build.log'
    args = [sys.executable, '-m', 'fontmake', '-g', str(path), '-o', 'ttf',
            '--output-path', str(out), '--family-name', source['family'],
            '--master-dir', str(work/'masters'), '--instance-dir', str(work/'instances')]
    with log.open('w') as stream:
        subprocess.run(args, cwd=work, env={**os.environ,'SOURCE_DATE_EPOCH':'1767225600'},
                       stdout=stream, stderr=subprocess.STDOUT, check=True)
    font = TTFont(out, recalcTimestamp=False)
    font['head'].created = font['head'].modified = 3876336000
    font.save(out)
    cache.write_text(json.dumps({'input':key,'output':hashlib.sha256(out.read_bytes()).hexdigest()})+'\n')
    return out
