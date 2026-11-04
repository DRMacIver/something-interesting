"""Preview registered regional flag recipes."""
from emoji_regional_flags_svg import *

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--regions',nargs='*');args=parser.parse_args();regions=args.regions or EXAMPLES
    sheet=Image.new('RGB',(1000,240*((len(regions)+4)//5)),'#f5f2eb');d=ImageDraw.Draw(sheet);reports=[]
    for i,region in enumerate(regions):
        (paper,*masks,ink),r=prepare(region);pixels=np.full((*ink.shape,3),255,dtype=np.uint8)
        for mask,rgb in zip(masks,r['rgbs']):pixels[mask]=rgb
        pixels[ink]=17;im=Image.fromarray(pixels);im.thumbnail((185,185));x=i%5*200;y=i//5*240;sheet.paste(im,(x+5,y+5));d.text((x+5,y+195),f'{region}: {r["appliedStrength"]:.3f}',fill='black',font=ImageFont.load_default(size=16))
        d.text((x+5,y+215),f'{len(masks)} colours',fill='black',font=ImageFont.load_default(size=14));reports.append(r);print(region,r['appliedStrength'],len(masks),r['meanQuantizationError'],flush=True)
    out=ROOT/'output/font-review/pen-translation';sheet.save(out/'region-flags-prototype.png');(out/'region-flags-prototype.json').write_text(json.dumps(reports,indent=2)+'\n')
if __name__=='__main__':main()
