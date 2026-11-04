"""Compile isolated road and rail infrastructure candidates."""
import json
from pathlib import Path
from prototype_road_infrastructure import ROOT,RECIPES,prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
    files=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
    selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in files if Path(e['path']).stem.removeprefix('emoji_u') in RECIPES]
    assert len(selected)==8 and {key for key,_ in selected}==set(RECIPES)
    compile_flags(selected,prepare,prefix='road-infrastructure',
                  form_provider=lambda text:qualified_forms(ROOT,text),
                  family_name='Dad Road Infrastructure Candidate',glyph_prefix='road-infrastructure.')
    path=ROOT/'output/font-review/pen-translation/road-infrastructure-candidate.html'
    path.write_text(path.read_text().replace('Regional flag','Road infrastructure').replace('33.6px flags','33.6px objects').replace('A FLAG: ','AN ITEM: '))


if __name__=='__main__':main()
