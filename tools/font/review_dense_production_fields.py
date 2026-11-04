"""Offline actual private production font review; reads authenticated cache-warm output only."""
import argparse,json,math,hashlib
from pathlib import Path
import numpy as np
import pymupdf
from render_specimen import Font,render,ROOT
from dense_geometry_guards import validate_reconstruction


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def masks(before,after,size):
    shaped=[f.shape(before['text'],size) for f in (before['font'],after)]
    assert shaped[0]['glyphs']==shaped[1]['glyphs'],'Native field shaping changed'
    bounds=[min(s['bounds'][i] for s in shaped) if i<2 else max(s['bounds'][i] for s in shaped) for i in range(4)]
    left=math.floor(bounds[0])-8;top=math.floor(bounds[1])-8
    width=math.ceil(bounds[2])-left+8;height=math.ceil(bounds[3])-top+8
    result=[]
    for field in shaped:
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><g transform="translate({-left} {-top})">'+''.join(field['paths'])+'</g></svg>'
        with pymupdf.open(stream=svg.encode(),filetype='svg') as doc:
            pix=doc[0].get_pixmap(alpha=False)
            result.append(np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3).max(axis=2)<128)
    return result,shaped[0]['glyphs']


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,default=ROOT/'output/font-review/dense-warm');p.add_argument('--output',type=Path,default=ROOT/'output/font-review/dense-production-fields');a=p.parse_args()
    plan=json.loads((a.plan/'plan.json').read_text());proof=json.loads((a.plan/'verified.json').read_text())
    assert proof['status'].startswith('authenticated')
    rows={Path(r['file']).name:r for r in plan['denseShards']};groups={r['family']:g['index'] for g in plan['groups'] for r in g['shards']}
    cases=json.loads((ROOT/'tools/font/specimens/dense-native-fields.json').read_text())['cases'];records=[];samples=[];a.output.mkdir(parents=True,exist_ok=True)
    for case in cases:
        row=rows[Path(case['originalFile']).name];evidence=proof['families'][row['family']]
        source=ROOT/'output/font-review/supplemental-production-baselines'/Path(row['file']).name
        derived=a.plan/f"group-{groups[row['family']]}"/'fonts'/source.name
        assert sha(source)==row['sha256']==case['fontSha256'];assert sha(derived)==evidence['fontSha256']
        native=Font(source);actual=Font(derived);checks={}
        for size in (22,44,384):
            (before,after),glyphs=masks({'font':native,'text':case['text']},actual,size)
            try:check={'status':'pass','checks':validate_reconstruction(before,after)}
            except ValueError as error:check={'status':'review-required','reason':str(error)}
            check['nativeInkBounds']=native.shape(case['text'],size)['bounds'];check['derivedInkBounds']=actual.shape(case['text'],size)['bounds']
            checks[str(size)]=check
        report=json.loads((ROOT/evidence['report']).read_text());assert sha(ROOT/evidence['report'])==evidence['reportSha256']
        selected={g['gid'] for g in glyphs};dispositions=[r for r in report['records'] if r['gid'] in selected]
        records.append({'caseId':case['caseId'],'text':case['text'],'family':row['family'],'baseline':str(source.relative_to(ROOT)),'baselineSha256':sha(source),'derived':str(derived.relative_to(ROOT)),'derivedSha256':sha(derived),'reportSha256':evidence['reportSha256'],'fieldGuards':checks,'glyphs':glyphs,'selectedDispositions':dispositions,'visualDisposition':'pending offline review'})
        pair=[{'label':case['caseId']+' NATIVE BASELINE','font':str(source),'text':case['text']},{'label':case['caseId']+' ACTUAL PRODUCTION PEN','font':str(derived),'text':case['text']}];samples+=pair;render(pair,a.output/case['caseId'])
        print(case['caseId'],{k:v['status'] for k,v in checks.items()},flush=True)
    render(samples,a.output/'comparison');(a.output/'review.json').write_text(json.dumps({'status':'Actual authenticated private production fields; visual review pending','recipeSha256':proof['denseRecipeSha256'],'cases':records},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
