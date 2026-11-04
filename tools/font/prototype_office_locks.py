"""Render registered office-locks candidates."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from emoji_office_locks_svg import ROOT,RECIPES,prepare,STROKE_PATHS


def main():
 sheet=Image.new('RGB',(1000,500),'#f5f2eb');draw=ImageDraw.Draw(sheet);reports=[]
 for i,key in enumerate(RECIPES):
  (paper,*colours,ink),r=prepare(key)
  pixels=np.full((*ink.shape,3),255,dtype=np.uint8)
  for mask,rgb in zip(colours,r['rgbs']):pixels[mask]=rgb
  pixels[ink]=17
  image=Image.fromarray(pixels);image.thumbnail((180,180))
  x=i%5*200;y=i//5*250;sheet.paste(image,(x,y))
  draw.text((x,y+185),key,fill='black',font=ImageFont.load_default(size=12))
  reports.append(r);print(key,r['appliedStrength'],flush=True)
 out=ROOT/'output/font-review/pen-translation'
 sheet.save(out/'office-locks-prototype.png')
 (out/'office-locks-prototype.json').write_text(json.dumps(reports,indent=2)+'\n')


if __name__=='__main__':main()
