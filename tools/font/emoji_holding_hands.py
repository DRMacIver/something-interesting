"""Compile four holding-hands drawings with independent skin tones and exact RGI forms."""
import hashlib,importlib,json
import numpy as np
from emoji_sequences import qualified_forms

MODULE='emoji_holding_hands_svg'
ALIASES={'👩‍🤝‍👩':'1f46d','👩‍🤝‍👨':'1f46b','👨‍🤝‍👨':'1f46c'}
BASES={'1f9d1_200d_1f91d_200d_1f9d1','1f46d','1f46b','1f46c'}


def family_key(text):
    base=''.join(c for c in text if not 0x1F3FB<=ord(c)<=0x1F3FF and ord(c)!=0xFE0F)
    return ALIASES.get(base,'_'.join(f'{ord(c):04x}' for c in base))


def tone_pair(text):
    tones=[ord(c)-0x1F3FA for c in text if 0x1F3FB<=ord(c)<=0x1F3FF]
    if not tones:return (0,0)
    if len(tones)==1:return (tones[0],tones[0])
    assert len(tones)==2
    return tuple(tones)


def holding_forms(root):
    groups={key:[] for key in BASES}
    for line in (root/'data/unicode/18.0.0/emoji/emoji-test.txt').read_text().splitlines():
        if '; fully-qualified' not in line:continue
        text=''.join(chr(int(cp,16)) for cp in line.split(';')[0].split())
        key=family_key(text)
        if key in groups:groups[key].extend(qualified_forms(root,text))
    assert all(len(forms)==len(set(forms))==26 for forms in groups.values())
    assert all(set(map(tone_pair,forms))=={(0,0),*((a,b) for a in range(1,6) for b in range(1,6))} for forms in groups.values())
    return groups


def add_holding_hands(root,glyphs,metrics,cmap,layers,palette,review,outline):
    module=importlib.import_module(MODULE);groups=holding_forms(root)
    source_path=root/'output/imagegen/emoji-production/skin-palette-source.json'
    raw=source_path.read_bytes();skin_source=json.loads(raw)
    assert hashlib.sha256((root/skin_source['pdf']).read_bytes()).hexdigest()==skin_source['pdfSha256']
    indices=[]
    for rgb in skin_source['skinTones']:
        rgb=tuple(rgb)
        if rgb not in palette:palette.append(rgb)
        indices.append(palette.index(rgb))
    sequences,rules=[],[]
    for key in module.RECIPES:
        (white,left,right,ink),report=module.prepare(key)
        assert report['colourNames']==['left','right']
        assert report['appliedStrength']>0 and not report['fallback']
        assert not np.any(left&right)
        forms=groups[key];assert set(forms)==set(report['source']['include_sequences'])
        canonical=''.join(chr(int(cp,16)) for cp in key.split('_'))
        ys,xs=np.nonzero(white);bounds=list(map(int,(xs.min(),ys.min(),xs.max(),ys.max())))
        scale=760/max(bounds[2]-bounds[0]+1,bounds[3]-bounds[1]+1)
        transform=bounds[0],bounds[1],scale;advance=round((bounds[2]-bounds[0]+1)*scale)+100
        name='holding-hands.'+key
        glyphs[name]=outline(ink,transform);metrics[name]=(advance,50)
        assert glyphs[name].numberOfContours==report['sourceComponents']+report['sourceHoles'],key
        for suffix,mask in [('white',white),('left',left),('right',right),('ink',ink)]:
            glyphs[name+'.'+suffix]=outline(mask,transform);metrics[name+'.'+suffix]=(advance,50)
        if len(canonical)==1:
            assert ord(canonical) not in cmap;cmap[ord(canonical)]=name
        variants=[]
        for text in forms:
            a,b=tone_pair(text);variant=name+(f'.tones{a}{b}' if a or b else '')
            glyphs[variant]=glyphs[name];metrics[variant]=(advance,50)
            layers[variant]=[(name+'.white',0)]+([(name+'.left',indices[a-1]),(name+'.right',indices[b-1])] if a else [])+[(name+'.ink',1)]
            if len(text)>1:
                assert all(ord(c) in cmap for c in text),text
                rules.append((len(text),'sub '+' '.join(cmap[ord(c)] for c in text)+' by '+variant+';'))
                sequences.append(text)
            variants.append(dict(sequence=text,leftTone=a,rightTone=b,glyphName=variant))
        source=report['source'];identity=({'codepoint':f'U+{ord(canonical):04X}'} if len(canonical)==1 else {'sequence':canonical})
        review.append(dict(**identity,glyphName=name,category='holding-hands',variants=variants,
            source=source['path'],sourceSha256=source['sha256'],sourceRecipe=key,bounds=bounds,advance=advance,
            penTreatment=report,skinPaletteSha256=hashlib.sha256(raw).hexdigest(),
            license='NotoEmoji-SVG-Apache-2.0.txt',notice='NotoEmoji-SVG-NOTICE.txt'))
    return sequences,'\n'.join(rule for _,rule in sorted(rules,key=lambda item:-item[0]))
