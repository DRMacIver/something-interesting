"""Retain one exact native cubic feature after a complete-field merge.

U+18F6C merges a native component at384px/em despite isolated1024/384 glyph
guards. Keep its exact native Type2 charstring; the generic CFF kernel and cache
remain unchanged. Native subroutines/private tables are not modified by either
stage, so original callsubr references retain their original targets.
"""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
POLICIES={'UFSZeroExt.otf':[0x18f6c]}
REASON='Retain exact native U+18F6C charstring after whole-field384px component merge'


def policy_hash():return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def charstring_bytes(charstring):
    snapshot=copy.deepcopy(charstring);snapshot.compile();return snapshot.bytecode


def apply(font,source,adapt):
    points=POLICIES.get(Path(source).name)
    if not points:return adapt(font,source)
    if 'CFF ' not in font:raise ValueError('Cubic native-preservation policy requires original CFF output')
    cmap=font.getBestCmap();top=font['CFF '].cff.topDictIndex[0]
    names={cmap[cp] for cp in points}
    originals={name:copy.deepcopy(top.CharStrings[name]) for name in names}
    glyphs=[dict(gid=font.getGlyphID(name),glyph=name,charstringSha256=hashlib.sha256(charstring_bytes(originals[name])).hexdigest()) for name in sorted(names,key=font.getGlyphID)]
    result=adapt(font,source)
    if result is None:raise ValueError('Cubic preservation requires a pressure recipe')
    current=font['CFF '].cff.topDictIndex[0]
    for name,charstring in originals.items():current.CharStrings[name]=charstring
    policy=dict(module='tools/font/cubic_source_preservation.py',sha256=policy_hash(),codepoints=points,glyphs=glyphs,reason=REASON)
    report=json.loads((ROOT/result['report']).read_text())
    gids={row['gid'] for row in glyphs}
    assert gids<={row['gid'] for row in report['records']}
    for row in report['records']:
        if row['gid'] in gids:row.update(status='native-retained-guard',reason=REASON,sourcePolicy=True)
    report['counts']=dict(Counter(row['status'] for row in report['records']))
    report['sourcePolicy']=policy
    old=Path(result['report']);target=old.with_name(old.stem+'-cubic-preserve-'+policy_hash()+'.json')
    (ROOT/target).write_text(json.dumps(report,indent=2)+'\n')
    return {key:value for key,value in report.items() if key!='records'}|{'report':target.as_posix()}
