"""Bounded cache/performance/visual review of isolated dense adapter only."""
import json,time
from pathlib import Path
from fontTools.ttLib import TTFont
from dense_skeleton_lowres_adapter import apply
from supplemental_pressure import shaped
from render_specimen import render


def main():
    out=Path('output/font-review/dense-adapter-lowres');out.mkdir(parents=True,exist_ok=True)
    sources=json.loads(Path('docs/source-style-review.json').read_text())['sources'];records=[];samples=[]
    for row in sources:
        if row['number'] not in {176,183,197,198,199}:continue
        source=Path(row['fonts'][0]['file']);native=TTFont(source);text=row['sample'];names={g[0] for g in shaped(native,text)}
        record=apply(native,row['source'],cache_dir=out/'cache',glyph_names=names)
        output=out/f"{row['number']}.ttf";native.flavor=None;native.save(output)
        warm=apply(TTFont(source),row['source'],cache_dir=out/'cache',glyph_names=names)
        record.update(sourceNumber=row['number'],source=str(source),text=text,output=str(output),warmSeconds=warm['seconds'],warmCacheHits=warm['cacheHits']);records.append(record)
        count=record['glyphs']-record['counts'].get('native-retained-guard',0)-record['counts'].get('native-blank',0)
        for label,path in [('SOURCE',source),(f'DENSE ADAPTER {count}/{record["glyphs"]} ADAPTED',output)]:samples.append({'label':f"{row['number']} {label}",'font':str(path),'text':text})
        (out/'review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(row['number'],record['counts'],record['seconds'],warm['seconds'],flush=True)
    (out/'spec.json').write_text(json.dumps({'samples':samples},ensure_ascii=False,indent=2)+'\n');render(samples,out/'comparison')

if __name__=='__main__':main()
