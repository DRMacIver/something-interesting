"""The fuel-hose failure must be rejected before raster or visual acceptance."""
import importlib,json,sys
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
from svg_recipe_checks import selected_strokes
FAMILIES=[('emoji_book_mail_svg','data/font-sources/noto-emoji-book-mail-svg.json'),
          ('emoji_money_svg','data/font-sources/noto-emoji-money-svg.json'),
          ('emoji_clothing_svg','data/font-sources/noto-emoji-clothing-svg.json'),
          *[(name,'docs/remaining-object-emoji-svg-source-probe.json') for name in [
              'prototype_office_locks','prototype_tools_instruments','prototype_places_weather',
              'prototype_other_objects','prototype_globes','prototype_phoenix',
              'prototype_air_water','prototype_road_infrastructure','prototype_ground_vehicles']]]
CASES=[]
for name,manifest in FAMILIES:
    module=importlib.import_module(name)
    files={Path(e['path']).stem.removeprefix('emoji_u'):e for e in json.loads((ROOT/manifest).read_text())['files']}
    for key,recipe in module.RECIPES.items():CASES.append((name,key,recipe,files[key]))


@pytest.mark.parametrize('name,key,recipe,source',CASES,ids=[name+'-'+key for name,key,_,_ in CASES])
def test_every_selected_native_stroke_has_explicit_stroke_treatment(name,key,recipe,source):
    module=importlib.import_module(name)
    root=ET.fromstring((ROOT/source['path']).read_bytes())
    letters=getattr(module,'LETTER_PATHS',{}).get(key,([],''))[0]
    selected_strokes(root,recipe,getattr(module,'STROKE_PATHS',{}).get(key,set()),letters)


def test_open_native_hose_cannot_silently_become_a_filled_loop():
    root=ET.fromstring('<svg><path style="fill:none;stroke:grey;stroke-width:6" d="M0 0 Q20 20 10 0"/></svg>')
    with pytest.raises(AssertionError,match='Native stroke would become a filled shape'):
        selected_strokes(root,(1,[],[0],[],{}))
    assert selected_strokes(root,(1,[],[],[],{0:'grey'}),{0})==[0]


def test_inherited_stroke_style_with_css_whitespace_is_also_checked():
    root=ET.fromstring('<svg><g style=" stroke: grey; fill: none "><path d="M0 0 L10 20 L20 0"/></g></svg>')
    with pytest.raises(AssertionError,match='Native stroke would become a filled shape'):
        selected_strokes(root,(1,[],[0],[],{}))
    assert selected_strokes(root,(1,[],[],[],{}),{0})==[0]
