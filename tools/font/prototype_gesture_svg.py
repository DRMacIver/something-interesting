"""Source-derived gesture conversion and exposed-skin review; not yet production."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import pymupdf
from pen_translate import Settings,translate,same_features
ROOT=Path(__file__).resolve().parents[2]
# expected shape count, retained paint, solid ink, exposed skin
RECIPES={
 '1f64b':(27,{0}|set(range(7,18))|{24,25,26},{0}|set(range(11,18))|{26},{8,9,10,24}),
 '1f64b_200d_2642':(15,set(range(11))|{12,13,14},set(range(4,11))|{14},{1,2,3,12}),
 '1f64b_200d_2640':(16,{0,2,3,4,5,6}|set(range(8,16)),{0,5,6,8,9,10,11,12,15},{3,4,13}),
 '1f481':(27,{0}|set(range(7,17))|{18,19,20},{0}|set(range(11,17))|{20},{8,9,10,18}),
 '1f481_200d_2642':(15,set(range(10))|{11,12,13},set(range(4,10))|{13},{1,2,3,11}),
 '1f481_200d_2640':(16,{0}|set(range(2,10))|{12,13,14,15},{0}|set(range(5,10))|{14,15},{3,4,12}),
 '1f645':(21,{0,1,2,3,4,6,11,12,13,14,15,16,17,18,20},{0,13,14,15,16,17,20},{1,2,3,6,11}),
 '1f645_200d_2642':(21,set(range(10))|{11,12,18,19,20},{2,4,5,6,7,8,9},{0,1,3,11,18}),
 '1f645_200d_2640':(19,set(range(9))|{10,15,16,17},{0,2,3,4,5,6,7},{1,10,15}),
 '1f646':(27,{0,1}|set(range(8,18))|{23,24,25,26},{1}|set(range(11,18)),{8,9,10,23,25}),
 '1f646_200d_2642':(16,set(range(11))|{12,13,14,15},set(range(4,11)),{1,2,3,12,14}),
 '1f646_200d_2640':(17,{0}|set(range(2,12))|{13,14,15,16},{0}|set(range(5,12)),{3,4,13,15}),
 '1f64d':(24,{0,1}|set(range(8,18)),{1}|set(range(11,18)),{8,9,10}),
 '1f64d_200d_2642':(12,set(range(11)),set(range(4,11)),{1,2,3}),
 '1f64d_200d_2640':(13,{0}|set(range(2,12)),{0}|set(range(5,12)),{3,4}),
 '1f64e':(31,{0}|set(range(7,25)),{0,9,11,12,13}|set(range(17,25)),{8,10,14,15,16}),
 '1f64e_200d_2642':(19,set(range(16))|{17,18},{2,4,5,6}|set(range(10,16))|{17,18},{1,3,7,8,9}),
 '1f64e_200d_2640':(20,{0}|set(range(2,19)),{0,4,6,7,8}|set(range(11,19)),{3,5,9,10}),
}

from emoji_gesture_svg import prepare

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
 (out/'gesture-svg-prototype.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
