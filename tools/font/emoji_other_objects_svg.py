"""Registered other-objects recipes matching reviewed isolated fonts."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
RECIPES={
 '1f6ac':(18,[1],[16],[],{0:'grey',3:'orange',**{i:'white' for i in range(4,12)},12:'grey',13:'red',14:'red',15:'grey'}),
 '26b0':(18,[],[4,6,7],[],{0:'brown',1:'brown',2:'brown',3:'brown',**{i:'yellow' for i in range(8,14)}}),
 '1faa6':(16,[],list(range(5,13)),[],{0:'grey',1:'white',2:'grey',13:'grey',14:'grey'}),
 '26b1':(11,[],[9],[],{0:'yellow',1:'brown',2:'red',3:'red',4:'red',8:'yellow'}),
 '1f9ff':(7,[2],[4],[],{0:'blue',3:'light blue'}),
 '1faac':(24,[1],[3,18,22],[],{0:'blue',2:'light blue'}),
 '1f5ff':(21,[],[1,6,7,8,10,11],[],{0:'grey',2:'grey',3:'white',4:'grey',5:'white',12:'white'}),
 '1faa7':(8,[5],[],[],{0:'brown',4:'grey'}),
 '1faaa':(9,[1],[4,5,6,7],[],{0:'light blue',2:'blue',3:'blue'}),
}
STROKE_PATHS={}


def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-other-objects-svg.json',RECIPES,STROKE_PATHS,{},{},{},Path(__file__))


