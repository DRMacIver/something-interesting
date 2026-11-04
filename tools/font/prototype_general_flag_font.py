"""Compile eight canonical general flag candidates without registration."""
import json
from prototype_general_flags import ROOT, RECIPES, prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
    files=json.loads((ROOT/'docs/flags-emoji-svg-source-probe.json').read_text())['files']
    sources={e['path'].split('emoji_u')[-1].removesuffix('.svg'):e for e in files if e.get('licenseFamily')=='Noto-SVG-Apache-2.0'}
    selected=[(key,sources[key]) for key in RECIPES]
    compile_flags(selected,prepare,prefix='general-flags',form_provider=lambda text:qualified_forms(ROOT,text))


if __name__=='__main__':main()
