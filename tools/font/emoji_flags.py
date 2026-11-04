"""Compile registered general and regional flags before shorter emoji rules."""
import importlib
import json
import hashlib
import numpy as np
from fontTools.pens.ttGlyphPen import TTGlyphPen
from flag_outlines import clean_flag_outline


def add_flags(root,glyphs,metrics,cmap,layers,palette,review,outline):
    records=[]
    for kind,module_name in [('general','emoji_general_flags_svg'),('regional','emoji_regional_flags_svg')]:
        spec=json.loads((root/f'data/font-sources/noto-emoji-{kind}-flags-svg.json').read_text())
        module=importlib.import_module(module_name)
        for source in spec['files']:
            if source.get('build_target')!='emoji-artwork':continue
            key=module.label(source['sequence']) if kind=='regional' else source['path'].split('emoji_u')[-1].removesuffix('.svg')
            records.append((kind,module,key,source,spec.get('notices',[])))
    assert len(records)==270
    # Drawings that have a singleton form must be cmap bases, so longer pirate,
    # rainbow, transgender and subdivision rules can refer to their real glyphs.
    bases={ord(text):'flag.'+kind+'.'+key for kind,_,key,source,_ in records for text in source['include_sequences'] if len(text)==1}
    assert len(bases)==5 and not(set(bases)&set(cmap))
    cmap.update(bases)
    components=[]
    for cp in sorted({ord(c) for _,_,_,source,_ in records for text in source['include_sequences'] for c in text if ord(c) not in (0xfe0e,0xfe0f)}-set(cmap)):
        name=f'flag-component.u{cp:04X}';cmap[cp]=name;glyphs[name]=TTGlyphPen(None).glyph();metrics[name]=(0,0);components.append(cp)
    rules=[];sequences=[];variations=set()
    for kind,module,key,source,notices in records:
        (paper,*colours,ink),report=module.prepare(key)
        assert report['source']['sha256']==source['sha256']
        assert report['appliedStrength']>0 and not report['fallback']
        ys,xs=np.nonzero(paper);bounds=list(map(int,(xs.min(),ys.min(),xs.max(),ys.max())))
        scale=760/max(bounds[2]-bounds[0]+1,bounds[3]-bounds[1]+1);transform=bounds[0],bounds[1],scale
        advance=round((bounds[2]-bounds[0]+1)*scale)+100;name='flag.'+kind+'.'+key
        glyphs[name],removed=clean_flag_outline(ink,transform,outline);metrics[name]=(advance,50);layers[name]=[];layer_reports=[]
        for i,(mask,rgb) in enumerate([(paper,(255,255,255)),*zip(colours,map(tuple,report['rgbs'])),(ink,(17,17,17))]):
            if rgb not in palette:palette.append(rgb)
            layer=name+f'.layer{i}';glyphs[layer],dropped=clean_flag_outline(mask,transform,outline);metrics[layer]=(advance,50)
            layers[name].append((layer,palette.index(rgb)));layer_reports.append(dict(glyphName=layer,rgb=rgb,removedZeroAreaContours=dropped))
        forms=source['include_sequences']
        for text in forms:
            if len(text)>1:sequences.append(text)
            bare=text.replace('\ufe0f','').replace('\ufe0e','')
            if len(bare)>1:
                rule=(len(bare),'sub '+' '.join(cmap[ord(c)] for c in bare)+' by '+name+';')
                if rule not in rules:rules.append(rule)
            for base,selector in zip(text,text[1:]):
                if ord(selector) in (0xfe0e,0xfe0f):variations.add((ord(base),ord(selector)))
        identity=next((dict(codepoint=f'U+{ord(text):04X}') for text in forms if len(text)==1),{})
        review.append(dict(**identity,sequence=source['sequence'],qualificationForms=forms,glyphName=name,category=kind+'-flags',source=source['path'],sourceSha256=source['sha256'],sourceRecipe=key,
                           bounds=bounds,advance=advance,penTreatment=report,layers=layer_reports,removedZeroAreaInkContours=removed,
                           license=source['licenseFamily'],notices=notices if kind=='regional' else ['assets/fonts/licenses/NotoEmoji-SVG-Apache-2.0.txt','assets/fonts/licenses/NotoEmoji-SVG-NOTICE.txt']))
    assert len(sequences)==271 and len(set(sequences))==271
    return sequences,sorted(variations),'\n'.join(rule for _,rule in sorted(rules,key=lambda r:-r[0])),components
