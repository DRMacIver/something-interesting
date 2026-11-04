"""Compile eight kissing and heart-couple drawings with independent skin tones and exact RGI forms."""
import hashlib,importlib,json
import numpy as np
from emoji_sequences import qualified_forms

MODULE='emoji_couples_svg'
ALIASES={'🧑‍❤‍💋‍🧑':'1f48f','🧑‍❤‍🧑':'1f491'}
BASES={'1f491', '1f469_200d_2764_200d_1f468', '1f469_200d_2764_200d_1f469', '1f469_200d_2764_200d_1f48b_200d_1f468', '1f468_200d_2764_200d_1f468', '1f468_200d_2764_200d_1f48b_200d_1f468', '1f48f', '1f469_200d_2764_200d_1f48b_200d_1f469'}

def family_key(text):
    base=''.join(c for c in text if not 0x1F3FB<=ord(c)<=0x1F3FF and ord(c)!=0xFE0F)
    return ALIASES.get(base,'_'.join(f'{ord(c):04x}' for c in base))


def tone_pair(text):
    tones=[ord(c)-0x1F3FA for c in text if 0x1F3FB<=ord(c)<=0x1F3FF]
    if not tones:return (0,0)
    if len(tones)==1:return (tones[0],tones[0])
    assert len(tones)==2
    return tuple(tones)


def couple_forms(root):
    groups={key:[] for key in BASES}
    for line in (root/'data/unicode/18.0.0/emoji/emoji-test.txt').read_text().splitlines():
        if '; fully-qualified' not in line:continue
        text=''.join(chr(int(cp,16)) for cp in line.split(';')[0].split())
        key=family_key(text)
        if key in groups:groups[key].extend(qualified_forms(root,text))
    assert all(len(forms)==len(set(forms))==(46 if key in {'1f48f','1f491'} else 52) for key,forms in groups.items())
    assert all(set(map(tone_pair,forms))=={(0,0),*((a,b) for a in range(1,6) for b in range(1,6))} for forms in groups.values())
    return groups


def add_couples(root,glyphs,metrics,cmap,layers,palette,review,outline):
    module=importlib.import_module(MODULE);groups=couple_forms(root)
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
        (white,*materials,ink),report=module.prepare(key)
        masks=dict(zip(report['colourNames'],materials));left,right,red=(masks[k] for k in ['left','right','red'])
        red_rgb=tuple(report['rgbs'][report['colourNames'].index('red')])
        if red_rgb not in palette:palette.append(red_rgb)
        red_index=palette.index(red_rgb)
        assert report['appliedStrength']>0 and not report['fallback']
        assert not np.any(left&right)
        forms=groups[key];assert set(forms)==set(report['source']['include_sequences'])
        canonical=''.join(chr(int(cp,16)) for cp in key.split('_'))
        ys,xs=np.nonzero(white);bounds=list(map(int,(xs.min(),ys.min(),xs.max(),ys.max())))
        scale=760/max(bounds[2]-bounds[0]+1,bounds[3]-bounds[1]+1)
        transform=bounds[0],bounds[1],scale;advance=round((bounds[2]-bounds[0]+1)*scale)+100
        name='couples.'+key
        glyphs[name]=outline(ink,transform);metrics[name]=(advance,50)
        assert glyphs[name].numberOfContours==report['sourceComponents']+report['sourceHoles'],key
        for suffix,mask in [('white',white),('left',left),('right',right),('red',red),('ink',ink)]:
            glyphs[name+'.'+suffix]=outline(mask,transform);metrics[name+'.'+suffix]=(advance,50)
        if len(canonical)==1:
            assert ord(canonical) not in cmap;cmap[ord(canonical)]=name
        variants=[]
        for text in forms:
            a,b=tone_pair(text);variant=name+(f'.tones{a}{b}' if a or b else '')
            glyphs[variant]=glyphs[name];metrics[variant]=(advance,50)
            layers[variant]=[(name+'.white',0)]+([(name+'.left',indices[a-1]),(name+'.right',indices[b-1])] if a else [])+[(name+'.red',red_index),(name+'.ink',1)]
            if len(text)>1:
                plain=text.replace('\ufe0f','')
                assert all(ord(c) in cmap for c in plain),text
                components=[('['+cmap[ord(c)]+' u2764]' if c=='❤' else cmap[ord(c)]) for c in plain]
                rule=(len(plain),'sub '+' '.join(components)+' by '+variant+';')
                if rule not in rules:rules.append(rule)
                sequences.append(text)
            variants.append(dict(sequence=text,leftTone=a,rightTone=b,glyphName=variant))
        source=report['source'];identity=({'codepoint':f'U+{ord(canonical):04X}'} if len(canonical)==1 else {'sequence':canonical})
        review.append(dict(**identity,glyphName=name,category='couples',variants=variants,
            source=source['path'],sourceSha256=source['sha256'],sourceRecipe=key,bounds=bounds,advance=advance,
            penTreatment=report,skinPaletteSha256=hashlib.sha256(raw).hexdigest(),
            license='NotoEmoji-SVG-Apache-2.0.txt',notice='NotoEmoji-SVG-NOTICE.txt'))
    return sequences,'\n'.join(rule for _,rule in sorted(rules,key=lambda item:-item[0]))
