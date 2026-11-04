"""Render registered ground vehicle candidates."""
from emoji_ground_vehicles_svg import ROOT,RECIPES,STROKE_PATHS,STROKE_STYLES,PINHOLE_LIMITS,CRUMB_LIMITS,prepare

def main():
 import json
 import numpy as np
 from PIL import Image,ImageDraw,ImageFont
 sheet=Image.new('RGB',(1000,500),'#f5f2eb');draw=ImageDraw.Draw(sheet);reports=[]
 for i,key in enumerate(RECIPES):
  (paper,*colours,ink),r=prepare(key)
  pixels=np.full((*ink.shape,3),255,dtype=np.uint8)
  for mask,rgb in zip(colours,r['rgbs']):pixels[mask]=rgb
  pixels[ink]=17
  im=Image.fromarray(pixels);im.thumbnail((180,180));x=i%5*200;y=i//5*250
  sheet.paste(im,(x,y));draw.text((x,y+185),key,fill='black',font=ImageFont.load_default(size=12))
  reports.append(r);print(key,r['appliedStrength'],flush=True)
 out=ROOT/'output/font-review/pen-translation'
 sheet.save(out/'ground-vehicles-prototype.png')
 (out/'ground-vehicles-prototype.json').write_text(json.dumps(reports,indent=2)+'\n')

if __name__=='__main__':main()
