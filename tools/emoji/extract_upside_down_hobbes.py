"""Extract the original coloured upside-down Hobbes on PDF page 246."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import pymupdf

ROOT=Path(__file__).resolve().parents[2]
BOX=(522,744,618,862)
# Selection at six pixels per PDF point; blue pixels are separately removed.
POLYGON=[(25,210),(60,135),(150,100),(220,52),(265,52),(260,100),
 (290,100),(295,52),(350,45),(415,75),(435,153),(413,218),(350,232),
 (300,196),(305,198),(310,259),(280,291),(250,300),(255,330),(275,355),
 (280,395),(300,438),(323,460),(390,375),(430,318),(388,279),(395,250),
 (433,229),(438,200),(466,185),(495,202),(535,205),(551,238),(553,268),
 (553,284),(540,303),(526,314),(480,337),(450,401),(428,445),(449,471),
 (493,484),(495,520),(479,559),(462,592),(484,623),(481,663),(457,689),
 (363,696),(283,691),(235,687),(216,652),(145,683),(95,680),(60,673),
 (49,643),(60,608),(101,580),(133,553),(96,524),(75,506),(70,477),
 (94,455),(65,420),(39,375),(25,315)]


def main():
    source=ROOT/'calvin-and-hobbes.pdf'
    doc=pymupdf.open(source);page=doc[245]
    pix=page.get_pixmap(matrix=pymupdf.Matrix(6,6),clip=pymupdf.Rect(BOX))
    rgb=np.array(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
    selection=Image.new('L',(pix.width,pix.height))
    ImageDraw.Draw(selection).polygon(POLYGON,fill=255)
    values=rgb.astype(float);r,g,b=values.transpose(2,0,1)
    blue=(b-r>45)&(g-r>30)&(b>165)
    alpha=(np.asarray(selection)>0)&~blue
    # Remove grey scan paper in the white fur, and recover black ink from
    # its scan tint. Keep the original orange fills and their relative shades.
    neutral=(values.max(axis=2)-values.min(axis=2)<55)&(values.min(axis=2)>130)
    ink=(values.max(axis=2)<105)|((values.max(axis=2)<165)&(b>r))
    clean=np.clip(values*1.15,0,255).astype(np.uint8)
    clean[neutral]=255;clean[ink]=17
    result=Image.fromarray(np.dstack([clean,alpha.astype(np.uint8)*255]))
    result=result.crop(result.getbbox())
    out=ROOT/'assets/emoji-concepts/hobbes-upside-down-v1.png';result.save(out)
    preview=Image.new('RGBA',result.size,'white');preview.alpha_composite(result)
    preview.convert('RGB').save(out.with_name('hobbes-upside-down-v1-white-preview.png'))
    out.with_suffix('.json').write_text(json.dumps(dict(source='calvin-and-hobbes.pdf',
        sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),pdfPage=246,
        panel='bottom right',box=BOX,pixelsPerPoint=6,selection=POLYGON,
        method='Composite PDF render, background knockout, scan-white/black normalization; no image generation or anatomy changes',
        limitation='The speech bubble occludes the tip of the tail in the original; no continuation was invented.'),indent=2)+'\n')
    print(out)


if __name__=='__main__':main()
