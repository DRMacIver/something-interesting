"""Promote only the reviewed empty, named emoji shaping components."""
import json
import numpy as np
from emoji_standalone_components import POINTS, prepare, monochrome
from flag_outlines import clean_flag_outline
from svg_counter_review import review_counters

COMPONENT_NAMES = {**{cp:f'flag-component.u{cp:X}' for cp in range(0x1f1e6,0x1f200)},
                   **{cp:f'tone{cp-0x1f3fa}' for cp in range(0x1f3fb,0x1f400)},
                   **{cp:f'component.{cp:X}' for cp in range(0x1f9b0,0x1f9b4)}}


def add_standalone_components(root,glyphs,metrics,cmap,layers,palette,review,outline):
    spec = json.loads((root/'data/font-sources/noto-emoji.json').read_text())
    assert {chr(cp) for cp in POINTS} <= set(spec['files'][0]['include_sequences'])
    for cp,name in COMPONENT_NAMES.items():
        assert cmap.get(cp)==name and glyphs[name].numberOfContours==0 and metrics[name]==(0,0) and name not in layers, ('Only empty named components may be promoted',hex(cp),name)
    for cp,name in COMPONENT_NAMES.items():
        key=f'{cp:x}'
        (paper,*colours,ink),report=prepare(key)
        ys,xs=np.nonzero(paper)
        transform=xs.min(),ys.min(),760/max(np.ptp(xs)+1,np.ptp(ys)+1)
        advance=round((np.ptp(xs)+1)*transform[2])+100
        glyphs[name],removed=clean_flag_outline(monochrome(key),transform,outline)
        counters=review_counters(monochrome(key),transform,glyphs[name])
        metrics[name]=(advance,50)
        layers[name]=[]
        layer_reports=[]
        for i,(mask,rgb) in enumerate([(paper,(255,255,255)),*zip(colours,map(tuple,report['rgbs'])),(ink,(17,17,17))]):
            if rgb not in palette:
                palette.append(rgb)
            layer=name+f'.standalone.layer{i}'
            assert layer not in glyphs
            glyphs[layer],dropped=clean_flag_outline(mask,transform,outline)
            metrics[layer]=(advance,50)
            layers[name].append((layer,palette.index(rgb)))
            layer_reports.append(dict(glyphName=layer,rgb=rgb,removedZeroAreaContours=dropped))
        review_counters(ink,transform,glyphs[layer])
        review.append(dict(codepoint=f'U+{cp:04X}',sequence=chr(cp),qualificationForms=[chr(cp)],
                           glyphName=name,category='standalone_components',source=report['source'],
                           sourceSha256=report['sourceSha256'],sourceGlyph=report['sourceGlyph'],
                           bounds=list(map(int,[xs.min(),ys.min(),xs.max(),ys.max()])),advance=advance,
                           penTreatment={**report,'candidateOnly':False},layers=layer_reports,counterReview=counters,
                           removedZeroAreaInkContours=removed,license='NotoEmoji-OFL.txt',
                           letteringSource=report.get('letteringSource')))
    return set(COMPONENT_NAMES)
