"""Registered road-infrastructure recipes matching reviewed isolated fonts."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
RECIPES={
 '1f6e3':(30,[24],[5],list(range(6,18)),{0:'light blue',1:'light blue',2:'green',3:'green',4:'green',**{i:'grey' for i in range(18,24)},25:'green',26:'white',27:'white',28:'white',29:'white'}),
 '1f6e4':(30,[],list(range(8,20)),[],{0:'light blue',1:'light blue',**{i:'green' for i in range(2,7)},7:'grey',**{i:'brown' for i in range(20,26)},26:'grey',27:'grey'}),
 '26fd':(16,[3,7],[4,5,6,8,13],[],{0:'grey',2:'red',11:'grey',12:'grey',14:'red'}),
 '1f6a8':(6,[],[],[],{0:'grey',1:'white',2:'red',3:'red',5:'white'}),
 '1f6a5':(10,[],[],[],{0:'grey',1:'red',4:'green',7:'yellow'}),
 '1f6a6':(10,[],[],[],{0:'grey',1:'red',4:'green',7:'yellow'}),
 '1f6d1':(3,[],[],[],{0:'red'}),
 '1f6a7':(56,[],[16,*range(17,23),25,*range(26,32)],[],{
 **{i:'grey' for i in [0,1,2,3,4,23,32,35,38,41,44,47,50,53]},
 **{i:'yellow' for i in [5,6,8,10,11,13,15,24]},7:'orange',12:'orange',9:'white',14:'white'}),
}
STROKE_PATHS={'26fd':{0}}
STROKE_STYLES={'26fd':{0:{'width':6,'colour':'grey'}}}
# Barrier16/25 are clip definitions needed by its diagonal stripes. They do
# not paint directly; keeping them preserves the native rounded panel clips.


def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-road-infrastructure-svg.json',RECIPES,STROKE_PATHS,{},{},{},Path(__file__),stroke_styles=STROKE_STYLES.get(key))


