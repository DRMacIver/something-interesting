"""Supply Unicode mark attachment where math fonts only support math layout.

Keep existing anchors. Missing pairs use the source MATH optical accent point
and the actual glyph bounds. This changes positioning, never the source curves.
"""
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import hashlib,json
from fontTools.pens.boundsPen import BoundsPen
from fontTools.otlLib.builder import buildAnchor,buildCoverage,buildLookup,buildMarkBasePosSubtable,buildMarkGlyphSetsDef
from fontTools.ttLib.tables import otTables as ot


def unicode_categories(root):
    path=Path(root)/'data/unicode/18.0.0/UnicodeData.txt'
    expected=next(e['sha256'] for e in json.loads((Path(root)/'data/unicode/sources.json').read_text())['files'] if e['path']=='18.0.0/UnicodeData.txt')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
    return {int(f[0],16):(f[2],int(f[3])) for row in path.read_text().splitlines() if (f:=row.split(';'))}


def repair_marks(font,bases,categories):
    glyph_map=font.getReverseGlyphMap();gs=font.getGlyphSet();cmap=font.getBestCmap()
    bounds={}
    def box(name):
        if name not in bounds:
            pen=BoundsPen(gs);gs[name].draw(pen);bounds[name]=pen.bounds
        return bounds[name]
    bases={n for n in bases if box(n)}
    gap=round(font['head'].unitsPerEm*.035)
    marks={};styles={};normalized=[]
    for cp,name in cmap.items():
        category,ccc=categories.get(cp,('',0))
        if category not in {'Mn','Me'} or not box(name):continue
        advance,bearing=font['hmtx'][name]
        if advance:
            font['hmtx'][name]=(0,bearing);normalized.append(name)
        x0,y0,x1,y1=box(name)
        # Positional classes describe the destination, not where an unplaced
        # source drawing happens to sit relative to its own origin.
        group='overlay' if ccc==1 or category=='Me' else 'left' if ccc==224 else 'right' if ccc==226 else 'below' if ccc in {200,202,204,218,220,222,233,240} else 'above' if ccc in {8,214,216,228,230,232,234} else 'below' if y1<=0 else 'above'
        marks[name]=group
        styles[name]=('left' if ccc in {200,218,228} else 'right' if ccc in {8,216,222,232} else 'center',ccc in {200,202,214,216})
    gdef=font['GDEF'].table
    if gdef.GlyphClassDef is None:
        gdef.GlyphClassDef=ot.ClassDef();gdef.GlyphClassDef.classDefs={}
    for name in marks:gdef.GlyphClassDef.classDefs[name]=3
    layout=font['GPOS'].table
    supported=defaultdict(set)
    for lookup in layout.LookupList.Lookup:
        for sub in lookup.SubTable:
            sub=getattr(sub,'ExtSubTable',sub)
            if not hasattr(sub,'BaseCoverage'):continue
            for mark,record in zip(sub.MarkCoverage.glyphs,sub.MarkArray.MarkRecord):
                if mark not in marks:continue
                for base,base_record in zip(sub.BaseCoverage.glyphs,sub.BaseArray.BaseRecord):
                    if base in bases and base_record.BaseAnchor[record.Class] is not None:supported[mark].add(base)
    optical={}
    if 'MATH' in font:
        accents=font['MATH'].table.MathGlyphInfo.MathTopAccentAttachment
        if accents:optical={n:r.Value for n,r in zip(accents.TopAccentCoverage.glyphs,accents.TopAccentAttachment)}
    def base_anchor(name,group,align='center'):
        x0,y0,x1,y1=box(name);x=optical.get(name,round((x0+x1)/2));y=round((y0+y1)/2)
        if align!='center':x=round(x0 if align=='left' else x1)
        return buildAnchor(x,round(y1)) if group=='above' else buildAnchor(x if align!='center' else round((x0+x1)/2),round(y0)) if group=='below' else buildAnchor(round(x0),y) if group=='left' else buildAnchor(round(x1),y) if group=='right' else buildAnchor(round((x0+x1)/2),y)
    def mark_anchor(name,group,attached=False):
        x0,y0,x1,y1=box(name);x=round((x0+x1)/2);y=round((y0+y1)/2)
        separation=0 if attached else gap
        return buildAnchor(x,round(y0)-separation) if group=='above' else buildAnchor(x,round(y1)+separation) if group=='below' else buildAnchor(round(x1)+separation,y) if group=='left' else buildAnchor(round(x0)-separation,y) if group=='right' else buildAnchor(x,y)
    def feature(tag,indices):
        records=layout.FeatureList.FeatureRecord
        found=[i for i,r in enumerate(records) if r.FeatureTag==tag]
        if not found:
            record=ot.FeatureRecord();record.FeatureTag=tag;record.Feature=ot.Feature();record.Feature.FeatureParams=None;record.Feature.LookupListIndex=[];record.Feature.LookupCount=0
            records.append(record);found=[len(records)-1];layout.FeatureList.FeatureCount=len(records)
        for i in found:
            f=records[i].Feature;f.LookupListIndex.extend(indices);f.LookupCount=len(f.LookupListIndex)
        if not any(r.ScriptTag=='DFLT' for r in layout.ScriptList.ScriptRecord):
            record=ot.ScriptRecord();record.ScriptTag='DFLT';record.Script=ot.Script();record.Script.DefaultLangSys=None;record.Script.LangSysRecord=[];record.Script.LangSysCount=0
            layout.ScriptList.ScriptRecord.insert(0,record);layout.ScriptList.ScriptCount=len(layout.ScriptList.ScriptRecord)
        for record in layout.ScriptList.ScriptRecord:
            if record.Script.DefaultLangSys is None:
                lang=ot.LangSys();lang.LookupOrder=None;lang.ReqFeatureIndex=0xffff;lang.FeatureIndex=[];lang.FeatureCount=0;record.Script.DefaultLangSys=lang
            for lang in [record.Script.DefaultLangSys,*[r.LangSys for r in record.Script.LangSysRecord]]:
                for i in found:
                    if i not in lang.FeatureIndex:lang.FeatureIndex.append(i)
                lang.FeatureCount=len(lang.FeatureIndex)
    def append(lookup):
        index=len(layout.LookupList.Lookup);layout.LookupList.Lookup.append(lookup);layout.LookupList.LookupCount=index+1;return index
    groups=defaultdict(list)
    for mark,group in marks.items():
        missing=tuple(sorted(bases-supported[mark],key=glyph_map.get))
        if missing:groups[(group,*styles[mark],missing)].append(mark)
    indices=[];pairs=0
    for (group,align,attached,missing),names in sorted(groups.items()):
        sub=buildMarkBasePosSubtable({n:(0,mark_anchor(n,group,attached)) for n in names},{n:{0:base_anchor(n,group,align)} for n in missing},glyph_map)
        indices.append(append(buildLookup([sub],table='GPOS')));pairs+=len(names)*len(missing)
    if indices:feature('mark',indices)
    # Native mkmk tables already know how to stack the source marks. When a
    # math font has none, add same-side stacks and filter out the opposite side.
    native_mkmk=sorted({i for r in layout.FeatureList.FeatureRecord if r.FeatureTag=='mkmk' for i in r.Feature.LookupListIndex})
    if native_mkmk and indices:
        # Some native above-mark filtering sets also contain below marks. That
        # makes an above accent attach to a preceding below accent. Keep native
        # same-side anchor geometry, but skip marks on the opposite side.
        sets=gdef.MarkGlyphSetsDef
        for i in native_mkmk:
            lookup=layout.LookupList.Lookup[i]
            sides={marks[n] for sub in lookup.SubTable for n in sub.Mark1Coverage.glyphs if n in marks}
            if len(sides)!=1 or next(iter(sides)) not in {'above','below'}:continue
            side=next(iter(sides))
            allowed=set(sets.Coverage[lookup.MarkFilteringSet].glyphs)
            allowed={n for n in allowed if n not in marks or marks[n]==side}
            lookup.MarkFilteringSet=len(sets.Coverage)
            sets.Coverage.append(buildCoverage(allowed,glyph_map));sets.MarkSetCount=len(sets.Coverage)
        # Run the native stacks after the newly appended base attachment too.
        # Keep original lookup indices valid for contextual positioning rules.
        feature('mkmk',[append(deepcopy(layout.LookupList.Lookup[i])) for i in native_mkmk])
    elif not native_mkmk:
        sets=getattr(gdef,'MarkGlyphSetsDef',None)
        mark_sets=[set(c.glyphs) for c in sets.Coverage] if sets else []
        indices=[]
        for group in ['above','below']:
            names=[n for n,g in marks.items() if g==group]
            if not names:continue
            a=buildMarkBasePosSubtable({n:(0,mark_anchor(n,group)) for n in names},{n:{0:base_anchor(n,group)} for n in names},glyph_map)
            sub=ot.MarkMarkPos();sub.Format=1;sub.Mark1Coverage=a.MarkCoverage;sub.Mark2Coverage=a.BaseCoverage;sub.ClassCount=1;sub.Mark1Array=a.MarkArray;sub.Mark2Array=ot.Mark2Array();sub.Mark2Array.Mark2Count=a.BaseArray.BaseCount;sub.Mark2Array.Mark2Record=[]
            for r in a.BaseArray.BaseRecord:
                record=ot.Mark2Record();record.Mark2Anchor=r.BaseAnchor;sub.Mark2Array.Mark2Record.append(record)
            index=len(mark_sets);mark_sets.append(set(names));indices.append(append(buildLookup([sub],markFilterSet=index,table='GPOS')))
        if indices:
            gdef.Version=max(gdef.Version,0x00010002);gdef.MarkGlyphSetsDef=buildMarkGlyphSetsDef(mark_sets,glyph_map);feature('mkmk',indices)
    return dict(markGlyphs=len(marks),normalizedMarkAdvances=sorted(normalized),missingBaseMarkPairsRepaired=pairs,method='source MATH optical accent points and glyph ink bounds; native same-side anchors preserved; opposite-side stack marks skipped')
