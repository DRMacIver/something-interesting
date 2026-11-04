"""Compile reviewed signs with monochrome or semantic-colour layers."""
import importlib
import numpy as np
from emoji_sequences import qualified_forms

MODULES=('emoji_transport_signs_svg','emoji_other_mono_symbols_svg','emoji_warning_signs_svg','emoji_colour_symbols_svg','emoji_emblem_symbols_svg','emoji_potable_water_svg')
PROMOTABLE_COMPONENTS={0x2695}


def add_signs(root,glyphs,metrics,cmap,layers,palette,review,outline):
    sequences,variations,promoted=[],set(),[]
    for module_name in MODULES:
        module=importlib.import_module(module_name)
        for key in module.RECIPES:
            cp=int(key,16);canonical=chr(cp)
            (white,*colours,ink),report=module.prepare(key)
            rgbs=report.get('rgbs',[report['rgb']] if 'rgb' in report else [])
            assert len(colours)==len(rgbs),key
            forms=qualified_forms(root,canonical)
            assert set(forms)==set(report['source']['include_sequences'])
            ys,xs=np.nonzero(white)
            bounds=list(map(int,(xs.min(),ys.min(),xs.max(),ys.max())))
            scale=760/max(bounds[2]-bounds[0]+1,bounds[3]-bounds[1]+1)
            transform=bounds[0],bounds[1],scale
            advance=round((bounds[2]-bounds[0]+1)*scale)+100
            if cp in cmap:
                # Earlier sequence builders already refer to this glyph name.
                # Reuse it when giving the previously invisible medical symbol a drawing.
                name=cmap[cp]
                assert cp in PROMOTABLE_COMPONENTS and name==f'component.{cp:X}'
                assert glyphs[name].numberOfContours==0 and metrics[name]==(0,0)
                promoted.append(cp)
            else:
                name='sign.'+key
                cmap[cp]=name
            glyphs[name]=outline(ink,transform);metrics[name]=(advance,50)
            assert report['appliedStrength']>0 and not report['fallback']
            assert glyphs[name].numberOfContours==report['sourceComponents']+report['sourceHoles'],key
            specifications=[('white',white,0)]
            for index,(mask,rgb) in enumerate(zip(colours,rgbs)):
                rgb=tuple(rgb)
                if rgb not in palette:palette.append(rgb)
                specifications.append((f'colour{index}',mask,palette.index(rgb)))
            specifications.append(('ink',ink,1))
            layers[name]=[]
            for suffix,mask,colour_index in specifications:
                layer=name+'.'+suffix
                glyphs[layer]=outline(mask,transform);metrics[layer]=(advance,50)
                layers[name].append((layer,colour_index))
            sequences.extend(text for text in forms if text!=canonical)
            for text in forms:
                for base,selector in zip(text,text[1:]):
                    if ord(selector) in (0xFE0E,0xFE0F):variations.add((ord(base),ord(selector)))
            source=report['source']
            review.append(dict(codepoint=f'U+{cp:04X}',glyphName=name,category='signs',
                source=source['path'],sourceSha256=source['sha256'],sourceRecipe=key,
                bounds=bounds,advance=advance,penTreatment=report,
                license='NotoEmoji-SVG-Apache-2.0.txt',notice='NotoEmoji-SVG-NOTICE.txt'))
    return sequences,sorted(variations),promoted
