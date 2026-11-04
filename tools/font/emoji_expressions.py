"""Compile reviewed expressive faces, hearts and joined expression drawings."""
import importlib
import numpy as np
from fontTools.pens.ttGlyphPen import TTGlyphPen
from emoji_sequences import qualified_forms

FAMILIES=('balloon_symbols','expression_faces','pixel_alien','heart_variants',
          'heart_decoration','ghost','motion_symbols','coloured_expression',
          'eye_balloon','swearing_face')
MODULES=tuple('emoji_'+family+'_svg' for family in FAMILIES)
PROMOTABLE_COMPONENTS={0x1F4A5,0x1F4AB,0x1F4A8}


def add_expressions(root,glyphs,metrics,cmap,layers,palette,review,outline):
    sequences,variations,promoted,rules=[],set(),[],[]
    compounds=[];components=[]
    for module_name in MODULES:
        module=importlib.import_module(module_name)
        for key in module.RECIPES:
            canonical=''.join(chr(int(cp,16)) for cp in key.split('_'))
            forms=qualified_forms(root,canonical)
            (white,*colours,ink),report=module.prepare(key)
            assert set(forms)==set(report['source']['include_sequences'])
            rgbs=report.get('rgbs',[])
            assert len(colours)==len(rgbs),key
            ys,xs=np.nonzero(white)
            bounds=list(map(int,(xs.min(),ys.min(),xs.max(),ys.max())))
            scale=760/max(bounds[2]-bounds[0]+1,bounds[3]-bounds[1]+1)
            transform=bounds[0],bounds[1],scale
            advance=round((bounds[2]-bounds[0]+1)*scale)+100
            name='expression.'+key
            if len(canonical)==1:
                cp=ord(canonical)
                if cp in cmap:
                    name=cmap[cp]
                    assert cp in PROMOTABLE_COMPONENTS and name==f'component.{cp:X}'
                    assert glyphs[name].numberOfContours==0 and metrics[name]==(0,0)
                    promoted.append(cp)
                else:cmap[cp]=name
            else:
                # Resolve after all standalone drawings are installed: the eye
                # balloon needs the newly added speech-balloon base.
                compounds.append((canonical,name))
            assert name not in layers,key
            glyphs[name]=outline(ink,transform);metrics[name]=(advance,50)
            assert report['appliedStrength']>0 and not report['fallback']
            assert glyphs[name].numberOfContours==report['sourceComponents']+report['sourceHoles'],key
            specifications=[('white',white,0)]
            for index,(mask,rgb) in enumerate(zip(colours,rgbs)):
                rgb=tuple(rgb)
                if rgb not in palette:palette.append(rgb)
                specifications.append((f'colour{index}',mask,palette.index(rgb)))
            specifications.append(('ink',ink,1));layers[name]=[]
            for suffix,mask,colour_index in specifications:
                layer=name+'.'+suffix
                glyphs[layer]=outline(mask,transform);metrics[layer]=(advance,50)
                layers[name].append((layer,colour_index))
            sequences.extend(text for text in forms if len(canonical)>1 or text!=canonical)
            for text in forms:
                for base,selector in zip(text,text[1:]):
                    if ord(selector) in (0xFE0E,0xFE0F):variations.add((ord(base),ord(selector)))
            source=report['source']
            identity=({'codepoint':f'U+{ord(canonical):04X}'} if len(canonical)==1 else
                      {'sequence':forms[0],'qualificationForms':forms})
            review.append(dict(**identity,glyphName=name,category='expressions',
                source=source['path'],sourceSha256=source['sha256'],sourceRecipe=key,
                bounds=bounds,advance=advance,penTreatment=report,
                license='NotoEmoji-SVG-Apache-2.0.txt',notice='NotoEmoji-SVG-NOTICE.txt'))
    for canonical,name in compounds:
        for c in canonical:
            cp=ord(c)
            if cp not in cmap:
                assert cp==0x1FA79,canonical
                component=f'component.{cp:X}'
                cmap[cp]=component;glyphs[component]=TTGlyphPen(None).glyph()
                metrics[component]=(0,0);components.append(cp)
        inputs=[]
        for c in canonical:
            base=cmap[ord(c)]
            if ord(c)==0x2764:
                # This font uses a distinct coloured heart for FE0F. Both
                # qualification forms must reach the same joined drawing.
                assert 'u2764' in glyphs
                base='['+base+' u2764]'
            inputs.append(base)
        rules.append('sub '+' '.join(inputs)+' by '+name+';')
    return sequences,sorted(variations),promoted,'\n'.join(rules),components
