"""Registered money source recipes matching reviewed isolated fonts."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
RECIPES={
 '1fa99':(66,[50,53,*range(54,66)],[*range(16,24),28,29],[],{0:'yellow',13:'yellow',51:'yellow'}),
 '1f4b0':(129,[],[11,13],[],{7:'yellow',10:'yellow'}),
 '1f4b4':(7,[4],[],[],{0:'orange',1:'orange',2:'orange',5:'white'}),
 '1f4b5':(121,[6],[],[],{0:'green',1:'green',4:'green',2:'white'}),
 '1f4b6':(120,[4],[],[],{0:'blue',1:'blue',2:'blue',6:'white'}),
 '1f4b7':(120,[4],[],[],{0:'purple',1:'purple',3:'purple',6:'white'}),
 '1f4b8':(17,[0,11,13],[1,2,14,15],[],{4:'green',7:'green',8:'green',16:'green',5:'white',6:'white'}),
 '1f4b3':(4,[2],[1],[],{0:'yellow'}),
 '1f9fe':(14,[0],[1,13],[],{}),
 '1f4b9':(6,[],[],[],{0:'green',1:'green',4:'white',2:'white'}),
}
STROKE_PATHS={'1f4b4':{3},'1f4b5':{5},'1f4b6':{3},'1f4b7':{2},
              '1f4b8':{10},'1f4b3':{3},'1f4b9':{2},'1f9fe':set(range(2,13))}
LETTER_PATHS={'1f4b0':([11],'$'),'1f4b5':([2],'$')}
# Eighteen one/two-pixel slivers at coin star/rim overlaps, inspected at
# native(26.5,24)/(101.5,24) and around(60,105.3), not temple counters.
PINHOLE_LIMITS={'1fa99':(4,24)}
# Seven detached antialias pixels at the inspected feather tips.
CRUMB_LIMITS={'1f4b8':8}


def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-money-svg.json',
                       RECIPES,STROKE_PATHS,LETTER_PATHS,PINHOLE_LIMITS,CRUMB_LIMITS,Path(__file__),
                       stroke_styles={2:{'width':5,'colour':'white'}} if key=='1f4b9' else None)


