"""Compile hand props with skin-only tone variants and invariant objects."""
import hashlib,importlib,json
import numpy as np
from emoji_sequences import qualified_forms

MODULE='emoji_hand_props_svg'


def add_hand_props(root,glyphs,metrics,cmap,layers,palette,review,outline):
    module=importlib.import_module(MODULE)
    palette_path=root/'output/imagegen/emoji-production/skin-palette-source.json'
    skin_source=json.loads(palette_path.read_text())
    assert hashlib.sha256((root/skin_source['pdf']).read_bytes()).hexdigest()==skin_source['pdfSha256']
    skin_indices=[]
    for rgb in skin_source['skinTones']:
        rgb=tuple(rgb)
        if rgb not in palette:palette.append(rgb)
        skin_indices.append(palette.index(rgb))
    sequences,variations,rules,tones=[],set(),[],[]
    for key in module.RECIPES:
        cp=int(key,16);canonical=chr(cp);name='handprop.'+key
        assert cp not in cmap,key
        (white,*materials,ink),report=module.prepare(key)
        assert report['colourNames'][0]=='skin' and len(materials)==len(report['colourNames'])
        assert report['appliedStrength']>0 and not report['fallback']
        ys,xs=np.nonzero(white);bounds=list(map(int,(xs.min(),ys.min(),xs.max(),ys.max())))
        scale=760/max(bounds[2]-bounds[0]+1,bounds[3]-bounds[1]+1)
        transform=bounds[0],bounds[1],scale;advance=round((bounds[2]-bounds[0]+1)*scale)+100
        glyphs[name]=outline(ink,transform);metrics[name]=(advance,50);cmap[cp]=name
        assert glyphs[name].numberOfContours==report['sourceComponents']+report['sourceHoles'],key
        specifications=[('white',white),('skin',materials[0]),*[(f'colour{i}',mask) for i,mask in enumerate(materials[1:])],('ink',ink)]
        for suffix,mask in specifications:
            glyphs[name+'.'+suffix]=outline(mask,transform);metrics[name+'.'+suffix]=(advance,50)
        object_layers=[]
        for i,rgb in enumerate(report['rgbs'][1:]):
            rgb=tuple(rgb)
            if rgb not in palette:palette.append(rgb)
            object_layers.append((name+f'.colour{i}',palette.index(rgb)))
        variants=[];all_forms=[]
        for tone in range(6):
            text=canonical+(chr(0x1F3FA+tone) if tone else '')
            forms=qualified_forms(root,text);all_forms+=forms
            variant=name+(f'.tone{tone}' if tone else '')
            glyphs[variant]=glyphs[name];metrics[variant]=(advance,50)
            layers[variant]=[(name+'.white',0)]+([(name+'.skin',skin_indices[tone-1])] if tone else [])+object_layers+[(name+'.ink',1)]
            if tone:
                assert ord(text[-1]) in cmap
                rules.append('sub '+name+' '+cmap[ord(text[-1])]+' by '+variant+';')
                tones.extend(forms)
            sequences.extend(form for form in forms if form!=canonical)
            for form in forms:
                for base,selector in zip(form,form[1:]):
                    if ord(selector) in (0xFE0E,0xFE0F):variations.add((ord(base),ord(selector)))
            variants.append(dict(tone=tone,glyphName=variant,qualificationForms=forms))
        assert set(all_forms)==set(report['source']['include_sequences'])
        source=report['source']
        review.append(dict(codepoint=f'U+{cp:04X}',glyphName=name,category='hand-props',variants=variants,
            source=source['path'],sourceSha256=source['sha256'],sourceRecipe=key,bounds=bounds,advance=advance,
            penTreatment=report,skinPaletteSha256=hashlib.sha256(palette_path.read_bytes()).hexdigest(),
            license='NotoEmoji-SVG-Apache-2.0.txt',notice='NotoEmoji-SVG-NOTICE.txt'))
    return sequences,sorted(variations),'\n'.join(rules),tones
