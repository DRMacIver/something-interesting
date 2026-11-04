"""Compile isolated tool/instrument candidates without production changes."""
import json
from pathlib import Path
from prototype_tools_instruments import ROOT,RECIPES,prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms
import numpy as np
from build_emoji import outline
from flag_outlines import clean_flag_outline
from svg_counter_review import review_counters


def checked_prepare(key):
    masks,report=prepare(key);paper,*_,ink=masks
    ys,xs=np.nonzero(paper)
    transform=xs.min(),ys.min(),760/max(np.ptp(xs)+1,np.ptp(ys)+1)
    glyph,_=clean_flag_outline(ink,transform,outline)
    report['fontCounterReview']=review_counters(ink,transform,glyph,max_small_losses=1 if key=='1fa95' else 0)
    return masks,report


def main():
    files=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
    selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in files if e['subgroup'] in {'tool','musical-instrument'}]
    assert len(selected)==11 and {key for key,_ in selected}==set(RECIPES)
    compile_flags(selected,checked_prepare,prefix='tools-instruments',
                  form_provider=lambda text:qualified_forms(ROOT,text),
                  family_name='Dad Tools Instruments Candidate',glyph_prefix='tools-instruments.')
    path=ROOT/'output/font-review/pen-translation/tools-instruments-candidate.html'
    path.write_text(path.read_text().replace('Regional flag','Tools and instruments').replace('33.6px flags','33.6px objects').replace('A FLAG: ','AN ITEM: '))


if __name__=='__main__':main()
