"""Compile isolated components; does not change production emoji outputs."""
import json
from emoji_standalone_components import ROOT, POINTS, prepare, monochrome
from prototype_region_flag_font import compile_flags


if __name__ == '__main__':
    selected = [(f'{cp:x}', dict(sequence=chr(cp))) for cp in POINTS]
    compile_flags(selected, prepare, prefix='standalone-components',
                  family_name='Dad Standalone Components Candidate',
                  glyph_prefix='standalone-components.', fallback_provider=monochrome)
    folder = ROOT/'output/font-review/pen-translation'
    result = json.loads((folder/'standalone-components-candidate-validation.json').read_text())
    template = (ROOT/'tools/font/templates/standalone-components.html').read_text()
    template = template.replace('__FONT_HASH__',result['colourSha256'][:12]).replace('__INK_HASH__',result['inkSha256'][:12])
    template = template.replace('__FORMS__',json.dumps([dict(key=k,text=s['sequence']) for k,s in selected]))
    (folder/'standalone-components-candidate.html').write_text(template)
