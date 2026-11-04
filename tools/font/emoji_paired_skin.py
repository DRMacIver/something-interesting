"""Partition already-reviewed skin masks for separated paired figures."""
import numpy as np
from scipy import ndimage


def split_paired_skin(skin, ink):
    """Keep complete anatomical components on each side of the figure gap.

    This is intentionally limited to drawings whose two people are separated.
    Interlocking figures need their own source-derived anatomical masks.
    """
    _, xs = np.nonzero(ink)
    midpoint = (int(xs.min()) + int(xs.max())) / 2
    labels, count = ndimage.label(skin)
    left_ids, right_ids = [], []
    for index in range(1, count + 1):
        _, columns = np.nonzero(labels == index)
        assert not columns.min() < midpoint < columns.max(), 'skin crosses the figure gap'
        (left_ids if columns.mean() < midpoint else right_ids).append(index)
    assert left_ids and right_ids, 'expected two separate people'
    left = np.isin(labels, left_ids)
    right = np.isin(labels, right_ids)
    assert not (left & right).any() and np.array_equal(left | right, skin)
    return left, right, dict(midpoint=midpoint, leftComponents=left_ids,
                            rightComponents=right_ids,
                            leftPixels=int(left.sum()), rightPixels=int(right.sum()))


EXPECTED_BUNNY_COMPONENTS = {'1f46f': [[2, 4, 6, 8, 10, 11, 14, 15, 18], [1, 3, 5, 7, 9, 12, 13, 16, 17]], '1f46f_200d_2642': [[2, 5, 6, 8, 10, 12, 13, 17, 18], [1, 3, 4, 7, 9, 11, 14, 15, 16]], '1f46f_200d_2640': [[2, 5, 6, 9, 10, 13, 14], [1, 3, 4, 7, 8, 11, 12]]}
