"""Extract locked source art and original reusable inserts for reconstruction."""
from pathlib import Path
import sys
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import build_assets as b
HERE=Path(__file__).resolve().parent
ink,bg=b.layers(b.ROOT/'calvin-and-hobbes.pdf')
originals=[]
for i,p in enumerate(b.PANELS,1):
    p=dict(p);p.pop('repair',None)
    a,_=b.panel_art(ink,bg,p)
    if 'signature' in p:
        x0,y0=p['box'][:2];sx0,sy0,sx1,sy1=p['signature'];a[sy0-y0:sy1-y0,sx0-x0:sx1-x0]=True
    originals.append(a)
    Image.fromarray(np.where(a,0,255).astype('uint8')).save(HERE/f'original-{i}.png')
    b.smooth(a).save(HERE/f'locked-{i}.png')
# Exact line-art crop from the same scene, without balloons or lettering.
insert=Image.fromarray(np.where(originals[0][640:1020,385:817],0,255).astype('uint8'))
insert.save(HERE/'calvin-player-source.png')
# Panel 3 can reuse this exact seated Calvin and player, at source scale.
for number in (2,3):
    a=originals[number-1];h,w=a.shape
    canvas=Image.new('L',(w+800,1830),255)
    canvas.paste(Image.fromarray(np.where(a,0,255).astype('uint8')),(400,0))
    if number==3:canvas.paste(insert,(900,1150))
    # Crop only empty top space from the generation input; keep full coordinates
    # in the final assembly, and never rescale the locked original crop.
    canvas.crop((0,380,canvas.width,1830)).resize((canvas.width*2,2900)).save(HERE/f'canvas-{number}.png')
