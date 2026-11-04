"""Mechanically cut a diagonal forearm strip; never redraw the character."""
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'assets/emoji-concepts/hobbes-front-v1.png'


def shorten(source,shift=88,trim_shoulder=False):
    pixels=np.asarray(source.convert('RGB'))
    height,width=pixels.shape[:2]
    y,x=np.mgrid[:height,:width]
    along=(x-y)/np.sqrt(2)
    # The cut ends just before the nose. Everything beyond it, including the
    # complete face and ears, stays at its original coordinates and scale.
    cut_end=-60.
    cut_start=cut_end-shift*np.sqrt(2)
    across=(x+y)/np.sqrt(2)
    # A separator through the white space between the original paws. Their
    # outlines touch in the source, so connected-component splitting cannot
    # distinguish them. Small transverse translations align the tapered arm
    # edges at the join without stretching either paw.
    boundary=np.interp(along,[-600,-424,-364,-304,-244,-184],
                       [600,600,550,660,690,680])
    result=pixels.copy();result[along<cut_end]=255
    for upper,dx,dy in [(True,shift+8,-shift+8),(False,shift-2,-shift-2)]:
        selected=(along<cut_start)&((across<boundary) if upper else (across>=boundary))
        sy,sx=np.nonzero(selected)
        tx,ty=sx+dx,sy+dy
        valid=(tx>=0)&(tx<width)&(ty>=0)&(ty<height)
        # Copy ink and antialias pixels, leaving background white. Every
        # copied pixel is unscaled and unrotated original artwork.
        visible=pixels[sy,sx].min(axis=1)<250;valid &= visible
        result[ty[valid],tx[valid]]=pixels[sy[valid],sx[valid]]
    if trim_shoulder:
        # Existing shoulder ink fades out sooner; no replacement contour is
        # invented. This interval is wholly behind the original head.
        fade=np.clip((along-375.)/110.,0.,1.)[:,:,None]
        result=np.rint(result*(1-fade)+255*fade).astype(np.uint8)
    fixed=(along>=-55)&(along<=370)
    assert np.array_equal(result[fixed],pixels[fixed]),'Original face region changed'
    return Image.fromarray(result)


def main():
    source=Image.open(SOURCE)
    out=ROOT/'output/font-review/hobbes-mechanical';out.mkdir(parents=True,exist_ok=True)
    for shift in [60,75,88]:
        shorten(source,shift).save(out/f'arms-{shift}.png')
    chosen=shorten(source,88,trim_shoulder=True)
    path=ROOT/'assets/emoji-concepts/hobbes-arms-shortened-v1.png';chosen.save(path)
    path.with_suffix('.json').write_text(json.dumps(dict(
        source=SOURCE.relative_to(ROOT).as_posix(),method='Diagonal strip removal and rigid integer translation; no image generation',
        pawTranslations=[[96,-80],[86,-90]],removedAxisLength=float(88*np.sqrt(2)),cutEnd=-60,
        shoulderFade=[375,485],facePixelPreservation='All source pixels with -55 <= (x-y)/sqrt(2) <= 370 remain byte-identical',
        sourcePreserved=True),indent=2)+'\n')
    print(path)


if __name__=='__main__':main()
