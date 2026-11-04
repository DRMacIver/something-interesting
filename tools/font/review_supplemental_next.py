"""Local sample-only pressure review; never edits production or source fonts."""
import argparse,copy,hashlib,io,json
from pathlib import Path
import numpy as np
import pymupdf
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from supplemental_pressure import ROOT,pressure,raster,outline,shaped
from supplemental_adapter import preserve_native_bounds
from prototype_unifont_lettering import validate_reconstruction

OUT=ROOT/'output/font-review/supplemental-next-group'
FIELDS={23:'ἄνθρωπος ἀλήθεια κόσμε',65:'שָׁלוֹם עוֹלָם',53:'አማርኛ',184:'བོད་ཡིག',157:'தமிழ்',160:'తెలుగు',140:'සිංහල',72:'ಕನ್ನಡ',88:'മലയാളം',58:'ગુજરાતી',60:'ਪੰਜਾਬੀ',79:'ພາສາລາວ'}


def field_mask(font,text,resolution,view=None):
    positions=shaped(font,text);gs=font.getGlyphSet();runs=[];x=0;bounds=[]
    for name,advance,_,dx,dy in positions:
        p=SVGPathPen(gs);gs[name].draw(p)
        bp=BoundsPen(gs);gs[name].draw(bp)
        if bp.bounds:
            a,b,c,d=bp.bounds;bounds.append((x+dx+a,dy+b,x+dx+c,dy+d))
            runs.append(f'<path d="{p.getCommands()}" transform="translate({x+dx} {dy})"/>')
        x+=advance
    scale=resolution/font['head'].unitsPerEm
    if view is None:
        left=int(np.floor(min(b[0] for b in bounds)*scale))-24;top=int(np.ceil(max(b[3] for b in bounds)*scale))+24
        width=int(np.ceil(max(b[2] for b in bounds)*scale))-left+24;height=top-int(np.floor(min(b[1] for b in bounds)*scale))+24
        view=(left,top,scale,width,height)
    left,top,scale,width,height=view
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><g fill="black" transform="translate({-left} {top}) scale({scale} {-scale})">'+''.join(runs)+'</g></svg>'
    with pymupdf.open(stream=svg.encode(),filetype='svg') as doc:
        with pymupdf.open('pdf',doc.convert_to_pdf()) as pdf:
            pix=pdf[0].get_pixmap(alpha=False)
            mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
    return mask,view


def candidate(source,text,output,amount,robust_pores=False):
    native=TTFont(source);font=TTFont(source)
    if 'glyf' not in native:raise ValueError('Native CFF source requires separate contour-preserving adapter')
    before=shaped(native,text)
    if not all(native.getGlyphID(n) for n,*_ in before):raise ValueError('Pinned raw source lacks patched production sample glyph; needs packaged native context')
    layout={tag:font[tag].compile(font) for tag in ('GPOS','GDEF','GSUB','hmtx') if tag in font}
    names={n for n,*_ in before};records=[]
    # Flatten all compounds from pristine source to avoid indirect alterations.
    for name in native.getGlyphOrder():
        if native['glyf'][name].isComposite():
            p=DecomposingRecordingPen(native.getGlyphSet());native.getGlyphSet()[name].draw(p)
            pen=TTGlyphPen(None);p.replay(pen);font['glyf'][name]=preserve_native_bounds(pen.glyph(),native,name)
    for name in names:
        item=raster(native,name)
        if item is None:continue
        mask,transform=item;left,top,scale=transform;advance=native['hmtx'][name][0]*scale
        xx=np.arange(mask.shape[1])+left;protected=np.minimum(1,np.minimum(abs(xx),abs(xx-advance))/20)[None,:]
        seed=int.from_bytes(hashlib.sha256(name.encode()).digest()[:4],'big');original=font['glyf'][name];rec=None
        small,st=raster(native,name,384)
        for reduction in (1,.75,.5,.25):
            try:
                changed,checks=pressure(mask,amount*reduction,seed,protected)
                if not checks['changedPixels']:raise ValueError('No visible pressure change')
                proposed=preserve_native_bounds(outline(changed,transform),native,name);font['glyf'][name]=proposed
                vector,_=raster(font,name,viewport=(*transform,mask.shape[1],mask.shape[0]));vc=validate_reconstruction(mask,vector)
                if not np.any(vector!=mask):raise ValueError('No visible vector change')
                sv,_=raster(font,name,384,viewport=(*st,small.shape[1],small.shape[0]));sc=validate_reconstruction(small,sv)
                rec=dict(glyph=name,status='adapted',amount=amount*reduction,checks=checks,vectorChecks=vc,scale384Checks=sc);break
            except ValueError as error:
                font['glyf'][name]=original;rec=dict(glyph=name,status='native-retained-guard',reason=str(error))
        records.append(rec)
    assert shaped(font,text)==before
    assert all(font[tag].compile(font)==data for tag,data in layout.items())
    field_checks={}
    for resolution in (384,1024):
        base,view=field_mask(native,text,resolution);new,_=field_mask(font,text,resolution,view)
        if robust_pores:
            from check_supplemental_fields import pore_filter
            if resolution == 384:
                old,old_record=pore_filter(base);new_filtered,new_record=pore_filter(new)
            else:
                from scipy import ndimage as ndi
                from prototype_unifont_lettering import topology
                def scaled_filter(mask):
                    labels,n=ndi.label(ndi.binary_fill_holes(mask)&~mask);sizes=np.bincount(labels.ravel())
                    threshold=4*(resolution/384)**2;remove=[i for i in range(1,n+1) if sizes[i]<threshold]
                    result=mask.copy()
                    for i in remove:result[labels==i]=True
                    return result,dict(rawTopology=topology(mask),filteredTopology=topology(result),porePixelAreas=[int(sizes[i]) for i in remove],counterPixelAreas=[int(sizes[i]) for i in range(1,n+1) if i not in remove],thresholdPixelArea=threshold)
                old,old_record=scaled_filter(base);new_filtered,new_record=scaled_filter(new)
            checked=validate_reconstruction(old,new_filtered)
            field_checks[str(resolution)]=dict(checks=checked,source=old_record,candidate=new_record,poreCriterion='Only white pores below4pixels at384px/em, area-scaled at1024; no ink components or larger counters removed')
        else:
            field_checks[str(resolution)]=validate_reconstruction(base,new)
    for rec in font['name'].names:
        if rec.nameID in {1,3,4,6,16,17}:rec.string='Dad Native Pressure Review'.encode(rec.getEncoding(),errors='replace')
    font.flavor=None;font.save(output)
    actual=TTFont(output)
    assert shaped(actual,text)==before
    return dict(amount=amount,glyphs=records,wholeFieldChecks=field_checks,shapingUnchanged=True,layoutTablesUnchanged=sorted(layout),nativeBoundsPreserved=True)


def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--numbers',default=','.join(map(str,FIELDS)))
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args();OUT=args.output.resolve()
    wanted={int(x) for x in args.numbers.split(',')}
    OUT.mkdir(parents=True,exist_ok=True);review=json.loads((ROOT/'docs/source-style-review.json').read_text());reports=[];samples=[]
    for row in review['sources']:
        number=row['number']
        if number not in wanted:continue
        # Full pinned source for native context; packaged shards intentionally
        # contain only novel repertoire and may omit bases owned by earlier fonts.
        source=ROOT/row['source'];field=FIELDS.get(number,row['sample'])
        text=row['sample']+' '+field;output=OUT/f'{number}.ttf';result=None;errors=[]
        for amount in (.7,.45,.25):
            try:result=candidate(source,text,output,amount);break
            except ValueError as error:errors.append(str(error))
        rec=dict(number=number,source=row['source'],sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),baselineDecision=row['decision'],sample=row['sample'],nativeField=field,output=str(output.relative_to(ROOT)),attemptErrors=errors)
        if result:
            rec.update(result);rec['outputSha256']=hashlib.sha256(output.read_bytes()).hexdigest()
            for text_label,body in [('inventory',row['sample']),('native field',field)]:
                for label,path in [('source',source),('candidate',output)]:samples.append(dict(label=f'{number} {source.stem} {text_label} {label}',font=str(path),text=body))
        else:rec['status']='retained-native-field-guard'
        reports.append(rec)
        (OUT/'review.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
        (OUT/'spec.json').write_text(json.dumps(dict(samples=samples),ensure_ascii=False,indent=2)+'\n')
        print(number,source.name,'candidate' if result else 'retained',flush=True)

if __name__=='__main__':main()
