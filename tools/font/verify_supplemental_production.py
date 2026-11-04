"""Verify integrated supplemental shards against frozen production baselines."""
import argparse
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from supplemental_adapter import ROOT,recipe_hash
from supplemental_cubic_adapter import recipe_hash as cubic_recipe_hash, bounds as cubic_bounds, BOUNDS_TOLERANCE


def verify(entry,baselines):
    target=ROOT/entry['file'];source=baselines/target.name
    assert target.exists() and source.exists()
    assert hashlib.sha256(target.read_bytes()).hexdigest()==entry['sha256']
    old=TTFont(source);new=TTFont(target);treatment=entry['supplementalTreatment']
    expected=cubic_recipe_hash(entry['source']) if treatment['method']=='native-centred-cubic-pressure-v1' else recipe_hash(entry['source'])
    assert treatment['recipeSha256']==expected
    report=json.loads((ROOT/treatment['report']).read_text())
    assert report['recipeSha256']==treatment['recipeSha256']
    assert len(old.getGlyphOrder())==len(new.getGlyphOrder())==report['glyphs']
    old_map={cp:old.getGlyphID(name) for cp,name in old.getBestCmap().items()}
    new_map={cp:new.getGlyphID(name) for cp,name in new.getBestCmap().items()}
    assert old_map==new_map,'Cmap glyph identity changed'
    layout=[]
    for tag in ('GDEF','GSUB','GPOS','hmtx','vmtx'):
        assert (tag in old)==(tag in new)
        if tag in old:
            assert old[tag].compile(old)==new[tag].compile(new),f'{tag} native layout changed'
            layout.append(tag)
    assert old['head'].unitsPerEm==new['head'].unitsPerEm==treatment['nativeEmUnchanged']
    assert treatment['nativeBoundsPreserved']
    maximum_error=0
    empty_composites=[]
    old_set=old.getGlyphSet();new_set=new.getGlyphSet()
    for gid,(old_name,new_name) in enumerate(zip(old.getGlyphOrder(),new.getGlyphOrder())):
        if 'glyf' in old:
            a=old['glyf'][old_name];b=new['glyf'][new_name]
            if a.isComposite() and not b.numberOfContours:
                # Native empty component wrappers have no painted frame.
                # Require exact zero drawing on both sides, never ignore ink.
                p,q=DecomposingRecordingPen(old_set),DecomposingRecordingPen(new_set)
                old_set[old_name].draw(p);new_set[new_name].draw(q)
                assert p.value==q.value==[]
                assert report['records'][gid]['status']=='native-blank'
                empty_composites.append(gid)
            elif a.numberOfContours:
                assert (a.xMin,a.yMin,a.xMax,a.yMax)==(b.xMin,b.yMin,b.xMax,b.yMax),f'Native bbox changed at gid{gid}'
            else:assert not b.numberOfContours
        else:
            a=cubic_bounds(old,old_name);b=cubic_bounds(new,new_name)
            assert (a is None)==(b is None)
            if a is not None:
                error=max(abs(x-y) for x,y in zip(a,b));maximum_error=max(maximum_error,error)
                assert error<=BOUNDS_TOLERANCE,f'Native cubic bbox moved at gid{gid}'
    assert sorted(r['gid'] for r in report['records'])==list(range(report['glyphs']))
    for rec in report['records']:
        if rec['status']=='adapted':
            assert rec['changedPixels']>0 and rec['vectorChecks']['changedPixels']>0
            assert 'scale384Checks' in rec
    assert sum(report['counts'].values())==report['glyphs']
    return dict(source=entry['source'],file=entry['file'],sha256=entry['sha256'],glyphs=report['glyphs'],counts=report['counts'],layoutTablesUnchanged=layout,allNativeBoundsAndOriginsUnchanged=True,nativeBoundsMaxError=maximum_error,emptyNativeCompositeWrappers=empty_composites,report=entry['supplementalTreatment']['report'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/font-review/supplemental-production/verification.json');a=p.parse_args()
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ')[1].rstrip(';\n'))
    known={'native-centred-distance-pressure-v1','native-centred-cubic-pressure-v1'}
    rows=[verify(e,ROOT/'output/font-review/supplemental-production-baselines') for e in manifest['fonts'] if e.get('supplementalTreatment',{}).get('method') in known]
    other=[dict(source=e['source'],method=e['supplementalTreatment']['method']) for e in manifest['fonts'] if e.get('supplementalTreatment',{}).get('method') not in known and e.get('supplementalTreatment')]
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(dict(status='all integrated native layout and origin invariants pass',sources=len(rows),glyphs=sum(r['glyphs'] for r in rows),rows=rows,otherMethodsRequiringSeparateVerification=other),indent=2));print(f'{len(rows)} sources / {sum(r["glyphs"] for r in rows)} glyphs verified')

if __name__=='__main__':main()
