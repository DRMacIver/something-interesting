"""Whole-shaped-field guard for the bounded joining-pressure experiment."""
import argparse
import json, math
from pathlib import Path
import numpy as np
import pymupdf
from PIL import Image
from render_specimen import Font
from prototype_unifont_lettering import validate_reconstruction,topology

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--review',type=Path,default=Path('output/font-review/joining-pressure/review.json'))
parser.add_argument('--output',type=Path,default=Path('output/font-review/joining-pressure/whole-field-checks.json'))
parser.add_argument('--finer-ink',action='store_true',help='Use explicit75percent area floor with unchanged topology/counter guards for isolated fine-ink candidates')
args=parser.parse_args()
if args.finer_ink:
    from skeleton_fine_dense_pen import validate_reconstruction
records=json.loads(args.review.read_text())
results=[]
for record in records:
    text=record['text']
    # Whole joined field at a common native scale/viewport.
    a=Font(record['source']).shape(text,384)
    b=Font(record['output']).shape(text,384)
    assert a['glyphs']==b['glyphs']
    boxes=[a['bounds'],b['bounds']];left=min(x[0] for x in boxes)-10; top=min(x[1] for x in boxes)-10
    width=math.ceil(max(x[2] for x in boxes)-left+10);height=math.ceil(max(x[3] for x in boxes)-top+10)
    def mask(s):
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><g transform="translate({-left} {-top})">'+''.join(s['paths'])+'</g></svg>'
        with pymupdf.open(stream=svg.encode(),filetype='svg') as doc:
            pix=doc[0].get_pixmap(alpha=False)
            return np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
    old,new=mask(a),mask(b)
    result={'sourceNumber':record['sourceNumber'],'size':384,'sourceTopology':topology(old),'candidateTopology':topology(new)}
    try:result.update(status='pass',checks=validate_reconstruction(old,new))
    except ValueError as error:result.update(status='reject-whole-field',reason=str(error))
    results.append(result)
    print(record['sourceNumber'],result['status'],flush=True)
args.output.write_text(json.dumps(results,indent=2)+'\n')
