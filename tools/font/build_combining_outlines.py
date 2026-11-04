"""Export licensed nonspacing mark drawings for dynamic enclosure layout.

These are drawings, not replacements for native script shaping. Native text is
still shaped by its original font; the renderer uses these paths only where a
mark has to follow a dynamically sized enclosure or span two bases.
"""
import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.areaPen import AreaPen

from math_unicode_marks import unicode_categories

ROOT=Path(__file__).resolve().parents[2]
SUPPLIED_NOTICES={
    'build/unicode-sources/noto-gurung/NotoSansGurungKhema.ttf':'assets/fonts/licenses/Noto-gurung-OFL.txt',
    'build/unicode-sources/noto-olonal/NotoSerifOlOnal.ttf':'assets/fonts/licenses/Noto-olonal-OFL.txt',
    'build/unicode-sources/unicodia/UnicodiaDaarage.otf':'assets/fonts/licenses/Unicodia-LICENSE-Daarage.txt',
}


def read_manifest(path):
    return json.loads(path.read_text().split('export default ',1)[1].rstrip(';\n'))


def enclosure_contours(gs,name,unit):
    drawing=DecomposingRecordingPen(gs);gs[name].draw(drawing)
    parts=[];part=RecordingPen()
    for operation,args in drawing.value:
        getattr(part,operation)(*args)
        if operation not in {'closePath','endPath'}:continue
        path=SVGPathPen(None,ntos=lambda n:f'{n:.6f}'.rstrip('0').rstrip('.') if n else '0')
        bounds=BoundsPen(None);area=AreaPen(None)
        for pen in [path,bounds,area]:part.replay(TransformPen(pen,(unit,0,0,-unit,0,0)))
        parts.append(dict(path=path.getCommands(),bounds=[round(v,6) for v in bounds.bounds],area=round(area.value,9)))
        part=RecordingPen()
    return parts


def native_drawing(gs,name,unit):
    pen=SVGPathPen(gs,ntos=lambda n:f'{n:.6f}'.rstrip('0').rstrip('.') if n else '0')
    gs[name].draw(TransformPen(pen,(unit,0,0,-unit,0,0)))
    bounds=BoundsPen(gs);gs[name].draw(bounds)
    box=[round(v,6) for v in (bounds.bounds[0]*unit,-bounds.bounds[3]*unit,bounds.bounds[2]*unit,-bounds.bounds[1]*unit)] if bounds.bounds else None
    return dict(path=pen.getCommands(),bounds=box)


def numeric_enclosure(gs,name,unit,cp):
    parts=enclosure_contours(gs,name,unit)
    if cp in {0x488,0x489,0xa670}:
        assert len(parts)==8
        return dict(kind='radial',parts=parts)
    if cp==0xa671:
        assert len(parts)==2
        # These brackets have only straight segments. Keep every original
        # vertex so widening can extend the bars without thickening the legs.
        drawing=DecomposingRecordingPen(gs);gs[name].draw(drawing)
        vertices=[];index=0
        for operation,args in drawing.value:
            assert operation in {'moveTo','lineTo','closePath'}
            if operation=='closePath':
                parts[index]['vertices']=vertices;vertices=[];index+=1
            else:vertices.extend([[round(x*unit,6),round(-y*unit,6)] for x,y in args])
        return dict(kind='brackets',parts=parts)
    assert cp==0xa672 and len(parts)==10
    groups={side:[] for side in ['top','left','right','bottom']}
    for part in parts:
        x0,y0,x1,y1=part['bounds'];x=(x0+x1)/2
        side='left' if x<-.25 else 'right' if x>.25 else 'top' if y1<0 else 'bottom'
        groups[side].append(part)
    assert [len(v) for v in groups.values()]==[1,3,3,3]
    return dict(kind='sides',parts=[dict(side=side,path=''.join(p['path'] for p in values),bounds=[min(p['bounds'][0] for p in values),min(p['bounds'][1] for p in values),max(p['bounds'][2] for p in values),max(p['bounds'][3] for p in values)]) for side,values in groups.items()])


def source_record(path,entry,digest):
    font=TTFont(path)
    extra=SUPPLIED_NOTICES.get(entry.get('source'))
    jigmo='/jigmo/' in entry.get('source','')
    result=dict(file=entry['file'],sha256=digest,source=entry.get('source'),copyright=font['name'].getDebugName(0),licence=font['name'].getDebugName(13) or ('CC0 1.0 Universal' if jigmo else None),licenceURL=font['name'].getDebugName(14),notices=entry.get('notices',[])+([extra] if extra else [])+(['assets/fonts/licenses/Jigmo-CC0.txt'] if jigmo else []),suppliedNotice=(ROOT/extra).read_text() if extra else None)
    font.close()
    return result


def build():
    categories=unicode_categories(ROOT)
    wanted={cp for cp,(cat,_) in categories.items() if cat in {'Mn','Me'}}
    property_path=ROOT/'data/unicode/18.0.0/DerivedCoreProperties.txt'
    pin=next(e['sha256'] for e in json.loads((ROOT/'data/unicode/sources.json').read_text())['files'] if e['path']=='18.0.0/DerivedCoreProperties.txt')
    assert hashlib.sha256(property_path.read_bytes()).hexdigest()==pin
    ignored=set()
    for row in property_path.read_text().splitlines():
        fields=row.split('#')[0].strip().split(';')
        if len(fields)<2 or fields[1].strip()!='Default_Ignorable_Code_Point':continue
        bounds=fields[0].strip().split('..');ignored.update(range(int(bounds[0],16),int(bounds[-1],16)+1))
    behavioural={cp:dict(category=categories[cp][0],ccc=categories[cp][1]) for cp in wanted&ignored}
    wanted-=ignored
    scripts=read_manifest(ROOT/'js/font-manifest.js')['fonts']
    # Prefer existing hand-treated accents, then handwritten enclosure forms.
    wenkai=next(e for e in scripts if e['source'].endswith('/LXGWWenKai-Regular.ttf') and any(a<=0x20dd<=b for a,b in e['ranges']))
    fonts=[dict(family='Dad Combining Outlines',file='assets/fonts/dad-lettering-unicode.woff2'),{**wenkai,'only':[0x20dd,0x20de]},*scripts]
    drawings={};sources=[]
    for entry in fonts:
        if 'ranges' in entry and not any(any(a<=cp<=b for a,b in entry['ranges']) for cp in wanted-drawings.keys()):continue
        path=ROOT/entry['file'];digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if 'sha256' in entry:assert digest==entry['sha256']
        font=TTFont(path);cmap=font.getBestCmap()
        points=(wanted-drawings.keys())&cmap.keys()
        if 'only' in entry:points&=set(entry['only'])
        if not points:continue
        source_index=len(sources)
        extra=SUPPLIED_NOTICES.get(entry.get('source'))
        sources.append(dict(file=entry['file'],sha256=digest,source=entry.get('source'),copyright=font['name'].getDebugName(0),licence=font['name'].getDebugName(13),licenceURL=font['name'].getDebugName(14),notices=entry.get('notices',[])+([extra] if extra else []),suppliedNotice=(ROOT/extra).read_text() if extra else None))
        unit=1/font['head'].unitsPerEm;gs=font.getGlyphSet()
        for cp in sorted(points):
            name=cmap[cp]
            drawings[cp]=dict(**native_drawing(gs,name,unit),ccc=categories[cp][1],category=categories[cp][0],source=source_index,glyph=name)
            if cp in {0x488,0x489,0xa670,0xa671,0xa672}:
                drawings[cp]['numericEnclosure']=numeric_enclosure(gs,name,unit,cp)
            if cp in {0x1abe,0x20dd,0x20de,0x20df,0x20e0,0x20e2,0x20e3,0x20e4}:
                contours=enclosure_contours(gs,name,unit)
                if len(contours)==2 and contours[0]['area']*contours[1]['area']<0:
                    outer,inner=sorted(contours,key=lambda e:abs(e['area']),reverse=True)
                    drawings[cp]['ring']=dict(outer=outer,inner=inner)
                elif cp in {0x20e0,0x20e3}:
                    outer=max(contours,key=lambda e:abs(e['area']))
                    holes=[e for e in contours if e['area']*outer['area']<0]
                    assert holes
                    # The keycap has a decorative recess as well as its actual
                    # writing surface. The cancelled circle has two half holes.
                    if cp==0x20e3:drawings[cp]['contentBounds']=max(holes,key=lambda e:abs(e['area']))['bounds']
                    else:drawings[cp]['contentBounds']=[min(h['bounds'][0] for h in holes),min(h['bounds'][1] for h in holes),max(h['bounds'][2] for h in holes),max(h['bounds'][3] for h in holes)]
    missing=wanted-drawings.keys()
    assert not missing,sorted(hex(cp) for cp in missing)
    # A missing mark can interrupt a native variation cluster. Keep its native
    # prefix shaped intact, and retain the exact source drawing for native marks
    # that must move outside an intervening foreign mark. Deduplicate geometry,
    # not provenance: every family/point retains its own source and glyph name.
    variants=[read_manifest(ROOT/'js/cjk-variant-manifest.js'),read_manifest(ROOT/'js/math-variant-manifest.js'),*[e for e in scripts if e.get('nativeVariations')],*read_manifest(ROOT/'js/marked-cjk-variant-manifest.js')['fonts']]
    variant_drawings=[];drawing_ids={};variation_marks={}
    source_ids={s['file']:i for i,s in enumerate(sources)}
    for entry in variants:
        path=ROOT/entry['file'];digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest==entry['sha256']
        font=TTFont(path);cmap=font.getBestCmap();gs=font.getGlyphSet();unit=1/font['head'].unitsPerEm
        points=wanted&cmap.keys()
        if not points:continue
        if entry['file'] not in source_ids:
            source_ids[entry['file']]=len(sources);sources.append(source_record(path,entry,digest))
        rows={}
        for cp in sorted(points):
            drawing=native_drawing(gs,cmap[cp],unit)
            key=json.dumps(drawing,separators=(',',':'))
            if key not in drawing_ids:
                drawing_ids[key]=len(variant_drawings);variant_drawings.append(drawing)
            rows[cp]=dict(drawing=drawing_ids[key],glyph=cmap[cp])
        variation_marks[entry['family']]=dict(source=source_ids[entry['file']],marks=rows)
    result=dict(unicode='18.0.0',family='Dad Combining Outlines',status='Native licensed mark paths for dynamic layout; source presence is not linguistic or attachment validation',sources=sources,marks=drawings,behaviouralMarks=behavioural,nativeContextOnly=[cp for cp,e in drawings.items() if not e['bounds']],variationMarks=variation_marks,variantDrawings=variant_drawings)
    output=ROOT/'js/combining-outline-manifest.js'
    temporary=output.with_suffix('.tmp.js')
    temporary.write_text('// Generated by tools/font/build_combining_outlines.py; see per-source notices and font licences.\nexport default '+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';\n')
    temporary.replace(output)
    print(f'{len(drawings)-len(result["nativeContextOnly"])} mark drawings, {len(result["nativeContextOnly"])} native-context records from {len(sources)} sources; {output.stat().st_size:,} bytes')
    return result


if __name__=='__main__':build()
