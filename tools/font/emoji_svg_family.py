"""Compile registered reviewed singleton SVG families into Dad Emoji."""
import json
from pathlib import Path
import numpy as np
from flag_outlines import clean_flag_outline


def add_svg_family(root,glyphs,metrics,cmap,layers,palette,review,outline,
                   family,prepare,expected_drawings,expected_aliases,*,counter_losses=None,promotable_components=None):
    spec=json.loads((root/f'data/font-sources/noto-emoji-{family}-svg.json').read_text())
    sources=[e for e in spec['files'] if e.get('build_target')=='emoji-artwork']
    assert len(sources)==expected_drawings
    sequences=[]
    variations=set()
    for source in sources:
        key=Path(source['path']).stem.removeprefix('emoji_u')
        forms=source['include_sequences']
        bare={text.replace('\ufe0f','').replace('\ufe0e','') for text in forms}
        assert len(bare)==1
        text=bare.pop()
        assert len(text)==1
        cp=ord(text)
        name=family+'.'+key
        if cp in cmap:
            name=cmap[cp]
            assert (promotable_components or {}).get(cp)==name and glyphs[name].numberOfContours==0 and metrics[name]==(0,0) and name not in layers,('Only empty named shaping components may be promoted',hex(cp),name)
        (paper,*colours,ink),report=prepare(key)
        assert report['source']['sha256']==source['sha256']
        assert report['appliedStrength']>0 and not report['fallback']
        ys,xs=np.nonzero(paper)
        bounds=list(map(int,(xs.min(),ys.min(),xs.max(),ys.max())))
        scale=760/max(bounds[2]-bounds[0]+1,bounds[3]-bounds[1]+1)
        transform=bounds[0],bounds[1],scale
        advance=round((bounds[2]-bounds[0]+1)*scale)+100
        cmap[cp]=name
        glyphs[name],removed=clean_flag_outline(ink,transform,outline)
        counter_review=None
        if counter_losses is not None:
            from svg_counter_review import review_counters
            counter_review=review_counters(ink,transform,glyphs[name],max_small_losses=counter_losses.get(key,0))
        metrics[name]=(advance,50)
        layers[name]=[]
        layer_reports=[]
        for i,(mask,rgb) in enumerate([(paper,(255,255,255)),*zip(colours,map(tuple,report['rgbs'])),(ink,(17,17,17))]):
            if rgb not in palette:palette.append(rgb)
            layer=name+f'.layer{i}'
            glyphs[layer],dropped=clean_flag_outline(mask,transform,outline)
            metrics[layer]=(advance,50)
            layers[name].append((layer,palette.index(rgb)))
            layer_reports.append(dict(glyphName=layer,rgb=rgb,removedZeroAreaContours=dropped))
        for form in forms:
            if len(form)>1:sequences.append(form)
            for base,selector in zip(form,form[1:]):
                if ord(selector) in (0xfe0e,0xfe0f):variations.add((ord(base),ord(selector)))
        review.append(dict(codepoint=f'U+{cp:04X}',sequence=source['sequence'],qualificationForms=forms,
                           glyphName=name,category=source['subgroup'],source=source['path'],
                           sourceSha256=source['sha256'],sourceRecipe=key,bounds=bounds,
                           advance=advance,penTreatment=report,layers=layer_reports,
                           removedZeroAreaInkContours=removed,counterReview=counter_review,license=spec['license'],
                           notices=spec['notices']))
    assert len(sequences)==expected_aliases and len(set(sequences))==expected_aliases
    return sequences,sorted(variations)
