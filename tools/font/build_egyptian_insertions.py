"""Recover matched insertion regions and outlines from pinned native shaping.

The empty full-blank probe activates the source font's own cell selection,
positioning and contextual container variant without contributing any ink.
"""
import json
import re
import hashlib
from itertools import permutations
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.svgLib.path import parse_path
from fontTools.pens.transformPen import TransformPen
from review_egyptian_insertions import ROOT,CACHE,CONTROLS,build as review


def sampled_ink_hits(path, region):
    """Conservative screening, not a proof that a region is ink-free."""
    recording=RecordingPen();parse_path(path,recording)
    x,y,w,h=region;hits=0
    for i in range(10):
        for j in range(10):
            pen=PointInsidePen(None,(x+w*(i+.5)/10,y+h*(j+.5)/10))
            recording.replay(pen);hits+=pen.getResult()
    return hits


def container_candidates(inventory,font):
    """Only Unicode-registered rotations with an explicit native UVS mapping."""
    rows={row['source_glyph']:row for row in inventory['entries']}
    cmap=font.getBestCmap();plain={cp:row for row in rows.values() for cp in row['codepoints']}
    candidates=[([cp],row,row['source_glyph']) for cp,row in sorted(plain.items())]
    registered=set()
    for line in (ROOT/'data/unicode/18.0.0/StandardizedVariants.txt').read_text().splitlines():
        if not line.lstrip().startswith('#') and 'EGYPTIAN HIEROGLYPH' in line and 'rotated' in line:
            registered.add(tuple(int(c,16) for c in line.split(';')[0].split()))
    for table in font['cmap'].tables:
        if table.format!=14:continue
        for vs,pairs in sorted(table.uvsDict.items()):
            for cp,glyph in pairs:
                if (cp,vs) not in registered:continue
                glyph=glyph or cmap[cp]
                row=rows.get(glyph) or plain.get(cp)
                if row:candidates.append(([cp,vs],row,glyph))
    return [(chars+([0x13440] if mirror else []),row,glyph)
            for chars,row,glyph in candidates for mirror in [False,True]]


def documented_region(row,control,width,height,cfg):
    """Source cell rule when a seven-cell body misses the font's six-cell rule.

    Keep the declared insertion dimensions and edge/centre anchor, including
    the native upward y offset in twentieths of the full surface. The same
    rule reproduces the actually shaped G25 bottom-start offset exactly.
    """
    areas=[a for a in row['areas'] if a['control']==control]
    if not areas:return None
    area=max(areas,key=lambda a:a['container_cell'][0]*a['container_cell'][1])
    if area['offset_axis'] not in {None,'y'}:return None
    w,h=[a*b for a,b in zip(area['insertion_cell'],[cfg['hfu'],cfg['vfu']])]
    name=area['name']
    x=cfg['sb'] if name in {'ts','bs'} else width-cfg['sb']-w if name in {'te','be'} else (width-w)/2
    y=0 if name in {'ts','te','ti'} else height-h if name in {'bs','be','bi'} else (height-h)/2
    if area['offset_axis']=='y':y-=height*area['offset_twentieths']/20
    return [x,y,w,h]


def build():
    inventory=review()  # verifies all source hashes
    raw=(CACHE/'eot.ttf').read_bytes();font=TTFont(CACHE/'eot.ttf');gs=font.getGlyphSet()
    native=hb.Font(hb.Face(raw));cfg=inventory['coordinate_system'];top=cfg['vfu']*cfg['vhu']+cfg['vbase']
    entries={};rejected=[];geometry_warnings=[]
    for container,row,expected_glyph in container_candidates(inventory,font):
        # Native mirror alternates need not share the original glyph name:
        # C2a -> C2b and D54 <-> D55 are actual source substitutions.
        baseline=hb.Buffer();baseline.add_str(''.join(map(chr,container)));baseline.guess_segment_properties();hb.shape(native,baseline)
        baseline_names=[]
        for info in baseline.glyph_infos:
            name=font.getGlyphName(info.codepoint);extent=native.get_glyph_extents(info.codepoint)
            if name!='mr' and extent and extent.width and extent.height:baseline_names.append(name)
        if len(baseline_names)==1:expected_glyph=baseline_names[0]
        available=sorted({a['control'] for a in row['areas']})
        combinations=[p for n in range(1,len(available)+1) for p in permutations(available,n)]
        for controls in combinations:
            key='-'.join(f'{c:X}' for c in [*container,*controls]);text=''.join(map(chr,container))+''.join(chr(c)+'\U00013441' for c in controls)
            buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(native,buf)
            cursor=0;regions=[];outlines=[];names=[];bounds=[];seen=[];helpers=[];pending=[]
            for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
                name=font.getGlyphName(info.codepoint);x=cursor+pos.x_offset;y=pos.y_offset
                extent=native.get_glyph_extents(info.codepoint)
                if name=='mr' and container[-1]==0x13440:
                    helpers.append(name);cursor+=pos.x_advance;continue
                if re.fullmatch(r'i(ts|bs|te|be|mi|ti|bi)0[A-Z]',name):pending.append(name)
                control_match=re.fullmatch(r'(ts|bs|te|be|mi|ti|bi)[1-6][1-6]',name)
                if control_match:seen.append(CONTROLS[control_match[1]])
                match=re.fullmatch(r'it([1-6])([1-6])',name)
                if match:regions.append([x,top-cfg['vbase']-y,int(match[1])*cfg['hfu'],int(match[2])*cfg['vfu']])
                if extent and extent.width and extent.height:
                    pen=SVGPathPen(gs);gs[name].draw(TransformPen(pen,(1,0,0,-1,x,top-y)))
                    bp=BoundsPen(gs);gs[name].draw(TransformPen(bp,(1,0,0,-1,x,top-y)))
                    bounds.append(bp.bounds);outlines.append(pen.getCommands());names.append(name)
                cursor+=pos.x_advance
            height=cfg['vfu']*cfg['vhu']
            region_rule=None
            if not regions and not seen and len(controls)==1 and pending:
                # G18/I7 have real seven-cell source bodies, while their
                # documented insertion rules target six cells. Do not expose
                # the font's unresolved ibs/ite helper or invent a cavity.
                region=documented_region(row,controls[0],cursor,height,cfg)
                name=next(k for k,v in CONTROLS.items() if v==controls[0])
                if region and any(p.startswith('i'+name+'0') for p in pending):
                    regions=[region];seen=list(controls);region_rule='documented native edge/centre cell rule'
            if len(regions)!=len(controls) or seen!=list(controls) or len(outlines)!=1 or not names[0].startswith(expected_glyph) or cursor<=0:
                rejected.append({'key':key,'glyphs':names,'regions':regions});continue
            source_transform=None
            if helpers:
                # U13440 mirrors the preceding sign, not its later inserted
                # children. Consume the source's mr instruction as an affine
                # reflection of that outline in its native surface; retain
                # the source control coordinates and child orientation.
                source_transform=[-1,0,0,1,cursor,0]
                pen=SVGPathPen(None);bp=BoundsPen(None)
                parse_path(outlines[0],TransformPen(pen,source_transform))
                parse_path(outlines[0],TransformPen(bp,source_transform))
                outlines=[pen.getCommands()];bounds=[bp.bounds]
            warnings=[]
            if any(min(x,y)<0 or x+w>cursor or y+h>height for x,y,w,h in regions):
                warnings.append('native region extends outside nominal cell')
            overlap=any(min(a[0]+a[2],b[0]+b[2])>max(a[0],b[0]) and
                        min(a[1]+a[3],b[1]+b[3])>max(a[1],b[1])
                        for i,a in enumerate(regions) for b in regions[i+1:])
            if overlap:
                warnings.append('native insertion regions overlap')
            hits=sum(sampled_ink_hits(outlines[0],region) for region in regions)
            if hits:
                warnings.append('native region intersects sampled container ink')
            # Preserve the source shaper's actual positions. Native insertions
            # can overlap or overflow (Unicode18 §11.4.2); rejecting them for
            # an invented empty-rectangle requirement exposes source helper
            # boxes instead of the requested extended sign. Reserve the whole
            # source surface and record geometry observations separately.
            x0,y0,x1,y1=bounds[0];dx=-min(0,x0,*[r[0] for r in regions]);dy=-min(0,y0,*[r[1] for r in regions])
            entries[key]={'width':max(cursor,x1,*[x+w for x,y,w,h in regions])+dx,'height':max(height,y1,*[y+h for x,y,w,h in regions])+dy,
                          'region':[regions[0][0]+dx,regions[0][1]+dy,*regions[0][2:]],'pathOffset':[dx,dy],'pathBounds':list(bounds[0]),
                          'path':outlines[0],'sourceGlyph':names[0],'container':container,'controls':list(controls)}
            if len(controls)>1:entries[key]['regions']=[[x+dx,y+dy,w,h] for x,y,w,h in regions]
            if source_transform:entries[key]['sourceTransform']=source_transform
            if region_rule:entries[key]['regionRule']=region_rule
            if warnings:
                entries[key]['sourceGeometryWarnings']=warnings
                geometry_warnings.append({'key':key,'warnings':warnings,'sampledInkHits':hits})
    manifest={'source':'build/unicode-sources/egyptian-text/eot.ttf','sha256':hashlib.sha256(raw).hexdigest(),
              'license':'SIL OFL 1.1; see assets/fonts/licenses','entries':entries}
    count=lambda predicate:sum(predicate(e) for e in entries.values())
    return manifest,{'accepted':len(entries),
        'unmodified_single':count(lambda e:len(e['container'])==1 and len(e['controls'])==1),
        'unmodified_multiple':count(lambda e:len(e['container'])==1 and len(e['controls'])>1),
        'mirrored':count(lambda e:e['container'][-1]==0x13440 and len(e['container'])==2),
        'rotated':count(lambda e:len(e['container'])==2 and e['container'][-1]!=0x13440),
        'rotated_mirrored':count(lambda e:len(e['container'])==3),
        'consumedMirrorHelpers':count(lambda e:'sourceTransform' in e),
        'documentedCellRules':count(lambda e:'regionRule' in e),
        'rejected':rejected,'sourceGeometryWarnings':geometry_warnings,'method':'Native full-blank probes for ordered subsets of documented controls and registered rotations; container-alone probes identify native mirror alternates.65explicit mr helpers become affine sign reflections while source slots/children retain their coordinates.4unresolved size rules use documented native slot dimensions/anchors, calibrated against a working native offset. Source regions may overlap/overflow; envelopes reserve every region and native ink. Sampling records observations, not collision-freedom or linguistic validation.'}



if __name__=='__main__':
    manifest,report=build()
    (ROOT/'js/egyptian-insertion-manifest.js').write_text('// Derived from the pinned OFL Egyptian Text font.\nexport default '+json.dumps(manifest,separators=(',',':'))+';\n')
    (ROOT/'docs/egyptian-insertion-build.json').write_text(json.dumps(report,indent=2)+'\n')
    print({'accepted':report['accepted'],'rejected':len(report['rejected'])})
