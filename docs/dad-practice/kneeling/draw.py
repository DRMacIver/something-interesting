import sys
TOOLS='/Users/drmaciver/Projects/calvins-dad/tools/extensions'
sys.path[:0]=[TOOLS+'/reconstruction-v2',TOOLS+'/poses']
import numpy as np, practice, ink
TD='/private/tmp/claude-501/-Users-drmaciver-Projects-calvins-dad/c2d6deef-f737-41b5-92c4-cdb6d89b6f8e/scratchpad/poses'
OUT='.'
task=practice.Task(TD,'kneeling')
pen=ink.Ink(task.size,seed=5)
T=12; H=22

def shape(pts,w=T,fill=255,widths=None):
    pen.fill(pts,fill,wobble=0)
    pen.stroke(pts,widths or [w,w*1.5,w,w*0.8,w*1.4,w],closed=True)
def line(pts,w=T*0.8,taper=(0.3,1,0.8,0.25)):
    pen.stroke(pts,[w*t for t in taper])
def fold(pts,w=T):   # thick-to-thin brush fold
    pen.stroke(pts,[w*1.2,w*0.8,w*0.3])

def sole(cx,cy,w,h,ang):
    """Upturned sole seen from behind: tall oval, heel block at top, tread band below."""
    c=np.array([cx,cy],float); a=np.radians(ang)
    R=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
    def P(x,y): return tuple(c+R@np.array([x*w/2,y*h/2]))
    outer=[P(0,-1),P(.62,-.85),P(.95,-.35),P(1,.2),P(.8,.75),P(.35,1),P(-.1,1.0),P(-.7,.82),P(-1,.3),P(-.95,-.3),P(-.6,-.85)]
    shape(outer,H*1.1,widths=[H*1.3,H*1.6,H*1.2,H,H*1.5,H*1.7,H*1.3,H,H*1.2,H*1.5,H*1.4])
    # inner rim (sole thickness)
    pen.stroke([P(-.62,-.62),P(0,-.72),P(.62,-.6),P(.74,0),P(.55,.55),P(.1,.78),P(-.5,.6),P(-.7,.05),P(-.62,-.62)],[T*.5,T*.8,T*.9,T*.6,T*.8,T*.9,T*.6,T*.5,T*.5])
    # heel block
    shape([P(-.5,-.55),P(.5,-.52),P(.52,-.12),P(-.5,-.1)],T*.9,widths=[T,T*1.3,T*.9,T])
    # flat tread band with ticks
    for yy in (.12,.26,.4,.54):
        line([P(-.55,yy),P(0,yy+.04),P(.55,yy)],T*.55,(1,1,1,.8))
    # waist notch between heel and forefoot
    line([P(-.7,-.05),P(-.45,.02)],T*1.2,(1,1,.4,.2))
    line([P(.74,-.02),P(.52,.04)],T*1.2,(1,1,.4,.2))
    return P

# far sole, then near sole, directly behind the calves, under the haunch
sole(1010,1715,190,300,10)
sole(845,1725,200,320,-8)
# ---------- calf along the floor
shape([(240,1560),(430,1555),(640,1560),(740,1580),(752,1650),(740,1735),(640,1745),(430,1745),(280,1740),(200,1690)],T)
# ---------- near shoe
# cuff / bunched cloth at ankle, over the shoe heel
shape([(690,1570),(745,1560),(782,1585),(790,1650),(776,1730),(730,1752),(690,1735),(700,1640)],T,widths=[T,T*1.8,T,T*.8,T*1.4,T])
fold([(705,1600),(730,1630),(722,1690)],T*.8)
fold([(780,1600),(755,1625),(758,1700)],T*.6)
# calf folds
fold([(590,1570),(560,1630),(590,1695)],T*.9)
fold([(480,1590),(455,1650),(480,1700)],T*.6)
# ---------- thigh: belt to knee, round seat
thigh=[(1110,1215),(1118,1330),(1108,1450),(1050,1535),(960,1580),(860,1590),(700,1565),(520,1530),(380,1520),(260,1500),(200,1570),(220,1640),(290,1650),(260,1560)]
thigh=[(1105,1220),(1120,1340),(1100,1470),(1030,1550),(900,1590),(760,1585),(600,1620),(420,1640),(280,1660),(200,1610),(215,1530),(320,1470),(500,1400),(680,1350),(860,1320),(1000,1290)]
shape(thigh,T,widths=[T,T*1.4,T*1.1,T*.8,T*1.5,T*1.1,T])
# knee crook folds fanning from the kneecap
fold([(250,1580),(330,1545),(430,1545)],T*1.1)
fold([(235,1630),(320,1620),(400,1600)],T*.8)
fold([(300,1500),(380,1480),(430,1500)],T*.7)
# crease where thigh lies over calf
line([(420,1640),(600,1625),(740,1590)],T*.7)
# back pocket and seat
line([(930,1340),(1060,1318)],T*.8)
line([(1060,1318),(1068,1400),(1000,1450),(935,1400),(930,1340)],T*.8)
line([(945,1352),(1050,1334)],T*.35)
fold([(900,1500),(960,1470),(1050,1500)],T*.9)   # seat/heel crease
fold([(820,1400),(760,1450),(770,1520)],T*.8)
fold([(700,1420),(760,1460),(790,1520)],T*1.1)
fold([(560,1470),(620,1500),(660,1545)],T*.9)
fold([(980,1400),(940,1440),(960,1500)],T*.8)
fold([(850,1450),(900,1490),(890,1545)],T*.8)
# ---------- belt band
shape([(1100,1175),(1110,1225),(1000,1295),(860,1328),(700,1346),(610,1340),(610,1290),(700,1300),(860,1285),(990,1248)],T*.8)
for bx,by in ((1010,1252),(880,1292),(760,1312)):
    line([(bx,by-20),(bx-4,by+14)],T*.6,(1,1,1,1))
# ---------- shirt body, tucked to belt
shape([(470,700),(620,715),(780,760),(900,850),(1010,990),(1085,1110),(1100,1185),(990,1250),(860,1285),(700,1305),(560,1310),(470,1290),(380,1150),(335,1010),(400,860)],T*1.1)
line([(420,720),(520,730),(600,790)],T*0.7)
# shirt back creases, brush weight
fold([(930,970),(985,1040),(1020,1110)],T*1.1)
fold([(640,930),(690,1010),(700,1080)],T*.8)
fold([(980,1200),(940,1235),(880,1252)],T*.8)   # tuck pull at belt
# ---------- sleeve: short, loose, scalloped hem
sl=[(425,880),(520,792),(620,820),(682,950),(700,1085),(690,1165),(655,1185),(620,1170),(585,1192),(545,1172),(505,1196),(465,1180),(425,1200),(385,1060)]
pen.fill(sl,255,wobble=0)
pen.stroke(sl[:6],[T,T*1.6,T,T*.9,T*1.5,T],closed=False)
pen.stroke([sl[0],sl[-1],sl[-2],sl[-3],sl[-4]],[T,T*1.3,T,T*.9,T])
# scalloped hem: heavy bumps
line([(690,1165),(655,1190),(620,1172),(585,1196),(545,1175),(505,1199),(465,1183),(425,1204)],T*1.5,(1,1.3,.9,1.3,.9,1.3,.9,1))
# many fold lines, swelling then pinching
fold([(470,960),(540,940),(610,990)],T*1.3)
fold([(430,1060),(500,1045),(580,1070),(640,1130)],T*1.1)
fold([(560,870),(615,900),(645,955)],T*.9)
fold([(660,1010),(630,1060),(640,1110)],T*.8)
fold([(450,1110),(500,1120),(540,1150)],T*.8)
fold([(405,980),(430,940)],T*.7)
fold([(520,1000),(560,1030),(545,1070)],T*.6)
fold([(560,1165),(540,1135),(500,1135)],T*.7)   # elbow pull
# ---------- forearm, bent: elbow tucked in, angled down to the wrist
shape([(600,1180),(540,1195),(430,1235),(345,1275),(300,1300),(285,1345),(340,1352),(440,1315),(540,1262),(610,1215)],T,widths=[T,T*1.4,T*.9,T,T*1.3,T])
line([(520,1245),(430,1290),(350,1325)],T*.45)
line([(560,1200),(520,1215),(520,1240)],T*.5)
# sleeve hem overlaps the arm
line([(640,1182),(600,1195),(560,1182)],T*1.1,(1,1.2,.8))
# ---------- hand, resting on the floor, gripping: thumb on top, four finger bumps
hand=[(310,1296),(262,1292),(215,1298),(170,1318),(130,1345),(110,1385),(128,1418),(165,1430),(205,1424),(240,1432),(285,1425),(322,1385),(335,1345)]
shape(hand,T,widths=[T,T*1.3,T,T*.9,T*1.2,T*1.4,T])
# distinct thumb along the top, tip pointing toward the fingers
shape([(318,1290),(270,1272),(215,1280),(188,1300),(225,1306),(275,1310),(320,1318)],T*.9,widths=[T,T*1.2,T*.9,T,T*.8,T])
# four finger bumps curling down on the left/bottom edge
for (x0,y0,x1,y1) in ((200,1318,170,1345),(235,1345,185,1375),(270,1372,205,1400),(295,1400,230,1422)):
    line([(x0,y0),((x0+x1)/2-8,(y0+y1)/2+6),(x1,y1)],T*.7,(1,1,.9,.4))
line([(330,1340),(300,1365),(300,1400)],T*.5)   # wrist crease
# ---------- floor line under everything
line([(300,1758),(520,1766),(740,1760)],T)
line([(780,1850),(900,1858),(1000,1850)],T*.7)
task.save(pen.mask(),OUT)
