"""Compile isolated remaining ground-vehicle candidates."""
import json
from pathlib import Path
from prototype_ground_vehicles import ROOT,RECIPES,prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
 files=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
 selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in files if Path(e['path']).stem.removeprefix('emoji_u') in RECIPES]
 assert len(selected)==10 and {key for key,_ in selected}==set(RECIPES)
 compile_flags(selected,prepare,prefix='ground-vehicles',form_provider=lambda text:qualified_forms(ROOT,text),family_name='Dad Ground Vehicles Candidate',glyph_prefix='ground-vehicles.')
 path=ROOT/'output/font-review/pen-translation/ground-vehicles-candidate.html'
 path.write_text(path.read_text().replace('Regional flag','Ground vehicle').replace('33.6px flags','33.6px vehicles').replace('A FLAG: ','A VEHICLE: '))

if __name__=='__main__':main()
