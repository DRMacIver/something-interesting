"""Recheck rejected local fields with explicit tiny scan-pore accounting."""
import argparse,hashlib,json
from pathlib import Path
from fontTools.ttLib import TTFont
from review_supplemental_next import candidate,ROOT
from check_supplemental_fields import check

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('groups',nargs='+');args=p.parse_args();review=json.loads((ROOT/'docs/source-style-review.json').read_text())
 for group in args.groups:
  out=ROOT/'output/font-review'/('supplemental-'+group)
  rows=json.loads((out/'review.json').read_text())
  for rec in rows:
   if rec.get('shapingUnchanged'):continue
   row=next(r for r in review['sources'] if r['number']==rec['number']);source=ROOT/row['source']
   with TTFont(source) as f:
    if not all(ord(c) in f.getBestCmap() for c in row['sample']):source=ROOT/row['fonts'][0]['file']
   with TTFont(source) as f:separator=' ' if 32 in f.getBestCmap() else ''
   text=row['sample']+separator+row['sample'];output=out/f"{row['number']}-robust.ttf";attempts=[];result=None
   for amount in (.7,.45,.25,.1):
    try:
     result=candidate(source,text,output,amount,robust_pores=True)
     direct=check(source,output,text)
     if direct['status']!='pass':raise ValueError('Independent shaped-field guard: '+direct['reason'])
     result['independent384FieldCheck']=direct;break
    except ValueError as error:attempts.append(str(error));result=None
   report=dict(number=row['number'],nativeInput=str(source.relative_to(ROOT)),nativeInputSha256=hashlib.sha256(source.read_bytes()).hexdigest(),sample=row['sample'],nativeFieldText=text,separator=separator,output=str(output.relative_to(ROOT)),attemptErrors=attempts)
   if result:report.update(result);report['outputSha256']=hashlib.sha256(output.read_bytes()).hexdigest()
   else:report['status']='retained-robust-native-field-guard'
   (out/f"{row['number']}-robust-review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(group,row['number'],'candidate' if result else 'retained',flush=True)
if __name__=='__main__':main()
