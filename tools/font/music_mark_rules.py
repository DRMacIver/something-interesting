"""Extend native music mark classes, contexts, substitutions and anchors."""
from copy import deepcopy


def extend_mark_rules(font, old, new, outputs=None):
    outputs = outputs or {}
    def extend(obj):
        # Contextual coverage/class definitions have no parallel arrays.
        if isinstance(obj, list):
            for item in obj: extend(item)
        elif hasattr(obj, '__dict__'):
            if hasattr(obj, 'glyphs') and old in obj.glyphs: obj.glyphs.append(new)
            elif hasattr(obj, 'classDefs'):
                if old in obj.classDefs: obj.classDefs[new] = obj.classDefs[old]
            else:
                for value in vars(obj).values(): extend(value)
    extend(font['GDEF'].table)
    for tag in ('GSUB', 'GPOS'):
        for lookup in font[tag].table.LookupList.Lookup:
            for s in lookup.SubTable:
                kind = lookup.LookupType
                if (tag == 'GSUB' and kind in (5, 6)) or (tag == 'GPOS' and kind == 8):
                    extend(s)
                elif tag == 'GSUB' and hasattr(s, 'mapping'):
                    if old in s.mapping:
                        value = deepcopy(s.mapping[old])
                        s.mapping[new] = [outputs.get(v, v) for v in value] if isinstance(value, list) else outputs.get(value, value)
                elif tag == 'GPOS' and kind == 1 and old in s.Coverage.glyphs:
                    if s.Format == 2:
                        s.Value.append(deepcopy(s.Value[s.Coverage.glyphs.index(old)]))
                        s.ValueCount = len(s.Value)
                    s.Coverage.glyphs.append(new)
                elif tag == 'GPOS' and kind == 4 and old in s.MarkCoverage.glyphs:
                    s.MarkArray.MarkRecord.append(deepcopy(s.MarkArray.MarkRecord[s.MarkCoverage.glyphs.index(old)]))
                    s.MarkCoverage.glyphs.append(new)
                    s.MarkArray.MarkCount = len(s.MarkArray.MarkRecord)
                elif tag == 'GPOS' and kind == 4 and old in s.BaseCoverage.glyphs:
                    s.BaseArray.BaseRecord.append(deepcopy(s.BaseArray.BaseRecord[s.BaseCoverage.glyphs.index(old)]))
                    s.BaseCoverage.glyphs.append(new)
                    s.BaseArray.BaseCount = len(s.BaseArray.BaseRecord)
                elif tag == 'GPOS' and kind == 3 and old in s.Coverage.glyphs:
                    s.EntryExitRecord.append(deepcopy(s.EntryExitRecord[s.Coverage.glyphs.index(old)]))
                    s.Coverage.glyphs.append(new)
                    s.EntryExitCount = len(s.EntryExitRecord)
                elif tag == 'GPOS' and kind == 6 and old in s.Mark2Coverage.glyphs:
                    s.Mark2Array.Mark2Record.append(deepcopy(s.Mark2Array.Mark2Record[s.Mark2Coverage.glyphs.index(old)]))
                    s.Mark2Coverage.glyphs.append(new)
                    s.Mark2Array.Mark2Count = len(s.Mark2Array.Mark2Record)
