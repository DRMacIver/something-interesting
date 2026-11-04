"""Isolated exact native Chemical fine-feature preservation; pressure kernel unchanged."""
import copy
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
SOURCE='UnicodiaFunky.ttf'
CODEPOINTS=[0x1cee0,0x1cee1,0x1cee2,0x1cee3,0x1cee4,0x1cee5,0x1cee8,0x1cee9,0x1ceea,0x1ceeb,0x1ceec,0x1ceed,0x1ceee,0x1ceef,0x1f8d1]
NAMED_GLYPHS=[]
REASON='Retain already hand-inked equal-length harpoon and fourteen geomantic dot-grid figures with native component closure after pressure violated existing six-unit length and strict four-unit center bounds'


def policy_hash():return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def construction(source):
    source=Path(source);source=source if source.is_absolute() else ROOT/source
    manifest='data/font-sources/unicodia.json'
    entry=next(row for row in json.loads((ROOT/manifest).read_text())['files'] if Path(row['path']).name==SOURCE)
    scope=entry['ink_ranges']
    digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==entry['sha256']
    assert all(any(a<=cp<=b for a,b in scope) for cp in CODEPOINTS)
    return dict(module='tools/font/alphabet_ink.py',sha256=hashlib.sha256((ROOT/'tools/font/alphabet_ink.py').read_bytes()).hexdigest(),scope=scope,scopeManifest=manifest,chemicalModule='tools/font/chemical_symbols.py',chemicalSha256=hashlib.sha256((ROOT/'tools/font/chemical_symbols.py').read_bytes()).hexdigest(),sourceFile=source.relative_to(ROOT).as_posix(),sourceSha256=digest)


def apply(font,source,adapt):
    if Path(source).name!=SOURCE:return adapt(font,source)
    points=CODEPOINTS
    original_order=font.getGlyphOrder()[:]
    if any(name not in original_order for name in NAMED_GLYPHS):
        raise ValueError('Chemical preservation requires pristine native glyph names')
    names=set()
    def visit(name):
        if name in names:return
        names.add(name)
        for child in font['glyf'][name].getComponentNames(font['glyf']):visit(child)
    for cp in points:visit(font.getBestCmap()[cp])
    for name in NAMED_GLYPHS:visit(name)
    originals={n:copy.deepcopy(font['glyf'][n]) for n in names}
    result=adapt(font,source)
    if result is None:raise ValueError('Source preservation needs a pressure recipe')
    if font.getGlyphOrder()!=original_order:raise ValueError('Pressure callback changed native glyph order/names')
    for name,glyph in originals.items():font['glyf'][name]=glyph
    policy=dict(module='tools/font/chemical_source_preservation.py',sha256=policy_hash(),codepoints=points,namedGlyphs=NAMED_GLYPHS,glyphs=[dict(gid=font.getGlyphID(n),glyph=n) for n in sorted(names,key=font.getGlyphID)],reason=REASON,sourceConstruction=construction(source))
    report=json.loads((ROOT/result['report']).read_text())
    for rec in report['records']:
        if rec['glyph'] in names and originals[rec['glyph']].numberOfContours:
            rec.update(status='native-retained-guard',reason=policy['reason'],sourcePolicy=True)
    report['counts']=dict(Counter(r['status'] for r in report['records']))
    report['sourcePolicy']=policy
    old=Path(result['report']);target=old.with_name(old.stem+'-chemical-preserve-'+policy_hash()+'.json')
    (ROOT/target).write_text(json.dumps(report,indent=2)+'\n')
    return {k:v for k,v in report.items() if k!='records'}|{'report':target.as_posix()}
