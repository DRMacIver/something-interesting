"""Bounded cold/warm and native-field review; no production font writes."""
import hashlib,json
from pathlib import Path
from fontTools.ttLib import TTFont
from dense_native_adapter import apply
from supplemental_pressure import shaped
from render_specimen import render


def main():
    out=Path('output/font-review/dense-native-adapter');out.mkdir(parents=True,exist_ok=True)
    cases=json.loads(Path('tools/font/specimens/dense-native-fields.json').read_text())['cases'];records=[];samples=[]
    for case in cases:
        source=Path(case['font']);assert hashlib.sha256(source.read_bytes()).hexdigest()==case['fontSha256']
        native=TTFont(source);text=case['text'];names={g[0] for g in shaped(native,text)}
        record=apply(native,case['source'],cache_dir=out/'cache',glyph_names=names)
        output=out/(case['caseId']+'.ttf');native.flavor=None;native.save(output)
        warm=apply(TTFont(source),case['source'],cache_dir=out/'cache',glyph_names=names)
        record.update(sourceNumber=case['sourceNumber'],caseId=case['caseId'],source=str(source),originalFile=case['originalFile'],text=text,output=str(output),warmSeconds=warm['seconds'],warmCacheHits=warm['cacheHits']);records.append(record)
        count=record['glyphs']-record['counts'].get('native-retained-guard',0)-record['counts'].get('native-blank',0)
        for label,path in [('SOURCE',source),(f'NATIVE PEN {count}/{record["glyphs"]} ADAPTED',output)]:samples.append({'label':f"{case['caseId']} {label}",'font':str(path),'text':text})
        (out/'review-expanded.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(case['caseId'],record['counts'],record['seconds'],warm['seconds'],flush=True)
    (out/'spec-expanded.json').write_text(json.dumps({'samples':samples},ensure_ascii=False,indent=2)+'\n')
    render(samples,out/'expanded-comparison');render(samples[-4:],out/'197-han-comparison')

if __name__=='__main__':main()
