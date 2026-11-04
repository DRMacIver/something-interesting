"""Registered tools-instruments recipes matching reviewed isolated fonts."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
RECIPES={
 '1f5e1':(21,[3],[2,8,9,10,11],[],{0:'yellow',1:'brown',4:'yellow',6:'blue'}),
 '2694':(46,[1,10],[0,9,4,5,6,17,18,19],[],{2:'brown',3:'brown',7:'yellow',8:'yellow',11:'brown',12:'brown',13:'yellow',14:'yellow'}),
 '1f4a3':(11,[],[2,4,8],[5],{1:'yellow',3:'grey',9:'brown'}),
 '1fa83':(10,[0],[],[],{3:'brown',4:'yellow',5:'yellow',7:'yellow',8:'yellow'}),
 '1f3f9':(9,[],[3,4,5,6],[],{0:'brown',1:'brown',7:'red',8:'red'}),
 '1f6e1':(51,[],[],[],{0:'grey',1:'grey',2:'blue',3:'white',4:'grey',**{i:'white' for i in [*range(5,17),*range(29,40)]}}),
 '1fa97':(45,[1,18,19,*range(33,45)],[*range(10,15),17,*range(20,30)],[],{15:'red',16:'red',30:'red',31:'red',32:'red'}),
 '1fa95':(32,[16],[2,5,9,10,11,12,13,22],[],{0:'grey',1:'grey',3:'grey',4:'grey',6:'brown',8:'brown',14:'yellow',15:'grey',**{i:'white' for i in [18,19,20,21,23,24,25,26]},27:'brown'}),
 '1fa98':(35,[19],[9,10,12,13,15,16,22,25,26,27,30,31,32,33,34],[],{0:'brown',1:'brown',8:'yellow',17:'yellow',18:'brown',**{i:'white' for i in [2,3,4,5,6,7,11,14,21,23,24,28,29]}}),
 '1fa87':(37,[],[8,9,10,22,23,24,30,31,32,33,36],[],{0:'brown',1:'brown',2:'brown',3:'green',4:'brown',5:'yellow',7:'yellow',16:'brown',17:'green',18:'brown',19:'yellow',21:'yellow'}),
 '1fa88':(21,[],[3,4,6,8,10,12,14,16],[],{0:'yellow',1:'brown',2:'yellow',18:'brown'}),
}
STROKE_PATHS={'1fa95':{18,19,20,21,23,24,25,26,27},
              '1fa98':{2,3,4,5,6,7,11,14,18,21,23,24,28,29}}
# Bounded raster slivers: banjo250pixels, all outside native white strings;
# drum68pixels at head-rim/cord overlaps (one antialias pixel at a cord tip).
PINHOLE_LIMITS={'1fa95':(8,256),'1fa98':(8,80)}
STROKE_STYLES={'1fa95':{**{i:{'width':.5,'colour':'white'} for i in [18,19,20,21,23,24,25,26]},27:{'width':2.6114,'colour':'brown'}}}
# Path20 contains only a move command and paints nothing in the donor.
STROKE_STYLES['1fa98']={**{i:{'width':1.1,'colour':'white'} for i in range(2,8)},
                       **{i:{'width':1.7,'colour':'white'} for i in [11,14,23,24,28,29]},
                       18:{'width':2.3,'colour':'brown'},21:{'width':2.3,'colour':'white'}}


def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-tools-instruments-svg.json',
                       RECIPES,STROKE_PATHS,{},PINHOLE_LIMITS,{'1fa98':4},Path(__file__),
                       stroke_styles=STROKE_STYLES.get(key),
                       boundary_blur=.2 if key in {'1fa95','1fa98'} else .45)


