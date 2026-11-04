"""Before/after sheet for the opt-in pen translation prototype."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pen_translate import Settings, ink_mask, translate

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'output/font-review/pen-translation'
SAMPLES = [
    ('Toothy grin', 'faces-expansion-v1.png', (0, 0, 384, 365)),
    ('Spectacles', 'faces-playful-v1.png', (768, 350, 1152, 650)),
    ('Steam', 'faces-strained-v1.png', (0, 650, 384, 1024)),
    ('Mouthless', 'faces-strained-v1.png', (1152, 650, 1536, 1024)),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB', (1120, 1080), '#f5f2eb')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=22)
    small = ImageFont.load_default(size=15)
    draw.text((24, 16), 'Deterministic pen treatment - prototype', fill='black', font=font)
    for col, text in enumerate(['Original', 'Controlled / 1.0', 'Expressive / 1.7']):
        draw.text((150+col*320, 58), text, fill='black', font=font)
    records = []
    for row, (name, source, box) in enumerate(SAMPLES):
        image = Image.open(ROOT/'output/imagegen/emoji-production'/source).crop(box)
        mask = ink_mask(image)
        yy, xx = np.nonzero(mask)
        mask = mask[yy.min():yy.max()+1, xx.min():xx.max()+1]
        draw.text((20, 110+row*230), name, fill='black', font=small)
        for col, strength in enumerate([0, 1, 1.7]):
            result, record = translate(mask, Settings(strength=strength, seed=17+row))
            record.update(name=name, source=source, box=box)
            records.append(record)
            result.save(OUT/f'{row}-{col}.png')
            # Ink bounding box normalization gives each icon the same display size.
            a = np.asarray(result); ys, xs = np.nonzero(a < 128)
            thumb = result.crop((xs.min()-5, ys.min()-5, xs.max()+6, ys.max()+6))
            thumb.thumbnail((176, 176), Image.Resampling.LANCZOS)
            x, y = 145+col*320, 105+row*230
            sheet.paste(thumb, (x+(180-thumb.width)//2, y))
            tiny = result.crop((xs.min()-5, ys.min()-5, xs.max()+6, ys.max()+6))
            tiny.thumbnail((24, 24), Image.Resampling.LANCZOS)
            sheet.paste(tiny, (x+210, y+70))
            draw.text((x+194, y+106), '24 px', fill='#555555', font=small)
            draw.text((x, y+184), f'Applied {record["appliedStrength"]:.2f}', fill='#555555', font=small)
    draw.text((24, 1040), 'Same expressions; no image generation. Not applied to the production font.', fill='black', font=small)
    sheet.save(OUT/'comparison.png')
    (OUT/'review.json').write_text(json.dumps(records, indent=2)+'\n')
    print(json.dumps([{k:r[k] for k in ['name','appliedStrength','backoffs','fallback']} for r in records],indent=2))


if __name__ == '__main__': main()
