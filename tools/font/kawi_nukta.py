"""Kawi nukta attachment and identity-preserving above-mark combinations."""
from copy import deepcopy
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.otlLib.builder import buildLigatureSubstSubtable, buildLookup
from hebrew_marks import bounds
from music_mark_rules import extend_mark_rules

POINT = 0x11F5A


def _rules(font, old, new):
    extend_mark_rules(font, old, new, {old: new})
    for lookup in font['GPOS'].table.LookupList.Lookup:
        if lookup.LookupType != 6: continue
        for s in lookup.SubTable:
            if old in s.Mark1Coverage.glyphs:
                s.Mark1Array.MarkRecord.append(deepcopy(s.Mark1Array.MarkRecord[s.Mark1Coverage.glyphs.index(old)]))
                s.Mark1Coverage.glyphs.append(new)
                s.Mark1Array.MarkCount = len(s.Mark1Array.MarkRecord)


def _glyph(font, name, drawing, metrics):
    pen = TTGlyphPen(None); drawing.replay(pen)
    order = list(font.getGlyphOrder()); font['glyf'][name] = pen.glyph()
    font.setGlyphOrder(order + [name])
    font['glyf'][name].recalcBounds(font['glyf'])
    font['hmtx'][name] = (metrics[0], font['glyf'][name].xMin)


def _record(font, name):
    pen = DecomposingRecordingPen(font.getGlyphSet())
    font.getGlyphSet()[name].draw(pen)
    return pen


def add_mark(font, donor):
    old = font.getBestCmap()[0x11F00]; new = 'nuktakawi'
    source = donor.getBestCmap()[POINT]
    a, b = bounds(font, old), bounds(donor, source)
    scale = font['head'].unitsPerEm / donor['head'].unitsPerEm
    aligned = RecordingPen()
    _record(donor, source).replay(TransformPen(aligned, (scale, 0, 0, scale,
        (a[0] + a[2] - (b[0] + b[2]) * scale) / 2, a[1] - b[1] * scale)))
    _glyph(font, new, aligned, (0, 0)); _rules(font, old, new)
    # Four dots use four copies of a donor dot on a square grid. This retains
    # the proposal's four-dot distinction instead of superimposing anusvara.
    contours, contour = [], []
    for op in aligned.value:
        contour.append(op)
        if op[0] == 'closePath': contours.append(contour); contour = []
    assert len(contours) == 3
    dot = RecordingPen(); dot.value = contours[0]
    from fontTools.pens.boundsPen import BoundsPen
    bp = BoundsPen(None); dot.replay(bp); x0,y0,x1,y1 = bp.bounds
    four = RecordingPen(); step = max(x1-x0, y1-y0) + 65
    for x, y in [(0,0),(step,0),(0,step),(step,step)]:
        dot.replay(TransformPen(four,(1,0,0,1,x-x0,y-y0)))
    _glyph(font, 'nuktakawi.four', four, (0,0))
    # Native above-form fusion runs first. Combine nukta with its resulting
    # mark, preserving repha/vowel bodies and native attachment classes.
    hosts = list(font['GPOS'].table.LookupList.Lookup[34].SubTable[0].Mark1Coverage.glyphs)
    hosts.remove(new)
    ligatures = {}
    for host in hosts:
        base = host
        dots = new
        if 'anusvara' in host:
            dots = 'nuktakawi.four'
            base = {'anusvarakawi': None, 'repha_anusvarakawi':'rephakawi',
                'vowelI_anusvarakawi':'vowelIkawi', 'vowelIi_anusvarakawi':'vowelIikawi',
                'vowelEu_anusvarakawi':'vowelEukawi', 'repha_vowelEu_anusvarakawi':'repha_vowelEukawi'}.get(host, host.replace('_anusvarakawi',''))
        target = new + '_' + host
        drawing = RecordingPen()
        if base:
            _record(font, base).replay(drawing)
            box = bounds(font, base); top = box[3] + 70; center = (box[0]+box[2])/2
        else:
            hostbox = bounds(font, host)
            top = hostbox[1]; center = (hostbox[0]+hostbox[2])/2
        dotbox = bounds(font, dots)
        _record(font, dots).replay(TransformPen(drawing,(1,0,0,1,
            center-(dotbox[0]+dotbox[2])/2, top-dotbox[1])))
        _glyph(font,target,drawing,font['hmtx'][host]); _rules(font,host,target)
        ligatures[(new,host)] = target
        ligatures[(host,new)] = target
    table = font['GSUB'].table
    _transparent_nukta(font, new)
    lookup = buildLookup([buildLigatureSubstSubtable(ligatures)], flags=0)
    index = len(table.LookupList.Lookup); table.LookupList.Lookup.append(lookup)
    table.LookupList.LookupCount = index+1
    for record in table.FeatureList.FeatureRecord:
        if record.FeatureTag == 'abvs':
            record.Feature.LookupListIndex.append(index); record.Feature.LookupCount += 1
    for t in font['cmap'].tables:
        if t.isUnicode() and t.format==12: t.cmap[POINT]=new
    notice='\n'.join(sorted({n.toUnicode() for n in donor['name'].names if n.nameID==0}))
    for record in font['name'].names:
        if record.nameID==0: record.string=(record.toUnicode()+'\n'+notice).encode(record.getEncoding())


def _transparent_nukta(font, new):
    # Native contextual rules predate nukta. Ignore only this new mark while
    # selecting original conjunct/vowel forms; retain every original mark's
    # filtering behavior. The final nukta ligature lookup still sees it.
    from fontTools.ttLib.tables import otTables as ot
    gdef=font['GDEF'].table
    sets=getattr(gdef,'MarkGlyphSetsDef',None)
    if sets is None:
        sets=ot.MarkGlyphSetsDef();sets.MarkSetTableFormat=1;sets.Coverage=[]
        gdef.MarkGlyphSetsDef=sets;gdef.Version=max(gdef.Version,0x00010002)
    for lookup in font['GSUB'].table.LookupList.Lookup:
        if lookup.LookupFlag & 8: continue
        coverage=ot.Coverage()
        coverage.glyphs=([n for n in sets.Coverage[lookup.MarkFilteringSet].glyphs if n!=new]
            if lookup.LookupFlag & 16 else [n for n,c in gdef.GlyphClassDef.classDefs.items() if c==3 and n!=new])
        lookup.LookupFlag|=16;lookup.MarkFilteringSet=len(sets.Coverage)
        sets.Coverage.append(coverage)
    sets.MarkSetCount=len(sets.Coverage)
