"""Compile registered money drawings for isolated font review."""
import json
from pathlib import Path
from prototype_money_objects import ROOT,RECIPES,prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
    files=json.loads((ROOT/'data/font-sources/noto-emoji-money-svg.json').read_text())['files']
    selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in files if e['subgroup']=='money']
    assert len(selected)==10 and {key for key,_ in selected}==set(RECIPES)
    compile_flags(selected,prepare,prefix='money',
                  form_provider=lambda text:qualified_forms(ROOT,text),
                  family_name='Dad Money Candidate',glyph_prefix='money.')
    path=ROOT/'output/font-review/pen-translation/money-candidate.html'
    path.write_text(path.read_text().replace('Regional flag','Money').replace('33.6px flags','33.6px objects').replace('A FLAG: ','MONEY: '))


if __name__=='__main__':main()
