"""Detailed SVG pregnancy/feeding drawings and separately coloured exposed skin."""
import json
from fontTools.pens.ttGlyphPen import TTGlyphPen
from emoji_svg import RECIPES, prepare
from emoji_sequences import qualified_forms
import numpy as np


def add_detailed_people(root,glyphs,metrics,cmap,layers,review,outline):
    sequences,components,rules,tones=[],[],[],[]
    spec=json.loads((root/'data/font-sources/noto-emoji-svg.json').read_text())
    for key in RECIPES:
        canonical=''.join(chr(int(cp,16)) for cp in key.split('_'))
        (white,skin,ink),report=prepare(key)
        source=report['source']
        ys,xs=np.nonzero(white);x0,y0,x1,y1=map(int,(xs.min(),ys.min(),xs.max(),ys.max()))
        scale=760/max(x1-x0+1,y1-y0+1);transform=x0,y0,scale
        advance=round((x1-x0+1)*scale)+100
        name='detailed.'+key.replace('_','.')
        glyphs[name]=outline(ink,transform);metrics[name]=advance,50
        assert glyphs[name].numberOfContours>=report['sourceComponents']+report['sourceHoles'],key
        if len(canonical)==1:
            assert ord(canonical) not in cmap
            cmap[ord(canonical)]=name
        for suffix,mask in [('white',white),('skin',skin),('ink',ink)]:
            glyphs[name+'.'+suffix]=outline(mask,transform);metrics[name+'.'+suffix]=advance,50
        for i in range(6):
            text=canonical[:1]+(chr(0x1F3FA+i) if i else '')+canonical[1:]
            forms=qualified_forms(root,text)
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
            if i:tones.extend(forms)
        identity=dict(codepoint=f'U+{ord(canonical):04X}') if len(canonical)==1 else dict(sequence=canonical)
        review.append(dict(**identity,label=key,glyphName=name,category='detailed-people',
                           source=source['path'],sourceSha256=source['sha256'],sourcePixels=report['sourcePixels'],
                           sourceRecipe=key,bounds=[x0,y0,x1,y1],advance=advance,penTreatment=report,
                           license='NotoEmoji-SVG-Apache-2.0.txt',notice='NotoEmoji-SVG-NOTICE.txt'))
    return sequences,components,'\n'.join(rule for _,rule in sorted(rules,key=lambda item:-item[0])),tones
