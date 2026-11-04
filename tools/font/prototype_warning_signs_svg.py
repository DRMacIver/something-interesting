"""Preview production warning_signs recipes."""
from emoji_warning_signs_svg import *

def main():
 import argparse
 from build_emoji import outline
 parser=argparse.ArgumentParser();parser.add_argument('--keys',nargs='*');parser.add_argument('--strict',action='store_true');args=parser.parse_args();keys=args.keys or list(RECIPES)
 out=ROOT/'output/font-review/pen-translation';path=out/'warning-signs-svg-prototype.json';records=[r for r in json.loads(path.read_text()) if r['key'] not in keys] if path.exists() else []
 sheet=Image.new('RGB',(1000,230*((len(keys)+4)//5)),'#f5f2eb');d=ImageDraw.Draw(sheet)
 for i,key in enumerate(keys):
  (white,colour,ink),r=prepare(key);ys,xs=np.nonzero(white);scale=760/max(np.ptp(xs)+1,np.ptp(ys)+1);g=outline(ink,(xs.min(),ys.min(),scale));r.update(compiledContours=g.numberOfContours,topologyAccepted=g.numberOfContours==r['sourceComponents']+r['sourceHoles'])
  rgb=np.full((*ink.shape,3),255,dtype='uint8');rgb[colour]=r['rgb'];rgb[ink]=17;tile=Image.fromarray(rgb);tile.thumbnail((180,180));x=i%5*200;y=i//5*230;sheet.paste(tile,(x+10,y));d.text((x+5,y+180),f'{key}: {r["appliedStrength"]:.3f}',fill='black',font=ImageFont.load_default(size=15));d.text((x+5,y+201),f'{g.numberOfContours}/{r["sourceComponents"]+r["sourceHoles"]} contours',fill='black',font=ImageFont.load_default(size=14));records.append(r);print(key,r['appliedStrength'],r['topologyAccepted'],r['colourRegions'],r['regionCount'],flush=True)
 sheet.save(out/'warning-signs-svg-prototype.png');path.write_text(json.dumps(records,indent=2)+'\n')
 if args.strict:assert all(r['topologyAccepted'] for r in records)
if __name__=='__main__':main()
