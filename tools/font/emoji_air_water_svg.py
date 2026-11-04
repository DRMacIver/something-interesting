"""Registered air-water recipes matching reviewed isolated fonts."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe
ROOT=Path(__file__).resolve().parents[2]
RECIPES={
 '2708':(30,[21],[10,11,14,15,22,26,27,28,29],[],{0:'blue',1:'blue',16:'blue',17:'blue',**{i:'grey' for i in [2,3,4,5,6,7,8,12,20,23]}}),
 '1f6e9':(22,[6],[0,13,14,15,16,20,21],[],{1:'blue',3:'blue',8:'blue',10:'blue',5:'grey',19:'grey'}),
 '1fa82':(41,[],[0,1,6,7,9,11,12,13,14,15,16,18,19,35,40],[],{2:'yellow',3:'orange',4:'green',5:'green',8:'green',10:'blue',17:'red',20:'yellow',21:'green',22:'green',23:'blue',24:'blue',25:'purple',26:'pink',27:'red',28:'pink',29:'purple',30:'red',31:'blue',32:'green',33:'green',34:'orange',36:'red',37:'red',38:'red',39:'red'}),
 '1f4ba':(17,[14],[],[],{**{i:'grey' for i in [0,1,2,4,5,15,16]},**{i:'blue' for i in [3,6,7,8,9,10,11,12,13]}}),
 '1f6f0':(34,[27],[26,29,33],[],{0:'blue',13:'blue',**{i:'yellow' for i in [7,9,10,11,20,21,22,23,24]},8:'brown',12:'brown',25:'grey',28:'grey'}),
 '1f6f8':(34,[],[12],[],{6:'light blue',7:'grey',8:'grey',9:'grey',11:'grey',13:'light blue',14:'blue',15:'green',16:'white',**{i:'green' for i in [23,25,27,29,32]},**{i:'white' for i in [24,26,28,30,33]}}),
 '2693':(7,[],[],[],{0:'grey'}),
 '1f6f3':(26,[1,8,11,13],[0,2,3,4,5,7,9,10,12,17,18,19,20,21,22,23,24],[],{6:'red',14:'blue',15:'blue',16:'blue'}),
}
# Only the donor's genuinely stroked paths/lines. Parachute cords are filled
# ribbons and remain in the ink selection, preserving their native geometry.
STROKE_PATHS={'1f6f0':{2,3,4,5,6,15,16,17,18,19,30,31,32}}
# Twenty-one <4pixel slivers at canopy/cord joins.
PINHOLE_LIMITS={'1fa82':(4,24)}
# Three isolated scan pixels along the tail/body seam at native(35.6,35).
CRUMB_LIMITS={'1f6e9':3}


def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-air-water-svg.json',RECIPES,STROKE_PATHS,{},PINHOLE_LIMITS,CRUMB_LIMITS,Path(__file__))


