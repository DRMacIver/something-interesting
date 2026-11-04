"""Capture an immutable, named-glyph baseline before adding emoji forms."""
import argparse
import hashlib
import io
import json
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]


def capture(output):
    paths = [ROOT/'assets/fonts/dad-emoji.woff2', ROOT/'assets/fonts/dad-emoji-ink.woff2',
             ROOT/'js/emoji-manifest.js']
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    manifest = json.loads(paths[2].read_text().split('export default ', 1)[1].rstrip(';\n'))
    faces = []
    for path in paths[:2]:
        font = TTFont(path)
        names = font.getGlyphOrder()
        font.flavor = None
        data = io.BytesIO()
        font.save(data)
        faces.append((hb.Font(hb.Face(data.getvalue())), names))
    cases = []
    for text in sorted(manifest['sequences']):
        shapes = []
        for font, names in faces:
            buffer = hb.Buffer()
            buffer.add_str(text)
            buffer.guess_segment_properties()
            hb.shape(font, buffer)
            shapes.append([dict(name=names[g.codepoint], position=[p.x_advance, p.y_advance, p.x_offset, p.y_offset])
                           for g, p in zip(buffer.glyph_infos, buffer.glyph_positions)])
        if shapes[0] != shapes[1] or len(shapes[0]) != 1 or shapes[0][0]['position'][0] <= 0:
            raise ValueError('Emoji companions do not share one positive-advance drawing: '+repr(text))
        cases.append(dict(text=text, glyphs=shapes[0]))
    if hashes != {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}:
        raise ValueError('Production files changed during capture; no baseline written')
    # Exclusive creation protects previously accepted baselines from replacement.
    with output.open('x') as stream:
        json.dump(dict(products=hashes, count=len(cases), cases=cases), stream, ensure_ascii=False, separators=(',', ':'))
        stream.write('\n')
    print(f'Captured {len(cases)} forms from both companions: {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    capture(parser.parse_args().output)
