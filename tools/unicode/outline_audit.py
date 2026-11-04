"""Check routed character drawings separately from raw cmap coverage.

Replay the app's actual single-character font selection, then inspect positive
outline or COLR-layer bounds in a selected bundled font. This does not validate
glyph identity, linguistic shaping, final style or contextual combinations.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb

from audit import ROOT, inventory, properties, records, code_range, font_dependent_formats

SEMANTIC_BLANKS={0x2800:'Braille pattern blank has zero dots; structural identity tested in tests/test_font_grid.py',0x13441:'Egyptian full blank intentionally reserves whitespace; Unicode18 section11.4.3 and js/egyptian-layout.js verify spacing',0x13442:'Egyptian half blank intentionally reserves whitespace; Unicode18 section11.4.3 and js/egyptian-layout.js verify spacing'}
NATIVE_CONTEXT={0x11d45:'Masaram Gondi virama selects contextual base forms',0x11d97:'Gunjala Gondi virama selects contextual base forms'}


def drawn_glyph(font,name,seen=None,gs=None):
    seen=set() if seen is None else seen
    if name in seen:return False
    seen.add(name)
    gs=font.getGlyphSet() if gs is None else gs
    pen=BoundsPen(gs);gs[name].draw(pen)
    if pen.bounds:
        x0,y0,x1,y1=pen.bounds
        if x1>x0 and y1>y0:return True
    # The production emoji font uses COLR v0 roots with no monochrome outline.
    layers=getattr(font.get('COLR'),'ColorLayers',{}) or {}
    return any(drawn_glyph(font,layer.name,seen,gs) for layer in layers.get(name,[]))


def shaping_font(font):
    stream=io.BytesIO();flavor=font.flavor;font.flavor=None
    try:font.save(stream)
    finally:font.flavor=flavor
    return hb.Font(hb.Face(stream.getvalue()))


def shaped_glyph_names(font,shaper,text):
    buffer=hb.Buffer();buffer.add_str(text);buffer.guess_segment_properties();hb.shape(shaper,buffer)
    return [font.getGlyphName(info.codepoint) for info in buffer.glyph_infos]


def routed_points(points):
    script="""
import {requiredFonts,contains} from './js/fonts.js';
import inventory from './js/font-manifest.js';
import {fontRuns} from './js/emoji-routing.js';
import {makeFontString} from './js/comic.js';
import {readFileSync} from 'node:fs';
const points=JSON.parse(readFileSync(0,'utf8'));
const files=['assets/fonts/dad-lettering-unicode.woff2'],ids=new Map([[files[0],0]]),routes=[],gaps=[];
for(const cp of points){
  const text=String.fromCodePoint(cp),selection=requiredFonts([text]);
  const run=fontRuns(text)[0];
  const ordered=[...makeFontString(20,selection.fonts.map(f=>f.family),run.emojiPolicy,run.fontFamily).matchAll(/"([^"]+)"/g)].map(m=>m[1]);
  const candidates=new Map(selection.fonts.filter(f=>contains(f.ranges,cp)).map(f=>[f.family,f.file]));
  if(contains(inventory.baseRanges,cp))candidates.set('Dad Lettering',files[0]);
  const selected=selection.emojiFallbacks.length?[]:ordered.filter(f=>candidates.has(f)).slice(0,1).map(f=>candidates.get(f));
  const indexes=selected.map(file=>{if(!ids.has(file)){ids.set(file,files.length);files.push(file);}return ids.get(file);});
  if(!indexes.length||selection.missing.length||selection.emojiFallbacks.length)gaps.push({cp,missing:selection.missing,emojiFallbacks:selection.emojiFallbacks});
  routes.push([cp,indexes]);
}
process.stdout.write(JSON.stringify({files,routes,gaps}));
"""
    result=subprocess.run(['node','--input-type=module','-e',script],input=json.dumps(sorted(points)),text=True,capture_output=True,cwd=ROOT,check=True)
    return json.loads(result.stdout)


def audit():
    chars=inventory();ignored=set()
    for row in records(ROOT/'data/unicode/18.0.0/DerivedCoreProperties.txt'):
        if row[1]=='Default_Ignorable_Code_Point':ignored.update(code_range(row[0]))
    format_glyphs=font_dependent_formats()&chars.keys()
    visible={cp for cp,category in chars.items() if category not in {'Cc','Cf','Zs','Zl','Zp'} and cp not in ignored}|format_glyphs
    routes=routed_points(visible)
    by_file={i:[] for i in range(len(routes['files']))}
    for cp,files in routes['routes']:
        for i in files:by_file[i].append(cp)
    drawn=set();empty={};fonts=[];substituted=[]
    for i,relative in enumerate(routes['files']):
        blob=(ROOT/relative).read_bytes();font=TTFont(io.BytesIO(blob));cmap=font.getBestCmap();cache={};gs=font.getGlyphSet();shaper=None
        for cp in by_file[i]:
            # Egyptian blanks use the app's spacing compositor; a source font
            # can contain internal helper ink that is not the final app output.
            if cp in SEMANTIC_BLANKS:continue
            name=cmap.get(cp)
            if name is None or font.getGlyphID(name)==0:continue
            if name not in cache:cache[name]=drawn_glyph(font,name,gs=gs)
            if cache[name]:drawn.add(cp)
            else:
                # A dotted-circle carrier emitted for an isolated empty virama
                # is not a drawing of that virama. Keep its contextual proof
                # separate even when the font emits visible carrier ink.
                if cp in NATIVE_CONTEXT:
                    empty.setdefault(cp,[]).append(relative);continue
                # Shorthand and other complex fonts can use an empty input
                # glyph that GSUB expands into several real component drawings.
                if shaper is None:shaper=shaping_font(font)
                names=shaped_glyph_names(font,shaper,chr(cp))
                for output in names:
                    if output not in cache:cache[output]=drawn_glyph(font,output,gs=gs)
                if all(font.getGlyphID(n)>0 for n in names) and any(cache[n] for n in names):
                    drawn.add(cp);substituted.append({'cp':cp,'file':relative,'outputGlyphs':len(names)})
                else:empty.setdefault(cp,[]).append(relative)
        fonts.append({'file':relative,'sha256':hashlib.sha256(blob).hexdigest(),'requestedCharacters':len(by_file[i])})
        font.close()
    exceptions={cp:SEMANTIC_BLANKS.get(cp,NATIVE_CONTEXT.get(cp)) for cp in visible-drawn if cp in SEMANTIC_BLANKS or cp in NATIVE_CONTEXT}
    unexplained=visible-drawn-exceptions.keys()
    scripts=properties(ROOT/'data/unicode/18.0.0/Scripts.txt')
    routed_sources={cp:[routes['files'][i] for i in indexes] for cp,indexes in routes['routes'] if cp in exceptions}
    return {'unicode':'18.0.0','scope':'Assigned drawing requirements, including font-dependent prepended format signs: actual app single-character font loading, with positive outline/COLR-layer bounds or default isolated GSUB output in the first painted bundled font. Other controls/spaces/default-ignorables require separate behaviour evidence. Not semantic, linguistic, stylistic or full contextual rendering validation.','visibleRequirements':len(visible),'fontDependentFormatRequirements':len(format_glyphs),'routedDrawingPresent':len(drawn),'shapedEmptyRoots':substituted,'semanticBlankOrNativeContext':[{'cp':cp,'reason':reason,'routedSources':routed_sources[cp]} for cp,reason in sorted(exceptions.items())],'unexplainedDrawingGaps':[{'cp':cp,'category':chars[cp],'script':scripts.get(cp),'emptySources':empty.get(cp,[])} for cp in sorted(unexplained)],'routingGaps':routes['gaps'],'fonts':fonts,'references':['https://www.unicode.org/versions/Unicode18.0.0/core-spec/chapter-11/'],'limits':['Font-dependent format signs are counted as drawing requirements and also need contextual behaviour validation; other controls need separate behaviour evidence.','Single-character selection is not proof that a larger cluster or mixed-script run keeps the same font.','Positive geometry does not rule out a wrong drawing or a visible placeholder.','COLR v0 layers are inspected as outlines; final colour/alpha/pixel appearance still needs browser evidence.','Context-only exceptions require independent native shaping tests; they are not invented visible drawings.','Known semantic blanks use dedicated app layout; other dynamic compositors still require their own runtime evidence.']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'docs/unicode-outline-coverage.json')
    args=parser.parse_args();report=audit();args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(f"{report['routedDrawingPresent']}/{report['visibleRequirements']} routed drawings; {len(report['semanticBlankOrNativeContext'])} explicit exceptions; {len(report['unexplainedDrawingGaps'])} unexplained drawing gaps; {len(report['routingGaps'])} routing gaps")
