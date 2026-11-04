"""Compile isolated office, bell and lock candidates."""
import json
from pathlib import Path
from prototype_office_locks import ROOT,RECIPES,prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
    files=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
    selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in files if e['subgroup'] in {'hotel','lock','office'}]
    assert len(selected)==6 and {key for key,_ in selected}==set(RECIPES)
    compile_flags(selected,prepare,prefix='office-locks',
                  form_provider=lambda text:qualified_forms(ROOT,text),
                  family_name='Dad Office Locks Candidate',glyph_prefix='office-locks.')
    path=ROOT/'output/font-review/pen-translation/office-locks-candidate.html'
    path.write_text(path.read_text().replace('Regional flag','Office and locks').replace('33.6px flags','33.6px objects').replace('A FLAG: ','AN ITEM: '))


if __name__=='__main__':main()
