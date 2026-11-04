"""Attach sampled source decisions without claiming full linguistic approval."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = 'docs/unicode-style-dispositions.json'


def review_for_source(source):
    rows = json.loads((ROOT / RECORD).read_text())['sources']
    row = next(r for r in rows if r['source'] == source)
    # Only the stable decision is hashed. Build status and later validation
    # evidence evolve independently and must not invalidate a font recipe.
    decision = {k: row[k] for k in ('number', 'source', 'sourceSha256', 'disposition')}
    digest = hashlib.sha256(json.dumps(decision, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'record': RECORD, 'number': row['number'],
            'disposition': row['disposition'], 'decisionSha256': digest,
            'scope': 'sampled source style; not all-glyph or linguistic approval'}
