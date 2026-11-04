"""Native cubic pressure for separately reviewed CFF script sources.

Preserve native CFF output, glyph order, metrics and shaping tables. Keep
rejected native charstring programs and persist per-glyph evidence.
This module is isolated until explicitly wired into the production builder.
"""
import copy
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from fontTools.misc.psCharStrings import T2CharString
from fontTools.misc.fixedTools import floatToFixedToFloat
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.basePen import NullPen
from fontTools.pens.recordingPen import RecordingPen

from supplemental_pressure import ROOT, raster, pressure, outline
from prototype_unifont_lettering import validate_reconstruction

SOURCES={'UFSZeroExt.otf':{'amount':.7,'category':'guarded-historical-cubic-forms'}}
RESOLUTION=1024
METHOD='native-centred-cubic-pressure-v1'
# Type 2 serializes relative coordinates to 16.16 fixed point. Hundreds of
# relative segments can accumulate a tiny rounding difference after saving.
BOUNDS_TOLERANCE=.01  # native design units, below .00025px at dialogue size
CACHE=ROOT/'build/font-cache/cubic-pressure'


def recipe_hash(source):
    settings=SOURCES[Path(source).name]
    files=('supplemental_cubic_adapter.py','supplemental_pressure.py','prototype_unifont_lettering.py')
    return hashlib.sha256(b''.join(Path(__file__).with_name(p).read_bytes() for p in files)+json.dumps([METHOD,RESOLUTION,settings],sort_keys=True).encode()).hexdigest()


def bounds(font,name):
    pen=BoundsPen(font.getGlyphSet());font.getGlyphSet()[name].draw(pen)
    return pen.bounds


def fit(glyph,native_bounds):
    glyph.recalcBounds(None)
    new=(glyph.xMin,glyph.yMin,glyph.xMax,glyph.yMax);old=native_bounds
    sx=(old[2]-old[0])/(new[2]-new[0]);sy=(old[3]-old[1])/(new[3]-new[1])
    if not .85<=sx<=1.15 or not .85<=sy<=1.15:raise ValueError('Native attachment frame change too large')
    for i,(x,y) in enumerate(glyph.coordinates):glyph.coordinates[i]=(old[0]+(x-new[0])*sx,old[1]+(y-new[1])*sy)
    return glyph


def apply(font,source):
    settings=SOURCES.get(Path(source).name)
    if settings is None:return None
    if 'CFF ' not in font:raise ValueError('Native cubic recipe requires CFF outlines')
    # Shares the immutable production-baseline destination with the TrueType
    # adapter; this call neither changes its kernel nor its source recipes.
    from supplemental_adapter import baseline
    baseline(source)
    native=copy.deepcopy(font);top=font['CFF '].cff.topDictIndex[0]
    snapshot=io.BytesIO();snapshot_font=copy.deepcopy(native);snapshot_font.flavor=None;snapshot_font.save(snapshot)
    native_hash=hashlib.sha256(snapshot.getvalue()).hexdigest()
    layout={tag:font[tag].compile(font) for tag in ('GPOS','GDEF','GSUB','hmtx','vmtx') if tag in font}
    em=font['head'].unitsPerEm;recipe=recipe_hash(source);records=[]
    CACHE.mkdir(parents=True,exist_ok=True)
    for gid,name in enumerate(native.getGlyphOrder()):
        original=top.CharStrings[name]
        original.decompile()
        # The complete native hash covers subroutines and binary hint masks;
        # glyph programs can contain bytes and need not be JSON encoded.
        key=hashlib.sha256(json.dumps([recipe,native_hash,name,native['hmtx'][name]],sort_keys=True).encode()).hexdigest()
        cache=CACHE/(key+'.json')
        if cache.exists():
            stored=json.loads(cache.read_text());rec=stored['record']
            if rec['status']=='adapted':top.CharStrings[name]=T2CharString(program=stored['program'],private=original.private,globalSubrs=original.globalSubrs)
        else:
            item=raster(native,name,RESOLUTION);program=None
            if item is None:rec=dict(gid=gid,glyph=name,status='native-blank')
            else:
                mask,transform=item;left,ytop,scale=transform;advance=native['hmtx'][name][0]*scale
                xx=np.arange(mask.shape[1])+left;protected=np.minimum(1,np.minimum(abs(xx),abs(xx-advance))/20)[None,:]
                small,view=raster(native,name,384);native_box=bounds(native,name)
                seed=int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big')
                for reduction in (1,.75,.5,.25):
                    try:
                        changed,checks=pressure(mask,settings['amount']*reduction,seed,protected)
                        if not checks['changedPixels']:raise ValueError('No visible pressure change')
                        glyph=fit(outline(changed,transform),native_box)
                        advance=font['hmtx'][name][0]
                        encoded_width=None if advance==original.private.defaultWidthX else advance-original.private.nominalWidthX
                        pen=T2CharStringPen(encoded_width,None,roundTolerance=0);glyph.draw(pen,None)
                        proposed=pen.getCharString(private=original.private,globalSubrs=original.globalSubrs)
                        proposed.decompile()
                        # Validate the exact serializable Type 2 coordinates,
                        # not higher-precision values that disappear on save.
                        proposed.program=[floatToFixedToFloat(x,16) if isinstance(x,float) else x for x in proposed.program]
                        top.CharStrings[name]=proposed
                        vector,_=raster(font,name,viewport=(*transform,mask.shape[1],mask.shape[0]));vc=validate_reconstruction(mask,vector)
                        vc['changedPixels']=int(np.sum(vector!=mask))
                        if not vc['changedPixels']:raise ValueError('No visible cubic vector change')
                        small_new,_=raster(font,name,384,viewport=(*view,small.shape[1],small.shape[0]));sc=validate_reconstruction(small,small_new)
                        delta=max(abs(x-y) for x,y in zip(native_box,bounds(font,name)))
                        if delta>BOUNDS_TOLERANCE:raise ValueError('Native cubic ink frame moved')
                        proposed.decompile();program=proposed.program
                        rec=dict(gid=gid,glyph=name,status='adapted',**checks,vectorChecks=vc,scale384Checks=sc,nativeBoundsMaxError=delta)
                        break
                    except (ValueError,ZeroDivisionError) as error:
                        top.CharStrings[name]=original
                        rec=dict(gid=gid,glyph=name,status='native-retained-guard',reason=str(error))
            cache.write_text(json.dumps(dict(record=rec,program=program),sort_keys=True))
        records.append(rec)
        if gid%100==99:print(f'  cubic pressure {Path(source).name}: {gid+1}/{len(native.getGlyphOrder())}',flush=True)
    assert font['head'].unitsPerEm==em
    assert all(font[tag].compile(font)==data for tag,data in layout.items())
    width_repairs=[]
    for gid,name in enumerate(font.getGlyphOrder()):
        charstring=top.CharStrings[name];charstring.draw(NullPen())
        advance=font['hmtx'][name][0]
        if charstring.width!=advance:
            # Some pre-pressure alphabet drawings inherited an absolute-width
            # operand. Repair that operand only; never redraw retained curves.
            assert records[gid]['status']=='native-retained-guard'
            charstring.decompile();program=list(charstring.program)
            private=charstring.private;nominal=private.nominalWidthX;default=private.defaultWidthX
            assert program[0]==advance and charstring.width==advance+nominal
            encoded=None if advance==default else advance-nominal
            old_width=charstring.width
            if encoded is None:program.pop(0)
            else:program[0]=encoded
            corrected=T2CharString(program=program,private=private,globalSubrs=charstring.globalSubrs)
            before,after=RecordingPen(),RecordingPen();charstring.draw(before);corrected.draw(after)
            assert before.value==after.value,'Width repair changed native drawing'
            assert corrected.width==advance
            top.CharStrings[name]=corrected
            records[gid]['widthRepair']=dict(method='explicit-type2-width-operand-only',nativeDecodedAdvance=old_width,hmtxAdvance=advance,encodedOperandBefore=advance,encodedOperandAfter=encoded,nominalWidthX=nominal,defaultWidthX=default)
            width_repairs.append(gid)
        else:assert charstring.width==advance
    counts={s:sum(r['status']==s for r in records) for s in sorted({r['status'] for r in records})}
    report=dict(method=METHOD,recipeSha256=recipe,nativeInputSha256=native_hash,settings=settings,resolution=RESOLUTION,glyphs=len(records),counts=counts,layoutTablesUnchanged=sorted(layout),nativeEmUnchanged=em,nativeBoundsPreserved=True,nativeBoundsTolerance=BOUNDS_TOLERANCE,charstringAdvancesMatchHmtx=True,widthOnlyRepairGids=width_repairs,records=records)
    saved=ROOT/'output/font-review/supplemental-cubic-production'/f'{native_hash}-{recipe}.json';saved.parent.mkdir(parents=True,exist_ok=True);saved.write_text(json.dumps(report,indent=2)+'\n')
    return {k:v for k,v in report.items() if k!='records'}|{'report':saved.relative_to(ROOT).as_posix()}
