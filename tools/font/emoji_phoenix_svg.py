"""Registered phoenix recipes matching reviewed isolated fonts."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
KEY='1f426_200d_1f525'
RECIPES={KEY:(19,[],[14,15,16,17],[],{
 0:'red',1:'orange',2:'red',3:'orange',4:'orange',5:'red',6:'red',7:'red',
 8:'yellow',9:'orange',10:'orange',11:'orange',12:'orange',13:'yellow',18:'yellow'})}

# Fifty sub-four-pixel scan slivers at overlapping selected native borders.
PINHOLE_LIMITS={KEY:(4,64)}

def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-phoenix-svg.json',RECIPES,{},{},PINHOLE_LIMITS,{},Path(__file__))


