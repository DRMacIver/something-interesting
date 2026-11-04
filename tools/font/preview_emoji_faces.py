"""Review the compiled COLR face glyphs, enlarged and at 24 pixels."""
import argparse
import json
import math
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--music', action='store_true')
    parser.add_argument('--clocks', action='store_true')
    parser.add_argument('--category', choices=['activity-people','gesture-people','transport_extra','new-svg','detailed-people','detailed-people-tones','roles','role-tones','professions','profession-tones','person-forms','person-form-tones','people','people-tones','household','science','recreation','celebrations','electronics','clothing','mixed-handshakes','produce','apples','timepieces','stationery','places','buildings','music','clocks','transport','tools','expressions','compounds','mammals','birds','wildlife','plants','colour-faces','sports','food','dining','sky','gestures','gesture-tones'])
    args = parser.parse_args()
    category = args.category or ('music' if args.music else 'clocks' if args.clocks else None)
    font = TTFont(ROOT/'assets/fonts/dad-emoji.woff2')
    glyphs = font.getGlyphSet()
    review = json.loads((ROOT/'output/imagegen/emoji-production/glyph-review.json').read_text())
    entries = [e for e in review['glyphs'] if 'penTreatment' in e]
    if category:
        entries = [e for e in entries if e.get('category') == ('gestures' if category=='gesture-tones' else 'people' if category=='people-tones' else 'person-forms' if category=='person-form-tones' else 'professions' if category=='profession-tones' else 'roles' if category=='role-tones' else 'detailed-people' if category=='detailed-people-tones' else category)]
    if category=='gesture-tones':
        examples={0x270A,0x1F44C,0x1F90C,0x1F91E,0x1F448,0x1F44B,0x1FAF6,0x1FAF7,0x1F64C,0x1F64F,0x1F91D}
        entries=[dict(e,glyphName=f'u{int(e["codepoint"][2:],16):X}'+(f'.tone{i}' if i else ''),
                      codepoint=e.get('codepoint',e.get('label',''))+(f' tone {i}' if i else ' neutral'))
                 for e in entries if int(e['codepoint'][2:],16) in examples for i in range(6)]
    if category in {'people-tones','person-form-tones','profession-tones','role-tones','detailed-people-tones'}:
        entries=[dict(e,glyphName=e['glyphName']+(f'.tone{i}' if i else ''),
                      codepoint=e.get('codepoint',e.get('label',''))+(f' tone {i}' if i else ' neutral'))
                 for e in entries for i in range(6)]
    cols, cellw, cellh = (4 if category in {'music','colour-faces'} else 6 if category else 8), 180, 192
    image = Image.new('RGB', (cols*cellw, math.ceil(len(entries)/cols)*cellh+54), '#f5f2eb')
    draw = ImageDraw.Draw(image)
    label = ImageFont.load_default(size=15)
    draw.text((16, 12), 'Compiled expressive glyphs - enlarged and 24 px', font=ImageFont.load_default(size=22), fill='black')
    for i, entry in enumerate(entries):
        name = entry.get('glyphName') or font.getBestCmap()[int(entry['codepoint'][2:], 16)]
        paths = []
        for layer in font['COLR'].ColorLayers[name]:
            pen = SVGPathPen(glyphs); glyphs[layer.name].draw(pen)
            c = font['CPAL'].palettes[0][layer.colorID]
            paths.append(f'<path d="{pen.getCommands()}" fill="rgb({c.red},{c.green},{c.blue})"/>')
        advance = font['hmtx'][name][0]
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{advance}" height="1000"><rect width="100%" height="100%" fill="white"/><g transform="translate(0 850) scale(1 -1)">{"".join(paths)}</g></svg>'
        document = pymupdf.open(stream=svg.encode(), filetype='svg')
        pdf = pymupdf.open('pdf', document.convert_to_pdf())
        x, y = i%cols*cellw, i//cols*cellh+54
        for size, dx, dy in [(120, 10, 0), (24, 145, 60)]:
            pix = pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000, size/1000), alpha=False)
            image.paste(Image.frombytes('RGB', (pix.width, pix.height), pix.samples), (x+dx, y+dy))
        amount = entry['penTreatment']['appliedStrength']
        caption = entry.get('codepoint', entry.get('label'))
        caption_font = label
        for size in range(15, 8, -1):
            caption_font = ImageFont.load_default(size=size)
            if draw.textlength(caption, font=caption_font) <= cellw-15:
                break
        draw.text((x+10, y+130), caption, font=caption_font, fill='black')
        draw.text((x+10, y+151), f'Applied {amount:.2f}', font=label, fill='#555555')
    out = ROOT/'output/font-review/pen-translation'/f'compiled-{category or "faces"}.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(out)
    print(out)


if __name__ == '__main__': main()
