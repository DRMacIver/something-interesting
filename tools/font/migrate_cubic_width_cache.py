"""Authenticate and migrate only Type2 width operands; never overwrite old caches."""
import argparse
import copy
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import sys

from fontTools.ttLib import TTFont
from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.recordingPen import RecordingPen
import supplemental_cubic_adapter as adapter
import cubic_source_preservation as preservation

ROOT=adapter.ROOT
EVIDENCE=ROOT/'output/font-review/cubic-width-diagnosis'
NATIVE_HASH='57506979a184c69119b61f1c42c22f48acbd221ef535bbbf0cdef673821cd9d3'


def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_text())
def drawing(cs):
    pen=RecordingPen();cs.draw(pen);return pen.value

def compiled(cs):
    cs=copy.deepcopy(cs);cs.compile();return cs.bytecode


def migrate(write=False):
    plan=read(EVIDENCE/'kernel-width-fix-plan.json')
    old_module=(EVIDENCE/'supplemental_cubic_adapter-before-width-fix.py').read_bytes()
    assert sha(old_module)==plan['baseSha256']
    assert sha(Path(adapter.__file__).read_bytes())==plan['candidateSha256']
    settings=adapter.SOURCES['UFSZeroExt.otf']
    old_recipe=sha(old_module+b''.join((ROOT/'tools/font'/n).read_bytes() for n in ('supplemental_pressure.py','prototype_unifont_lettering.py'))+json.dumps([adapter.METHOD,adapter.RESOLUTION,settings],sort_keys=True).encode())
    new_recipe=adapter.recipe_hash('UFSZeroExt.otf');assert new_recipe!=old_recipe
    manifest=read_manifest(ROOT/'js/font-manifest.js');entry=next(e for e in manifest['fonts'] if Path(e['source']).name=='UFSZeroExt.otf')
    assert sha((ROOT/entry['source']).read_bytes())==entry['sourceSha256']
    pinned=next(row for row in read(ROOT/'data/font-sources/ufs.json')['files'] if row['path']==entry['source'])
    assert pinned['sha256']==entry['sourceSha256']
    actual_path=ROOT/entry['file'];assert sha(actual_path.read_bytes())==entry['sha256']
    t=entry['supplementalTreatment'];assert t['recipeSha256']==old_recipe and t['nativeInputSha256']==NATIVE_HASH
    assert ':supplemental-cubic-pressure:'+old_recipe in entry['recipe']
    report=read(ROOT/t['report']);assert {k:v for k,v in report.items() if k!='records'}=={k:v for k,v in t.items() if k!='report'}
    base_path=ROOT/'output/font-review/supplemental-cubic-production'/f'{NATIVE_HASH}-{old_recipe}.json';base=read(base_path)
    assert base['recipeSha256']==old_recipe and base['nativeInputSha256']==NATIVE_HASH
    assert base['glyphs']==report['glyphs']==1301
    assert dict(Counter(r['status'] for r in base['records']))==base['counts']
    assert [r['gid'] for r in base['records']]==list(range(1301))
    native_path=ROOT/'output/font-review/supplemental-production-baselines'/actual_path.name
    native_meta=read(native_path.with_suffix('.json'));assert sha(native_path.read_bytes())==native_meta['sha256']
    assert native_meta['sourceSha256']==entry['sourceSha256'] and native_meta['source']==entry['source']
    native=TTFont(native_path,recalcTimestamp=False);actual=TTFont(actual_path,recalcTimestamp=False)
    # The diagnosed source-native reconstruction differs only in WOFF2 headbit11.
    native['head'].flags &= ~0x800;native.flavor=None;stream=io.BytesIO();native.save(stream);assert sha(stream.getvalue())==NATIVE_HASH
    assert native.getGlyphOrder()==actual.getGlyphOrder()
    assert native.getBestCmap()==actual.getBestCmap()
    for tag in ('hmtx','vmtx','GPOS','GSUB','GDEF','cmap'):
        assert (tag in native)==(tag in actual)
        if tag in native:assert native.getTableData(tag)==actual.getTableData(tag)
    assert native['head'].unitsPerEm==actual['head'].unitsPerEm==base['nativeEmUnchanged']
    assert t['sourcePolicy']['sha256']==preservation.policy_hash()
    assert t['sourcePolicy']['module']=='tools/font/cubic_source_preservation.py'
    assert t['sourcePolicy']['codepoints']==preservation.POLICIES['UFSZeroExt.otf']
    protected={native.getGlyphID(native.getBestCmap()[cp]) for cp in t['sourcePolicy']['codepoints']}
    assert protected=={r['gid'] for r in t['sourcePolicy']['glyphs']}
    old_cs=native['CFF '].cff.topDictIndex[0].CharStrings;current_cs=actual['CFF '].cff.topDictIndex[0].CharStrings
    pending=[];rows=[]
    for gid,name in enumerate(native.getGlyphOrder()):
        original=old_cs[name];record=base['records'][gid];assert record['glyph']==name
        shown=report['records'][gid]
        if gid in protected:
            assert shown['sourcePolicy'] is True and shown['status']=='native-retained-guard'
            assert compiled(current_cs[name])==compiled(original)
            policy=next(r for r in t['sourcePolicy']['glyphs'] if r['gid']==gid)
            assert policy['charstringSha256']==sha(compiled(original))
        else:assert shown==record
        advance=native['hmtx'][name][0]
        def key(recipe):return sha(json.dumps([recipe,NATIVE_HASH,name,native['hmtx'][name]],sort_keys=True).encode())
        old_key,new_key=key(old_recipe),key(new_recipe);old_path=adapter.CACHE/(old_key+'.json');stored=read(old_path);assert stored['record']==record
        migrated=copy.deepcopy(stored)
        widths=None
        if record['status']=='adapted':
            before=T2CharString(program=list(stored['program']),private=original.private,globalSubrs=original.globalSubrs)
            if gid not in protected:assert compiled(before)==compiled(current_cs[name])
            commands=drawing(before);assert stored['program'][0]==advance
            nominal=original.private.nominalWidthX;default=original.private.defaultWidthX
            assert before.width==advance+nominal
            program=list(stored['program']);encoded=None if advance==default else advance-nominal
            if encoded is None:program.pop(0)
            else:program[0]=encoded
            after=T2CharString(program=program,private=original.private,globalSubrs=original.globalSubrs)
            assert drawing(after)==commands and after.width==advance
            # Force exact serializable Type2 decode and compare geometry again.
            after.compile();decoded=T2CharString(bytecode=after.bytecode,private=original.private,globalSubrs=original.globalSubrs)
            assert drawing(decoded)==commands and decoded.width==advance
            migrated['program']=program;widths={'oldDecoded':before.width,'newDecoded':decoded.width,'hmtx':advance}
        else:
            assert stored['program'] is None
            if gid not in protected:assert compiled(original)==compiled(current_cs[name])
        assert migrated['record']==stored['record'],'Raster/topology/frame guard provenance changed'
        data=json.dumps(migrated,sort_keys=True).encode();target=adapter.CACHE/(new_key+'.json')
        if target.exists():assert target.read_bytes()==data
        pending.append((target,data));rows.append(dict(gid=gid,glyph=name,status=record['status'],oldKey=old_key,newKey=new_key,oldCacheSha256=sha(old_path.read_bytes()),newCacheSha256=sha(data),widths=widths,drawableGeometryExact=True,guardRecordUnchanged=True))
    assert len(pending)==1301
    # Every identity/program/cache proof finishes before the first write.
    if write:
        for path,data in pending:
            if not path.exists():path.write_bytes(data)
    proof=dict(status='all1301 authenticated; new cache written' if write else 'dry run all1301 authenticated; no cache writes',oldRecipeSha256=old_recipe,newRecipeSha256=new_recipe,nativeInputSha256=NATIVE_HASH,sourceSha256=entry['sourceSha256'],actualOldFontSha256=entry['sha256'],oldBaseReportSha256=sha(base_path.read_bytes()),oldPolicyReportSha256=sha((ROOT/t['report']).read_bytes()),glyphs=len(rows),adaptedProgramWidthsCorrected=sum(r['widths'] is not None for r in rows),counterTopologyGuardRecordsUnchanged=True,oldCachesOverwritten=False,rows=rows)
    output=EVIDENCE/('cache-migration.json' if write else 'cache-migration-dry-run.json');output.write_text(json.dumps(proof,indent=2)+'\n');print(proof['status'],proof['adaptedProgramWidthsCorrected'],'adapted programs',flush=True)
    return proof


def read_manifest(path):return json.loads(path.read_text().split('export default ')[1].rstrip(';\n'))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args();migrate(args.apply)
