"""Show public scan crops beside compiled Seal outlines, large and at 24 px."""
import json
from pathlib import Path
import pymupdf
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from build_seal_recovery import mask
ROOT=Path(__file__).resolve().parents[2]
spec=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())
manifest=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
entry=next(e for e in manifest['fonts'] if e['source'].endswith('/DadSealRecovery-Regular.ttf'))
f=TTFont(ROOT/entry['file']);gs=f.getGlyphSet();out=Image.new('RGB',(720,len(spec['glyphs'])*210+50),'#f5f2eb');d=ImageDraw.Draw(out)
d.text((15,12),'Public scan / compiled outline / 24 px',font=ImageFont.load_default(size=22),fill='black')
for i,r in enumerate(spec['glyphs']):
 y=50+i*210;scan,_=mask(r);scan.thumbnail((150,175));out.paste(scan.convert('RGB'),(15,y));name=f.getBestCmap()[int(r['codepoint'],16)];pen=SVGPathPen(gs);gs[name].draw(pen)
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000"><rect width="100%" height="100%" fill="white"/><path transform="translate(0 850) scale(1 -1)" d="{pen.getCommands()}"/></svg>'
 doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf())
 for size,x in [(180,220),(24,440)]:
  pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000));out.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(x,y))
 d.text((490,y+35),'U+'+r['codepoint']+'\n'+r['sequence'],font=ImageFont.load_default(size=20),fill='black')
out.save(ROOT/'output/font-review/seal-recovery.png')
