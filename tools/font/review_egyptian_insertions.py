"""Inventory pinned font-specific insertion cells without executing source code.

These are Egyptian Text cell coordinates, not normalized UniHieroglyphica
anchors. Preserve every source alternative: selecting a cell requires matching
its actual container glyph and shaping metrics first.
"""
import ast
import hashlib
import json
import re
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'build/unicode-sources/egyptian-text'
CONTROLS={'ts':0x13432,'bs':0x13433,'te':0x13434,'be':0x13435,
          'mi':0x13439,'ti':0x1343a,'bi':0x1343b}


def literal_assignment(path,name):
    for node in ast.parse(path.read_text()).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError(f'Missing literal {name}')


def build():
    manifest=json.loads((ROOT/'data/font-sources/egyptian-text.json').read_text())
    for name in ['insertions.py','config.py','eot.ttf','TOOLS-LICENSE.txt']:
        path=CACHE/name
        entry=next(e for e in manifest['files'] if e['path']==str(path.relative_to(ROOT)))
        if hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError(f'Unverified source: {name}')
    data=literal_assignment(CACHE/'insertions.py','insertions')
    config=literal_assignment(CACHE/'config.py','pvar')
    font=TTFont(CACHE/'eot.ttf');gs=font.getGlyphSet();reverse={}
    for cp,name in font.getBestCmap().items():reverse.setdefault(name,[]).append(cp)
    rows=[]
    for glyph,controls in data.items():
        if glyph in gs:
            pen=BoundsPen(gs);gs[glyph].draw(pen);bounds=list(pen.bounds) if pen.bounds else None
        else:bounds=None
        areas=[]
        for control,cells in controls.items():
            if control not in CONTROLS:raise ValueError(control)
            for cell,value in cells.items():
                match=re.fullmatch(r'([1-6])([1-6])(?:([xy])(-?\d+))?',value)
                if not match:raise ValueError(value)
                width,height,axis,offset=match.groups()
                areas.append({'control':CONTROLS[control],'name':control,
                    'container_cell':[cell//10,cell%10],'insertion_cell':[int(width),int(height)],
                    'offset_axis':axis,'offset_twentieths':int(offset or 0),'source_value':value})
        rows.append({'source_glyph':glyph,'codepoints':reverse.get(glyph,[]),
                     'source_glyph_present':glyph in gs,'source_bounds':bounds,'areas':areas})
    return {'status':'reference inventory; renderer subset tracked in egyptian-insertion-build.json',
        'source_commit':manifest['commit'],'license':'MIT (metadata), OFL (font)',
        'coordinate_system':{k:config[k] for k in ['hfu','vfu','vbase','sb','chu','vhu']},
        'scope_note':'Font-specific cells and offsets. Do not apply to a different font or assume a generic corner rectangle.',
        'signs':len(rows),'mapped_signs':sum(bool(r['codepoints']) for r in rows),
        'areas':sum(len(r['areas']) for r in rows),'entries':rows}


if __name__=='__main__':
    report=build()
    (ROOT/'docs/egyptian-insertion-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:report[k] for k in ['signs','mapped_signs','areas']})
