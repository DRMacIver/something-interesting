"""Route missing Seal characters to real historical editions, not index aliases.

TH-Y identifiers enumerate additions from other editions; they do not establish
that a drawing exists in the Tenghuaxie book. This report is a review queue,
never automatic authorization to assign a glyph from a modern Han equivalent.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
REFERENCES = ROOT / 'data/unicode/18.0.0/SealSources.txt'
def font_paths():
    """Count only shipped Seal subsets, including additional licensed donors."""
    manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    return [ROOT/e['file'] for e in manifest['fonts']
            if any(a<=0x3fc3f and b>=0x3d000 for a,b in e['ranges'])]


def editions(properties):
    result = []
    for edition, key in [('CCZ', 'kSEAL_CCZSrc'), ('DYC', 'kSEAL_DYCSrc'),
                         ('QJZ', 'kSEAL_QJZSrc'), ('THX', 'kSEAL_THXSrc')]:
        sequence = properties.get(key)
        if sequence and not (edition == 'THX' and sequence.startswith('TH-Y')):
            result.append({'edition': edition, 'sequence': sequence})
    return result


def build_report():
    fonts=font_paths()
    refs = {}
    for line in REFERENCES.read_text().splitlines():
        fields = line.split('\t')
        if len(fields) == 3:
            cp, key, value = fields
            refs.setdefault(int(cp[2:], 16), {})[key] = value
    covered = set()
    for path in fonts:
        with TTFont(path) as font:
            covered.update(font.getBestCmap())
    candidates = []
    for cp, properties in sorted(refs.items()):
        if cp in covered:
            continue
        sources = editions(properties)
        candidates.append({'codepoint': f'{cp:X}', 'sources': sources,
                           'enumeration': properties['kSEAL_THXSrc'],
                           'radical': properties['kSEAL_Rad'],
                           'modernEquivalent': properties.get('kSEAL_MCJK'),
                           'preferredReviewEdition': sources[0]['edition'] if sources else None})
    return {'unicode': '18.0.0',
            'status': 'Source-location review queue; identities and scan crops still require visual verification',
            'sourceDefinition': 'https://www.unicode.org/reports/tr60/tr60-3.html',
            'sourceHashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [REFERENCES, *fonts]},
            'missing': len(candidates),
            'withoutCCZ': sum(not any(s['edition'] == 'CCZ' for s in r['sources']) for r in candidates),
            'preferredReviewCounts': dict(sorted(Counter(r['preferredReviewEdition'] or 'unresolved' for r in candidates).items())),
            'candidates': candidates}


if __name__ == '__main__':
    report = build_report()
    (ROOT / 'docs/seal-edition-candidates.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    print(f"{report['missing']} Seal gaps: {report['preferredReviewCounts']}")
