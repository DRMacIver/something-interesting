"""Exact native component closure for a reviewed source-specific fine feature.

U+1262D's narrow connector fractured in a whole field at384px despite passing
isolated glyph and1024px checks. Retain its complete original component closure;
other numerals keep the accepted pressure finish. This wrapper does not change
the generic pressure kernel or invalidate unrelated source caches.
"""
import copy
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
POLICIES={'ArchaicCuneiformNumerals.ttf':[0x1262d]}


def policy_hash():return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def apply(font,source,adapt):
    points=POLICIES.get(Path(source).name)
    if not points:return adapt(font,source)
    names=set()
    def visit(name):
        if name in names:return
        names.add(name)
        for child in font['glyf'][name].getComponentNames(font['glyf']):visit(child)
    for cp in points:visit(font.getBestCmap()[cp])
    originals={n:copy.deepcopy(font['glyf'][n]) for n in names}
    result=adapt(font,source)
    if result is None:raise ValueError('Source preservation needs a pressure recipe')
    for name,glyph in originals.items():font['glyf'][name]=glyph
    policy=dict(module='tools/font/source_preservation.py',sha256=policy_hash(),codepoints=points,glyphs=[dict(gid=font.getGlyphID(n),glyph=n) for n in sorted(names,key=font.getGlyphID)],reason='Retain native U+1262D connector and complete component closure after whole-field384px fracture')
    report=json.loads((ROOT/result['report']).read_text())
    for rec in report['records']:
        if rec['glyph'] in names and originals[rec['glyph']].numberOfContours:
            rec.update(status='native-retained-guard',reason=policy['reason'],sourcePolicy=True)
    report['counts']=dict(Counter(r['status'] for r in report['records']))
    report['sourcePolicy']=policy
    old=Path(result['report']);target=old.with_name(old.stem+'-preserve-'+policy_hash()+'.json')
    (ROOT/target).write_text(json.dumps(report,indent=2)+'\n')
    return {k:v for k,v in report.items() if k!='records'}|{'report':target.as_posix()}
