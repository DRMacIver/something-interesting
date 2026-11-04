"""Registered places-weather recipes matching reviewed isolated fonts."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
RECIPES={
 '1f9f1':(49,[],[],[],{i:'red' if i%3 else 'brown' for i in range(25,49)}),
 '1faa8':(7,[],[1,4,6],[],{0:'grey',2:'white',3:'white',5:'white'}),
 '1fab5':(14,[],[0,3,4,6,7,9,11,12,13],[],{1:'brown',8:'yellow'}),
 '26fa':(7,[],[0,4,5,6],[],{1:'orange',2:'red',3:'brown'}),
 '1f488':(15,[0],[8,9,11],[],{1:'red',2:'blue',3:'red',4:'grey',5:'grey',6:'grey',7:'grey'}),
 '1f321':(10,[0],list(range(5,10)),[],{3:'red'}),
 '1fa90':(12,[],[],[],{0:'yellow',2:'green',3:'white',4:'white',5:'orange',8:'blue'}),
 '1f308':(6,[],[],[],{0:'red',1:'orange',2:'yellow',3:'green',4:'blue',5:'purple'}),
}
STROKE_PATHS={}
# One detached scan pixel at native(81.5,99.92), beside a bark mark.
CRUMB_LIMITS={'1fab5':1}


def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-places-weather-svg.json',RECIPES,STROKE_PATHS,{},{},CRUMB_LIMITS,Path(__file__))


