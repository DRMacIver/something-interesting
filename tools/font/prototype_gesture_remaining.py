"""Render the final four gesture poses using their production conversion."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from emoji_gesture_svg import ROOT,RECIPES as ALL_RECIPES,prepare
RECIPES={k:v for k,v in ALL_RECIPES.items() if k.split('_')[0] in {'1f647','1f926','1f937','1f9cf'}}

def main():
 from build_emoji import outline
 records=[];out=ROOT/'output/font-review/pen-translation'
 for base in sorted({key.split('_')[0] for key in RECIPES}):
  keys=[k for k in RECIPES if k.split('_')[0]==base];sheet=Image.new('RGB',(350*len(keys),430),'#f5f2eb');draw=ImageDraw.Draw(sheet)
  for j,key in enumerate(keys):
   (white,skin,ink),r=prepare(key);ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1);glyph=outline(ink,(xs.min(),ys.min(),factor))
   r.update(key=key,compiledContours=glyph.numberOfContours,topologyAccepted=glyph.numberOfContours==r['sourceComponents']+r['sourceHoles'],treatmentAccepted=r['appliedStrength']>0 and not r['fallback'])
   rgb=np.full((*ink.shape,3),255,dtype='uint8');rgb[skin]=(171,129,90);rgb[ink]=17
   tile=Image.fromarray(rgb);tile.thumbnail((330,330));sheet.paste(tile,(j*350,0))
   draw.text((j*350+4,335),key,fill='black',font=ImageFont.load_default(size=15))
   draw.text((j*350+4,360),f'{r["appliedStrength"]:.3f}; contours {glyph.numberOfContours}/{r["sourceComponents"]+r["sourceHoles"]}',fill='black',font=ImageFont.load_default(size=15))
   draw.text((j*350+4,385),f'Skin {r["skinRegions"]}; regions {r["enclosedRegions"]}',fill='black',font=ImageFont.load_default(size=14))
   records.append(r)
  sheet.save(out/f'gesture-svg-{base}-prototype.png')
 (out/'gesture-svg-remaining-prototype.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
