"""Extract the original standing Hobbes in page 254's top-left panel."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
BOX = (72, 117, 178, 281)
# Coordinates in the six-pixels-per-point composite render. Follow the figure,
# excluding the adjacent balloon, Calvin's hand, and the panel border.
POLYGON = [(204,65),(247,60),(258,26),(332,23),(363,42),(387,24),
 (444,14),(456,60),(436,106),(433,137),(464,126),(458,149),
 (505,154),(477,179),(518,194),(484,213),(502,231),(459,235),
 (472,242),(530,231),(580,236),(621,249),(621,387),(607,415),
 (617,534),(622,679),(618,802),(629,867),(635,910),(620,946),
 (565,967),(467,976),(401,951),(338,943),(278,918),(269,896),
 (292,854),(345,829),(343,788),(345,765),(379,730),(400,694),
 (407,615),(411,542),(395,511),(396,472),(372,465),(365,440),
 (379,424),(355,434),(367,399),(374,381),(347,400),(354,365),
 (364,350),(325,352),(297,359),(260,370),(219,405),(215,429),
 (239,437),(248,459),(235,489),(208,504),(144,517),(99,529),
 (53,516),(31,492),(28,474),(19,456),(16,423),(23,404),(43,398),
 (69,410),(57,386),(52,365),(65,349),(90,347),(111,357),(139,392),
 (162,368),(177,338),(202,318),(241,301),(268,292),(216,281),
 (191,269),(168,266),(181,245),(191,228),(183,211),(204,213),
 (211,197),(218,186),(212,174),(226,172),(220,153),(225,106),
 (235,92),(205,94),(204,87),(232,78)]

def main():
    source = ROOT / 'calvin-and-hobbes.pdf'
    doc = pymupdf.open(source)
    pix = doc[253].get_pixmap(matrix=pymupdf.Matrix(6,6),clip=pymupdf.Rect(BOX))
    rgb = np.array(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
    selection = Image.new('L',(pix.width,pix.height))
    ImageDraw.Draw(selection).polygon(POLYGON,fill=255)
    # The original black line layer is distinct from the grey scan paper.
    grey = rgb.mean(axis=2)
    alpha = np.asarray(selection.filter(ImageFilter.MaxFilter(17))).copy()
    alpha[:400,621:] = 0
    # Short balloon-line fragments beside the ear and muzzle are not ink
    # belonging to Hobbes. These boxes contain no character linework.
    alpha[:55,:258] = 0
    alpha[43:66,455:] = 0
    alpha[255:300,:183] = 0
    alpha[240:255,:173] = 0
    value = np.clip((grey-110)*255/55,0,255).astype(np.uint8)
    result = Image.fromarray(np.dstack([value,value,value,alpha]))
    result = result.crop(result.getbbox())
    out = ROOT/'assets/emoji-concepts/hobbes-standing-254-v1.png'
    result.save(out)
    preview = Image.new('RGBA',result.size,'white');preview.alpha_composite(result)
    preview.convert('RGB').save(out.with_name(out.stem+'-white-preview.png'))
    out.with_suffix('.json').write_text(json.dumps(dict(source='calvin-and-hobbes.pdf',
        sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),pdfPage=254,
        panel='top left',box=BOX,pixelsPerPoint=6,selection=POLYGON,
        method='Composite PDF render; figure selection and scan contrast normalization; no image generation or anatomy changes',
        limitation='His right arm is clipped by the original panel boundary; no continuation is invented.'),indent=2)+'\n')
    print(out)

if __name__=='__main__':main()
