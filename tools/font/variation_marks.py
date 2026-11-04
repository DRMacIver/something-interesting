"""Keep available source marks alongside UVS bases in split font shards."""
from native_variations import variation_bases


def additional_marks(font, points, marks):
    if not any(points.intersection(bases) for bases in variation_bases(font).values()):
        return set()
    return marks-set(points)
