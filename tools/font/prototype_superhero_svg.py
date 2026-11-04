"""Preview production superhero recipes."""
from emoji_superhero_svg import *

def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--keys',nargs='*');parser.add_argument('--strict',action='store_true');args=parser.parse_args()
 active={k:v for k,v in RECIPES.items() if not args.keys or k in args.keys}
 from build_emoji import outline
 out=ROOT/'output/font-review/pen-translation';record_path=out/'superhero-svg-prototype.json'
 records=[r for r in json.loads(record_path.read_text()) if r['key'] not in active] if record_path.exists() else []
 for base in sorted({key.split('_')[0] for key in active}):
  keys=[k for k in active if k.split('_')[0]==base];sheet=Image.new('RGB',(350*len(keys),430),'#f5f2eb');draw=ImageDraw.Draw(sheet)
  for j,key in enumerate(keys):
   (white,skin,ink),r=prepare(key);ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1);glyph=outline(ink,(xs.min(),ys.min(),factor))
   r.update(key=key,compiledContours=glyph.numberOfContours,topologyAccepted=glyph.numberOfContours==r['sourceComponents']+r['sourceHoles'],treatmentAccepted=r['appliedStrength']>0 and not r['fallback'])
   rgb=np.full((*ink.shape,3),255,dtype='uint8');rgb[skin]=(171,129,90);rgb[ink]=17
   tile=Image.fromarray(rgb);tile.thumbnail((330,330));sheet.paste(tile,(j*350,0))
   draw.text((j*350+4,335),key,fill='black',font=ImageFont.load_default(size=15))
   draw.text((j*350+4,360),f'{r["appliedStrength"]:.3f}; contours {glyph.numberOfContours}/{r["sourceComponents"]+r["sourceHoles"]}',fill='black',font=ImageFont.load_default(size=15))
   draw.text((j*350+4,385),f'Skin regions {len(r["skinRegions"])}/{r["enclosedRegions"]}',fill='black',font=ImageFont.load_default(size=14))
   records.append(r)
  sheet.save(out/f'superhero-svg-{base}-prototype.png')
 (out/'superhero-svg-prototype.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
 failures=[r['key'] for r in records if not (r['topologyAccepted'] and r['treatmentAccepted'])]
 print(f'{len(records)-len(failures)} / {len(records)} drawings preserve treatment and compiled contours')
 if args.strict:assert not failures,failures
if __name__=='__main__':main()
