"""Native Sharada Kashmiri vowels: detached marks and preserved AA ligatures."""
from copy import deepcopy
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from hebrew_marks import bounds
from music_mark_rules import extend_mark_rules

REFERENCES={0x11b60:0x111bc,0x11b62:0x111b6,0x11b63:0x111b7,
            0x11b64:0x111bc,0x11b66:0x111bc}
COMPOSITES={0x11b61:0xe0185,0x11b65:0xe0186,0x11b67:0xe0187}
POINTS=set(REFERENCES)|set(COMPOSITES)
SELECTORS={cp:0xe0180+i for i,cp in enumerate(sorted(REFERENCES))}


def record(font,name):
    p=DecomposingRecordingPen(font.getGlyphSet());font.getGlyphSet()[name].draw(p);return p


def add_glyph(font,name,drawing,advance=0):
    p=TTGlyphPen(None);drawing.replay(p);order=list(font.getGlyphOrder())
    font['glyf'][name]=p.glyph();font.setGlyphOrder(order+[name])
    font['glyf'][name].recalcBounds(font['glyf'])
    font['hmtx'][name]=(advance,font['glyf'][name].xMin)


def add_marks(font,donor):
    cmap=font.getBestCmap()
    notice='\n'.join(sorted({n.toUnicode() for n in donor['name'].names if n.nameID==0}))
    for n in font['name'].names:
        if n.nameID==0 and notice not in n.toUnicode():
            n.string=(n.toUnicode()+'\n'+notice).encode(n.getEncoding())
    for cp,refcp in REFERENCES.items():
        assert cp not in cmap
        old=cmap[refcp];new=f'kashmiri{cp:X}'
        # Preserve every contextual below-mark position, not its old vowel body.
        originals=[n for n in font.getGlyphOrder() if n==old or n.startswith(old+'.alt')]
        outputs={name:new+name[len(old):] for name in originals}
        a,b=bounds(font,old),bounds(donor,donor.getBestCmap()[cp])
        scale=font['head'].unitsPerEm/donor['head'].unitsPerEm
        dx=(a[0]+a[2]-(b[0]+b[2])*scale)/2
        dy=(a[3]-b[3]*scale) if cp in (0x11b62,0x11b63) else (a[1]-b[1]*scale)
        for original,target in outputs.items():
            box=bounds(font,original)
            x=dx+(box[0]+box[2]-a[0]-a[2])/2
            y=dy+(box[3]-a[3] if cp in (0x11b62,0x11b63) else box[1]-a[1])
            drawing=RecordingPen();record(donor,donor.getBestCmap()[cp]).replay(
                TransformPen(drawing,(scale,0,0,scale,x,y)))
            add_glyph(font,target,drawing)
        for original,target in outputs.items():
            extend_mark_rules(font,original,target,outputs)
            for lookup in font['GPOS'].table.LookupList.Lookup:
                if lookup.LookupType!=6:continue
                for s in lookup.SubTable:
                    if original in s.Mark1Coverage.glyphs:
                        s.Mark1Array.MarkRecord.append(deepcopy(s.Mark1Array.MarkRecord[s.Mark1Coverage.glyphs.index(original)]))
                        s.Mark1Coverage.glyphs.append(target);s.Mark1Array.MarkCount=len(s.Mark1Array.MarkRecord)
                    if target in s.Mark2Coverage.glyphs:
                        anchors=s.Mark2Array.Mark2Record[s.Mark2Coverage.glyphs.index(target)].Mark2Anchor
                        oldbox,newbox=bounds(font,original),bounds(font,target)
                        delta=newbox[3]-oldbox[3] if refcp==0x111bc else newbox[1]-oldbox[1]
                        for anchor in anchors:
                            if anchor:anchor.YCoordinate+=round(delta)
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format==12:table.cmap[cp]=new
    _add_right_vowels(font,donor)
    _below_clearance(font)
    uvs=CmapSubtable.newSubtable(14);uvs.platformID,uvs.platEncID,uvs.language=0,5,0;uvs.cmap={}
    uvs.uvsDict={SELECTORS[cp]:[(ref,font.getBestCmap()[cp])] for cp,ref in REFERENCES.items()}
    uvs.uvsDict.update({selector:[(0x111b3,font.getBestCmap()[cp])] for cp,selector in COMPOSITES.items()})
    font['cmap'].tables.append(uvs)


def _below_clearance(font):
    """Give detached arcs their own class without moving native connected U/UU."""
    from fontTools.ttLib.tables import otTables as ot
    def anchor(x,y):
        a=ot.Anchor();a.Format=1;a.XCoordinate=round(x);a.YCoordinate=round(y);return a
    for lookup in font['GPOS'].table.LookupList.Lookup:
        if lookup.LookupType!=4:continue
        for s in lookup.SubTable:
            indices=[i for i,n in enumerate(s.MarkCoverage.glyphs)
                     if n.startswith(('kashmiri11B62','kashmiri11B63'))]
            if not indices:continue
            original_class=s.MarkArray.MarkRecord[indices[0]].Class
            new_class=s.ClassCount;s.ClassCount+=1
            for name,r in zip(s.BaseCoverage.glyphs,s.BaseArray.BaseRecord):
                box=bounds(font,name);old=r.BaseAnchor[original_class]
                if box:
                    r.BaseAnchor.append(anchor(old.XCoordinate if old else (box[0]+box[2])/2,
                                               box[1]))
                else:r.BaseAnchor.append(None)
            for i in indices:
                box=bounds(font,s.MarkCoverage.glyphs[i]);r=s.MarkArray.MarkRecord[i]
                r.Class=new_class;r.MarkAnchor=anchor((box[0]+box[2])/2,box[3]+50)


def _add_right_vowels(font,donor):
    from indic_input_rules import extend_inputs
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates
    old=font.getBestCmap()[0x111b3]
    # Native modifier anchors retain the right-side placement on fused AA forms.
    anchors={}
    for lookup in font['GPOS'].table.LookupList.Lookup:
        if lookup.LookupType!=4:continue
        for sub in lookup.SubTable:
            if 'VowelModifier' not in sub.MarkCoverage.glyphs:continue
            cls=sub.MarkArray.MarkRecord[sub.MarkCoverage.glyphs.index('VowelModifier')].Class
            for name,r in zip(sub.BaseCoverage.glyphs,sub.BaseArray.BaseRecord):
                if r.BaseAnchor[cls] and name not in anchors:
                    a=r.BaseAnchor[cls];anchors[name]=(a.XCoordinate,a.YCoordinate)
    origin=anchors[old]
    # Four native fused forms lack modifier anchors. Their right-side stems
    # remain identifiable in the original outline at the 550/625 headline.
    for host in ('RJaa','RNnaa','SsNnaa','SsTtaa'):
        pts,_,_=font['glyf'][host].getCoordinates(font['glyf'])
        right=max(x for x,y in pts if y==625)
        left=max(x for x,y in pts if y==550 and x<right)
        anchors[host]=(origin[0]+(left+right)/2-101.5,origin[1])
    for cp in COMPOSITES:
        name=f'kashmiri{cp:X}';source=donor.getBestCmap()[cp]
        add_glyph(font,name,record(donor,source),font['hmtx'][old][0])
        # The source's lower body is exactly native AA. Extract only the extra
        # top part for fused consonant-AA forms, retaining its curve flags.
        glyph=deepcopy(donor['glyf'][source]);pts,ends,flags=glyph.getCoordinates(donor['glyf'])
        indices={0x11b61:[0,1,2,11],0x11b65:list(range(8,18)),0x11b67:list(range(12))}[cp]
        glyph.coordinates=GlyphCoordinates([pts[i] for i in indices])
        glyph.flags=flags.__class__([flags[i] for i in indices])
        glyph.endPtsOfContours=[len(indices)-1];glyph.numberOfContours=1
        extension=RecordingPen();glyph.draw(extension,donor['glyf'])
        extend_inputs(font,old,name)
        for lookup in font['GSUB'].table.LookupList.Lookup:
            for sub in lookup.SubTable:
                if not hasattr(sub,'ligatures'):continue
                for head,ligatures in sub.ligatures.items():
                    for lig in ligatures:
                        if name not in [head,*lig.Component]:continue
                        base=lig.LigGlyph;target=base+'.'+name
                        if target not in font.getGlyphOrder():
                            assert base in anchors,base
                            x,y=anchors[base];drawing=record(font,base)
                            extension.replay(TransformPen(drawing,(1,0,0,1,x-origin[0],y-origin[1])))
                            add_glyph(font,target,drawing,font['hmtx'][base][0])
                            # Base positioning/GDEF of fused forms must survive.
                            from music_mark_rules import extend_mark_rules
                            extend_mark_rules(font,base,target,{base:target})
                        lig.LigGlyph=target
        for table in font['cmap'].tables:
            if table.isUnicode() and table.format==12:table.cmap[cp]=name
