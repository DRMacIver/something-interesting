"""Render final integrated supplemental candidates beside frozen native/Dad."""
import argparse
import hashlib
import json
from pathlib import Path
from supplemental_adapter import ROOT
from render_specimen import render
from check_supplemental_fields import check


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'output/font-review/supplemental-production')
    p.add_argument('--manifest',type=Path,default=ROOT/'js/font-manifest.js')
    p.add_argument('--source',action='append',help='Limit to these source basenames; repeat as needed')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    triage=json.loads((ROOT/'docs/source-style-review.json').read_text())['sources']
    review_files=[ROOT/'docs/supplemental-next-group-review.json',*sorted((ROOT/'docs').glob('supplemental-systematic-??-review.json')),ROOT/'docs/guarded-normalized-review.json',ROOT/'docs/joining-pressure-review.json']
    fields={}
    for path in review_files:
        data=json.loads(path.read_text())
        for row in data.get('sources',data.get('acceptedSources',[])):
            text=row.get('nativeField') or row.get('text') or row.get('sample')
            if text:fields[row['number']]=text
    manifest=json.loads(a.manifest.read_text().split('export default ')[1].rstrip(';\n'))
    samples=[];checks=[];seen=set()
    for e in manifest['fonts']:
        if a.source and Path(e['source']).name not in a.source:continue
        if e.get('supplementalTreatment',{}).get('method') not in {'native-centred-distance-pressure-v1','native-centred-cubic-pressure-v1'}:continue
        row=next(r for r in triage if r['source']==e['source'])
        if row['number'] in seen:continue
        seen.add(row['number']);field=fields.get(row['number'],row['sample'])
        native=ROOT/'output/font-review/supplemental-production-baselines'/Path(e['file']).name
        texts=[field]+([row['sample']] if field!=row['sample'] else [])
        for text in texts:
            for label,font in [('native',native),('pressure',ROOT/e['file'])]:samples.append(dict(label=f"{row['number']} {Path(e['source']).stem} {label}",font=str(font),text=text))
            result=check(native,ROOT/e['file'],text);result.update(sourceNumber=row['number'],text=text,font=e['file'],fontSha256=hashlib.sha256((ROOT/e['file']).read_bytes()).hexdigest(),nativeSha256=hashlib.sha256(native.read_bytes()).hexdigest());checks.append(result);print(row['number'],result['status'],flush=True)
    # Three before/after source pairs per page, each at22/44 beside Dad.
    for i in range(0,len(samples),6):
        output=a.output/f'page-{i//6+1}';render(samples[i:i+6],output)
    (a.output/'whole-field-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
    print(f'{len(seen)} sources, {len(checks)} fields, {(len(samples)+5)//6} pages')
    rejected=[r for r in checks if r['status']!='pass']
    if rejected:
        raise SystemExit(f"Production whole-field review rejected {len(rejected)} fields; inspect whole-field-checks.json")

if __name__=='__main__':main()
