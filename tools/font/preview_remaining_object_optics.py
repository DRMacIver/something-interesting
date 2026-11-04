"""Inspect candidate object outlines with the approved optical stroke."""
import argparse,json
import numpy as np
import pymupdf
from PIL import Image,ImageDraw,ImageFont
from fontTools.pens.svgPathPen import SVGPathPen
from build_emoji import outline
from prototype_remaining_objects import ROOT,RECIPES,prepare
from svg_counter_review import review_counters


def preview(recipes,prepare,prefix,counter_losses=None):
    columns=min(5,len(recipes))
    sheet=Image.new('RGB',(300*columns,260*((len(recipes)+columns-1)//columns)),'#f5f2eb');draw=ImageDraw.Draw(sheet);reports=[]
    for i,key in enumerate(recipes):
        (paper,*colours,ink),r=prepare(key);ys,xs=np.nonzero(paper);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1);transform=xs.min(),ys.min(),factor
        advance=round((np.ptp(xs)+1)*factor)+100
        specifications=[(paper,(255,255,255)),*zip(colours,r['rgbs']),(ink,(17,17,17))]
        paths=[];glyphs=[]
        for mask,rgb in specifications:
            glyph=outline(mask,transform);pen=SVGPathPen(None);glyph.draw(pen,None);paths.append((pen.getCommands(),tuple(rgb)));glyphs.append(glyph)
        counters=review_counters(ink,transform,glyphs[-1],max_small_losses=(counter_losses or {}).get(key,0))
        for size,x,y in [(180,5,5),(33.6,235,80)]:
            stroke=f'<path d="{paths[-1][0]}" fill="none" stroke="#111111" stroke-width="18" stroke-linejoin="round" stroke-miterlimit="2"/>' if size==33.6 else ''
            layers=''.join(f'<path d="{path}" fill="rgb{rgb}"/>' for path,rgb in paths)
            svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{advance}" height="1000"><rect width="100%" height="100%" fill="white"/><g transform="translate(0 850) scale(1 -1)">{stroke}{layers}</g></svg>'
            doc=pymupdf.open(stream=svg.encode(),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(size/1000,size/1000))
            sheet.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),((i%columns)*300+x,(i//columns)*260+y))
        draw.text(((i%columns)*300+5,(i//columns)*260+210),key,fill='black',font=ImageFont.load_default(size=16));reports.append(dict(key=key,counterReview=counters,source=r['source'],compiledInkContours=int(glyphs[-1].numberOfContours),sourceComponents=r['sourceComponents'],sourceHoles=r['sourceHoles'],appliedStrength=r['appliedStrength']))
    out=ROOT/'output/font-review/pen-translation';sheet.save(out/(prefix+'-optics.png'));(out/(prefix+'-optics.json')).write_text(json.dumps(reports,indent=2)+'\n');print(len(reports),'candidate object contour checks passed')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--family',choices=['book-mail','money','clothing','tools-instruments','office-locks','places-weather','other-objects','globes','phoenix','air-water','road-infrastructure','ground-vehicles'],default='book-mail');args=parser.parse_args()
    if args.family=='money':
        from prototype_money_objects import RECIPES as recipes,prepare as money_prepare
        preview(recipes,money_prepare,'money')
    elif args.family=='clothing':
        from prototype_clothing_objects import RECIPES as recipes,prepare as clothing_prepare
        preview(recipes,clothing_prepare,'clothing')
    elif args.family=='other-objects':
        from prototype_other_objects import RECIPES as recipes,prepare as objects_prepare
        preview(recipes,objects_prepare,'other-objects')
    elif args.family=='ground-vehicles':
        from prototype_ground_vehicles import RECIPES as recipes,prepare as ground_prepare
        preview(recipes,ground_prepare,'ground-vehicles')
    elif args.family=='road-infrastructure':
        from prototype_road_infrastructure import RECIPES as recipes,prepare as road_prepare
        preview(recipes,road_prepare,'road-infrastructure')
    elif args.family=='air-water':
        from prototype_air_water import RECIPES as recipes,prepare as air_water_prepare
        preview(recipes,air_water_prepare,'air-water')
    elif args.family=='phoenix':
        from prototype_phoenix import RECIPES as recipes,prepare as phoenix_prepare
        preview(recipes,phoenix_prepare,'phoenix')
    elif args.family=='globes':
        from prototype_globes import RECIPES as recipes,prepare as globes_prepare
        preview(recipes,globes_prepare,'globes',counter_losses={'1f30f':1})
    elif args.family=='places-weather':
        from prototype_places_weather import RECIPES as recipes,prepare as places_prepare
        preview(recipes,places_prepare,'places-weather')
    elif args.family=='office-locks':
        from prototype_office_locks import RECIPES as recipes,prepare as office_prepare
        preview(recipes,office_prepare,'office-locks')
    elif args.family=='tools-instruments':
        from prototype_tools_instruments import RECIPES as recipes,prepare as instrument_prepare
        preview(recipes,instrument_prepare,'tools-instruments',counter_losses={'1fa95':1})
    else:preview(RECIPES,prepare,'remaining-objects')


if __name__=='__main__':main()
