"""Registered globes recipes matching reviewed isolated fonts."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
RECIPES={
 '1f30d':(12,[],[],[],{0:'blue',1:'green',2:'green',3:'green',4:'green',5:'white',6:'green',10:'blue',11:'blue'}),
 '1f30e':(8,[],[],[],{0:'blue',1:'white',2:'green',3:'green',7:'blue'}),
 '1f30f':(18,[],[],[],{0:'blue',1:'blue',2:'green',4:'blue',**{i:'green' for i in range(5,17)}}),
}
STROKE_PATHS={}


def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-globes-svg.json',RECIPES,STROKE_PATHS,{},{},{},Path(__file__))


