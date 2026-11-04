"""Preserve special-stem ornaments through every native stem substitution."""
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from hebrew_marks import bounds
from music_mark_rules import extend_mark_rules

POINTS = {0x1D25F, 0x1D280, 0x1D281}


def add_stems(font, donor):
    old = font.getBestCmap()[0x1D165]
    variants = [n for n in font.getGlyphOrder() if n.startswith(old)]
    assert len(variants) == 7
    for cp in sorted(POINTS):
        new = f'u{cp:05X}'
        outputs = {n: n.replace(old, new) for n in variants}
        recording = RecordingPen()
        donor.getGlyphSet()[donor.getBestCmap()[cp]].draw(recording)
        contours, contour = [], []
        for op in recording.value:
            contour.append(op)
            if op[0] == 'closePath':
                contours.append(contour); contour = []
        # The donor's narrow rectangle is the stem. Replace it with each
        # native stem length, keeping the distinctive ornament intact.
        stem_index = 3 if cp == 0x1D25F else 0
        stem = contours.pop(stem_index)
        xs = [p[0] for _, points in stem for p in points]
        ys = [p[1] for _, points in stem for p in points]
        assert max(xs) - min(xs) == 37 and max(ys) - min(ys) == 662
        assert font['head'].unitsPerEm == donor['head'].unitsPerEm
        ornament = RecordingPen(); ornament.value = [op for c in contours for op in c]
        for source, target in outputs.items():
            box = bounds(font, source)
            pen = TTGlyphPen(font.getGlyphSet())
            font.getGlyphSet()[source].draw(pen)
            dx = (box[0] + box[2] - min(xs) - max(xs)) / 2
            dy = box[3] - max(ys)
            ornament.replay(TransformPen(Cu2QuPen(pen, max_err=.5), (1, 0, 0, 1, dx, dy)))
            order = list(font.getGlyphOrder())
            font['glyf'][target] = pen.glyph(); font.setGlyphOrder(order + [target])
            font['hmtx'][target] = font['hmtx'][source]
            font['hmtx'][target] = (font['hmtx'][source][0], round(bounds(font, target)[0]))
        for source, target in outputs.items():
            extend_mark_rules(font, source, target, outputs)
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format == 12: table.cmap[cp] = new
