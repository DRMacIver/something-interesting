"""Compile the final reviewed object families and the joined phoenix drawing."""
import importlib,json
import numpy as np
from emoji_svg_family import add_svg_family
from flag_outlines import clean_flag_outline
from svg_counter_review import review_counters
PROMOTABLE_COMPONENTS={0x1F308:'flag-component.u1F308',0x2708:'component.2708'}
FAMILIES=[('office-locks',6,1),('tools-instruments',11,3),('places-weather',8,1),
          ('other-objects',9,2),('globes',3,0),('air-water',8,4),
          ('road-infrastructure',8,2),('ground-vehicles',10,2)]


def add_final_objects(root,glyphs,metrics,cmap,layers,palette,review,outline):
    sequences=[];variations=[]
    for family,count,aliases in FAMILIES:
        module=importlib.import_module('emoji_'+family.replace('-','_')+'_svg')
        losses={'1fa95':1} if family=='tools-instruments' else {'1f30f':1} if family=='globes' else {}
        forms,pairs=add_svg_family(root,glyphs,metrics,cmap,layers,palette,review,
                                   outline,family,module.prepare,count,aliases,counter_losses=losses,promotable_components=PROMOTABLE_COMPONENTS)
        sequences+=forms;variations+=pairs
    phoenix_forms,rule=add_phoenix(root,glyphs,metrics,cmap,layers,palette,review,outline)
    return sequences+phoenix_forms,sorted(set(variations)),rule


def add_phoenix(root,glyphs,metrics,cmap,layers,palette,review,outline):
    from emoji_phoenix_svg import KEY,prepare
    spec=json.loads((root/'data/font-sources/noto-emoji-phoenix-svg.json').read_text())
    assert len(spec['files'])==1
    source=spec['files'][0];forms=source['include_sequences'];text='\U0001f426\u200d\U0001f525'
    assert forms==[text]
    # Resolve the existing standalone bird, joiner and fire. Their drawings and
    # metrics remain intact; only the exact joined sequence selects this glyph.
    inputs=[cmap[ord(c)] for c in text]
    assert len(set(inputs))==3
    (paper,*colours,ink),report=prepare(KEY)
    assert report['source']==source and report['appliedStrength']>0 and not report['fallback']
    ys,xs=np.nonzero(paper);bounds=list(map(int,(xs.min(),ys.min(),xs.max(),ys.max())))
    scale=760/max(bounds[2]-bounds[0]+1,bounds[3]-bounds[1]+1)
    transform=bounds[0],bounds[1],scale
    advance=round((bounds[2]-bounds[0]+1)*scale)+100
    name='phoenix.'+KEY;assert name not in glyphs
    glyphs[name],removed=clean_flag_outline(ink,transform,outline)
    counter_review=review_counters(ink,transform,glyphs[name])
    metrics[name]=(advance,50);layers[name]=[];layer_reports=[]
    for i,(mask,rgb) in enumerate([(paper,(255,255,255)),*zip(colours,map(tuple,report['rgbs'])),(ink,(17,17,17))]):
        if rgb not in palette:palette.append(rgb)
        layer=name+f'.layer{i}'
        glyphs[layer],dropped=clean_flag_outline(mask,transform,outline)
        metrics[layer]=(advance,50);layers[name].append((layer,palette.index(rgb)))
        layer_reports.append(dict(glyphName=layer,rgb=rgb,removedZeroAreaContours=dropped))
    review.append(dict(sequence=text,qualificationForms=forms,glyphName=name,category=source['subgroup'],
        source=source['path'],sourceSha256=source['sha256'],sourceRecipe=KEY,bounds=bounds,
        advance=advance,penTreatment=report,layers=layer_reports,counterReview=counter_review,
        removedZeroAreaInkContours=removed,license=spec['license'],notices=spec['notices']))
    return forms,'sub '+' '.join(inputs)+' by '+name+';'
