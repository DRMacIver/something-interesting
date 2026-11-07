import random
rg=random.Random(7)
def shape(pts, w=O, fill=255, outline=True):
    pen.fill(pts, fill, wobble=0.8)
    if outline: pen.stroke(pts, [w], closed=True, wobble=0.8)
def taper(pts, w0, w1=None, col=0, mid=None):
    ws=[w0,mid or w0,w1 if w1 is not None else w0]
    pen.stroke(pts, ws, colour=col, wobble=0.5)
def pshape(pts,fill=255,w=O):
    m=poly(pts); pen.paint(m,fill)
    pts2=list(pts)+[pts[0]]
    for a,b in zip(pts2,pts2[1:]): taper([a,b],w)

m=np.zeros((H,W),bool); m[:1099,857:865]=True; m[1093:1099,35:865]=True; m[:57,:]=False
pen.paint(m,0)

# far arm: thin sleeve sliver behind torso, bare forearm vanishing behind hip
shape([(722,292),(765,305),(790,350),(800,420),(796,470),(762,478),(748,440),(738,360)],O)
for a,b in [((752,320),(776,470)),((768,335),(790,462))]:
    taper([a,((a[0]+b[0])/2+2,(a[1]+b[1])/2),b],0.022*Hw,0.015*Hw)
taper([(764,478),(797,470)],0.05*Hw)
shape([(766,478),(790,472),(775,540),(750,585),(730,575),(752,520)],O)

# torso: narrow twisted column
torso=[(580,298),(576,370),(590,450),(596,530),(590,596),(660,602),(750,596),(748,520),(738,440),(742,380),(742,306)]
pen.fill(torso,255,wobble=0.8)
taper([(596,450),(598,530),(592,596)],O)
taper([(742,380),(738,440),(748,520),(752,594)],O)
for x in [610,626,660,676,692,708,724]:
    top=rg.randint(318,345); bot=rg.randint(555,584)
    taper([(x-1,top),(x+rg.uniform(-2,2),(top+bot)/2),(x+rg.uniform(-3,2),bot)],0.03*Hw,0.02*Hw)
# placket, buttons
taper([(642,298),(640,440),(646,590)],T)
for y in (370,450,530):
    pen.fill([(643,y-5),(649,y-5),(649,y+4),(643,y+4)],0,wobble=0.3)
# dark strap on chest
pshape([(684,300),(696,298),(706,440),(714,596),(704,596),(694,440)],0,w=O)
# collar wedge
taper([(600,300),(640,326),(690,300)],0.05*Hw)

# near arm: sleeve hangs straight, narrow; cuff, forearm, hand to pocket
ns=[(578,296),(550,320),(536,380),(532,440),(534,476),(590,478),(608,440),(612,370),(606,320)]
shape(ns,O)
for a,b in [((562,324),(550,470)),((578,330),(566,472)),((594,330),(584,474)),((548,345),(538,462))]:
    taper([a,((a[0]+b[0])/2-2,(a[1]+b[1])/2),b],0.022*Hw,0.014*Hw)
# rolled cuff band
pshape([(534,462),(592,466),(594,486),(536,482)],255,w=0.05*Hw)
taper([(538,474),(592,476)],T)
# forearm bare, tapering to wrist, hand into pocket slit
shape([(540,484),(588,488),(596,540),(604,580),(578,590),(556,552)],O)
taper([(574,500),(582,540)],T)
# hand: four fingers disappear into pocket
shape([(572,582),(606,576),(622,596),(612,612),(578,606)],O)
for x in (590,601,611): taper([(x,590),(x+1,608)],0.022*Hw)

# trousers: one black silhouette, angular and wobbly, waist bunch, wide hem
tr=[(574,588),(580,602),(562,618),(566,650),(556,690),(574,730),(566,780),(582,840),(574,900),(582,960),(568,1010),(572,1034),
    (640,1030),(700,1032),(790,1036),(802,1008),(782,960),(784,900),(776,840),(782,780),(774,720),(792,670),(802,630),(790,604),(772,588),(700,584),(640,592)]
pen.fill(tr,0,wobble=0.6)
# angular notches on edges (white nicks)
for pts in [[(562,642),(570,648),(562,656)],[(558,704),(568,712),(559,720)],[(570,774),(579,782),(569,790)],[(570,852),(580,860),(571,868)],
            [(788,644),(780,650),(789,658)],[(780,804),(788,812),(779,820)]]:
    pen.fill(pts,255,wobble=0.2)
# waist bunch bulge
pen.fill([(574,590),(560,606),(566,626),(600,618)],0,wobble=0.3)
# a few short folds at knee and hip (tiny)
taper([(626,600),(636,622),(630,640)],0.012*Hw,col=255,mid=0.022*Hw)
taper([(640,822),(660,830),(676,828)],0.01*Hw,col=255,mid=0.018*Hw)
# belt: thin white line just under shirt hem
taper([(596,600),(660,604),(740,597)],0.01*Hw,col=255,mid=0.016*Hw)

# far shoe (behind, partly hidden)
fsh=[(722,1020),(752,1014),(780,1026),(798,1044),(794,1062),(766,1070),(722,1068)]
shape(fsh,0.05*Hw)
taper([(752,1030),(768,1042)],T); taper([(738,1026),(754,1038)],T)
taper([(724,1060),(770,1064),(794,1056)],0.05*Hw,0.07*Hw)
# near shoe, toe left, lumpy
nsh=[(562,1060),(566,1038),(590,1026),(630,1022),(680,1018),(718,1020),(736,1036),(738,1060),(718,1076),(650,1084),(584,1080)]
shape(nsh,0.055*Hw)
# dark inner shadow near ankle
pen.fill([(690,1024),(730,1032),(730,1052),(704,1046)],0,wobble=0.3)
# heavy sole stripe
taper([(564,1062),(620,1072),(700,1074),(736,1060)],0.075*Hw,0.085*Hw)
taper([(566,1052),(620,1060),(700,1060)],0.02*Hw)
# toe cap line + tongue + laces
taper([(582,1034),(592,1052),(612,1062)],T)
for a,b in [((610,1030),(628,1046)),((626,1026),(644,1042)),((642,1022),(660,1038)),((658,1020),(676,1036))]:
    taper([a,b],0.028*Hw,0.02*Hw)
taper([(636,1038),(670,1034),(700,1034)],0.02*Hw)
# trouser hem drapes over the shoe: ragged black
pen.fill([(560,1010),(600,1022),(660,1026),(720,1022),(748,1024),(742,1000),(580,996)],0,wobble=0.8)
taper([(580,1024),(640,1032),(720,1030)],0.03*Hw,col=0)
