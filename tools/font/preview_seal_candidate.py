"""Review a pinned Seal scan recipe beside its compiled outline at comic size."""
import argparse,json
from pathlib import Path
import pymupdf
from PIL import Image,ImageDraw
from fontTools.pens.svgPathPen import SVGPathPen
from build_seal_recovery import ROOT,mask,trace


def preview(record,output):
    scan,ink=mask(record)
    glyph=trace(ink);pen=SVGPathPen(None);glyph.draw(pen,None)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000"><rect width="100%" height="100%" fill="white"/><path transform="translate(0 850) scale(1 -1)" d="{pen.getCommands()}"/></svg>'
    sheet=Image.new('RGB',(720,260),'#f5f2eb');draw=ImageDraw.Draw(sheet)
    scan.thumbnail((180,200));sheet.paste(scan,(10,30))
    draw.text((10,5),record['sequence']+' scan / compiled candidate / 24px',fill='black')
    with pymupdf.open(stream=svg.encode(),filetype='svg') as doc:
        with pymupdf.open('pdf',doc.convert_to_pdf()) as pdf:
            for size,x in [(200,220),(24,460)]:
                pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000))
                sheet.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(x,30))
    output.parent.mkdir(parents=True,exist_ok=True);sheet.save(output)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();record=json.loads(args.recipe.read_text())
    output=args.output or ROOT/'output/font-review/seal-pending'/(record['sequence']+'-optics.png')
    preview(record,output);print(output)


if __name__=='__main__':main()
