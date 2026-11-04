"""Compile isolated place, material and weather candidates."""
import json
from pathlib import Path
from prototype_places_weather import ROOT,RECIPES,prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
    files=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
    selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in files if e['subgroup'] in {'place-building','place-other','sky & weather'}]
    assert len(selected)==8 and {key for key,_ in selected}==set(RECIPES)
    compile_flags(selected,prepare,prefix='places-weather',
                  form_provider=lambda text:qualified_forms(ROOT,text),
                  family_name='Dad Places Weather Candidate',glyph_prefix='places-weather.')
    path=ROOT/'output/font-review/pen-translation/places-weather-candidate.html'
    path.write_text(path.read_text().replace('Regional flag','Places and weather').replace('33.6px flags','33.6px objects').replace('A FLAG: ','AN ITEM: '))


if __name__=='__main__':main()
