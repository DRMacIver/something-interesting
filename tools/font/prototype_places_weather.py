"""Render registered places-weather candidates."""
import argparse,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from emoji_places_weather_svg import ROOT,RECIPES,prepare,STROKE_PATHS,CRUMB_LIMITS


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('keys',nargs='*');args=parser.parse_args()
 keys=args.keys or list(RECIPES)
 if len(set(keys))!=len(keys) or any(key not in RECIPES for key in keys):parser.error('expected distinct recipe keys')
 prefix='places-weather' if set(keys)==set(RECIPES) else 'places-weather-partial'
 sheet=Image.new('RGB',(1000,500),'#f5f2eb');draw=ImageDraw.Draw(sheet);reports=[]
 for i,key in enumerate(keys):
  (paper,*colours,ink),r=prepare(key)
  pixels=np.full((*ink.shape,3),255,dtype=np.uint8)
  for mask,rgb in zip(colours,r['rgbs']):pixels[mask]=rgb
  pixels[ink]=17
  image=Image.fromarray(pixels);image.thumbnail((180,180))
  x=i%5*200;y=i//5*250;sheet.paste(image,(x,y))
  draw.text((x,y+185),key,fill='black',font=ImageFont.load_default(size=12))
  reports.append(r);print(key,r['appliedStrength'],flush=True)
 out=ROOT/'output/font-review/pen-translation'
 sheet.save(out/(prefix+'-prototype.png'))
 (out/(prefix+'-prototype.json')).write_text(json.dumps(reports,indent=2)+'\n')


if __name__=='__main__':main()
