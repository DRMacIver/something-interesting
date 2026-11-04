"""Finite standardized contextual pairs must change real native shaping."""
import json
import subprocess
from test_font_scripts import ROOT,shape
from test_contextual_variants import pinned_context_native, assert_raw_native_context, assert_context_identity, drawing


def test_all_contextual_standardized_variants_keep_complete_native_source_shaping():
    requests=[];counts={}
    for row in (ROOT/'data/unicode/18.0.0/StandardizedVariants.txt').read_text().splitlines():
        if not row or row.startswith('#'):continue
        cp,vs=[int(v,16) for v in row.split(';')[0].split()]
        script='Mongolian' if 0x1800<=cp<=0x18af else 'PhagsPa' if 0xa840<=cp<=0xa87f else 'Manichaean' if 0x10ac0<=cp<=0x10aff else None
        if not script:continue
        counts[script]=counts.get(script,0)+1
        base=chr({'Mongolian':0x1820,'PhagsPa':0xa840,'Manichaean':0x10ac0}[script])
        requests.append(dict(script=script,selected=chr(cp)+chr(vs),ordinary=chr(cp),contexts=[['',''],['',base],[base,''],[base,base]]))
    assert counts=={'Mongolian':117,'PhagsPa':6,'Manichaean':5}
    code=r'''
      import fs from 'node:fs';
      import {requiredFonts} from './js/fonts.js';
      import {fontRuns} from './js/emoji-routing.js';
      const requests=JSON.parse(fs.readFileSync(0,'utf8'));
      console.log(JSON.stringify(requests.map(row=>{
        const contexts=row.contexts.map(([a,b])=>{
          const text=a+row.selected+b,selection=requiredFonts([text]),runs=fontRuns(text);
          if(selection.missing.length||selection.fonts.length!==1||runs.length!==1||runs[0].text!==text)throw Error(text);
          return {text,ordinary:a+row.ordinary+b,font:selection.fonts[0]};
        });return {...row,contexts};
      })));
    '''
    rows=json.loads(subprocess.check_output(['node','--input-type=module','-e',code],cwd=ROOT,input=json.dumps(requests),text=True))
    entries={entry['file']:entry for entry in json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))['fonts']}
    native_paths={}
    for row in rows:
        changed=False
        for context in row['contexts']:
            font=context['font'];file=font['file']
            assert font['source'].endswith('/NotoSans'+row['script']+'-Regular.ttf')
            entry=entries[file];assert entry['source']==font['source']
            if file not in native_paths:
                native_font,native_paths[file]=pinned_context_native(entry)
                native_font.close()
            original,native=ROOT/entry['source'],native_paths[file]
            source_selected,frozen=assert_raw_native_context(original,native,context['text'])
            selected=shape(ROOT/file,context['text'],True)
            assert_context_identity(frozen,selected)
            source_plain,ordinary_native=assert_raw_native_context(original,native,context['ordinary'])
            assert_context_identity(ordinary_native,shape(ROOT/file,context['ordinary'],True))
            # Prove real selector ink in the native source, never pressure noise.
            changed|=[drawing(original,g[0]) for g in source_selected if drawing(original,g[0])]!=[drawing(original,g[0]) for g in source_plain if drawing(original,g[0])]
        assert changed,row['selected']


def test_only_standardized_mark_selector_has_native_dotted_form_in_context():
    categories={int(f[0],16):f[2] for row in (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines() if (f:=row.split(';'))}
    mark_pairs=[]
    for row in (ROOT/'data/unicode/18.0.0/StandardizedVariants.txt').read_text().splitlines():
        if not row or row.startswith('#'):continue
        cp,vs=[int(v,16) for v in row.split(';')[0].split()]
        if categories.get(cp,'').startswith('M'):mark_pairs.append((cp,vs))
    assert mark_pairs==[(0x1031,0xfe00)]
    entries=json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))['fonts']
    entry=next(e for e in entries if e['source'].endswith('/PadaukBook-Regular.ttf'))
    native_font,native=pinned_context_native(entry)
    native_font.close()
    original=ROOT/entry['source']
    for text in ['ေ\ufe00','ကေ\ufe00','ကေ\ufe00ခ','ကေ\ufe00ကေ']:
        source_selected,frozen=assert_raw_native_context(original,native,text)
        assert_context_identity(frozen,shape(ROOT/entry['file'],text,True))
        plain=text.replace('\ufe00','')
        source_plain,ordinary_native=assert_raw_native_context(original,native,plain)
        assert_context_identity(ordinary_native,shape(ROOT/entry['file'],plain,True))
        assert [drawing(original,g[0]) for g in source_selected if drawing(original,g[0])]!=[drawing(original,g[0]) for g in source_plain if drawing(original,g[0])]
        assert shape(ROOT/entry['file'],text,True)!=shape(ROOT/entry['file'],plain,True)
