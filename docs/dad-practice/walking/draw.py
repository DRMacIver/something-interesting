import sys
TOOLS='/Users/drmaciver/Projects/calvins-dad/tools/extensions'
sys.path[:0]=[TOOLS+'/reconstruction-v2', TOOLS+'/poses']
import numpy as np
import practice, ink
TASKS='/private/tmp/claude-501/-Users-drmaciver-Projects-calvins-dad/c2d6deef-f737-41b5-92c4-cdb6d89b6f8e/scratchpad/poses'
OUT='.'
task=practice.Task(TASKS,'walking')
pen=ink.Ink(task.size, seed=5)
T=6.5; H=12.0; t=4.5   # outline, heavy, thin

def S(pts,w,**k): return pen.stroke(pts,w if isinstance(w,list) else [w,w],**k)
def W(pts,**k): return pen.fill(pts,colour=255,**k)

# ---------- trousers: one black silhouette ----------
# far leg, trailing, cuff crumpled at the ankle
pen.fill([(452,520),(520,540),(512,640),(468,760),(452,880),(452,940),(398,946),(384,925),(398,830),(412,700),(425,590)],wobble=1.5)
# near leg, baggy, swinging forward
pen.fill([(440,520),(560,520),(618,590),(655,720),(690,860),(688,925),(676,946),(622,940),(598,880),(545,775),(500,690),(440,640)],wobble=1.5)
# rounded knee of the near leg
pen.fill([(540,742),(585,715),(640,730),(656,790),(632,835),(578,830)],wobble=1.2)
# few short white folds
S([(566,752),(592,742),(618,752)],[t*.3,t*.9,t*.3],colour=255)
S([(582,782),(606,792),(630,785)],[t*.3,t*.8,t*.3],colour=255)
S([(540,640),(560,668),(566,700)],[t*.3,t*.7,t*.3],colour=255)
S([(430,700),(440,740),(436,775)],[t*.3,t*.7,t*.3],colour=255)
# crumpled cuffs: white slits
S([(650,905),(668,914),(684,908)],[t*.3,t*.9,t*.3],colour=255)
S([(408,915),(426,924),(444,918)],[t*.3,t*.9,t*.3],colour=255)

# ---------- shirt body: back curves smoothly from neck to waist ----------
shirt=[(452,262),(436,310),(424,380),(420,450),(428,520),(444,556),(520,566),(612,556),(620,470),(612,390),(592,312),(566,262)]
W(shirt,wobble=1.0)
# back contour, tapering
S([(456,262),(436,312),(424,380),(421,450),(428,520),(440,556)],[3,T*.9,T*1.1,T*1.1,T,T*.8])
# tucked hem bunching over the belt
S([(440,552),(480,560),(530,565),(580,562),(618,552)],[T,T*1.4,T*1.6,T*1.4,T])
S([(500,548),(512,556),(526,546)],[t*.3,t*.9,t*.3])   # bunched wrinkle
S([(560,545),(572,556),(588,548)],[t*.3,t*.8,t*.3])
# belt
pen.stroke([(444,570),(520,580),(615,570)],[15,16,14],wobble=1)
# belly contour
S([(620,520),(622,470),(614,400),(596,330)],[T*.5,T*.9,T,T*.7])
# collar open at neck (below head) with placket
S([(498,262),(520,282),(548,292),(578,264)],[3,T*.8,T*.8,3])
S([(522,280),(538,314),(552,300)],[t*.4,t*.6,t*.3])
S([(566,300),(576,380),(582,470),(584,545)],[t*.3,t*.55,t*.5,t*.3])

# ---------- near arm: short sleeve, thin forearm tube, small curled hand ----------
# forearm (bare), thin tube angled forward from the sleeve hem to the wrist
W([(515,410),(548,400),(584,402),(596,470),(600,520),(572,524),(556,470)],wobble=.8)
S([(524,414),(548,468),(572,524)],[T*.7,T*.9,T*.9])       # back edge
S([(588,402),(598,462),(602,520)],[T*.7,T,T*.8])          # front edge
# sleeve: narrow, ends with straight hem and a thin band
sl=[(468,296),(512,272),(582,286),(606,330),(606,398),(506,424),(480,360)]
W(sl,wobble=.8)
S([(470,300),(480,360),(506,424)],[T*.5,T,T])
S([(588,290),(603,335),(606,400)],[T*.6,T,T*.8])
S([(506,424),(556,414),(606,399)],[T*1.2,T*1.2,T*1.1])    # straight hem
S([(510,438),(556,428),(602,414)],[t*.3,t*.5,t*.3])      # thin band
S([(500,300),(522,350),(534,408)],[t*.3,t*.6,t*.3])      # fold
# hand: wrist cuff-line, palm, four curled fingers + attached thumb (white, thin ink)
S([(560,526),(584,532),(606,526)],[t*.5,t*.8,t*.5])
W([(562,530),(602,528),(624,548),(634,580),(630,606),(612,612),(598,600),(580,606),(566,580),(558,552)],wobble=.6)
S([(562,530),(558,556),(568,584),(582,606)],[t*.8,T*.9,T*.8,t*.5])       # near (thumb) side
S([(602,528),(624,548),(634,580),(630,606)],[T*.8,T,T,t*.6])
S([(582,606),(598,600),(612,612),(630,606)],[t*.8,t*.9,t*.9,t*.7])
for x0 in (584,600,616):                                        # finger separations
    S([(x0,552),(x0+6,576),(x0+6,602)],[t*.3,t*.7,t*.3])
S([(566,536),(580,552),(592,562)],[t*.3,t*.6,t*.3])             # thumb crease

# ---------- shoes: low, thin sole line, tongue + laces, pointed toe ----------
def sneaker(upper, sole, toecap, laces, tongue):
    W(upper,wobble=.6)
    S(upper,[T*.9],closed=True)
    S(sole,[H*.8,H,H*.9,H*.6])
    S(toecap,[t*.4,t*.8,t*.4])
    for a,b in laces: S([a,b],[t*.6,t*.6])
    S(tongue,[t*.3,t*.7,t*.3])
# near: heel down, toe tipped up, slim and angular
sneaker(
 [(640,952),(658,938),(690,936),(716,924),(748,902),(780,886),(786,896),(776,912),(742,938),(700,960),(652,972),(638,966)],
 [(638,970),(690,974),(742,950),(782,906)],
 [(744,908),(756,924),(742,938)],
 [((692,930),(704,944)),((708,920),(720,934)),((724,910),(736,924))],
 [(662,936),(682,924),(716,918)])
# far: trailing, nearly flat, pointed toe left
sneaker(
 [(456,950),(440,942),(400,950),(352,972),(350,982),(366,988),(440,988),(488,982),(498,964)],
 [(358,988),(420,993),(470,990),(498,976)],
 [(386,956),(380,972),(386,986)],
 [((424,950),(436,962)),((408,953),(420,965)),((394,957),(406,969))],
 [(452,946),(432,940),(406,948)])
task.save(pen.mask(),OUT)
