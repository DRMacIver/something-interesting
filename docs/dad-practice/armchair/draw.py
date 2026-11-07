import sys
TOOLS='/Users/drmaciver/Projects/calvins-dad/tools/extensions'
sys.path[:0]=[TOOLS+'/reconstruction-v2',TOOLS+'/poses']
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
import practice, ink
TASKS='/private/tmp/claude-501/-Users-drmaciver-Projects-calvins-dad/c2d6deef-f737-41b5-92c4-cdb6d89b6f8e/scratchpad/poses'
OUT='.'
task=practice.Task(TASKS,'armchair')
pen=ink.Ink(task.size,seed=3)
Hw=task.head_width
kit=json_kit=__import__('json').load(open(practice.REF/'parts.json'))
def poly(pts):
    im=Image.new('L',task.size,0);ImageDraw.Draw(im).polygon([tuple(p) for p in pts],fill=255)
    return np.asarray(im)>0
def place(idx,at,angle=0,flip=False,scale=1.0,clip=None):
    m=task.part(kit[idx],at,angle,flip,scale)
    if clip is not None: m&=clip
    return m
def solid(m):  # paper under a part
    f=ndi.binary_fill_holes(ndi.binary_closing(m,iterations=3))
    pen.paint(f,255)
    pen.paint(m,0)

# --- shirt torso (paper fill then outline)
torso=[(190,262),(262,248),(300,300),(345,400),(418,430),(422,500),(300,520),(240,490),(200,450),(185,390),(180,340)]
pen.fill(torso,255,wobble=0)
# front edge of shirt (belly side)
pen.stroke([(188,262),(176,310),(184,370),(196,430),(232,478)],[5,7,8,7,6],wobble=1.0)
# back edge below existing line
pen.stroke([(416,425),(422,470),(420,505)],[6,7,7],wobble=0.8)
# collar/shoulder line
pen.stroke([(150,292),(172,272),(192,262)],[6,6,5],wobble=0.8)
# shirt tail / belt line
pen.stroke([(228,480),(290,486),(350,478),(418,470)],[4,6,6,5],wobble=1.0)
# placket stub
pen.stroke([(330,402),(338,440),(345,470)],[4,5,5],wobble=0.8)

# --- trousers: one black silhouette
trou=[(412,470),(340,474),(262,490),(200,520),(158,560),(138,605),(148,660),(160,715),(156,752),
      (240,754),(242,705),(248,660),(268,650),(272,720),(270,762),(345,764),(342,700),(338,650),(412,650)]
pen.fill(trou,0,wobble=1.0)
xs=np.arange(task.size[0])[None,:]
pen.paint((xs>417)&task.region&(np.arange(task.size[1])[:,None]>440)&(np.arange(task.size[1])[:,None]<650),255)
# chair/furniture at left continuing behind the leg
pen.paint(poly([(96,480),(240,480),(200,520),(158,560),(138,605),(148,660),(160,715),(156,742),(96,742)])&task.region,0)
pen.stroke([(100,838),(250,840),(330,833),(418,832)],[5,6,6,4],wobble=0.8)

pen.stroke([(240,486),(200,516),(160,556),(140,604),(150,660),(160,715)],[3,6,7,7,6,5],colour=255,wobble=0.5)
# white fold marks
pen.stroke([(215,552),(190,575),(180,600)],[2,9,2],colour=255,wobble=0.6)
pen.stroke([(300,520),(340,540),(380,548)],[2,8,2],colour=255,wobble=0.6)
pen.stroke([(150,732),(200,738),(238,734)],[3,5,3],colour=255,wobble=0.4)  # near cuff
pen.stroke([(275,742),(310,748),(342,742)],[3,5,3],colour=255,wobble=0.4)

# --- shoes
solid(place(336,(345,782),0,False,0.9,clip=xs<418))   # far shoe toe right
solid(place(103,(192,775),0,True,0.8))    # near shoe toe left

# --- near arm: sleeve + hand
solid(place(331,(155,325),0,False,0.88))
solid(place(220,(78,352),20,True,0.8))

task.save(pen.mask()&task.region,OUT)
