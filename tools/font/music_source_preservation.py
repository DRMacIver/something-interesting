"""Isolated exact native Music fine-feature preservation; pressure kernel unchanged."""
import copy
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
SOURCE='NotoMusic-Regular.ttf'
CODEPOINTS=[]
NAMED_GLYPHS=['u1D25B_low']
REASON='Retain exact constructed native low four-stroke tremolo and component closure after an extra vector contour and whole-field384/1024px counter-overlap rejection'


def policy_hash():return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def construction(source):
    source=Path(source);source=source if source.is_absolute() else ROOT/source
    return dict(module='tools/font/music_tremolos.py',sha256=hashlib.sha256((ROOT/'tools/font/music_tremolos.py').read_bytes()).hexdigest(),rulesModule='tools/font/music_mark_rules.py',rulesSha256=hashlib.sha256((ROOT/'tools/font/music_mark_rules.py').read_bytes()).hexdigest(),sourceCodepoint=0x1d169,sourceFile=source.relative_to(ROOT).as_posix(),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest())


def apply(font,source,adapt):
    if Path(source).name!=SOURCE:return adapt(font,source)
    points=CODEPOINTS
    original_order=font.getGlyphOrder()[:]
    if any(name not in original_order for name in NAMED_GLYPHS):
        raise ValueError('Music preservation requires pristine native glyph names')
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
    policy=dict(module='tools/font/music_source_preservation.py',sha256=policy_hash(),codepoints=points,namedGlyphs=NAMED_GLYPHS,glyphs=[dict(gid=font.getGlyphID(n),glyph=n) for n in sorted(names,key=font.getGlyphID)],reason=REASON,sourceConstruction=construction(source))
    report=json.loads((ROOT/result['report']).read_text())
    for rec in report['records']:
        if rec['glyph'] in names and originals[rec['glyph']].numberOfContours:
            rec.update(status='native-retained-guard',reason=policy['reason'],sourcePolicy=True)
    report['counts']=dict(Counter(r['status'] for r in report['records']))
    report['sourcePolicy']=policy
    old=Path(result['report']);target=old.with_name(old.stem+'-music-preserve-'+policy_hash()+'.json')
    (ROOT/target).write_text(json.dumps(report,indent=2)+'\n')
    return {k:v for k,v in report.items() if k!='records'}|{'report':target.as_posix()}
