"""Production adapter for visually accepted supplemental pressure groups.

All retained native glyphs (including GSUB closure) are attempted. Glyph caches
are content-addressed by native drawing, metrics and complete recipe/code hashes.
Rejected transformations remain native and are explicitly listed. Native GPOS,
GDEF, GSUB, hmtx and em values are unchanged. No hidden fallback fonts are used.
"""
import hashlib
import io
import json
from pathlib import Path
import shutil
import time

import numpy as np
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

from supplemental_pressure import ROOT, raster, pressure, outline
from prototype_unifont_lettering import validate_reconstruction

RECIPE_PATH=Path(__file__).with_name('supplemental_recipes.json')
RECIPES=json.loads(RECIPE_PATH.read_text())
SOURCES=RECIPES['sources']
CACHE=ROOT/'build/font-cache/supplemental-pressure'

def recipe_hash(source):
    kernel=b''.join(Path(__file__).with_name(p).read_bytes() for p in
        ('supplemental_adapter.py','supplemental_pressure.py','prototype_unifont_lettering.py'))
    recipe={k:v for k,v in RECIPES.items() if k!='sources'}
    recipe['source']=SOURCES[Path(source).name]
    return hashlib.sha256(kernel+json.dumps(recipe,sort_keys=True).encode()).hexdigest()


def baseline(source):
    """Save original production shards once, before any accepted replacement."""
    root=ROOT/'output/font-review/supplemental-production-baselines'
    manifest=ROOT/'js/font-manifest.js'
    if not manifest.exists():return
    data=json.loads(manifest.read_text().split('export default ')[1].rstrip(';\n'))
    for entry in data['fonts']:
        if Path(entry['source']).name!=Path(source).name:continue
        dest=root/Path(entry['file']).name
        if not dest.exists():
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/entry['file'],dest)
            dest.with_suffix('.json').write_text(json.dumps(entry,indent=2))


def preserve_native_bounds(proposed,native,name):
    """Keep TrueType phantom origin and native attachment coordinate frame.

    FontTools and browsers use the LSB/xMin relationship when establishing the
    design origin. Preserve the exact native glyf bbox and hmtx together; fit
    the experimental contour inside those extents rather than shifting anchors.
    """
    original=native['glyf'][name]
    proposed.recalcBounds(native['glyf'])
    old=(original.xMin,original.yMin,original.xMax,original.yMax)
    new=(proposed.xMin,proposed.yMin,proposed.xMax,proposed.yMax)
    scales=[]
    for axis in (0,1):
        extent=new[axis+2]-new[axis]
        scale=(old[axis+2]-old[axis])/extent if extent else 1
        if not .85<=scale<=1.15:raise ValueError('Pressure would move native attachment frame too far')
        scales.append(scale)
    for i,(x,y) in enumerate(proposed.coordinates):
        proposed.coordinates[i]=(round(old[0]+(x-new[0])*scales[0]),round(old[1]+(y-new[1])*scales[1]))
    proposed.recalcBounds(native['glyf'])
    if (proposed.xMin,proposed.yMin,proposed.xMax,proposed.yMax)!=old:
        raise ValueError('Pressure failed to preserve native TrueType bbox')
    return proposed


def apply(font,source):
    settings=SOURCES.get(Path(source).name)
    if not settings:return None
    if 'glyf' not in font:raise ValueError('Accepted supplemental recipe requires native TrueType outlines')
    baseline(source)
    font.flavor=None;data=io.BytesIO();font.save(data)
    native=TTFont(io.BytesIO(data.getvalue()),recalcTimestamp=False)
    # Preserve pre-serialization names: post3 can discard source glyph names,
    # but target layout tables still address the original in-memory names.
    native.setGlyphOrder(list(font.getGlyphOrder()))
    layout={tag:font[tag].compile(font) for tag in ('GPOS','GDEF','GSUB','hmtx') if tag in font}
    # A retained compound must keep its original drawing even when one of its
    # components is adapted. Flatten compounds from the immutable native font
    # before editing component glyphs; all shaping glyph IDs stay unchanged.
    for name in native.getGlyphOrder():
        if native['glyf'][name].isComposite():
            decomposed=DecomposingRecordingPen(native.getGlyphSet())
            native.getGlyphSet()[name].draw(decomposed)
            pen=TTGlyphPen(None);decomposed.replay(pen)
            font['glyf'][name]=preserve_native_bounds(pen.glyph(),native,name)
    em=font['head'].unitsPerEm;method_hash=recipe_hash(source);records=[];started=time.monotonic();hits=0
    CACHE.mkdir(parents=True,exist_ok=True)
    for index,name in enumerate(native.getGlyphOrder()):
        pen=SVGPathPen(native.getGlyphSet());native.getGlyphSet()[name].draw(pen)
        key=hashlib.sha256(json.dumps([method_hash,settings,em,native['hmtx'][name],name,pen.getCommands()],sort_keys=True).encode()).hexdigest()
        record_path=CACHE/(key+'.json');glyph_path=CACHE/(key+'.glyf')
        if record_path.exists():
            rec=json.loads(record_path.read_text());hits+=1
            if rec['status']=='adapted':font['glyf'][name]=Glyph(data=glyph_path.read_bytes())
        else:
            item=raster(native,name,RECIPES['resolution'])
            if item is None:rec=dict(glyph=name,status='native-blank')
            else:
                mask,transform=item;left,top,scale=transform;advance=native['hmtx'][name][0]*scale
                xx=np.arange(mask.shape[1])+left
                protected=np.minimum(1,np.minimum(abs(xx),abs(xx-advance))/20)[None,:]
                seed=int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big')
                original=font['glyf'][name]
                rec=None
                small_native,small_transform=raster(native,name,resolution=384)
                for reduction in (1,.75,.5,.25):
                    try:
                        changed,checks=pressure(mask,settings['amount']*reduction,seed,protected)
                        if not checks['changedPixels']:raise ValueError('No visible change at guarded source resolution')
                        proposed=preserve_native_bounds(outline(changed,transform),native,name)
                        font['glyf'][name]=proposed
                        vector,_=raster(font,name,viewport=(*transform,mask.shape[1],mask.shape[0]))
                        vector_checks=validate_reconstruction(mask,vector)
                        vector_checks['changedPixels']=int(np.sum(vector!=mask))
                        if not vector_checks['changedPixels']:raise ValueError('No visible vector change at guarded source resolution')
                        small_vector,_=raster(font,name,resolution=384,viewport=(*small_transform,small_native.shape[1],small_native.shape[0]))
                        scale_checks=validate_reconstruction(small_native,small_vector)
                        rec=dict(glyph=name,status='adapted',**checks,vectorChecks=vector_checks,scale384Checks=scale_checks)
                        glyph_path.write_bytes(proposed.compile(font['glyf']))
                        break
                    except ValueError as error:
                        font['glyf'][name]=original
                        rec=dict(glyph=name,status='native-retained-guard',reason=str(error))
            record_path.write_text(json.dumps(rec,sort_keys=True))
        rec=dict(rec,gid=index)
        records.append(rec)
        if index%100==99:print(f'  pressure {Path(source).name}: {index+1}/{len(native.getGlyphOrder())} glyphs, {hits} cached, {time.monotonic()-started:.1f}s',flush=True)
    assert font['head'].unitsPerEm==em
    assert all(font[tag].compile(font)==raw for tag,raw in layout.items()), 'Native layout tables changed'
    font.recalcBBoxes=True
    elapsed=time.monotonic()-started
    counts={status:sum(r['status']==status for r in records) for status in sorted({r['status'] for r in records})}
    report=dict(method=RECIPES['method'],recipeSha256=method_hash,settings=settings,resolution=RECIPES['resolution'],glyphs=len(records),counts=counts,layoutTablesUnchanged=sorted(layout),nativeEmUnchanged=em,nativeBoundsPreserved=True,records=records)
    reports=ROOT/'output/font-review/supplemental-production'
    reports.mkdir(parents=True,exist_ok=True)
    report_path=reports/(hashlib.sha256(data.getvalue()).hexdigest()+'-'+method_hash+'.json');report_path.write_text(json.dumps(report,indent=2))
    print(f'  pressure {Path(source).name}: {counts}, {elapsed:.1f}s ({hits} cached)',flush=True)
    return {k:v for k,v in report.items() if k!='records'}|{'report':report_path.relative_to(ROOT).as_posix()}
