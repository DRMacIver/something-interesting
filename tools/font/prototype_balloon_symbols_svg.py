"""Preview production balloon_symbols recipes."""
from emoji_balloon_symbols_svg import *

def main():
 import argparse
 from build_emoji import outline
 parser=argparse.ArgumentParser();parser.add_argument('--keys',nargs='*');parser.add_argument('--strict',action='store_true');args=parser.parse_args();keys=args.keys or list(SYMBOLS)
 out=ROOT/'output/font-review/pen-translation';path=out/'balloon-symbols-svg-prototype.json';records=[r for r in json.loads(path.read_text()) if r['key'] not in keys] if path.exists() else []
 sheet=Image.new('RGB',(1000,230*((len(keys)+4)//5)),'#f5f2eb');d=ImageDraw.Draw(sheet)
 for i,key in enumerate(keys):
  (white,ink),r=prepare(key);ys,xs=np.nonzero(white);scale=760/max(np.ptp(xs)+1,np.ptp(ys)+1);g=outline(ink,(xs.min(),ys.min(),scale));r.update(compiledContours=g.numberOfContours,topologyAccepted=g.numberOfContours==r['sourceComponents']+r['sourceHoles'])
  tile=Image.fromarray(np.where(ink,17,255).astype('uint8')).convert('RGB');tile.thumbnail((180,180));x=i%5*200;y=i//5*230;sheet.paste(tile,(x+10,y));d.text((x+5,y+180),f'{key}: {r["appliedStrength"]:.3f}',fill='black',font=ImageFont.load_default(size=15));d.text((x+5,y+201),f'{g.numberOfContours}/{r["sourceComponents"]+r["sourceHoles"]} contours',fill='black',font=ImageFont.load_default(size=14));records.append(r);print(key,r['appliedStrength'],r['topologyAccepted'],flush=True)
 sheet.save(out/'balloon-symbols-svg-prototype.png');path.write_text(json.dumps(records,indent=2)+'\n')
 if args.strict:assert all(r['topologyAccepted'] for r in records)
if __name__=='__main__':main()
