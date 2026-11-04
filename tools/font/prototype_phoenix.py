"""Render registered phoenix candidates."""
import json
import numpy as np
from PIL import Image
from emoji_phoenix_svg import ROOT,RECIPES,prepare,KEY,PINHOLE_LIMITS


def main():
 (paper,*colours,ink),r=prepare(KEY)
 pixels=np.full((*ink.shape,3),255,dtype=np.uint8)
 for mask,rgb in zip(colours,r['rgbs']):pixels[mask]=rgb
 pixels[ink]=17
 image=Image.fromarray(pixels);image.thumbnail((300,300))
 out=ROOT/'output/font-review/pen-translation';image.save(out/'phoenix-prototype.png')
 (out/'phoenix-prototype.json').write_text(json.dumps(r,indent=2)+'\n')
 print(KEY,r['appliedStrength'],r['filledRasterPinholePixels'])


if __name__=='__main__':main()
