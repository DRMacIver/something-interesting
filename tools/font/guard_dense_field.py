"""Guard candidate glyphs at exact384px native complete-field pixel positions.
Restores explicit original drawings if a glyph fails; never edits production.
"""
from copy import deepcopy
import json,math
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from render_specimen import Font,render
from supplemental_pressure import shaped,raster
from skeleton_fine_dense_pen import validate_reconstruction


def guard(record,size=384):
    source=TTFont(record['source']);font=TTFont(record['output'])
    before=Font(record['source']).shape(record['text'],size)
    after=Font(record['output']).shape(record['text'],size)
    origin=10-min(before['bounds'][0],after['bounds'][0]);baseline=10-min(before['bounds'][1],after['bounds'][1])
    scale=size/source['head'].unitsPerEm
    positions=shaped(source,record['text']);x=y=0;checks={};rejected=set()
    for name,ax,ay,ox,oy in positions:
        if name in rejected:x+=ax;y+=ay;continue
        boxes=[]
        for f in (source,font):
            gs=f.getGlyphSet();pen=BoundsPen(gs);gs[name].draw(pen)
            if pen.bounds:boxes.append(pen.bounds)
        if not boxes:x+=ax;y+=ay;continue
        px=(x+ox)*scale;py=(y+oy)*scale
        xmin=origin+px+min(b[0] for b in boxes)*scale;xmax=origin+px+max(b[2] for b in boxes)*scale
        ymin=baseline-py-max(b[3] for b in boxes)*scale;ymax=baseline-py-min(b[1] for b in boxes)*scale
        cropx=math.floor(xmin)-8;cropy=math.floor(ymin)-8
        viewport=(cropx-origin-px,baseline-py-cropy,scale,math.ceil(xmax)-cropx+8,math.ceil(ymax)-cropy+8)
        a,_=raster(source,name,viewport=viewport);b,_=raster(font,name,viewport=viewport)
        try:checks[name]={'status':'pass','checks':validate_reconstruction(a,b)}
        except ValueError as error:
            font['glyf'][name]=deepcopy(source['glyf'][name]);rejected.add(name)
            checks[name]={'status':'restored-source','reason':str(error)}
        x+=ax;y+=ay
    font.flavor=None;font.save(record['output'])
    for row in record['glyphs']:
        row['completeFieldPixelGuard']=checks.get(row['glyph'])
        if row['glyph'] in rejected:
            row['previousStatus']=row['status'];row['status']='retained-field-guard'
    record['subpixelFieldGuardSize']=size
    return record


def main():
    root=Path('output/font-review/skeleton-fluid-dense-pen')
    rows=json.loads((root/'review.json').read_text());rows=[guard(r) for r in rows]
    (root/'review.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    samples=[]
    for row in rows:
        count=sum(g['status']=='candidate' for g in row['glyphs']);total=len(row['glyphs'])
        for label,font in [('SOURCE',row['source']),(f'FLUID PEN {count}/{total} ADAPTED',row['output'])]:samples.append({'label':f"{row['sourceNumber']} {label}",'font':font,'text':row['text']})
    (root/'spec.json').write_text(json.dumps({'samples':samples},ensure_ascii=False,indent=2)+'\n')
    render(samples,root/'guarded-comparison')

if __name__=='__main__':main()
