"""Build one isolated width-correct CFF from authenticated frozen native input."""
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
import supplemental_cubic_adapter as adapter
import cubic_source_preservation as policy

ROOT=adapter.ROOT
DIRECTORY=ROOT/'output/font-review/cubic-width-diagnosis/candidate'
STYLE='smooth native cubic variable pressure; native CFF/layout retained; rejected drawings retained with explicit audit; specialist review provisional'


def build():
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ')[1].rstrip(';\n'))
    entry=next(e for e in manifest['fonts'] if Path(e['source']).name=='UFSZeroExt.otf')
    old_recipe=entry['supplementalTreatment']['recipeSha256'];name=Path(entry['file']).name
    native=TTFont(ROOT/'output/font-review/supplemental-production-baselines'/name,recalcTimestamp=False)
    native['head'].flags &= ~0x800;native.flavor=None
    metadata=policy.apply(native,entry['source'],adapter.apply)
    assert metadata['nativeInputSha256']=='57506979a184c69119b61f1c42c22f48acbd221ef535bbbf0cdef673821cd9d3'
    assert metadata['charstringAdvancesMatchHmtx'] is True
    assert metadata['widthOnlyRepairGids']==[1210,1211,1212,1245,1248]
    DIRECTORY.mkdir(parents=True,exist_ok=True);target=DIRECTORY/name;native.flavor='woff2';native.save(target)
    updated=dict(entry,file=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,recipe=entry['recipe'].replace(':supplemental-cubic-pressure:'+old_recipe,':supplemental-cubic-pressure:'+metadata['recipeSha256']),supplementalTreatment=metadata,style=STYLE)
    manifest['fonts']=[updated if e is entry else e for e in manifest['fonts']]
    (DIRECTORY/'manifest.js').write_text('export default '+json.dumps(manifest,separators=(',',':'))+';\n')
    (DIRECTORY/'entry.json').write_text(json.dumps(updated,indent=2)+'\n')
    print('Isolated corrected1301 candidate ready',updated['file'],updated['sha256'],flush=True)

if __name__=='__main__':build()
