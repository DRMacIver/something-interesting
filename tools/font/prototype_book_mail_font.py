"""Compile isolated book/mail candidates; never changes production assets.

The shared candidate compiler retains its legacy `flags` report container, but
these glyphs and font names explicitly identify object candidates.
"""
import json
from pathlib import Path
from prototype_remaining_objects import ROOT, RECIPES, prepare
from prototype_region_flag_font import compile_flags
from emoji_sequences import qualified_forms


def main():
    sources=json.loads((ROOT/'docs/remaining-object-emoji-svg-source-probe.json').read_text())['files']
    selected=[(Path(e['path']).stem.removeprefix('emoji_u'),e) for e in sources
              if e['subgroup'] in {'book-paper','mail'}]
    assert len(selected)==30
    assert {key for key,_ in selected}<=set(RECIPES)
    prefix='book-mail'
    compile_flags(selected,prepare,prefix=prefix,
                  form_provider=lambda text:qualified_forms(ROOT,text),
                  family_name='Dad Book Mail Candidate',glyph_prefix='object.')
    path=ROOT/f'output/font-review/pen-translation/{prefix}-candidate.html'
    html=path.read_text().replace('Regional flag','Book and mail').replace('33.6px flags','33.6px objects').replace('A FLAG: ','AN ITEM: ')
    path.write_text(html)


if __name__=='__main__':main()
