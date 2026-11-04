"""Render six source/candidate pairs per bounded local review page."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('group');args=p.parse_args()
 out=ROOT/'output/font-review'/('supplemental-systematic-'+args.group)
 rows=json.loads((out/'review.json').read_text())
 for row in rows:
  override=out/f"{row['number']}-robust-review.json"
  if not override.exists():override=out/f"{row['number']}-packaged-review.json"
  if override.exists():
   rec=json.loads(override.read_text());row['renderNativeInput']=rec['nativeInput']
   if rec.get('shapingUnchanged'):row['output']=rec['output'];row['shapingUnchanged']=True
 for page,start in enumerate(range(0,len(rows),6),1):
  samples=[]
  for row in rows[start:start+6]:
   source=row.get('renderNativeInput',row['source']);text=row['sample']
   label=f"{row['number']} {Path(row['source']).stem}"
   samples.append(dict(label=label+' source',font=source,text=text))
   if row.get('shapingUnchanged'):samples.append(dict(label=label+' normalized pressure',font=row['output'],text=text))
  spec=out/f'page-{page}.spec.json';spec.write_text(json.dumps(dict(samples=samples),ensure_ascii=False,indent=2))
  subprocess.run([sys.executable,str(ROOT/'tools/font/render_specimen.py'),'--spec',str(spec),'--output',str(out/f'page-{page}')],check=True)
  print('rendered',args.group,page,flush=True)
if __name__=='__main__':main()
