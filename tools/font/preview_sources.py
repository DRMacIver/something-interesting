"""Render source candidates with HarfBuzz, independent of Pillow's RAQM build.

Outline rasterisation is for review sheets only, never used to build fonts.
"""
from pathlib import Path
import io
import math

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = [
    ("Original Dad Lettering", "assets/fonts/dad-lettering.woff2", "THERE ARE TWO TYPES OF THINGS."),
    ("Kalam / Devanagari", "build/unicode-sources/google/ofl/kalam/Kalam-Regular.ttf", "नमस्ते दुनिया"),
    ("Aref Ruqaa / Arabic", "build/unicode-sources/google/ofl/arefruqaa/ArefRuqaa-Regular.ttf", "مرحبا بالعالم"),
    ("Klee One / Japanese", "build/unicode-sources/google/ofl/kleeone/KleeOne-Regular.ttf", "世界は不思議なことでいっぱいだ。"),
    ("WenKai / Chinese", "build/unicode-sources/wenkai/fonts/TTF/LXGWWenKai-Regular.ttf", "世界充满了奇妙的事物。"),
    ("Gaegu / Korean", "build/unicode-sources/google/ofl/gaegu/Gaegu-Regular.ttf", "세상은 신기한 일로 가득해요."),
]


class FlattenPen(BasePen):
    def __init__(self, glyphs):
        super().__init__(glyphs)
        self.contours = []

    def _moveTo(self, point):
        self.contours.append([point])

    def _lineTo(self, point):
        self.contours[-1].append(point)

    def _curveToOne(self, p1, p2, p3):
        p0 = self._getCurrentPoint()
        for i in range(1, 17):
            t = i / 16
            self._lineTo(tuple((1-t)**3*p0[k] + 3*(1-t)**2*t*p1[k]
                              + 3*(1-t)*t*t*p2[k] + t**3*p3[k] for k in (0, 1)))

    def _qCurveToOne(self, p1, p2):
        p0 = self._getCurrentPoint()
        for i in range(1, 13):
            t = i / 12
            self._lineTo(tuple((1-t)**2*p0[k]+2*(1-t)*t*p1[k]+t*t*p2[k] for k in (0, 1)))

    def _closePath(self):
        pass

    def _endPath(self):
        pass


def area(points):
    return sum(a[0]*b[1]-a[1]*b[0] for a, b in zip(points, points[1:]+points[:1]))


def render_line(image, path, text, size, x, baseline):
    font = TTFont(path)
    font.flavor = None
    data = io.BytesIO()
    font.save(data)
    face = hb.Face(data.getvalue())
    shaper = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(shaper, buf)
    if any(g.codepoint == 0 for g in buf.glyph_infos):
        raise ValueError(f"Missing shaped glyph in {path}: {text}")
    scale = size / face.upem
    order = font.getGlyphOrder()
    glyphs = font.getGlyphSet()
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = FlattenPen(glyphs)
        glyphs[order[info.codepoint]].draw(pen)
        contours = [[(x+(px+pos.x_offset)*scale, baseline-(py+pos.y_offset)*scale)
                     for px, py in contour] for contour in pen.contours if len(contour) > 2]
        if contours:
            left = math.floor(min(p[0] for c in contours for p in c)) - 1
            top = math.floor(min(p[1] for c in contours for p in c)) - 1
            right = math.ceil(max(p[0] for c in contours for p in c)) + 1
            bottom = math.ceil(max(p[1] for c in contours for p in c)) + 1
            mask = Image.new("L", (right-left, bottom-top))
            draw = ImageDraw.Draw(mask)
            contours.sort(key=lambda c: abs(area(c)), reverse=True)
            sign = area(contours[0])
            for contour in contours:
                draw.polygon([(px-left, py-top) for px, py in contour], fill=255 if area(contour)*sign > 0 else 0)
            image.paste("black", (left, top, right, bottom), mask)
        x += pos.x_advance * scale
        baseline -= pos.y_advance * scale


def main():
    factor = 3
    image = Image.new("RGB", (1400*factor, 1450*factor), "white")
    draw = ImageDraw.Draw(image)
    # Labels use a bundled source, so the review tool needs no system font.
    label = ImageFont.truetype(str(ROOT / "build/unicode-sources/noto/NotoSans-Regular.ttf"), 24*factor)
    for i, (title, path, text) in enumerate(SAMPLES):
        y = 20+i*235
        draw.text((30*factor, y*factor), title, font=label, fill="black")
        render_line(image, ROOT/path, text, 58*factor, 30*factor, (y+120)*factor)
        render_line(image, ROOT/path, text, 28*factor, 30*factor, (y+195)*factor)
    out = ROOT / "output/font-review/handwriting-sources.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    image.resize((1400, 1450), Image.Resampling.LANCZOS).save(out)
    print(out)


if __name__ == "__main__":
    main()
