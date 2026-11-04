"""Registered office-locks recipes matching reviewed isolated fonts."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
RECIPES={
 '1f6ce':(11,[],[2,5,8],[],{0:'brown',1:'brown',3:'yellow',4:'yellow',6:'yellow',7:'yellow'}),
 '1f50f':(24,[],[1,11,15],[],{0:'yellow',5:'yellow',6:'grey',23:'grey',8:'grey',9:'yellow',12:'yellow',20:'yellow'}),
 '1f510':(16,[],[3,12],[],{0:'yellow',7:'yellow',8:'grey',13:'yellow'}),
 '1f4c8':(13,[0],[12],[],{11:'red'}),
 '1f4c9':(13,[0],[12],[],{11:'blue'}),
 '1f4ca':(11,[0],[9,10],[],{6:'green',7:'red',8:'blue'}),
}
STROKE_PATHS={'1f4c8':set(range(1,11)),'1f4c9':set(range(1,11)),'1f4ca':set(range(1,6))}


def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-office-locks-svg.json',RECIPES,STROKE_PATHS,{},{},{},Path(__file__))


