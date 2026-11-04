"""Registered clothing source recipes matching reviewed isolated fonts."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
RECIPES={
 '1f453':(5,[0,1],[2],[],{}),
 '1f576':(5,[],[0,1],[],{2:'grey'}),
 '1faad':(14,[],[3,*range(5,11),13],[],{0:'brown',2:'brown',4:'red',11:'brown'}),
 '1f6cd':(19,[],[3,4,13,18],[],{1:'green',2:'green',9:'green',11:'pink',12:'pink'}),
 '1faae':(5,[],[0,1,3],[],{}),
 '1f4ff':(89,[],[78,86],[],{**{i:'brown' for i in [*range(0,78,3),79]},82:'yellow'}),
 '1f484':(12,[],[8,9,10],[],{0:'red',1:'red',3:'yellow'}),
 '1f48d':(17,[],[15],[],{1:'grey',2:'blue',3:'blue',4:'white',5:'blue',6:'blue',7:'white',8:'blue',9:'blue',10:'blue',11:'blue',12:'white'}),
 '1f48e':(11,[],[],[],{0:'white',1:'blue',2:'blue',3:'blue',4:'blue',5:'white',6:'white',7:'blue',8:'blue',9:'blue',10:'white'}),
}
STROKE_PATHS={'1f6cd':{0,6,10,17},'1f4ff':{83,84}}
# One isolated antialias pixel at the bead/cord overlap (82.58,98.08).
CRUMB_LIMITS={'1f4ff':2}


def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-clothing-svg.json',
                       RECIPES,STROKE_PATHS,{}, {},CRUMB_LIMITS,Path(__file__))


