"""Reviewed outlined person roles: skin, headwear and equipment stay separate."""
from emoji_professions import prepare_regions, add_reviewed_roles

FORMS = {
    '👮': (5, [5]),
    '👮\u200d♂️': (5, [5]),
    '👮\u200d♀️': (5, [5]),
    '🕵️': (6, [3, 5]),
    '🕵️\u200d♂️': (6, [3, 5]),
    '🕵️\u200d♀️': (6, [3, 5]),
    '💂': (2, [1]),
    '💂\u200d♂️': (2, [1]),
    '💂\u200d♀️': (2, [1]),
    '🥷': (3, [1]),
    '👷': (2, [2]),
    '👷\u200d♂️': (2, [2]),
    '👷\u200d♀️': (2, [2]),
    '🫅': (3, [3]),
    '🤴': (3, [3]),
    '👸': (3, [3]),
    '👳': (5, [5]),
    '👳\u200d♂️': (5, [5]),
    '👳\u200d♀️': (5, [5]),
    '👲': (5, [5]),
    '🧕': (2, [2]),
    '🤵': (2, [1]),
    '🤵\u200d♂️': (2, [1]),
    '🤵\u200d♀️': (2, [1]),
    '👰': (6, [4]),
    '👰\u200d♂️': (6, [4]),
    '👰\u200d♀️': (6, [4]),
}


def prepare(font, shaping_font, canonical):
    return prepare_regions(font, shaping_font, canonical, *FORMS[canonical])


def add_roles(root, glyphs, metrics, cmap, layers, review, outline):
    return add_reviewed_roles(root, glyphs, metrics, cmap, layers, review, outline,
                              FORMS, prepare, 'roles', 'role')
