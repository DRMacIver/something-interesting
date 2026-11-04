"""Person activity SVG drawings and independently coloured exposed skin."""
import hashlib
from fontTools.pens.ttGlyphPen import TTGlyphPen
from emoji_activity_svg import RECIPES, prepare
from emoji_sequences import qualified_forms
from emoji_paired_skin import split_paired_skin, EXPECTED_BUNNY_COMPONENTS
import numpy as np


def add_activity_people(root,glyphs,metrics,cmap,layers,review,outline):
    sequences,components,rules,tones=[],[],[],[]
    for key in RECIPES:
        canonical=''.join(chr(int(cp,16)) for cp in key.split('_'))
        (white,skin,ink),report=prepare(key)
        source=report['source']
        ys,xs=np.nonzero(white);x0,y0,x1,y1=map(int,(xs.min(),ys.min(),xs.max(),ys.max()))
        scale=760/max(x1-x0+1,y1-y0+1);transform=x0,y0,scale
        advance=round((x1-x0+1)*scale)+100
        name='activityperson.'+key.replace('_','.')
        glyphs[name]=outline(ink,transform);metrics[name]=advance,50
        assert glyphs[name].numberOfContours>=report['sourceComponents']+report['sourceHoles'],key
        if len(canonical)==1:
            assert ord(canonical) not in cmap
            cmap[ord(canonical)]=name
        for suffix,mask in [('white',white),('skin',skin),('ink',ink)]:
            glyphs[name+'.'+suffix]=outline(mask,transform);metrics[name+'.'+suffix]=advance,50
        paired_review=None
        for i in range(6):
            text=canonical[:1]+(chr(0x1F3FA+i) if i else '')+canonical[1:]
            forms=qualified_forms(root,text)
            if key in {'1f3cc','1f3ca','26f9','1f3cb','1f3c4'} and i==0:
                for selector in ['\ufe0e','\ufe0f']:
                    if text+selector not in forms:forms.append(text+selector)
            assert set(forms)<=set(source['include_sequences'])
            variant=name+(f'.tone{i}' if i else '')
            glyphs[variant]=glyphs[name];metrics[variant]=advance,50
            layers[variant]=[(name+'.white',0)]+([(name+'.skin',5+i)] if i else [])+[(name+'.ink',1)]
            for char in text:
                cp=ord(char)
                if cp not in cmap:
                    component=f'component.{cp:X}';cmap[cp]=component
                    glyphs[component]=TTGlyphPen(None).glyph();metrics[component]=0,0;components.append(cp)
            if len(text)>1:
                rules.append((len(text),'sub '+' '.join(cmap[ord(c)] for c in text)+' by '+variant+';'))
                sequences.extend(forms)
            else:
                sequences.extend(form for form in forms if form!=text)
            if i:tones.extend(forms)
        if key in EXPECTED_BUNNY_COMPONENTS or key.startswith('1f93c'):
            if key.startswith('1f93c'):
                from emoji_wrestling_svg import split_skin
                left,right,paired_review=split_skin(white,skin,ink,report)
                paired_review['programSha256']=hashlib.sha256((root/'tools/font/emoji_wrestling_svg.py').read_bytes()).hexdigest()
                bridge='🫯'
            else:
                left,right,paired_review=split_paired_skin(skin,ink)
                assert [paired_review['leftComponents'],paired_review['rightComponents']]==EXPECTED_BUNNY_COMPONENTS[key]
                paired_review['programSha256']=hashlib.sha256((root/'tools/font/emoji_paired_skin.py').read_bytes()).hexdigest()
                bridge='🐰'
            for side,mask in [('left',left),('right',right)]:
                layer=name+'.skin.'+side
                glyphs[layer]=outline(mask,transform);metrics[layer]=advance,50
            person='👨' if key.endswith('2642') else '👩' if key.endswith('2640') else '🧑'
            paired_forms=[]
            for a in range(1,6):
                for b in range(1,6):
                    if a==b:continue
                    text=person+chr(0x1f3fa+a)+'\u200d'+bridge+'\u200d'+person+chr(0x1f3fa+b)
                    forms=qualified_forms(root,text)
                    assert set(forms)<=set(source['include_sequences'])
                    variant=name+f'.tones{a}.{b}'
                    glyphs[variant]=glyphs[name];metrics[variant]=advance,50
                    layers[variant]=[(name+'.white',0),(name+'.skin.left',5+a),(name+'.skin.right',5+b),(name+'.ink',1)]
                    missing=[f'U+{ord(char):04X}' for char in text if ord(char) not in cmap]
                    assert not missing,(key,text,missing)
                    rules.append((len(text),'sub '+' '.join(cmap[ord(char)] for char in text)+' by '+variant+';'))
                    sequences.extend(forms);tones.extend(forms);paired_forms.extend(forms)
            assert len(paired_forms)==20 and set(paired_forms)==set(source['paired_sequences'])
        identity=dict(codepoint=f'U+{ord(canonical):04X}') if len(canonical)==1 else dict(sequence=canonical)
        review.append(dict(**identity,label=key,glyphName=name,category='activity-people',
                           source=source['path'],sourceSha256=source['sha256'],sourcePixels=report['sourcePixels'],
                           sourceRecipe=key,pairedSkin=paired_review,bounds=[x0,y0,x1,y1],advance=advance,penTreatment=report,
                           license='NotoEmoji-SVG-Apache-2.0.txt',notice='NotoEmoji-SVG-NOTICE.txt'))
    return sequences,components,'\n'.join(rule for _,rule in sorted(rules,key=lambda item:-item[0])),tones
