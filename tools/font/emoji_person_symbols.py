"""Compile person silhouettes and neutral family symbols with longest-first GSUB."""
import importlib
import numpy as np
from emoji_sequences import qualified_forms

MODULE='emoji_person_symbols_svg'


def add_person_symbols(root,glyphs,metrics,cmap,layers,review,outline):
    module=importlib.import_module(MODULE)
    sequences,variations,rules=[],set(),[]
    for key in module.RECIPES:
        canonical=''.join(chr(int(cp,16)) for cp in key.split('_'))
        forms=qualified_forms(root,canonical)
        (white,ink),report=module.prepare(key)
        assert set(forms)==set(report['source']['include_sequences'])
        assert report['appliedStrength']>0 and not report['fallback']
        ys,xs=np.nonzero(white);bounds=list(map(int,(xs.min(),ys.min(),xs.max(),ys.max())))
        scale=760/max(bounds[2]-bounds[0]+1,bounds[3]-bounds[1]+1)
        transform=bounds[0],bounds[1],scale;advance=round((bounds[2]-bounds[0]+1)*scale)+100
        name='personsymbol.'+key
        glyphs[name]=outline(ink,transform);metrics[name]=(advance,50)
        assert glyphs[name].numberOfContours==report['sourceComponents']+report['sourceHoles'],key
        layers[name]=[]
        for suffix,mask,index in [('white',white,0),('ink',ink,1)]:
            layer=name+'.'+suffix;glyphs[layer]=outline(mask,transform);metrics[layer]=(advance,50)
            layers[name].append((layer,index))
        if len(canonical)==1:
            cp=ord(canonical);assert cp not in cmap,key;cmap[cp]=name
        else:
            assert all(ord(c) in cmap for c in canonical),canonical
            rules.append((len(canonical),'sub '+' '.join(cmap[ord(c)] for c in canonical)+' by '+name+';'))
        sequences.extend(text for text in forms if len(canonical)>1 or text!=canonical)
        for text in forms:
            for base,selector in zip(text,text[1:]):
                if ord(selector) in (0xFE0E,0xFE0F):variations.add((ord(base),ord(selector)))
        source=report['source']
        identity=({'codepoint':f'U+{ord(canonical):04X}'} if len(canonical)==1 else
                  {'sequence':forms[0],'qualificationForms':forms})
        review.append(dict(**identity,glyphName=name,category='person-symbols',
            source=source['path'],sourceSha256=source['sha256'],sourceRecipe=key,
            bounds=bounds,advance=advance,penTreatment=report,
            license='NotoEmoji-SVG-Apache-2.0.txt',notice='NotoEmoji-SVG-NOTICE.txt'))
    return sequences,sorted(variations),'\n'.join(rule for _,rule in sorted(rules,key=lambda pair:-pair[0]))
