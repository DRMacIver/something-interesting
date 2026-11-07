import sys
T='/Users/drmaciver/Projects/calvins-dad/tools/extensions'
sys.path[:0]=[T+'/reconstruction-v2',T+'/poses']
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion
import practice, ink
TASKS='/private/tmp/claude-501/-Users-drmaciver-Projects-calvins-dad/c2d6deef-f737-41b5-92c4-cdb6d89b6f8e/scratchpad/poses'
OUT='.'
task=practice.Task(TASKS,'floor')
pen=ink.Ink(task.size,seed=3)
B=0;W=255
def polymask(pts):
    m=Image.new('L',task.size,0);ImageDraw.Draw(m).polygon([tuple(p) for p in pts],fill=255)
    return np.asarray(m)>0
def poly(pts,c): pen.paint(polymask(pts),c)
def shape(points,lw=6,wobble=1.2,fill=W):
    """closed outlined shape: black outline lw px, interior `fill`."""
    curve=pen.fill(points,B,wobble=wobble)
    m=polymask(curve)
    inner=binary_erosion(m,iterations=lw)
    pen.paint(inner,fill)
    return m
def limb(pts,widths,line=6):
    pen.stroke(pts,[w+2*line for w in widths],B)
    pen.stroke(pts,widths,W)
def line(pts,w=(2,5,2),c=B): pen.stroke(pts,list(w),c)

# panel borders redrawn
for x0,x1 in ((500,511),(538,546)):
    poly([(x0,440),(x1,440),(x1,740),(x0,740)],B)

# ---- far arm: forearm running right behind the torso into the border, fist
limb([(320,414),(400,418),(470,424)],[46,44,42],6)
shape([(450,402),(480,398),(503,410),(506,440),(486,452),(458,448),(446,426)],6)
line([(480,404),(486,420),(482,440)],(3,5,3))
line([(462,406),(466,420),(462,438)],(3,4,3))

# ---- far leg (right, behind near knee, cut by border)
shape([(400,628),(440,612),(490,618),(512,648),(512,700),(470,712),(410,706),(385,670)],6)
line([(470,640),(486,660),(484,690)],(2,6,2))
pen.stroke([(405,700),(450,708),(505,704)],[3,6,4],B)

# ---- sneaker + sock at left
shape([(150,614),(184,610),(196,636),(190,664),(150,662)],5)           # sock
shape([(132,646),(164,650),(190,664),(192,704),(150,714),(96,714),(66,704),(58,682),(68,660),(92,646),(112,642)],7,wobble=1.0)  # shoe
shape([(58,694),(70,710),(110,718),(160,716),(194,708),(194,692),(150,702),(100,698),(72,688)],5,fill=B)   # heavy sole band
line([(64,676),(86,660),(110,664),(118,686)],(4,6,4))      # toe cap
line([(136,650),(150,646),(172,652)],(3,4,3))             # ankle opening rim
for (a,b) in (((126,658),(154,666)),((120,672),(156,680)),((116,686),(158,692))):
    pen.stroke([a,b],[6,6],B)                                  # lace bars

# ---- near leg: thigh then shin (crossed), one white silhouette with outline
shape([(98,598),(126,578),(200,584),(290,588),(360,584),(415,574),(458,584),(480,615),(470,650),(420,656),(330,650),(240,650),(160,650),(112,640),(96,620)],6)
# shin lying below, in front
shape([(196,654),(260,646),(360,646),(436,652),(474,672),(462,698),(420,708),(340,712),(250,714),(204,710),(188,692),(188,668)],6)
# crease shadow under thigh
pen.fill([(250,650),(330,648),(430,654),(400,664),(320,662),(250,664)],B,wobble=.6)
# cuff arc on the shin at left
line([(200,656),(192,680),(202,708)],(5,7,5))
# folds
line([(330,592),(352,616),(346,640)],(2,5,2))
line([(255,592),(280,614),(276,640)],(2,4,2))
line([(398,660),(425,672),(450,672)],(2,4,2))
line([(290,676),(312,692),(310,706)],(2,5,2))
line([(236,662),(248,682),(244,702)],(2,4,2))
pen.stroke([(300,714),(380,716),(440,710)],[3,6,3],B)

# ---- torso
pen.fill([(228,295),(160,340),(112,430),(100,520),(104,590),(180,598),(260,585),(300,520),(318,430),(312,330)],B)
for off in (-70,-30,12,52):
    x0=240+off*0.9
    pen.stroke([(x0+22,335),(x0-6,420),(x0-38,500),(x0-52,570)],[4,15,15,6],W)
pen.stroke([(104,588),(180,602),(262,588)],[6,8,5],W)
# collar
poly([(232,292),(262,338),(292,304)],W)
pen.stroke([(232,292),(262,338),(292,304)],[7,7,7],B)
poly([(300,312),(300,350),(342,328),(318,306)],W)
pen.stroke([(300,312),(300,350),(342,328)],[7,7,7],B)

# ---- near arm: bare forearm resting on the knee
limb([(292,438),(364,462),(438,498)],[64,56,48],7)
# sleeve
poly([(222,326),(312,314),(346,400),(352,448),(232,420)],W)
pen.fill([(226,330),(312,318),(342,400),(346,442),(236,418),(226,380)],B,wobble=.8)
pen.stroke([(300,330),(318,375),(332,430)],[4,12,5],W)
pen.stroke([(262,340),(266,380),(274,420)],[4,12,5],W)
pen.stroke([(236,420),(290,432),(347,446)],[5,7,5],B)

# ---- near hand: compact fist clamped over the knee
Wr=np.array([436,498.]);a=np.radians(55);d=np.array([np.cos(a),np.sin(a)]);n=np.array([-d[1],d[0]])
def P(u,v): return tuple(Wr+u*d+v*n)
# back of hand
shape([P(-10,-28),P(20,-34),P(50,-32),P(72,-22),P(78,4),P(72,28),P(44,34),P(14,32),P(-10,26)],6)
# four curled fingers, overlapped, knuckles at the front edge, tips tucked down onto the knee
for i,v in enumerate((-24,-8,8,24)):
    ln=(30,36,34,26)[i]
    limb([P(58,v),P(80+ln*0.3,v+2),P(88+ln*0.5,v+4+i)],[18,17,15],4)
    line([P(80,v-7),P(84,v),P(80,v+6)],(2,3,2),c=B)
# thumb: attached, lying along the top edge toward the knuckles
limb([P(8,-30),P(34,-42),P(60,-38)],[17,16,13],4)
line([P(20,-8),P(40,-4),P(56,-8)],(2,3,2))
mask=pen.mask()
task.save(mask,OUT)
