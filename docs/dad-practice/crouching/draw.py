import sys
T='/Users/drmaciver/Projects/calvins-dad/tools'
sys.path[:0]=[T+'/extensions/reconstruction-v2',T+'/extensions/poses']
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation
import practice, ink
S='/private/tmp/claude-501/-Users-drmaciver-Projects-calvins-dad/c2d6deef-f737-41b5-92c4-cdb6d89b6f8e/scratchpad/poses'
OUT='.'
task=practice.Task(S,'crouching')
pen=ink.Ink(task.size,seed=5)
Hw=task.head_width
w=lambda f:f*Hw
W,H=task.size

def shape(items,grow=0):
    """union of capsules ('c',p,q,r) and polys ('p',pts); returns bool mask"""
    m=Image.new('L',(W*3,H*3),0); d=ImageDraw.Draw(m)
    for it in items:
        if it[0]=='c':
            _,p,q,r=it; r+=grow
            d.line([(p[0]*3,p[1]*3),(q[0]*3,q[1]*3)],fill=255,width=int(2*r*3))
            for c in (p,q): d.ellipse([(c[0]-r)*3,(c[1]-r)*3,(c[0]+r)*3,(c[1]+r)*3],fill=255)
        elif it[0]=='e':
            _,c,rx,ry=it; rx+=grow; ry+=grow
            d.ellipse([(c[0]-rx)*3,(c[1]-ry)*3,(c[0]+rx)*3,(c[1]+ry)*3],fill=255)
        else:
            pts=[(x*3,y*3) for x,y in it[1]]
            d.polygon(pts,fill=255)
            if grow:
                d.line(pts+[pts[0]],fill=255,width=int(2*grow*3))
                for x,y in pts: d.ellipse([x-grow*3,y-grow*3,x+grow*3,y+grow*3],fill=255)
    return np.asarray(m.resize((W,H),Image.LANCZOS))>127
def inked(items,lw):
    pen.paint(shape(items,lw),0); pen.paint(shape(items),255)

# ---------------- trousers: one black silhouette
pen.fill([(62,610),(110,585),(180,585),(250,598),(315,618),(345,650),(335,685),(300,715),(262,745),(225,772),(150,790),(85,780),(62,720)],0,wobble=2)
# white fold highlights (few, short)
pen.stroke([(160,600),(210,612),(250,625)],[1,6,1],colour=255)
pen.stroke([(300,640),(318,660),(316,680)],[1,6,1],colour=255)
pen.stroke([(120,660),(112,700),(120,730)],[1,5,1],colour=255)

# ---------------- shoes: two fat oval sneakers, near one in front
def shoe(cx,cy,sx=1.0,sy=1.0,heavy=True):
    # toe right: body oval, toe cap, ankle opening
    body=[('e',(cx,cy),62*sx,27*sy),('e',(cx+30*sx,cy+2*sy),42*sx,25*sy)]
    inked(body,w(.07 if heavy else .05))
    # sole stripe
    pen.stroke([(cx-58*sx,cy+19*sy),(cx,cy+27*sy),(cx+55*sx,cy+22*sy),(cx+70*sx,cy+10*sy)],[w(.04),w(.05),w(.05),w(.03)],wobble=.8)
    # toe cap line
    pen.stroke([(cx+22*sx,cy-14*sy),(cx+32*sx,cy),(cx+26*sx,cy+16*sy)],[w(.03),w(.035),w(.03)],wobble=.6)
    # ankle opening (black)
    pen.fill([(cx-48*sx,cy-14*sy),(cx-30*sx,cy-23*sy),(cx-8*sx,cy-20*sy),(cx-20*sx,cy-9*sy)],0,wobble=.5)
    # laces
    for k in (0,1):
        pen.stroke([(cx+(-2+11*k)*sx,cy-24*sy),(cx+(6+11*k)*sx,cy-10*sy)],[w(.025),w(.03)],wobble=.4)
shoe(150,800,0.95,0.95,False)   # far shoe, tucked behind/left
shoe(258,792,1.2,1.2)

# ---------------- torso: smooth hunched hoodie-like shirt, no stripes
back=[(222,352),(165,342),(122,362),(94,420),(76,500),(64,570),(62,612)]
pen.fill([(222,352),(165,342),(122,362),(94,420),(76,500),(64,570),(62,612),(120,616),(200,612),(250,590),(300,535),(340,490),(320,440),(270,400)],255,wobble=0)
pen.stroke(back,[w(.03),w(.06),w(.08),w(.08),w(.07),w(.06),w(.05)],wobble=1.4)
# hood / collar fold behind the neck
pen.stroke([(225,352),(212,385),(214,420),(240,448),(285,468)],[w(.05),w(.06),w(.06),w(.05),w(.035)])
pen.stroke([(190,356),(178,385),(190,415),(222,436)],[w(.03),w(.045),w(.04),w(.025)])
# hem / belt line curved over seat
pen.stroke([(62,608),(120,616),(190,614),(245,598)],[w(.05),w(.06),w(.06),w(.045)],wobble=1.2)
# a few folds on the back
pen.stroke([(105,470),(130,500),(125,540)],[w(.02),w(.03),w(.02)],wobble=.8)
pen.stroke([(140,560),(165,585),(200,598)],[w(.02),w(.03),w(.02)],wobble=.8)

# ---------------- far arm hanging to the knee: forearm + spread hand on thigh
# forearm from under the belly
inked([('c',(184,548),(206,610),19),('c',(190,560),(210,612),14)],w(.04))
# hand lying on thigh fingers right
hx,hy=212,622
hand=[('e',(hx,hy),30,19),
      ('c',(hx+16,hy-10),(hx+58,hy-6),6.5),
      ('c',(hx+18,hy-1),(hx+64,hy+6),6.5),
      ('c',(hx+16,hy+8),(hx+58,hy+19),6.2),
      ('c',(hx+10,hy+14),(hx+44,hy+30),5.5),
      ('c',(hx-12,hy-14),(hx+16,hy-26),6)]   # thumb up/back
inked(hand,w(.035))

# ---------------- near upper arm: sleeve shoulder -> elbow
sleeve=[(150,372),(212,396),(280,440),(345,484),(372,538),(340,572),(290,556),(235,528),(170,490),(118,440),(112,410)]
pen.fill(sleeve,255,wobble=1)
pen.stroke([(150,366),(212,392),(282,438),(346,482)],[w(.05),w(.055),w(.05),w(.05)])
pen.stroke([(108,415),(118,446),(172,494),(236,531),(292,560),(338,575)],[w(.04),w(.07),w(.07),w(.06),w(.06),w(.05)])
# plain straight hem, no cuff
pen.stroke([(346,482),(362,512),(372,538)],[w(.05),w(.05),w(.05)])
pen.stroke([(372,538),(340,575)],[w(.05),w(.05)])
# elbow folds
for a,b,c in [((300,500),(320,520),(318,548)),((270,486),(290,508),(292,532)),((225,430),(250,455),(262,480))]:
    pen.stroke([a,b,c],[w(.015),w(.03),w(.015)],wobble=.8)

# ---------------- forearm (bare) elbow -> wrist, raised
fore=[('p',[(340,512),(372,545),(412,500),(392,468)]),('c',(356,528),(402,484),15)]
inked(fore,w(.045))
# ---------------- open raised hand, palm toward face, fingers up
hx,hy=410,452
palm=[('e',(hx,hy),26,24)]
fingers=[('c',(hx-12,hy-14),(hx-20,hy-62),7),   # index
         ('c',(hx-2,hy-18),(hx-4,hy-72),7),     # middle
         ('c',(hx+10,hy-16),(hx+16,hy-66),6.5), # ring
         ('c',(hx+19,hy-8),(hx+36,hy-50),5.5),  # little
         ('c',(hx-20,hy+4),(hx-40,hy-22),7)]    # thumb out toward face
inked(palm+fingers,w(.03))
# finger divisions a little thicker at the bases
pen.stroke([(hx-8,hy-12),(hx-12,hy-36)],[w(.02),w(.015)])

task.save(pen.mask(),OUT)
