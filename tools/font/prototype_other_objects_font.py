"""Compile isolated other-objects candidates."""
import json
from pathlib import Path
from prototype_other_objects import ROOT,RECIPES,prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
    files=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
    selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in files if e['subgroup'] in {'other-object'}]
    assert len(selected)==9 and {key for key,_ in selected}==set(RECIPES)
    compile_flags(selected,prepare,prefix='other-objects',
                  form_provider=lambda text:qualified_forms(ROOT,text),
                  family_name='Dad Other Objects Candidate',glyph_prefix='other-objects.')
    path=ROOT/'output/font-review/pen-translation/other-objects-candidate.html'
    path.write_text(path.read_text().replace('Regional flag','Other Objects').replace('33.6px flags','33.6px objects').replace('A FLAG: ','AN ITEM: '))


if __name__=='__main__':main()
