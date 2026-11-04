"""Fit the licensed short-diagonal zero drawing to a fullwidth character cell."""
from copy import deepcopy
from pathlib import Path
from math_unicode_marks import repair_marks,unicode_categories

REFERENCE='https://www.unicode.org/Public/18.0.0/ucd/StandardizedVariants.txt'


def add_fullwidth_zero(font):
    cmap=font.getBestCmap()
    assert 0xff10 not in cmap,'Do not replace an existing fullwidth drawing'
    table=next(t for t in font['cmap'].tables if t.format==14 and ord('0') in dict(t.uvsDict.get(0xfe00,[])))
    variant=dict(table.uvsDict[0xfe00])[ord('0')]
    assert variant and variant!=cmap[ord('0')]
    em=font['head'].unitsPerEm
    order=list(font.getGlyphOrder())
    for original,name in [(cmap[ord('0')],'fullwidthZero.default'),(variant,'fullwidthZero.shortDiagonal')]:
        assert name not in font['glyf']
        glyph=deepcopy(font['glyf'][original])
        assert not glyph.isComposite()
        advance,bearing=font['hmtx'][original]
        shift=(em-advance)//2
        glyph.removeHinting()
        glyph.coordinates.translate((shift,0))
        glyph.recalcBounds(font['glyf'])
        font['glyf'][name]=glyph
        font['hmtx'][name]=(em,bearing+shift)
        order.append(name)
    font.setGlyphOrder(order)
    for subtable in font['cmap'].tables:
        if subtable.isUnicode() and subtable.format!=14:
            subtable.cmap[0xff10]='fullwidthZero.default'
    table.uvsDict[0xfe00]=sorted([*table.uvsDict[0xfe00],(0xff10,'fullwidthZero.shortDiagonal')])
    cmap=font.getBestCmap()
    bases={n or cmap[cp] for t in font['cmap'].tables if t.format==14 for rows in t.uvsDict.values() for cp,n in rows}
    bases.update(cmap[cp] for t in font['cmap'].tables if t.format==14 for rows in t.uvsDict.values() for cp,_ in rows)
    return repair_marks(font,bases,unicode_categories(Path(__file__).resolve().parents[2]))


def derivations():
    return [dict(sequence='０\ufe00',drawingSequence='0\ufe00',reference=REFERENCE,
                 adaptation='native short-diagonal zero translated into an em-wide cell; source contours retained; fullwidth logical character and advance preserved')]
