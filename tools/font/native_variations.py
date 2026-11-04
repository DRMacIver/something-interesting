"""Retain native Unicode variation sequences when splitting source fonts."""


def variation_bases(font):
    """Selector -> bases, including default and explicitly drawn variants."""
    result = {}
    for table in font['cmap'].tables:
        if table.format == 14:
            for selector, records in table.uvsDict.items():
                result.setdefault(selector, set()).update(cp for cp, _ in records)
    return result


def retain_selectors(font, points):
    # A selector need not have an ordinary cmap glyph. FontTools only retains
    # format14 records when both base and selector are requested explicitly.
    return set(points) | {selector for selector, bases in variation_bases(font).items()
                          if bases.intersection(points)}


def variation_ranges(font):
    result = {}
    for selector, bases in sorted(variation_bases(font).items()):
        ranges = []
        for cp in sorted(bases):
            if ranges and cp == ranges[-1][1] + 1:
                ranges[-1][1] = cp
            else:
                ranges.append([cp, cp])
        if ranges:
            result[str(selector)] = ranges
    return result
