"""Isolated cached adapter for accepted dense-script finer pen direction.
Not imported by production builders until coordinator integration. Immutable
native drawings feed all adaptations; caches deduplicate glyphs across shards.
"""
from copy import deepcopy
import hashlib,io,json,time
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from supplemental_pressure import ROOT,raster,outline
from supplemental_adapter import preserve_native_bounds
from native_contour_pressure import transform as flex
from dense_skeleton_lowres_kernel import reink_candidates,validate_reconstruction
from dense_display_raster import GlyphRaster

SOURCES={'NotoSerifKhitanSmallScript-Regular.ttf','NotoSerifTangut-Regular.ttf','Jigmo.ttf','Jigmo2.ttf','Jigmo3.ttf'}
CACHE=ROOT/'build/font-cache/dense-skeleton-lowres'
SETTINGS={'resolution':512,'secondaryResolution':384,'flex':[.005,.003,0],'nativeFallbackFlex':[.005,.003],'minimumComponentAreaRatio':.75,'minimumCounterOverlap':.75,'branchesPruned':0,'subpixelPhases':[0,.5]}


def recipe_hash(source=None):
    inputs=('dense_skeleton_lowres_adapter.py','dense_skeleton_lowres_kernel.py','dense_display_raster.py','native_contour_pressure.py','supplemental_pressure.py','supplemental_adapter.py','prototype_unifont_lettering.py')
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
    if high is None:return {'status':'native-blank'}
    low=native_paint(SETTINGS['secondaryResolution'])
    items={SETTINGS['resolution']:high,SETTINGS['secondaryResolution']:low}
    lowmask,lowframe=low;left,top,scale=lowframe
    for dx in SETTINGS['subpixelPhases']:
        for dy in SETTINGS['subpixelPhases']:
            if dx==dy==0:continue
            viewport=(left+dx,top+dy,scale,lowmask.shape[1],lowmask.shape[0])
            native_mask,_=native_paint(viewport=viewport)
            items[f"384@{dx},{dy}"]=(native_mask,viewport[:3])
    mask,frame=high;last='No accepted skeleton candidate';original=deepcopy(font['glyf'][name])
    for ink,checks in reink_candidates(mask,seed):
        try:base=preserve_native_bounds(outline(ink,frame),native,name)
        except ValueError as error:last=str(error);continue
        for amplitude in SETTINGS['flex']:
            font['glyf'][name]=base
            try:
                if amplitude:
                    proposed,field=flex(font,name,amplitude=amplitude)
                    font['glyf'][name]=preserve_native_bounds(proposed,native,name)
                else:field={'amplitude':0}
                guards=_guards(native,font,name,items)
            except ValueError as error:last=str(error);continue
            return {'status':'skeleton-pen','reink':checks,'flex':field,'vectorGuards':guards,'nativeBoundsPreserved':True}
    # Finely detailed rejected signs keep native stroke widths and receive only
    # a gentle, injective contour flex, preserving the exact native bbox.
    for amplitude in SETTINGS['nativeFallbackFlex']:
        try:
            proposed,field=flex(native,name,amplitude=amplitude)
            font['glyf'][name]=preserve_native_bounds(proposed,native,name)
            guards=_guards(native,font,name,items)
            return {'status':'guarded-native-flex','flex':field,'vectorGuards':guards,'nativeBoundsPreserved':True,'reinkRejection':last}
        except ValueError as error:last=str(error)
    font['glyf'][name]=original
    return {'status':'native-retained-guard','reason':last,'nativeBoundsPreserved':True}


def apply(font,source,cache_dir=CACHE,glyph_names=None):
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
        key=hashlib.sha256(json.dumps([method,em,name,native['hmtx'][name],pen.getCommands()],sort_keys=True).encode()).hexdigest()
        root=cache_dir/key[:2];root.mkdir(exist_ok=True);meta=root/(key+'.json');drawing=root/(key+'.glyf')
        if meta.exists():
            record=json.loads(meta.read_text());hits+=1
            if record['status'] in {'skeleton-pen','guarded-native-flex'}:font['glyf'][name]=Glyph(data=drawing.read_bytes())
        else:
            seed=int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big')
            record=_adapt(native,font,name,seed)
            if record['status'] in {'skeleton-pen','guarded-native-flex'}:
                font['glyf'][name].recalcBounds(font['glyf']);drawing.write_bytes(font['glyf'][name].compile(font['glyf']))
            meta.write_text(json.dumps(record,sort_keys=True))
        records.append({'glyph':name,'gid':index,'cacheKey':key,**record})
        if len(records)%100==0:print(f'dense {Path(source).name}: {len(records)} glyphs, {hits} cached, {time.monotonic()-started:.1f}s',flush=True)
    assert font['head'].unitsPerEm==em
    assert all(font[t].compile(font)==raw for t,raw in immutable.items()),'Native layout/metrics changed'
    statuses=sorted({r['status'] for r in records})
    return {'method':'native-skeleton-finer-pen-v1','recipeSha256':method,'settings':SETTINGS,'glyphs':len(records),'cacheHits':hits,'seconds':time.monotonic()-started,'counts':{s:sum(r['status']==s for r in records) for s in statuses},'layoutTablesUnchanged':sorted(immutable),'nativeBoundsPreserved':True,'records':records,'limitations':['Per-glyph1024/384 guards do not replace complete-field subpixel guards or visual review','Native retained glyphs are explicit; no font fallback counts as custom styling','Small native-flex fallback keeps source stroke-width distinctions for dense detail']}
