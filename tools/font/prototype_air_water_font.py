"""Compile isolated aircraft and watercraft candidates."""
import json
from pathlib import Path
from prototype_air_water import ROOT,RECIPES,prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
    files=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
    selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in files if e['subgroup'] in {'transport-air','transport-water'}]
    assert len(selected)==8 and {key for key,_ in selected}==set(RECIPES)
    compile_flags(selected,prepare,prefix='air-water',
                  form_provider=lambda text:qualified_forms(ROOT,text),
                  family_name='Dad Air Water Candidate',glyph_prefix='air-water.')
    path=ROOT/'output/font-review/pen-translation/air-water-candidate.html'
    path.write_text(path.read_text().replace('Regional flag','Aircraft and watercraft').replace('33.6px flags','33.6px objects').replace('A FLAG: ','AN ITEM: '))


if __name__=='__main__':main()
