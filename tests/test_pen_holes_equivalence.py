"""Cropped holes retain the frozen algorithm's exact topology decisions."""
import numpy as np
from test_pen_translation_cache import oldpen,newpen,oldcompute,newcompute

def test_empty_and_nonbool_inputs_preserve_original_semantics():
 for mask in [np.zeros((0,0),bool),np.zeros((8,8),bool),np.ones((8,8),np.uint8),np.eye(8,dtype=np.int64),np.zeros((3,3,3),bool)]:
  assert newpen.holes(mask)==oldpen.holes(mask)


def test_exhaustive_random_and_edge_masks():
 rng=np.random.default_rng(129)
 for shape in [(1,1),(1,8),(2,4),(3,3),(4,4)]:
  for bits in range(1<<(shape[0]*shape[1])):
   mask=np.array([(bits>>i)&1 for i in range(shape[0]*shape[1])],dtype=bool).reshape(shape)
   assert newpen.holes(mask)==oldpen.holes(mask)
 for _ in range(2000):
  shape=tuple(rng.integers(1,65,size=2));mask=rng.random(shape)<rng.uniform(.01,.99)
  assert newpen.holes(mask)==oldpen.holes(mask)
 for n in [8,32,128]:
  for pad in [0,1,2]:
   mask=np.zeros((n,n),bool);mask[pad:n-pad or None,pad:n-pad or None]=True
   if n-2*pad>4:mask[pad+1:n-pad-1,pad+1:n-pad-1]=False
   assert newpen.holes(mask)==oldpen.holes(mask)
   mask[pad,n//2]=False;assert newpen.holes(mask)==oldpen.holes(mask)


def test_two_independent_cache_disabled_actual_prepares_exact(monkeypatch):
 import emoji_svg_recipe as recipe
 from emoji_other_objects_svg import prepare
 monkeypatch.setenv('DAD_DISABLE_PEN_CACHE','1')
 monkeypatch.setattr(recipe,'translate',oldcompute);a,ar=prepare('1f6ac')
 monkeypatch.setattr(recipe,'translate',newcompute);b,br=prepare('1f6ac')
 assert len(a)==len(b) and all(np.array_equal(x,y) for x,y in zip(a,b)) and ar==br


def test_array_subclasses_stay_on_original_full_frame_path(monkeypatch):
 class CustomArray(np.ndarray):pass
 mask=np.zeros((24,24),bool);mask[8:16,8:16]=True;mask[10:14,10:14]=False
 custom=mask.view(CustomArray)
 calls=[];fill=newpen.ndi.binary_fill_holes
 def observed(value):
  calls.append(value.shape);return fill(value)
 monkeypatch.setattr(newpen.ndi,'binary_fill_holes',observed)
 assert newpen.holes(custom)==oldpen.holes(custom)
 assert calls==[(24,24),(24,24)]
