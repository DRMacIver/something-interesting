"""Retry local native samples that require existing packaged glyph repairs."""
import argparse,hashlib,json
from pathlib import Path
from review_supplemental_next import candidate,ROOT

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('group');args=p.parse_args();out=ROOT/'output/font-review'/('supplemental-systematic-'+args.group)
 rows=json.loads((out/'review.json').read_text());review=json.loads((ROOT/'docs/source-style-review.json').read_text())
 for rec in rows:
  if rec.get('shapingUnchanged') or not any('lacks patched' in e for e in rec['attemptErrors']):continue
  row=next(r for r in review['sources'] if r['number']==rec['number']);source=ROOT/row['fonts'][0]['file'];output=out/f"{row['number']}-packaged.ttf";attempts=[];result=None
  for amount in (.7,.45,.25):
   try:result=candidate(source,row['sample']+' '+row['sample'],output,amount);break
   except ValueError as error:attempts.append(str(error))
  report=dict(number=row['number'],nativeInput=str(source.relative_to(ROOT)),nativeInputSha256=hashlib.sha256(source.read_bytes()).hexdigest(),sample=row['sample'],output=str(output.relative_to(ROOT)),attemptErrors=attempts)
  if result:report.update(result);report['outputSha256']=hashlib.sha256(output.read_bytes()).hexdigest()
  else:report['status']='retained-packaged-native-field-guard'
  (out/f"{row['number']}-packaged-review.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(row['number'],'candidate' if result else 'retained',flush=True)
if __name__=='__main__':main()
