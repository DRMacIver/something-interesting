"""Expand native Indic input rules for a new base; preserve existing outputs."""
from copy import deepcopy
from itertools import product


def extend_inputs(font, old, new):
    def cover(c):
        if old in c.glyphs and new not in c.glyphs:
            c.glyphs.append(new)

    def classes(c):
        if c is not None and old in c.classDefs:
            c.classDefs[new] = c.classDefs[old]

    def paired(c, records):
        if old in c.glyphs:
            records.append(deepcopy(records[c.glyphs.index(old)]))
            c.glyphs.append(new)

    def variants(items):
        return product(*[(v, new) if v == old else (v,) for v in items])

    def contextual(s):
        if s.Format == 3:
            for key, value in vars(s).items():
                if key.endswith('Coverage'):
                    for c in value: cover(c)
        elif s.Format == 2:
            cover(s.Coverage)
            for key, value in vars(s).items():
                if key.endswith('ClassDef'): classes(value)
        elif s.Format == 1:
            chain = hasattr(s, 'ChainSubRuleSet')
            set_key = 'ChainSubRuleSet' if chain else 'SubRuleSet'
            rule_key = 'ChainSubRule' if chain else 'SubRule'
            sets = getattr(s, set_key)
            paired(s.Coverage, sets)
            setattr(s, set_key + 'Count', len(sets))
            for ruleset in sets:
                if ruleset is None: continue
                expanded = []
                for rule in getattr(ruleset, rule_key):
                    keys = [k for k in ('Backtrack', 'Input', 'LookAhead') if hasattr(rule, k)]
                    for sequences in product(*(list(variants(getattr(rule, k))) for k in keys)):
                        r = deepcopy(rule)
                        for k, sequence in zip(keys, sequences): setattr(r, k, list(sequence))
                        expanded.append(r)
                setattr(ruleset, rule_key, expanded)
                setattr(ruleset, rule_key + 'Count', len(expanded))
        else: raise AssertionError(s.Format)

    for lookup in font['GSUB'].table.LookupList.Lookup:
        for s in lookup.SubTable:
            kind = lookup.LookupType
            if kind in (1, 2):
                if old in s.mapping: s.mapping[new] = deepcopy(s.mapping[old])
            elif kind == 4:
                original = deepcopy(s.ligatures)
                for first, ligatures in original.items():
                    for head in ([first, new] if first == old else [first]):
                        expanded = []
                        for ligature in ligatures:
                            for components in variants(ligature.Component):
                                item = deepcopy(ligature); item.Component = list(components)
                                expanded.append(item)
                        s.ligatures[head] = expanded
            elif kind in (5, 6): contextual(s)
            else: raise AssertionError(('GSUB', kind))

    for lookup in font['GPOS'].table.LookupList.Lookup:
        for s in lookup.SubTable:
            kind = lookup.LookupType
            if kind == 1:
                if s.Format == 1: cover(s.Coverage)
                else:
                    paired(s.Coverage, s.Value); s.ValueCount = len(s.Value)
            elif kind == 2:
                if s.Format == 2:
                    cover(s.Coverage); classes(s.ClassDef1); classes(s.ClassDef2)
                else:
                    paired(s.Coverage, s.PairSet); s.PairSetCount = len(s.PairSet)
                    for pairs in s.PairSet:
                        for record in list(pairs.PairValueRecord):
                            if record.SecondGlyph == old:
                                r = deepcopy(record); r.SecondGlyph = new
                                pairs.PairValueRecord.append(r)
                        pairs.PairValueCount = len(pairs.PairValueRecord)
            elif kind == 4:
                paired(s.BaseCoverage, s.BaseArray.BaseRecord)
                s.BaseArray.BaseCount = len(s.BaseArray.BaseRecord)
            elif kind == 6:
                # The source reference is a base, not a mark.
                assert old not in s.Mark1Coverage.glyphs + s.Mark2Coverage.glyphs
            elif kind == 8: contextual(s)
            else: raise AssertionError(('GPOS', kind))
    gdef = font['GDEF'].table
    classes(gdef.GlyphClassDef); classes(getattr(gdef, 'MarkAttachClassDef', None))
    if getattr(gdef, 'MarkGlyphSetsDef', None):
        for c in gdef.MarkGlyphSetsDef.Coverage: cover(c)
