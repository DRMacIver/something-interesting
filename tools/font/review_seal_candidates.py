"""Locate unassigned CCZ crops for manual review, never assign glyph identities.

Run after fetching/building sources. Output is a shortlist, not font input.
Reading order is page, right half then left, columns right-to-left, top-to-bottom.
Column phase is estimated from assigned crops so differing crop widths do not
mistake adjacent entries in one column for separate columns.
"""
import bisect
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
PROVENANCE = ROOT / 'build/unicode-sources/kaiyuan/data/provenance/glyphs.csv'
REFERENCES = ROOT / 'data/unicode/18.0.0/SealSources.txt'


def shortlist(rows, missing, include_empty=False):
    known = {int(r['sequence'][2:]): r for r in rows if r['sequence']}
    sequences = sorted(known)
    groups = defaultdict(list)
    for row in known.values():
        groups[row['commons_title'], row['page'], row['side']].append(row)

    def order(row):
        pitch = float(row['pitch'])
        assigned = groups[row['commons_title'], row['page'], row['side']]
        if not assigned or pitch <= 0:
            return None
        angles = [2 * math.pi * (int(r['x']) + int(r['w']) / 2) / pitch
                  for r in assigned]
        phase = math.atan2(sum(map(math.sin, angles)), sum(map(math.cos, angles))) * pitch / (2 * math.pi)
        column = round((int(row['x']) + int(row['w']) / 2 - phase) / pitch)
        return int(row['page']), 0 if row['side'] == 'right' else 1, -column, int(row['y'])

    result = []
    for cp, sequence in missing:
        number = int(sequence[2:])
        at = bisect.bisect_left(sequences, number)
        if number in known or at == 0 or at == len(sequences):
            continue
        before, after = known[sequences[at - 1]], known[sequences[at]]
        if before['commons_title'] != after['commons_title']:
            continue
        candidates = []
        for row in rows:
            if (row['commons_title'] != before['commons_title'] or row['codepoint']
                    or row['sequence'] or row['status'] != 'rejected'
                    or int(row['w']) <= 20 or int(row['h']) <= 35):
                continue
            position = order(row)
            if position is not None and order(before) < position < order(after):
                candidates.append(row)
        if candidates or include_empty:
            result.append(dict(codepoint=cp, sequence=sequence, before=before,
                               after=after, candidates=candidates))
    return result


def main():
    from review_seal_editions import font_paths
    mapped = set()
    for path in font_paths():
        with TTFont(path) as font:
            mapped.update(font.getBestCmap())
    missing = []
    for line in REFERENCES.read_text().splitlines():
        if '\tkSEAL_CCZSrc\t' in line:
            cp, _, sequence = line.split('\t')
            if int(cp[2:], 16) not in mapped:
                missing.append((cp[2:], sequence))
    with PROVENANCE.open() as source:
        rows = list(csv.DictReader(source))
    windows = shortlist(rows, missing, include_empty=True)
    report = dict(status='Unverified proximity candidates; manual reference and crop review required',
                  sourceHashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [PROVENANCE, REFERENCES]},
                  missingCCZ=len(missing), candidates=[r for r in windows if r['candidates']],
                  searchWindowsWithoutCandidates=[r for r in windows if not r['candidates']])
    review_path = ROOT / 'docs/seal-gap-review.json'
    if review_path.exists():
        reviews = {r['codepoint']: r['reviewOutcome']
                   for r in json.loads(review_path.read_text())['reviewedCandidates']}
        for candidate in windows:
            if candidate['codepoint'] in reviews:
                candidate['priorReview'] = reviews[candidate['codepoint']]
    output = ROOT / 'docs/seal-crop-candidates.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(f"{len(report['candidates'])} of {len(missing)} CCZ gaps have proximity candidates; none automatically accepted")


if __name__ == '__main__':
    main()
