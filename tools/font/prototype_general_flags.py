"""Preview registered general flag recipes."""
from emoji_general_flags_svg import *

def main():
 sheet=Image.new('RGB',(1000,500),'#f5f2eb');draw=ImageDraw.Draw(sheet);reports=[]
 for i,key in enumerate(RECIPES):
  (paper,*colours,ink),r=prepare(key);pixels=np.full((*ink.shape,3),255,dtype=np.uint8)
  for mask,rgb in zip(colours,r['rgbs']):pixels[mask]=rgb
  pixels[ink]=17;im=Image.fromarray(pixels);im.thumbnail((180,180));x=i%5*200;y=i//5*250;sheet.paste(im,(x,y));draw.text((x,y+185),key,fill='black',font=ImageFont.load_default(size=12));reports.append(r);print(key,r['appliedStrength'],flush=True)
 out=ROOT/'output/font-review/pen-translation';sheet.save(out/'general-flags-prototype.png');(out/'general-flags-prototype.json').write_text(json.dumps(reports,indent=2)+'\n')

if __name__=='__main__':main()
