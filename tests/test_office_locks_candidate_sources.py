"""Preserve chart direction, independent bars and functional lock details."""
import json,sys
from functools import lru_cache
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import pytest
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from prototype_office_locks import prepare
from emoji_svg_recipe import raster
STRUCTURE={e['key']:e for e in json.loads((ROOT/'output/font-review/pen-translation/remaining-objects-source-structure.json').read_text())}


@lru_cache(maxsize=8)
def candidate(key):return prepare(key)


def native_shape(key,index,stroke=False):
 root=ET.fromstring((ROOT/STRUCTURE[key]['source']['path']).read_bytes());parents={c:p for p in root.iter() for c in p}
 shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','circle','ellipse','polygon','rect','line','polyline'}]
 for i,e in enumerate(shapes):
  if i!=index:parents[e].remove(e)
  else:
   e.attrib.pop('style',None);e.set('fill','none' if stroke else '#111111');e.set('stroke','#111111' if stroke else 'none')
   if stroke:e.set('stroke-width','2')
 return raster(root)


@pytest.mark.parametrize('key,colour,rising',[('1f4c8','red',True),('1f4c9','blue',False)])
def test_chart_preserves_native_data_direction_and_all_ten_grid_lines(key,colour,rising):
 (_, *materials, ink),r=candidate(key)
 data=materials[r['colourNames'].index(colour)]&~ink
 native=np.pad(native_shape(key,11),r['padding'])
 assert (native&ndi.binary_dilation(data,iterations=12)).sum()/native.sum()>.95
 ys,xs=np.nonzero(data);left=ys[xs<np.quantile(xs,.15)].mean();right=ys[xs>np.quantile(xs,.85)].mean()
 assert (left>right)==rising
 for index in range(1,11):
  line=np.pad(skeletonize(native_shape(key,index,stroke=True)),r['padding'])
  assert (line&ndi.binary_dilation(ink,iterations=6)).sum()/line.sum()>.85,index


def test_bar_chart_retains_three_colours_and_native_height_order():
 (_, *materials, ink),r=candidate('1f4ca');heights={}
 for index,colour in [(6,'green'),(7,'red'),(8,'blue')]:
  paint=materials[r['colourNames'].index(colour)]&~ink
  native=np.pad(native_shape('1f4ca',index),r['padding'])
  assert (native&ndi.binary_dilation(paint,iterations=12)).sum()/native.sum()>.95
  y,x=np.nonzero(paint);heights[colour]=np.ptp(y)
 assert heights['blue']>heights['green']>heights['red']>100


@pytest.mark.parametrize('key,index',[('1f50f',1),('1f510',3)])
def test_both_locks_keep_the_native_black_keyhole(key,index):
 (_, *_, ink),r=candidate(key)
 native=np.pad(native_shape(key,index),r['padding'])
 assert native.sum()>100
 assert (native&ndi.binary_dilation(ink,iterations=6)).sum()/native.sum()>.95


def test_key_ring_keeps_a_real_open_counter():
 (paper,*materials,ink),r=candidate('1f510')
 # Native key-ring centre is an intentional hole, not a painted white decal.
 native=native_shape('1f510',13)
 counter=ndi.binary_fill_holes(native)&~native
 assert counter.sum()>1000
 y,x=np.unravel_index(ndi.distance_transform_edt(counter).argmax(),counter.shape)
 x+=r['padding'];y+=r['padding']
 assert not ink[y-4:y+5,x-4:x+5].any()
 assert not any(mask[y,x] for mask in materials)
