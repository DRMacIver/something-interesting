"""Horizontal Sibe quote forms share the narrow FE00 drawings.

Unicode 18 section 6.2.6 illustrates equal horizontal forms for FE00 and FE02;
their vertical orientations differ. This horizontal canvas renderer does not
implement vertical Sibe layout. No glyph is copied from the reference diagram.
"""
QUOTES={0x2018,0x2019,0x201c,0x201d}
REFERENCE='https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-6/'


def add_horizontal_sibe_quotes(font):
    table=next(t for t in font['cmap'].tables if t.format==14 and QUOTES<=dict(t.uvsDict.get(0xfe00,[])).keys())
    narrow=dict(table.uvsDict[0xfe00])
    existing=dict(table.uvsDict.get(0xfe02,[]))
    assert not QUOTES.intersection(existing),'Do not overwrite existing Sibe mappings'
    table.uvsDict[0xfe02]=sorted([*existing.items(),*((cp,narrow[cp]) for cp in QUOTES)])


def derivations(cmap):
    return [dict(sequence=chr(cp)+'\ufe02',drawingSequence=chr(cp)+'\ufe00',
                 scope='horizontal layout; vertical orientation remains unsupported',reference=REFERENCE)
            for cp in sorted(QUOTES.intersection(cmap))]
