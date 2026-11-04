"""Keep native CJK variants with the app's licensed, hand-treated accents.

Additional opt-in fonts only: no existing source font is replaced. The native
TrueType drawings, metrics, instructions and UVS remain intact. Adapt only the
borrowed CFF marks to each donor's TrueType grid, then add geometric attachment
for those new marks. Native CJK marks retain their original positioning path.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import io
from pathlib import Path

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables as ot
from fontTools.otlLib.builder import buildAnchor, buildLookup, buildMarkBasePosSubtable
import uharfbuzz as hb

from math_unicode_marks import repair_marks, unicode_categories
from native_variations import variation_ranges
from build_scripts import ranges

ROOT=Path(__file__).resolve().parents[2]
DONOR=ROOT/'assets/fonts/dad-lettering-unicode.woff2'
MANIFEST=ROOT/'js/marked-cjk-variant-manifest.js'


def read_manifest(path):
    return json.loads(path.read_text().split('export default ',1)[1].rstrip(';\n'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_accents(font, donor, categories):
    original=font.getBestCmap()
    source=donor.getBestCmap()
    points={cp for cp in source if categories.get(cp,('',0))[0] in {'Mn','Me'} and cp not in original}
    scale=font['head'].unitsPerEm/donor['head'].unitsPerEm
    gs=donor.getGlyphSet()
    order=list(font.getGlyphOrder())
    for cp in sorted(points):
        name=f'foreignAccent.u{cp:X}'
        assert name not in order
        pen=TTGlyphPen(None)
        # Maximum cubic approximation error: 0.05 target font units, before
        # normal integer TrueType point quantization. Source mark shapes only.
        gs[source[cp]].draw(TransformPen(Cu2QuPen(pen,max_err=.05,reverse_direction=True),(scale,0,0,scale,0,0)))
        glyph=pen.glyph();font['glyf'][name]=glyph
        glyph.recalcBounds(font['glyf'])
        font['hmtx'][name]=(0,getattr(glyph,'xMin',0))
        if 'vmtx' in font:font['vmtx'][name]=(font['head'].unitsPerEm,0)
        for table in font['cmap'].tables:
            if table.isUnicode() and (table.format==12 or table.format==4 and cp<=0xffff):table.cmap[cp]=name
        order.append(name)
    font.setGlyphOrder(order)
    if 'GDEF' not in font:
        font['GDEF']=newTable('GDEF');g=ot.GDEF();g.Version=0x10000
        g.GlyphClassDef=None;g.AttachList=None;g.LigCaretList=None;g.MarkAttachClassDef=None
        font['GDEF'].table=g
    if 'GPOS' not in font:
        font['GPOS']=newTable('GPOS');layout=ot.GPOS();layout.Version=0x10000
        layout.ScriptList=ot.ScriptList();layout.ScriptList.ScriptRecord=[];layout.ScriptList.ScriptCount=0
        layout.FeatureList=ot.FeatureList();layout.FeatureList.FeatureRecord=[];layout.FeatureList.FeatureCount=0
        layout.LookupList=ot.LookupList();layout.LookupList.Lookup=[];layout.LookupList.LookupCount=0
        font['GPOS'].table=layout
    bases={name for cp,name in original.items() if not categories.get(cp,('',0))[0].startswith('M')}
    for table in font['cmap'].tables:
        if table.format==14:
            bases.update(name or original[cp] for rows in table.uvsDict.values() for cp,name in rows)
    # Limit the category map to added points so the shared attachment helper
    # cannot change any native CJK mark classes, advances or positioning.
    attachment=repair_marks(font,bases,{cp:categories[cp] for cp in points})
    return points,attachment


def retain_native_mark_positions(font, source_path):
    """Encode the original font's single-mark fallback positions explicitly.

    Installing GPOS suppresses HarfBuzz's fallback positioning. Use its original
    glyph-specific results, including corner tone marks and spacing kana marks,
    rather than replacing them with the foreign accents' generic anchors.
    """
    original=TTFont(source_path,recalcTimestamp=False,recalcBBoxes=False)
    cmap=original.getBestCmap()
    marks={cp:cmap[cp] for cp in [*range(0x302a,0x3030),0x3099,0x309a] if cp in cmap}
    if not marks:return 0
    sequences={name:chr(cp) for cp,name in cmap.items() if cp not in marks}
    for table in original['cmap'].tables:
        if table.format==14:
            for selector,pairs in table.uvsDict.items():
                for cp,name in pairs:sequences[name or cmap[cp]]=chr(cp)+chr(selector)
    original.flavor=None;stream=io.BytesIO();original.save(stream)
    shaping=hb.Font(hb.Face(stream.getvalue()))
    anchors={}
    for name,sequence in sequences.items():
        values={}
        for group,(cp,mark) in enumerate(marks.items()):
            buffer=hb.Buffer();buffer.add_str(sequence+chr(cp));buffer.guess_segment_properties();hb.shape(shaping,buffer)
            info=buffer.glyph_infos;positions=buffer.glyph_positions
            assert len(info)==2 and info[0].codepoint==original.getGlyphID(name) and info[1].codepoint==original.getGlyphID(mark),(source_path,name,cp)
            assert positions[0].x_offset==positions[0].y_offset==positions[1].x_advance==0
            values[group]=buildAnchor(positions[0].x_advance+positions[1].x_offset,positions[1].y_offset)
        anchors[name]=values
    sub=buildMarkBasePosSubtable({name:(i,buildAnchor(0,0)) for i,name in enumerate(marks.values())},anchors,font.getReverseGlyphMap())
    layout=font['GPOS'].table;index=len(layout.LookupList.Lookup)
    layout.LookupList.Lookup.append(buildLookup([sub],table='GPOS'));layout.LookupList.LookupCount=index+1
    for record in layout.FeatureList.FeatureRecord:
        if record.FeatureTag=='mark':
            record.Feature.LookupListIndex.append(index);record.Feature.LookupCount=len(record.Feature.LookupListIndex)
    return len(anchors)*len(marks)


def build(only=None):
    scripts=read_manifest(ROOT/'js/font-manifest.js')['fonts']
    sources=[read_manifest(ROOT/'js/cjk-variant-manifest.js'),*[e for e in scripts if 'Jigmo' in e['source'] and e.get('nativeVariations')]]
    assert len(sources)==92
    donor=TTFont(DONOR);categories=unicode_categories(ROOT)
    previous=read_manifest(MANIFEST) if MANIFEST.exists() else []
    cached={e['baseVariantFamily']:e for e in (previous if isinstance(previous,list) else previous['fonts'])}
    recipe=':'.join(sha(p) for p in [Path(__file__),ROOT/'tools/font/math_unicode_marks.py',DONOR])
    entries=[]
    for source in sources:
        if only and source['family']!=only:continue
        source_path=ROOT/source['file'];assert sha(source_path)==source['sha256']
        old=cached.get(source['family'])
        if old and old['recipe']==recipe and old['sourceSha256']==source['sha256'] and (ROOT/old['file']).exists() and sha(ROOT/old['file'])==old['sha256']:
            entries.append(old);continue
        font=TTFont(source_path,recalcTimestamp=False,recalcBBoxes=False)
        points,attachment=add_accents(font,donor,categories)
        attachment['nativeSingleMarkPositionsRetained']=retain_native_mark_positions(font,source_path)
        identity=hashlib.sha256(source['family'].encode()).hexdigest()[:12]
        family='Dad Marked CJK '+identity
        for record in font['name'].names:
            if record.nameID in {1,2,3,4,6,16,17}:
                value='Regular' if record.nameID in {2,17} else family.replace(' ','') if record.nameID==6 else family
                record.string=value.encode(record.getEncoding(),errors='replace')
        font['name'].setName('CJK drawings: Jigmo, CC0. Added combining marks: '+donor['name'].getDebugName(0),0,3,1,0x409)
        font['name'].setName('SIL Open Font License 1.1; native CJK donor CC0. See font source notices.',13,3,1,0x409)
        font['name'].setName('Modified 2026-11-03: renamed; copied the recorded base CJK drawings, advances and instructions, including its existing pen finish. Borrowed the app lettering accents, converted them to TrueType and attached them to the base variant forms.',10,3,1,0x409)
        font['head'].created=font['head'].modified=2082844800
        font.recalcTimestamp=False;font.flavor='woff2'
        target=ROOT/f'assets/fonts/scripts/marked-cjk-{identity}.woff2'
        temporary=target.with_suffix('.tmp.woff2')
        font.save(temporary);temporary.replace(target)
        entry=dict(family=family,variationOnly=True,baseVariantFamily=source['family'],file=target.relative_to(ROOT).as_posix(),sha256=sha(target),bytes=target.stat().st_size,source=source['file'],sourceSha256=source['sha256'],markSource=DONOR.relative_to(ROOT).as_posix(),markSourceSha256=sha(DONOR),recipe=recipe,ranges=ranges(font.getBestCmap()),nativeVariations=variation_ranges(font),addedMarks=ranges(points),markAttachment=attachment,licence='assets/fonts/licenses/Noto-OFL.txt',notices=['assets/fonts/licenses/Jigmo-CC0.txt','assets/fonts/licenses/Noto-OFL.txt','assets/fonts/licenses/Unicodia-LICENSE-Funky.txt'],style='Recorded base CJK drawings and existing finish retained; handwritten accents adapted to TrueType. Specialist review provisional.')
        if source.get('denseTreatment'):
            inherited=source['denseTreatment']
            entry['inheritedDenseTreatment']=dict(method=inherited['method'],recipeSha256=inherited['recipeSha256'],sourceFile=source['file'],sourceSha256=source['sha256'])
        entries.append(entry)
        print(f'{source["family"]}: {len(points)} extra marks, {entry["bytes"]} bytes',flush=True)
    if only:
        target=ROOT/'output/font-review/marked-cjk-prototype.json'
        target.write_text(json.dumps(entries,indent=2)+'\n')
    else:
        MANIFEST.write_text('// Generated by tools/font/build_marked_cjk_variants.py\nexport default '+json.dumps(dict(unicode='18.0.0',fonts=entries),separators=(',',':'))+';\n')
    print(f'{len(entries)} marked CJK fonts, {sum(e["bytes"] for e in entries):,} bytes',flush=True)
    return entries


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--only');args=parser.parse_args();build(args.only)
