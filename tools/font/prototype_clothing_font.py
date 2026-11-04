"""Compile registered clothing/accessory drawings for isolated font review."""
import json
from pathlib import Path
from prototype_clothing_objects import ROOT,RECIPES,prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
    files=json.loads((ROOT/'data/font-sources/noto-emoji-clothing-svg.json').read_text())['files']
    selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in files if e['subgroup']=='clothing']
    assert len(selected)==9 and {key for key,_ in selected}==set(RECIPES)
    compile_flags(selected,prepare,prefix='clothing',
                  form_provider=lambda text:qualified_forms(ROOT,text),
                  family_name='Dad Clothing Candidate',glyph_prefix='clothing.')
    path=ROOT/'output/font-review/pen-translation/clothing-candidate.html'
    path.write_text(path.read_text().replace('Regional flag','Clothing').replace('33.6px flags','33.6px objects').replace('A FLAG: ','AN ITEM: '))


if __name__=='__main__':main()
