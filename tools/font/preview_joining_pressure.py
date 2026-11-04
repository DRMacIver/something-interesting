"""Bounded native joining/dense-source pressure review; no production edits."""
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from supplemental_pressure import candidate, shaped
from render_specimen import render

OUT=Path('output/font-review/joining-pressure')
TEXT={20:'سَلَامٌ عَلَيْكُمْ',50:'𛰀𛰁𛰂𛰃𛰄𛰅',181:'𐽰𐽱𐽲𐽳 𐽴𐽵𐽶',191:'سَلَامٌ عَلَيْكُمْ'}
NUMBERS={20,50,176,181,183,191,198,199}

def main():
    rows=json.loads(Path('docs/source-style-review.json').read_text())['sources']
    records=[]; samples=[]
    for row in rows:
        n=row['number']
        if n not in NUMBERS: continue
        source=Path(row['fonts'][0]['file']); text=TEXT.get(n,row['sample'])
        # Add the contributed glyph study after joining text so both actual
        # supplemental coverage and contextual native forms enter the candidate.
        if n in TEXT: text += ' '+row['sample']
        output=OUT/f'{n}.ttf'
        rec=candidate(source,text,output,amount=.45,bend=0)
        # Prove raw layout and positioning tables remain byte-identical, apart
        # from fontTools normalisation by comparing the same decoded encoding.
        before=TTFont(source); after=TTFont(output)
        rec['nativeTableChecks']={tag:before.getTableData(tag)==after.getTableData(tag) for tag in ('GSUB','GPOS','GDEF','hmtx') if tag in before}
        rec['sourceNumber']=n; records.append(rec)
        for label,font in [('SOURCE',source),('GUARDED PRESSURE',output)]:
            samples.append({'label':f'{n} {Path(row["source"]).stem} {label}','font':str(font),'text':text})
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/'review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
        (OUT/'spec.json').write_text(json.dumps({'samples':samples},ensure_ascii=False,indent=2)+'\n')
        print(n,'complete',flush=True)
    render(samples,OUT/'comparison')

if __name__=='__main__': main()
