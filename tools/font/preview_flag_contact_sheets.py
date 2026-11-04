"""Write compact, browser-rendered contact sheets from compiled flag fonts."""
import argparse,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--prefix',default='region-flags');args=parser.parse_args()
 folder=ROOT/'output/font-review/pen-translation';prefix=args.prefix
 report=json.loads((folder/(prefix+'-candidate.json')).read_text())
 data=[dict(region=e['region']+(f' alias{i}' if i else ''),text=text,canonical=e['sequence'],advance=e['advance']) for e in report['flags'] for i,text in enumerate(e.get('qualificationForms',[e['sequence']]))]
 template='''<!doctype html><meta charset="utf-8"><title>Flag font contact sheets</title>
<style>body{font:16px system-ui;background:#f5f2eb}canvas{display:block;background:white;margin:20px 0}@font-face{font-family:Flag;src:url(PREFIX-candidate.woff2?v=COLOURHASH)}@font-face{font-family:FlagInk;src:url(PREFIX-candidate-ink.woff2?v=INKHASH)}</style>
<h1>PREFIX: compiled flag contact sheets</h1><pre id="status">Loading…</pre><main></main><script>
const entries=ENTRIES;
async function main(){await Promise.all([document.fonts.load('140px Flag'),document.fonts.load('140px FlagInk')]);let failures=[];
for(let start=0;start<entries.length;start+=32){let canvas=document.createElement('canvas');canvas.width=1120;canvas.height=680;canvas.setAttribute('aria-label','Flag sheet '+(start/32+1));document.querySelector('main').append(canvas);let c=canvas.getContext('2d');
for(let i=start;i<Math.min(entries.length,start+32);i++){const e=entries[i],col=(i-start)%8,row=Math.floor((i-start)/8),x=col*140,y=row*170;c.fillStyle='#111';c.font='12px system-ui';c.fillText(e.region,x+5,y+17);c.font='140px Flag';c.fillText(e.text,x+5,y+130);c.font='33.6px FlagInk';c.strokeStyle='#111';c.lineWidth=33.6*.018;c.lineJoin='round';c.miterLimit=2;c.strokeText(e.text,x+5,y+163);c.font='33.6px Flag';c.fillText(e.text,x+5,y+163);
const probe=document.createElement('canvas');probe.width=160;probe.height=128;const p=probe.getContext('2d',{willReadFrequently:true});p.font='72px Flag';p.fillText(e.text,10,96);let a=p.getImageData(0,0,160,128).data;p.clearRect(0,0,160,128);p.fillText(e.canonical,10,96);let b=p.getImageData(0,0,160,128).data;if(a.some((v,j)=>v!==b[j]))failures.push(e.region+': alias differs');if(Math.abs(p.measureText(e.text).width-e.advance*.072)>.01)failures.push(e.region+': advance differs');}
}
document.querySelector('#status').textContent=JSON.stringify({forms:entries.length,sheets:Math.ceil(entries.length/32),failures},null,2);}
main().catch(e=>document.querySelector('#status').textContent='ERROR: '+e);
</script>'''
 for key,value in [('PREFIX',prefix),('COLOURHASH',report['sha256'][:12]),('INKHASH',hashlib.sha256((folder/(prefix+'-candidate-ink.woff2')).read_bytes()).hexdigest()[:12]),('ENTRIES',json.dumps(data))]:template=template.replace(key,value)
 (folder/(prefix+'-contact.html')).write_text(template)
 print(prefix,len(data),'forms')


if __name__=='__main__':main()
