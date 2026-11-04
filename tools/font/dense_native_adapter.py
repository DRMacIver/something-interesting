"""Isolated cached adapter for accepted dense-script finer pen direction.
Not imported by production builders until coordinator integration. Immutable
native drawings feed all adaptations; caches deduplicate glyphs across shards.
"""
from copy import deepcopy
import hashlib,io,json,time,os,tempfile
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
ROOT=Path(__file__).resolve().parents[2]
from supplemental_adapter import preserve_native_bounds
from native_contour_pressure import transform as flex
from dense_geometry_guards import validate_reconstruction
from native_contrast_pen import transform as contrast
from dense_display_raster import GlyphRaster

SOURCES={'NotoSerifKhitanSmallScript-Regular.ttf','NotoSerifTangut-Regular.ttf','Jigmo.ttf','Jigmo2.ttf','Jigmo3.ttf'}
CACHE=ROOT/'build/font-cache/dense-native'
SETTINGS={'resolution':1024,'secondaryResolution':384,'amounts':[.01,.0075,.005],'contrastMode':'inward-median','flex':[.003,0],'nativeFallbackFlex':[.003],'minimumComponentAreaRatio':.75,'minimumCounterOverlap':.75,'subpixelPhases':[0,.5]}


def atomic_write(path,data):
    with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.dense-',delete=False) as stream:
        stream.write(data);temporary=stream.name
    os.replace(temporary,path)


def recipe_hash(source=None):
    inputs=('dense_native_adapter.py','dense_geometry_guards.py','dense_display_raster.py','native_contrast_pen.py','native_contour_pressure.py','supplemental_adapter.py')
    return hashlib.sha256(b''.join(Path(__file__).with_name(p).read_bytes() for p in inputs)+json.dumps(SETTINGS,sort_keys=True).encode()).hexdigest()


def _guards(native,font,name,items):
    checks={};paint=GlyphRaster(font,name)
    for resolution,(mask,frame) in items.items():
        altered,_=paint(viewport=(*frame,mask.shape[1],mask.shape[0]))
        result=validate_reconstruction(mask,altered)
        # Keep auditable minima/maxima without repeating every tiny component
        # array for each subpixel phase in the all-glyph cache.
        ratios=result['componentAreaRatios'];counters=result['counterOverlap']
        checks[str(resolution)]={'components':len(ratios),'minComponentAreaRatio':min(ratios,default=1),'maxComponentAreaRatio':max(ratios,default=1),'counters':len(counters),'minCounterOverlap':min(counters,default=1)}
    return checks


def _adapt(native,font,name,seed):
    native_paint=GlyphRaster(native,name)
    high=native_paint(SETTINGS['resolution'])
    if high is None or not high[0].any():return {'status':'native-blank'}
    low=native_paint(SETTINGS['secondaryResolution'])
    items={SETTINGS['resolution']:high,SETTINGS['secondaryResolution']:low}
    lowmask,lowframe=low;left,top,scale=lowframe
    for dx in SETTINGS['subpixelPhases']:
        for dy in SETTINGS['subpixelPhases']:
            if dx==dy==0:continue
            viewport=(left+dx,top+dy,scale,lowmask.shape[1],lowmask.shape[0])
            native_mask,_=native_paint(viewport=viewport)
            items[f"384@{dx},{dy}"]=(native_mask,viewport[:3])
    mask,frame=high;last='No accepted native contrast candidate';original=deepcopy(font['glyf'][name])
    contour_count=len(native['glyf'][name].getCoordinates(native['glyf'])[1])
    for amount in SETTINGS['amounts']:
        try:
            result=contrast(native,name,amount=amount,mode=SETTINGS['contrastMode'])
            if result is None:break
            proposed,pen_record=result
            if proposed.numberOfContours!=contour_count:raise ValueError('Native contour count changed')
            base=preserve_native_bounds(proposed,native,name)
        except ValueError as error:last=str(error);continue
        for amplitude in SETTINGS['flex']:
            font['glyf'][name]=base
            try:
                if amplitude:
                    proposed,field=flex(font,name,amplitude=amplitude)
                    if proposed.numberOfContours!=contour_count:raise ValueError('Native contour count changed after flex')
                    font['glyf'][name]=preserve_native_bounds(proposed,native,name)
                else:field={'amplitude':0}
                guards=_guards(native,font,name,items)
            except ValueError as error:last=str(error);continue
            return {'status':'dense-native-pen','pen':pen_record,'flex':field,'vectorGuards':guards,'nativeBoundsPreserved':True,'nativeContourCountUnchanged':contour_count}
    # Finely detailed rejected signs keep native stroke widths and receive only
    # a gentle, injective contour flex, preserving the exact native bbox.
    for amplitude in SETTINGS['nativeFallbackFlex']:
        try:
            result=flex(native,name,amplitude=amplitude)
            if result is None:raise ValueError('Native outline has no two-dimensional ink bounds')
            proposed,field=result
            if proposed.numberOfContours!=contour_count:raise ValueError('Native contour count changed in fallback')
            font['glyf'][name]=preserve_native_bounds(proposed,native,name)
            guards=_guards(native,font,name,items)
            return {'status':'guarded-native-flex','flex':field,'vectorGuards':guards,'nativeBoundsPreserved':True,'penRejection':last}
        except ValueError as error:last=str(error)
    font['glyf'][name]=original
    return {'status':'native-retained-guard','reason':last,'nativeBoundsPreserved':True}


def apply(font,source,cache_dir=CACHE,glyph_names=None,report_dir=None):
    if Path(source).name not in SOURCES:return None
    if 'glyf' not in font:raise ValueError('Dense pen recipe requires native TrueType drawings')
    started=time.monotonic();cache_dir=Path(cache_dir);cache_dir.mkdir(parents=True,exist_ok=True)
    font.flavor=None;stream=io.BytesIO();font.save(stream)
    native=TTFont(io.BytesIO(stream.getvalue()),recalcTimestamp=False);native.setGlyphOrder(list(font.getGlyphOrder()))
    immutable={t:font[t].compile(font) for t in ('GSUB','GPOS','GDEF','hmtx') if t in font};em=font['head'].unitsPerEm
    names=set(glyph_names) if glyph_names is not None else set(native.getGlyphOrder())
    # Retained composites must not inherit an adapted component accidentally.
    for name in native.getGlyphOrder():
        if native['glyf'][name].isComposite():
            recording=DecomposingRecordingPen(native.getGlyphSet());native.getGlyphSet()[name].draw(recording)
            pen=TTGlyphPen(None);recording.replay(pen)
            font['glyf'][name]=preserve_native_bounds(pen.glyph(),native,name)
    records=[];hits=0;method=recipe_hash()
    for index,name in enumerate(native.getGlyphOrder()):
        if name not in names:continue
        pen=SVGPathPen(native.getGlyphSet());native.getGlyphSet()[name].draw(pen)
        # Glyph names remain in the key because they seed the approved pressure
        # phase. Source-file hashes are omitted so repeated shard closure shares
        # the same drawing/metric key rather than duplicating expensive work.
        native_frame=[getattr(native['glyf'][name],axis,0) for axis in ('xMin','yMin','xMax','yMax')]
        key=hashlib.sha256(json.dumps([method,em,name,native['hmtx'][name],native_frame,pen.getCommands()],sort_keys=True).encode()).hexdigest()
        root=cache_dir/key[:2];root.mkdir(exist_ok=True);meta=root/(key+'.json');drawing=root/(key+'.glyf')
        if meta.exists():
            record=json.loads(meta.read_text());hits+=1
            if record['status'] in {'dense-native-pen','guarded-native-flex'}:font['glyf'][name]=Glyph(data=drawing.read_bytes())
        else:
            seed=int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big')
            record=_adapt(native,font,name,seed)
            if record['status'] in {'dense-native-pen','guarded-native-flex'}:
                font['glyf'][name].recalcBounds(font['glyf']);atomic_write(drawing,font['glyf'][name].compile(font['glyf']))
            atomic_write(meta,json.dumps(record,sort_keys=True).encode())
        records.append({'glyph':name,'gid':index,'cacheKey':key,**record})
        if len(records)%100==0:print(f'dense {Path(source).name}: {len(records)} glyphs, {hits} cached, {time.monotonic()-started:.1f}s',flush=True)
    assert font['head'].unitsPerEm==em
    assert all(font[t].compile(font)==raw for t,raw in immutable.items()),'Native layout/metrics changed'
    statuses=sorted({r['status'] for r in records})
    report={'nativeInputSha256':hashlib.sha256(stream.getvalue()).hexdigest(),'nativeEmUnchanged':em,'method':'native-normal-finer-pen-v1','recipeSha256':method,'settings':SETTINGS,'glyphs':len(records),'cacheHits':hits,'seconds':time.monotonic()-started,'counts':{s:sum(r['status']==s for r in records) for s in statuses},'layoutTablesUnchanged':sorted(immutable),'nativeBoundsPreserved':True,'records':records,'limitations':['Per-glyph1024/384 guards do not replace complete-field subpixel guards or visual review','Native retained glyphs are explicit; no font fallback counts as custom styling','Small native-flex fallback keeps source stroke-width distinctions for dense detail']}

    if report_dir is not None:
        directory=Path(report_dir);directory.mkdir(parents=True,exist_ok=True)
        stable={key:value for key,value in report.items() if key not in {'cacheHits','seconds'}}
        source_path=Path(source)
        if source_path.is_absolute():
            try:stable['source']=source_path.relative_to(ROOT).as_posix()
            except ValueError:stable['source']=source_path.name
        else:stable['source']=source_path.as_posix()
        stable['sourceProfile']=source_path.name
        path=directory/(hashlib.sha256(stream.getvalue()).hexdigest()+'-'+method+'.json')
        atomic_write(path,json.dumps(stable,sort_keys=True).encode())
        try:reference=path.relative_to(ROOT).as_posix()
        except ValueError:reference=str(path)
        return {key:value for key,value in stable.items() if key!='records'}|{'report':reference}
    return report
