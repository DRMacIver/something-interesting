"""Translate the remaining ten licensed ground-vehicle drawings."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
RECIPES={
 '1f68d':(21,[19,20],[0,1,4,5,11,12,13],[],{2:'grey',3:'grey',6:'yellow',7:'yellow',8:'red',9:'grey',10:'grey',14:'light blue',15:'light blue',16:'light blue',17:'blue',18:'yellow'}),
 '1f691':(19,[0],[1,2,3,5,17],[],{4:'grey',6:'grey',7:'red',8:'yellow',9:'grey',10:'red',11:'red',14:'blue',15:'blue',16:'blue',18:'light blue'}),
 '1f694':(19,[15],[0,1,2,3,4,6,9,10,11,16],[],{5:'grey',7:'yellow',8:'yellow',12:'grey',13:'blue',14:'red',17:'light blue',18:'light blue'}),
 '1f698':(16,[10,12],[0,1,7,13],[],{2:'red',3:'red',4:'red',5:'red',6:'red',9:'yellow',11:'yellow',14:'light blue',15:'blue'}),
 '1f6fb':(18,[12],[2,3,4,10,11,14],[],{0:'red',1:'red',5:'grey',6:'grey',7:'grey',8:'grey',9:'red',13:'grey',15:'light blue',16:'red',17:'red'}),
 '1f3ce':(18,[],[12,15],[],{**{i:'red' for i in [0,1,2,3,4,5,9,11]},**{i:'grey' for i in [6,7,8,10,14,17]},13:'orange',16:'orange'}),
 '1f3cd':(23,[13],[1,2,6,7,10,14,16,21,22],[],{**{i:'red' for i in [4,9,17,18,19]},**{i:'grey' for i in [0,3,5,8,12,15,20]},11:'light blue'}),
 '1f6b2':(39,[],[*range(0,14),*range(15,27),30,31,33,34],[],{14:'grey',27:'grey',28:'grey',29:'grey',32:'blue',35:'grey',36:'grey',37:'grey',38:'grey'}),
 '1f6f9':(22,[],[13],[],{0:'grey',1:'grey',**{i:'red' for i in range(2,12)},12:'brown',**{i:'grey' for i in range(14,22)}}),
 '1f6fc':(27,[2,3,4,5,6],[16,19,23,24,25,26],[],{0:'blue',**{i:'yellow' for i in range(7,14)},14:'red',15:'green',17:'yellow',18:'orange',20:'grey',21:'yellow',22:'orange'}),
}
STROKE_PATHS={'1f68d':{18},'1f6f9':{0,1},'1f6fc':set(range(7,13))}
STROKE_STYLES={
 '1f68d':{18:{'width':2.545,'colour':'yellow'}},
 '1f6f9':{i:{'width':8,'colour':'grey'} for i in [0,1]},
 '1f6fc':{i:{'width':3,'colour':'yellow'} for i in range(7,13)},
}
PINHOLE_LIMITS={}
CRUMB_LIMITS={}

def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-ground-vehicles-svg.json',RECIPES,STROKE_PATHS,{},PINHOLE_LIMITS,CRUMB_LIMITS,Path(__file__),stroke_styles=STROKE_STYLES.get(key))

