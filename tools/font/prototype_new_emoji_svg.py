"""Review three new SVG ink recipes; does not modify the production font."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import pymupdf
from pen_translate import Settings,translate
from build_emoji import outline
from emoji_new_svg import prepare

ROOT=Path(__file__).resolve().parents[2]
RECIPES={
    '1fabe':(4,set(range(4)),set(),2.2),
    '1fac6':(12,set(range(1,12)),set(range(1,12)),1.3),
    '1fadd':(10,set(range(7)),set(range(2,7)),1.8),
}


def main():
    manifest=json.loads((ROOT/'docs/new-emoji-svg-source-probe.json').read_text())
    sheet=Image.new('RGB',(900,310),'#f5f2eb');draw=ImageDraw.Draw(sheet)
    reports=[]
    for column,(key,(expected,keep,solid,stroke)) in enumerate(RECIPES.items()):
        (white,ink),report=prepare(key)
        image=Image.fromarray(np.where(ink,0,255).astype('uint8'))
        ys,xs=np.nonzero(ink);factor=760/max(xs.max()-xs.min()+1,ys.max()-ys.min()+1)
        glyph=outline(ink,(xs.min(),ys.min(),factor))
        assert glyph.numberOfContours>=report["sourceComponents"]+report["sourceHoles"]
        image.save(ROOT/f"output/font-review/pen-translation/new-svg-ink-{key}.png")
        report.update(compiledContours=glyph.numberOfContours,codepoint=key,source=report["source"],sourcePixels=768,svgStrokeWidth=stroke,keptPaths=sorted(keep),solidPaths=sorted(solid),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),status='Production conversion review')
        reports.append(report)
        for size,x,y in [(210,column*300+5,15),(24,column*300+250,105)]:sheet.paste(image.resize((size,size),Image.Resampling.LANCZOS),(x,y))
        draw.text((column*300+10,242),f'U+{key.upper()} applied {report["appliedStrength"]:.3f}',fill='black',font=ImageFont.load_default(size=17))
        draw.text((column*300+10,269),f'Fallback: {report["fallback"]}',fill='black',font=ImageFont.load_default(size=14))
    out=ROOT/'output/font-review/pen-translation/new-svg-ink-prototype'
    sheet.save(out.with_suffix('.png'));out.with_suffix('.json').write_text(json.dumps(reports,indent=2)+'\n')
    print(out)


if __name__=='__main__':main()
