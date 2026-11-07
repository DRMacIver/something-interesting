import sys
TOOLS='/Users/drmaciver/Projects/calvins-dad/tools/extensions'
sys.path[:0]=[TOOLS+'/reconstruction-v2',TOOLS+'/poses']
import practice, ink, numpy as np
from PIL import Image, ImageDraw
TASKS='/private/tmp/claude-501/-Users-drmaciver-Projects-calvins-dad/c2d6deef-f737-41b5-92c4-cdb6d89b6f8e/scratchpad/poses'
OUT='.'
task=practice.Task(TASKS,'standing')
Hw=task.head_width
pen=ink.Ink(task.size,seed=1)
W,H=task.size
def poly(pts):
    im=Image.new('L',(W,H),0); ImageDraw.Draw(im).polygon([tuple(p) for p in pts],fill=255)
    return np.asarray(im)>0
def line(pts,w,**k): pen.stroke(pts,[w],**k)
O=0.04*Hw; T=0.03*Hw; HV=0.08*Hw
exec(open('body.py').read())
task.save(pen.mask(),OUT)
