"""Render font candidates beside official Seal identity-reference rows.

Research sheets only. Never extract the reference chart's font or outlines into
a font build. The original font programs, not these PNG sheets, are the donors.
"""
import argparse
import hashlib
import json
from pathlib import Path

import pymupdf
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[2]
CHART=ROOT/'build/unicode-sources/seal-recovery/U180-3D000-reference.pdf'


def review(font_name='Seal Sans',rows_per_sheet=6):
    probes=json.loads((ROOT/'docs/seal-font-probes-2026-11-03.json').read_text())
    probe=next(f for f in probes['fonts'] if f['family']==font_name)
    path=ROOT/probe['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==probe['sha256']
    reference=json.loads((ROOT/'data/font-sources/seal-recovery.json').read_text())['reference']
    assert hashlib.sha256(CHART.read_bytes()).hexdigest()==reference['sha256']
    candidates={r['codepoint']:r for r in probe['candidates']}
    doc=pymupdf.open(CHART);locations={}
    for index,page in enumerate(doc):
        for word in page.get_text('words'):
            if not (80<word[1]<735):continue
            try:cp=int(word[4],16)
            except ValueError:continue
            if cp in candidates and word[4]==f'{cp:X}':
                assert cp not in locations,hex(cp)
                locations[cp]=(index,[word[0]-4,word[1]-3,word[0]+145,word[1]+28])
    assert locations.keys()==candidates.keys(),set(candidates)-locations.keys()
    folder=ROOT/'output/font-review/seal-source-probes'/font_name.lower().replace(' ','-')
    folder.mkdir(parents=True,exist_ok=True)
    output=folder/'review.json'
    previous=json.loads(output.read_text()) if output.exists() else {}
    same_sources=(previous.get('sourceFontSha256')==probe['sha256']
                  and previous.get('reference',{}).get('sha256')==reference['sha256'])
    decisions={r['codepoint']:r for r in previous.get('characters',[])} if same_sources else {}
    font=ImageFont.truetype(str(path),100)
    items=[];points=sorted(candidates)
    for start in range(0,len(points),rows_per_sheet):
        group=points[start:start+rows_per_sheet]
        image=Image.new('RGB',(850,45+len(group)*180),'white');draw=ImageDraw.Draw(image)
        draw.text((8,8),'Official table: HEX / THX / CCZ / QJZ / DYC     |     '+font_name+' candidate',fill='black',font_size=17)
        sheet=folder/f'reference-{start//rows_per_sheet+1:02}.png'
        for row,cp in enumerate(group):
            index,clip=locations[cp];pix=doc[index].get_pixmap(matrix=pymupdf.Matrix(4,4),clip=pymupdf.Rect(clip))
            top=45+row*180
            draw.text((8,top),f'U+{cp:X} - reference page {index+1}',fill='black',font_size=17)
            image.paste(Image.frombytes('RGB',(pix.width,pix.height),pix.samples),(8,top+29))
            draw.line((620,top+20,620,top+165),fill='#aaa',width=1)
            candidate_font=font
            box=draw.textbbox((0,0),chr(cp),font=candidate_font,anchor='ls')
            width,height=box[2]-box[0],box[3]-box[1]
            if width>190 or height>130:
                candidate_font=ImageFont.truetype(str(path),max(1,int(100*min(190/width,130/height))))
                box=draw.textbbox((0,0),chr(cp),font=candidate_font,anchor='ls')
                width,height=box[2]-box[0],box[3]-box[1]
            draw.text((635+(190-width)/2-box[0],top+25+(145-height)/2-box[1]),chr(cp),font=candidate_font,fill='black',anchor='ls')
            draw.line((0,top+179,850,top+179),fill='#ddd',width=1)
            item=dict(codepoint=cp,referencePage=index+1,referenceClip=clip,sheet=sheet.relative_to(ROOT).as_posix(),candidateDrawingSha256=candidates[cp]['drawingSha256'],review='pending')
            old=decisions.get(cp,{})
            if old.get('candidateDrawingSha256')==item['candidateDrawingSha256']:
                for key in ('review','reviewCheckpoint'):
                    if key in old:item[key]=old[key]
            items.append(item)
        image.save(sheet)
    reviewed=sum(item['review']!='pending' for item in items)
    report=dict(status=f'{reviewed} of {len(items)} candidate drawings compared with reference; {len(items)-reviewed} pending. Not production adoption or full reader/style validation.',sourceFont=probe['path'],sourceFontSha256=probe['sha256'],reference=reference,characters=items)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(items)} candidates on {(len(items)+rows_per_sheet-1)//rows_per_sheet} sheets: {output}')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--font',default='Seal Sans');args=parser.parse_args();review(args.font)
