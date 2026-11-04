"""Match final regular font bytes to locally inspected production specimens.

This checks visual evidence continuity only. Native/cache lineage, source
preservation, whole-field guards and the full beta audit remain separate gates.
"""
import argparse
import hashlib
import json
from pathlib import Path
from supplemental_adapter import ROOT, SOURCES

REGULAR_METHOD = 'native-centred-distance-pressure-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def reconcile(manifest):
    triage = json.loads((ROOT/'docs/source-style-review.json').read_text())['sources']
    by_number = {r['number']: r for r in triage}
    expected = {r['source'] for r in triage if Path(r['source']).name in SOURCES}
    accepted = {}
    first_path = ROOT/'docs/supplemental-production-first15-review.json'
    first = json.loads(first_path.read_text())
    assert first['wholeFieldFailures'] == 0 and first['sources'] == 15
    for page in first['visualInspection']['pages']:
        assert sha(ROOT/page['file']) == page['sha256'], 'Frozen inspected image changed'
    for row in json.loads((ROOT/first['invariantVerification']).read_text())['rows']:
        assert row['source'] not in accepted
        accepted[row['source']] = (row['sha256'], str(first_path.relative_to(ROOT)))
    review_path = ROOT/'docs/supplemental-private-production-review.json'
    review = json.loads(review_path.read_text())
    for row in review['accepted']:
        source = by_number[row['sourceNumber']]['source']
        assert sha(ROOT/row['image']) == row['imageSha256'], 'Inspected image changed'
        assert sha(ROOT/row['font']) == row['fontSha256'], 'Inspected private candidate changed'
        assert source not in accepted, 'Duplicate source acceptance'
        accepted[source] = (row['fontSha256'], str(review_path.relative_to(ROOT)))
    assert set(accepted) == expected and len(expected) == 145, 'Regular review scope differs'
    rows = []
    for source in sorted(expected):
        entries = [e for e in manifest['fonts'] if e['source'] == source]
        assert len(entries) == 1, 'Regular source must have exactly one packaged shard'
        entry = entries[0]
        actual = sha(ROOT/entry['file'])
        assert actual == entry['sha256'], 'Manifest font SHA differs from actual asset'
        inspected, evidence = accepted[source]
        applied = entry.get('supplementalTreatment', {}).get('method') == REGULAR_METHOD
        matched = applied and actual == inspected
        rows.append(dict(source=source, file=entry['file'], sha256=actual,
                         inspectedSha256=inspected, evidence=evidence,
                         status='visual-input-match' if matched else 'pending-integration-or-rereview'))
    return dict(status='Visual input continuity only; not a beta completion claim',
                sources=len(rows), matched=sum(r['status']=='visual-input-match' for r in rows),
                pending=sum(r['status']!='visual-input-match' for r in rows), rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'js/font-manifest.js')
    parser.add_argument('--output', type=Path, default=ROOT/'output/font-review/production-visual-match.json')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text().split('export default ', 1)[1].rstrip(';\n'))
    result = reconcile(manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(f"{result['matched']}/{result['sources']} regular fonts match inspected bytes; {result['pending']} pending")
    if result['pending']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
