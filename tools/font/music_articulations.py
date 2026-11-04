"""Attach new articulations and flags using native musical positioning."""
from music_mark_rules import extend_mark_rules
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from hebrew_marks import bounds

ARTICULATIONS = {0x1D127, 0x1D128}
FLAGS = {0x1D250, 0x1D251, 0x1D252}
POINTS = ARTICULATIONS | FLAGS


def add_marks(font, donor):
    notice = '\n'.join(sorted({n.toUnicode() for n in donor['name'].names if n.nameID == 0}))
    for record in font['name'].names:
        if record.nameID == 0 and notice not in record.toUnicode():
            record.string = (record.toUnicode() + '\n' + notice).encode(record.getEncoding())
    for cp in sorted(POINTS):
        old = font.getBestCmap()[0x1D172 if cp in FLAGS else 0x1D17B]
        new = f'u{cp:05X}'
        scale = font['head'].unitsPerEm / donor['head'].unitsPerEm
        pen = TTGlyphPen(None)
        donor.getGlyphSet()[donor.getBestCmap()[cp]].draw(
            TransformPen(Cu2QuPen(pen, max_err=.5), (scale, 0, 0, scale, 0, 0)))
        order = list(font.getGlyphOrder()); font['glyf'][new] = pen.glyph()
        font.setGlyphOrder(order + [new]); font['hmtx'][new] = (0, 0)
        a, b = bounds(font, old), bounds(font, new)
        dx, dy = round((a[0] + a[2] - b[0] - b[2]) / 2), round(a[3] - b[3])
        if cp in FLAGS:
            # Align the stem edge and bottom flag; extra flags extend upwards.
            dx, dy = round(a[0] - b[0]), round(a[1] - b[1])
        aligned = TTGlyphPen(None)
        font.getGlyphSet()[new].draw(TransformPen(aligned, (1, 0, 0, 1, dx, dy)))
        font['glyf'][new] = aligned.glyph(); font['hmtx'][new] = (0, round(bounds(font, new)[0]))
        extend_mark_rules(font, old, new)
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format == 12: table.cmap[cp] = new
