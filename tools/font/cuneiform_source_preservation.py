"""Isolated exact native Cuneiform fine-feature preservation; pressure kernel unchanged."""
import copy
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
SOURCE='NotoSansCuneiform-Regular.ttf'
CODEPOINTS=[0x12493]
NAMED_GLYPHS=[]
REASON='Retain native Cuneiform U+12493 and complete component closure after whole-field384px ink fracture'


def policy_hash():return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def apply(font,source,adapt):
    if Path(source).name!=SOURCE:return adapt(font,source)
    points=CODEPOINTS
    original_order=font.getGlyphOrder()[:]
    if any(name not in original_order for name in NAMED_GLYPHS):
        raise ValueError('Cuneiform preservation requires pristine native glyph names')
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
    policy=dict(module='tools/font/cuneiform_source_preservation.py',sha256=policy_hash(),codepoints=points,namedGlyphs=NAMED_GLYPHS,glyphs=[dict(gid=font.getGlyphID(n),glyph=n) for n in sorted(names,key=font.getGlyphID)],reason=REASON)
    report=json.loads((ROOT/result['report']).read_text())
    for rec in report['records']:
        if rec['glyph'] in names and originals[rec['glyph']].numberOfContours:
            rec.update(status='native-retained-guard',reason=policy['reason'],sourcePolicy=True)
    report['counts']=dict(Counter(r['status'] for r in report['records']))
    report['sourcePolicy']=policy
    old=Path(result['report']);target=old.with_name(old.stem+'-cuneiform-preserve-'+policy_hash()+'.json')
    (ROOT/target).write_text(json.dumps(report,indent=2)+'\n')
    return {k:v for k,v in report.items() if k!='records'}|{'report':target.as_posix()}
