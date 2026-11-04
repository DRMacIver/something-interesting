"""Choose visible, actually contributed glyphs for every packaged source face.

This is a style review inventory, not linguistic validation. Native sentence
samples are used only where that source contributes characters in the sample;
other rows are explicitly glyph studies. No font programs are changed.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/unicode'))
from audit import inventory

SENTENCES=['مرحبا بالعالم','שלום עולם','नमस्ते दुनिया','こんにちは世界','世界充满了奇妙的事物','세상은 신기한 일로 가득해요',
    'বাংলা','தமிழ்','తెలుగు','ಕನ್ನಡ','മലയാളം','ગુજરાતી','ਪੰਜਾਬੀ','සිංහල','ภาษาไทย','ພາສາລາວ',
    'ភាសាខ្មែរ','မြန်မာဘာသာ','བོད་ཡིག','አማርኛ','Հայերեն','ქართული','Γειά σου κόσμε','Привет мир']


def manifest(file):return json.loads((ROOT/file).read_text().split('export default ',1)[1].rstrip(';\n'))
def points(ranges):return {cp for a,b in ranges for cp in range(a,b+1)}
def selector(cp):return 0xfe00<=cp<=0xfe0f or 0xe0100<=cp<=0xe01ef


def build():
    data=manifest('js/font-manifest.js');public=inventory();covered=points(data['baseRanges'])
    for name in ['js/emoji-manifest.js','js/grid-manifest.js']:covered.update(points(manifest(name)['ranges']))
    groups={}
    for font in data['fonts']:
        offered=points(font['ranges'])&public.keys();novel=offered-covered;covered.update(offered)
        group=groups.setdefault(font['source'],dict(source=font['source'],fonts=[],novel=set()))
        group['fonts'].append((font,offered,novel));group['novel'].update(novel)
    rows=[]
    for index,group in enumerate(groups.values()):
        fonts=group['fonts'];union=set().union(*(p for _,p,_ in fonts));novel=group['novel']
        text=next((s for s in SENTENCES if all(c.isspace() or ord(c) in union for c in s)
                   and any(ord(c) in novel for c in s)),None)
        role='native sentence specimen' if text else 'contributed glyph study'
        if not text:
            chosen=max(fonts,key=lambda row:len([cp for cp in row[2] if public[cp][0] in 'LNSP']))
            eligible=sorted(cp for cp in chosen[2] if public[cp][0] in 'LNSP')
            if eligible:
                selected=[eligible[round(i*(len(eligible)-1)/min(7,len(eligible)-1))] for i in range(min(8,len(eligible)))] if len(eligible)>1 else eligible
                text=''.join(map(chr,selected))
            else:
                pairs=[(cp,int(vs)) for font,_,_ in fonts for vs,ranges in font.get('nativeVariations',{}).items()
                       for cp in sorted(points(ranges)) if cp in public and public[cp][0] in 'LNSP']
                if pairs:
                    cp,vs=pairs[0];text=chr(cp)+' '+chr(cp)+chr(vs);role='native variation study'
                else:
                    eligible=sorted(novel) or sorted(union)
                    eligible=[cp for cp in eligible if public[cp][0]=='M' and not selector(cp)] or [cp for cp in eligible if public[cp][0] in 'LNSP']
                    if eligible:
                        text=' '.join(('◌' if 0x25cc in union else '')+chr(cp) for cp in eligible[:6]);role='native mark/symbol study'
                    else:text='';role='control/space-only source; no visible style sample'
        needed={ord(c) for c in text if not c.isspace() and not selector(ord(c))}
        loaded=[]
        for font,offered,_ in fonts:
            if needed&offered:
                loaded.append({key:font[key] for key in ['family','file','sha256']});needed-=offered
        assert not needed,(group['source'],needed)
        if not loaded:loaded=[{key:fonts[0][0][key] for key in ['family','file','sha256']}]
        for f in loaded:assert hashlib.sha256((ROOT/f['file']).read_bytes()).hexdigest()==f['sha256']
        rows.append(dict(index=index,source=group['source'],sourceSha256=hashlib.sha256((ROOT/group['source']).read_bytes()).hexdigest(),
            files=len(fonts),contributed=len(novel),role=role,text=text,fonts=loaded,
            allFamilies=[f['family'] for f,_,_ in fonts],declaredStyles=sorted({f.get('style','') for f,_,_ in fonts})))
    report=dict(unicode='18.0.0',status='Review inventory only; source presence and sample selection are not style acceptance or language validation.',
        manifestSha256=hashlib.sha256((ROOT/'js/font-manifest.js').read_bytes()).hexdigest(),sources=len(rows),shards=len(data['fonts']),
        samples=rows)
    target=ROOT/'output/font-review/source-style-atlas.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(rows)} source rows covering {len(data["fonts"])} shards; selected sample fonts and assigned coverage verified')
    return report


if __name__=='__main__':build()
