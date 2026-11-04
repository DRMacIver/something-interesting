"""Compile isolated flaming-bird compound candidates."""
import json
from pathlib import Path
from prototype_phoenix import ROOT,RECIPES,prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
    files=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
    selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in files if e['subgroup'] in {'animal-bird'}]
    assert len(selected)==1 and {key for key,_ in selected}==set(RECIPES)
    compile_flags(selected,prepare,prefix='phoenix',
                  form_provider=lambda text:qualified_forms(ROOT,text),
                  family_name='Dad Phoenix Candidate',glyph_prefix='phoenix.')
    path=ROOT/'output/font-review/pen-translation/phoenix-candidate.html'
    path.write_text(path.read_text().replace('Regional flag','Phoenix').replace('33.6px flags','33.6px objects').replace('A FLAG: ','AN ITEM: '))


if __name__=='__main__':main()
