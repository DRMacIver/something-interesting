"""Conservative mechanical cleanup of the page-246 Hobbes extraction."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[2]

def main():
    source=ROOT/'assets/emoji-concepts/hobbes-upside-down-v1.png'
    rgba=np.array(Image.open(source).convert('RGBA'))
    rgb=rgba[:,:,:3];opaque=rgba[:,:,3]>=128
    ink=opaque&(rgb.max(axis=2)<135)
    # Close only tiny scan pinholes, then smooth and very slightly contract
    # the ink boundary. No reposing, invented strokes, or image generation.
    closed=ndimage.binary_closing(ink,structure=ndimage.generate_binary_structure(2,1),border_value=0)
    smooth=ndimage.gaussian_filter(closed.astype(float),sigma=.65)>.58
    rgb[ink&~smooth]=255
    rgb[smooth]=17
    # Residual blue from the panel background is not character colour.
    cool=(rgb[:,:,2].astype(int)>rgb[:,:,0].astype(int)+8)&~smooth
    rgb[cool]=255
    opaque=ndimage.median_filter(opaque,size=3)|smooth
    rgba[:,:,:3]=rgb;rgba[:,:,3]=opaque.astype(np.uint8)*255
    out=source.with_name('hobbes-upside-down-v2.png')
    Image.fromarray(rgba).save(out)
    preview=Image.new('RGBA',(rgba.shape[1],rgba.shape[0]),'white');preview.alpha_composite(Image.fromarray(rgba))
    preview.convert('RGB').save(out.with_name(out.stem+'-white-preview.png'))
    out.with_suffix('.json').write_text(json.dumps(dict(source=source.relative_to(ROOT).as_posix(),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),pdfPage=246,method='Tiny pinhole closing; Gaussian ink-edge smoothing sigma 0.65 / threshold 0.58; blue-fringe removal; no image generation or anatomy changes',opticalStrokeRatio=.002),indent=2)+'\n')
    print(out)

if __name__=='__main__':main()
