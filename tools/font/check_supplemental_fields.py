"""Bounded local whole-field guards with explicit threshold-pore accounting.

At 384px/em a 1–3 pixel white pore can be introduced by antialias thresholding
without an outlined counter. Keep raw counts and areas; filter only these tiny
white pores, never ink components or real counters. Source and candidate receive
the identical threshold. Per-glyph 1024/384 checks remain independent guards.
"""
import argparse
import json
import math
from pathlib import Path
import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage as ndi
from render_specimen import Font
from prototype_unifont_lettering import topology,validate_reconstruction


def pore_filter(mask):
    labels,n=ndi.label(ndi.binary_fill_holes(mask)&~mask)
    sizes=np.bincount(labels.ravel());remove=[i for i in range(1,n+1) if sizes[i]<4]
    result=mask.copy()
    for i in remove:result[labels==i]=True
    return result,dict(rawTopology=topology(mask),filteredTopology=topology(result),porePixelAreas=[int(sizes[i]) for i in remove],counterPixelAreas=[int(sizes[i]) for i in range(1,n+1) if i not in remove])


def check(source,candidate,text,size=384):
    a=Font(source).shape(text,size);b=Font(candidate).shape(text,size)
    # Names can change after post3 serialization; retained IDs/positions cannot.
    def positions(shaped):return [{k:v for k,v in g.items() if k!='name'} for g in shaped['glyphs']]
    assert positions(a)==positions(b),'Native shaping or placement changed'
    boxes=[a['bounds'],b['bounds']];left=min(x[0] for x in boxes)-10;top=min(x[1] for x in boxes)-10
    width=math.ceil(max(x[2] for x in boxes)-left+10);height=math.ceil(max(x[3] for x in boxes)-top+10)
    def mask(s):
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><g transform="translate({-left} {-top})">'+''.join(s['paths'])+'</g></svg>'
        with pymupdf.open(stream=svg.encode(),filetype='svg') as doc:
            pix=doc[0].get_pixmap(alpha=False)
            return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
    old,old_record=pore_filter(mask(a));new,new_record=pore_filter(mask(b))
    result=dict(size=size,source=old_record,candidate=new_record,shapingUnchanged=True,poreCriterion='only white pores below4pixels at384px/em filtered; all ink components and other counters retained')
    try:result.update(status='pass',checks=validate_reconstruction(old,new))
    except ValueError as error:result.update(status='reject-whole-field',reason=str(error))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--review',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    results=[]
    for row in json.loads(a.review.read_text()):
        result=check(row['source'],row['output'],row['text']);result.update(sourceNumber=row['sourceNumber'],text=row['text']);results.append(result);print(row['sourceNumber'],result['status'],flush=True)
    a.output.write_text(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
