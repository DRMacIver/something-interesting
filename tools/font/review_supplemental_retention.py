"""Bounded visual triage of positive encoded glyphs retained by pressure guards.

Shows the three largest retained encoded drawings per integrated source. This
is exception triage, not an all-glyph or linguistic approval. Nonencoded GSUB
retentions are separately counted because a lone character cannot invoke them.
"""
import argparse
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from supplemental_adapter import ROOT
from render_specimen import Font,render
from fontTools.pens.boundsPen import BoundsPen


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=ROOT/'js/font-manifest.js')
    parser.add_argument('--output',type=Path,default=ROOT/'output/font-review/supplemental-production-retention')
    parser.add_argument('--source',action='append',help='Limit to these source basenames; repeat as needed')
    args=parser.parse_args()
    manifest=json.loads(args.manifest.read_text().split('export default ')[1].rstrip(';\n'));out=args.output;out.mkdir(parents=True,exist_ok=True)
    samples=[];records=[]
    for entry in manifest['fonts']:
        if args.source and Path(entry['source']).name not in args.source:continue
        if not entry.get('supplementalTreatment'):continue
        font=TTFont(ROOT/entry['file']);report=json.loads((ROOT/entry['supplementalTreatment']['report']).read_text());reverse={}
        for cp,name in font.getBestCmap().items():reverse.setdefault(font.getGlyphID(name),cp)
        actual_sha=hashlib.sha256((ROOT/entry['file']).read_bytes()).hexdigest()
        assert actual_sha==entry['sha256'],'Private/public font differs from manifest'
        gs=font.getGlyphSet()
        retained=[r for r in report['records'] if r['status']=='native-retained-guard'];encoded=[];unencoded=0
        for r in retained:
            gid=r['gid'];name=font.getGlyphName(gid)
            if gid not in reverse:unencoded+=1;continue
            pen=BoundsPen(gs);gs[name].draw(pen)
            if pen.bounds is None:continue
            x0,y0,x1,y1=pen.bounds
            area=(x1-x0)*(y1-y0);encoded.append((area,reverse[gid],r))
        chosen=[];loaded=Font(ROOT/entry['file'])
        for _,cp,rec in sorted(encoded,reverse=True):
            if len(chosen)>=3:break
            shaped=loaded.shape(chr(cp),22)
            if rec['gid'] not in {g['gid'] for g in shaped['glyphs']}:continue
            chosen.append(dict(codepoint=f'U+{cp:04X}',**rec))
            samples.append(dict(label=f"{Path(entry['source']).stem} retained U+{cp:04X} gid{rec['gid']}",font=entry['file'],text=chr(cp)))
        records.append(dict(source=entry['source'],file=entry['file'],fontSha256=actual_sha,treatmentReport=entry['supplementalTreatment']['report'],retainedGlyphs=len(retained),nonencodedRetainedGlyphs=unencoded,largestEncodedSamples=chosen))
    for i in range(0,len(samples),6):render(samples[i:i+6],out/f'page-{i//6+1}')
    (out/'review.json').write_text(json.dumps(dict(status='retained native drawing exception triage; visual review pending',selection='three largest positive encoded retained glyphs per source, requested gid confirmed painted',sources=records),ensure_ascii=False,indent=2))
    print(len(samples),'samples',len(records),'sources')

if __name__=='__main__':main()
