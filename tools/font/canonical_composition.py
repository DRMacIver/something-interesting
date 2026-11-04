"""Preserve Kirat Rai canonical equivalence missing in the licensed source.

The source has precomposed vowel drawings but no ccmp feature. Add ligatures
for their canonical decompositions, retaining every existing feature and glyph.
"""
from copy import deepcopy
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString


def compose_kirat(font):
    cmap = font.getBestCmap()
    sequences = [(0x16D6A, (0x16D63,0x16D67,0x16D67)),
                 (0x16D6A, (0x16D69,0x16D67)),
                 (0x16D69, (0x16D63,0x16D67)),
                 (0x16D68, (0x16D67,0x16D67))]
    rules = ['sub ' + ' '.join(cmap[cp] for cp in seq) + ' by ' + cmap[target] + ';'
             for target,seq in sequences if target in cmap and all(cp in cmap for cp in seq)]
    if not rules:
        return
    temporary = deepcopy(font)
    addOpenTypeFeaturesFromString(temporary, 'feature ccmp {\n'+'\n'.join(rules)+'\n} ccmp;', tables=['GSUB'])
    if 'GSUB' not in font:
        font['GSUB'] = temporary['GSUB']
        return
    old, new = font['GSUB'].table, temporary['GSUB'].table
    if getattr(old, 'FeatureVariations', None):
        raise ValueError('Variable feature remapping needs separate implementation')
    offset = len(old.LookupList.Lookup)
    old.LookupList.Lookup.extend(new.LookupList.Lookup)
    old.LookupList.LookupCount = len(old.LookupList.Lookup)
    record = new.FeatureList.FeatureRecord[0]
    record.Feature.LookupListIndex = [i+offset for i in record.Feature.LookupListIndex]
    index = len(old.FeatureList.FeatureRecord)
    old.FeatureList.FeatureRecord.append(record)
    systems = []
    for script in old.ScriptList.ScriptRecord:
        systems.extend([script.Script.DefaultLangSys] + [r.LangSys for r in script.Script.LangSysRecord])
    systems = [s for s in systems if s is not None]
    for system in systems:
        system.FeatureIndex.append(index)
        system.FeatureCount = len(system.FeatureIndex)
    # Feature records must be sorted by tag; repair every referring index.
    ordered = sorted(enumerate(old.FeatureList.FeatureRecord), key=lambda pair: pair[1].FeatureTag)
    remap = {before: after for after,(before,_) in enumerate(ordered)}
    old.FeatureList.FeatureRecord = [record for _,record in ordered]
    old.FeatureList.FeatureCount = len(ordered)
    for system in systems:
        system.FeatureIndex = sorted(remap[i] for i in system.FeatureIndex)
        if system.ReqFeatureIndex != 0xffff:
            system.ReqFeatureIndex = remap[system.ReqFeatureIndex]


def compose_tulu(font):
    """Complete Daarage's independent-vowel composition before its syllable rules.

    USE may reorder the EE sign before its base before ccmp, so accept both
    logical and reordered forms for independent AI. Other vowel-sign splitting
    and all original conjunct rules remain supplied by the source font.
    """
    from fontTools.ttLib.tables.otTables import Ligature
    cmap = font.getBestCmap()
    lookup = font['GSUB'].table.LookupList.Lookup[0]
    if lookup.LookupType != 4 or len(lookup.SubTable) != 1:
        raise ValueError('Pinned Daarage initial composition lookup changed')
    ligatures = lookup.SubTable[0].ligatures
    for target, sequence in [(0x11383, (0x11382, 0x113C9)),
                             (0x11385, (0x11384, 0x113BB)),
                             (0x1138E, (0x1138B, 0x113C2)),
                             (0x1138E, (0x113C2, 0x1138B)),
                             (0x11391, (0x11390, 0x113C9))]:
        rule = Ligature()
        rule.Component = [cmap[cp] for cp in sequence[1:]]
        rule.CompCount = len(sequence)
        rule.LigGlyph = cmap[target]
        ligatures.setdefault(cmap[sequence[0]], []).insert(0, rule)
