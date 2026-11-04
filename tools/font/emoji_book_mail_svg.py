"""Registered book/mail recipes matching the reviewed candidate font."""
from pathlib import Path
from emoji_svg_recipe import prepare_recipe,raster
ROOT=Path(__file__).resolve().parents[2]
# (native shape count, outlined paper paths, solid ink paths, unoutlined
# white cutouts, colour paths). Shading/highlight paths are omitted.
RECIPES={
 '1f4d4':(11,[2,8],[5],[],{0:'brown',3:'brown',4:'brown'}),
 '1f4d5':(8,[2],[5],[],{0:'red',3:'red',4:'red'}),
 '1f4d7':(8,[2],[5],[],{0:'green',3:'green',4:'green'}),
 '1f4d8':(8,[2],[5],[],{0:'blue',3:'blue',4:'blue'}),
 '1f4d9':(8,[2],[5],[],{0:'orange',3:'orange',4:'orange'}),
 '1f4eb':(16,[9],[4],[],{0:'brown',2:'blue',6:'red',12:'blue'}),
 '1f4ea':(16,[9],[4],[],{0:'brown',2:'blue',6:'red',12:'blue'}),
 '1f4ec':(16,[3,11],[2,6,13],[],{0:'brown',4:'blue',8:'red'}),
 '1f4ed':(13,[9],[3,11],[],{0:'brown',2:'blue',6:'red',12:'blue'}),
 '2709':(3,[0],[1],[],{}),
 '1f4e7':(6,[0],[1,2,5],[],{}),
 '1f4e8':(7,[0],[1],[],{}),
 '1f4e9':(4,[1],[3],[],{0:'red'}),
 '1f4e4':(5,[1,2],[0],[],{4:'red'}),
 '1f4e5':(5,[1,2],[0],[],{4:'red'}),
 '1f4ee':(14,[7],[6,9],[],{1:'grey',3:'red'}),
 '1f5f3':(11,[6],[3],[],{0:'blue',1:'blue',2:'blue'}),
 '1f4e6':(158,[58,59],[49,50,51,52,53,54,55,56,57],[],{46:'brown',47:'brown',48:'brown'}),
 '1f4c3':(7,[0],[6],[],{}),
 '1f4c4':(7,[0],[6],[],{}),
 '1f4d1':(19,[0,2,8],[],[],{3:'yellow',5:'blue',15:'red',16:'green'}),
 '1f3f7':(8,[0],[5,6],[],{}),
 '1f4d2':(30,[2],[6,7,10,11,14,15,18,19,22,23,26,27],[],{0:'yellow',3:'yellow',4:'yellow'}),
 '1f4da':(26,[1,2,12,14,19,20],[5,7,8,17,23],[],{0:'blue',3:'blue',4:'blue',9:'red',10:'red',11:'red',18:'green',21:'green',22:'green'}),
 '1f516':(12,[],[0,4,7],[],{6:'red',10:'white'}),
 '1f4dc':(29,[0,1,2,17,23],[18,19,24,25],[],{}),
 '1f4d6':(51,[7,8,9,10,11,12],[4,50,*range(14,50)],[],{0:'blue',1:'blue',2:'blue',3:'blue'}),
 '1f4d3':(111,[0,2,3],[4,5],list(range(8,111)),{}),
 '1f4f0':(47,[0,3,23,38],[18,19,20,22,*range(24,38)],[],{}),
 '1f5de':(30,[0,2,5,8,20],[1,3,6,7,9,*range(10,20),*range(21,28)],[],{28:'brown'}),
}
STROKE_PATHS={'1f4ec':{14,15},'1f4e8':{3,4,5,6},'1f4c3':{1,2,3,4,5},'1f4c4':{1,2,3,4,5},'1f4d1':{10,11,12,13,14},'1f4da':{6,13,15,16,24,25},'1f4dc':set(range(5,16))}
STROKE_PATHS.update({'1f4d6':{5,6},'1f4f0':{*range(4,18),*range(39,46)}})
LETTER_PATHS={'1f4e7':([5],'E')}

# Source-specific antialias slivers, inspected in native coordinates:
# open mailbox frame overlaps; stacked covers meet at (70,79.75).
PINHOLE_LIMITS={'1f4ec':(32,64),'1f4da':(8,16)}
# Rolled sheet: seven detached pixels at (23.7,55.6)/(117.8,100.4).
CRUMB_LIMITS={'1f4e6':4,'1f5de':8}


def prepare(key):
 return prepare_recipe(ROOT,key,'data/font-sources/noto-emoji-book-mail-svg.json',
                       RECIPES,STROKE_PATHS,LETTER_PATHS,PINHOLE_LIMITS,CRUMB_LIMITS,
                       Path(__file__))
