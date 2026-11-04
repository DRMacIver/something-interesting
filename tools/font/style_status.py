"""Reconcile all baseline source decisions with shipped treatment metadata.

Presence of a recipe is implementation evidence only. Visual acceptance and
native language correctness require the separately linked review records.
Run only after a terminal font build, while production assets are stable.
"""
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]


def build():
    baseline=json.loads((ROOT/'docs/source-style-review.json').read_text())
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ')[1].rstrip(';\n'))
    decisions={r['source']:r for r in json.loads((ROOT/'docs/unicode-style-dispositions.json').read_text())['sources']}
    groups={}
    for entry in manifest['fonts']:
        actual=hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest()
        if actual!=entry['sha256']:raise ValueError(f"Unfinished or stale build: {entry['file']}")
        groups.setdefault(entry['source'],[]).append(entry)
    sources=[]
    for row in baseline['sources']:
        fonts=groups[row['source']]
        decision=decisions[row['source']]
        assert decision['number']==row['number'] and decision['sourceSha256']==row['sourceSha256']
        applied=[dict(file=e['file'],sha256=e['sha256'],**{k:e[k] for k in ('opticalSize','supplementalTreatment','denseTreatment') if k in e}) for e in fonts]
        if any(e.get('denseTreatment') for e in fonts):state='dense-native-pen-shipped; inspect current production review'
        elif any(e.get('supplementalTreatment') for e in fonts):state='pen-recipe-shipped; inspect current production review'
        elif any(e.get('opticalSize') for e in fonts):state='optical-em-shipped; native curves retained'
        elif row['number'] in {6,25}:state='runtime-optical-ink; see hieroglyph-optical-review'
        elif decision['disposition']=='retain-native-calligraphic-style-provisionally':state='native-calligraphic-style-retained; sampled review recorded'
        elif row['decision']=='retain-current':state='baseline-provisional-retain'
        elif row['number'] in {102,150,161,177,188}:state='baseline-context-or-structural-disposition'
        else:state='unresolved-source-style-decision'
        sources.append(dict(number=row['number'],source=row['source'],sourceSha256=row['sourceSha256'],baselineDecision=row['decision'],sourceDisposition=decision['disposition'],implementationState=state,fonts=applied))
    report=dict(status='Implementation reconciliation; not a beta completion declaration or blanket visual approval',sources=len(sources),shards=len(manifest['fonts']),counts=dict(Counter(r['implementationState'] for r in sources)),baselineSha256=hashlib.sha256((ROOT/'docs/source-style-review.json').read_bytes()).hexdigest(),manifestSha256=hashlib.sha256((ROOT/'js/font-manifest.js').read_bytes()).hexdigest(),rows=sources,limitations=['Native positive outlines are not style or semantic proof.','Explicit retained glyphs inside adapted sources still require the source-specific fine-detail guard rationale.','Review records preserve baseline and candidate hashes separately; source counts do not replace visual acceptance.'])
    output=ROOT/'docs/unicode-style-status.json';output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['counts'],indent=2))
    return report

if __name__=='__main__':build()
