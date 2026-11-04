"""Build an isolated candidate font; never updates production manifests."""
import argparse
import json
import hashlib
import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from build_emoji import outline
from prototype_region_flags import prepare, label, EXAMPLES, ROOT


from flag_outlines import clean_flag_outline

def flag_outline(mask, transform):
    return clean_flag_outline(mask, transform, outline)

def compile_flags(selected, prepare, prefix='region-flags', form_provider=None,
                  family_name='Dad Regional Flag Candidate', glyph_prefix='flag.', fallback_provider=None):
    forms = {key: form_provider(source['sequence']) if form_provider else [source['sequence']] for key,source in selected}
    glyphs = {'.notdef': TTGlyphPen(None).glyph()}
    metrics = {'.notdef': (860,0)}
    cmap, layers, rules, reports = {}, {}, [], []
    palette = [(255,255,255),(17,17,17)]
    for cp in sorted({ord(c) for texts in forms.values() for text in texts for c in text}):
        name = f'u{cp:04X}'
        cmap[cp] = name
        glyphs[name] = TTGlyphPen(None).glyph()
        metrics[name] = (0,0)
    for region, source in selected:
        (paper, *colours, ink), report = prepare(region)
        ys,xs = np.nonzero(paper)
        transform = xs.min(),ys.min(),760/max(np.ptp(xs)+1,np.ptp(ys)+1)
        advance = round((np.ptp(xs)+1)*transform[2])+100
        name = glyph_prefix+region
        glyphs[name], removed = flag_outline(fallback_provider(region) if fallback_provider else ink, transform)
        metrics[name] = (advance,50)
        layers[name] = []
        layer_reports = []
        for i,(mask,rgb) in enumerate([(paper,(255,255,255)),*zip(colours,map(tuple,report['rgbs'])),(ink,(17,17,17))]):
            if rgb not in palette:
                palette.append(rgb)
            layer = name+f'.layer{i}'
            glyphs[layer], dropped = flag_outline(mask,transform)
            metrics[layer] = (advance,50)
            layers[name].append((layer,palette.index(rgb)))
            layer_reports.append(dict(rgb=rgb,contours=int(glyphs[layer].numberOfContours),removedZeroAreaContours=dropped))
        reports.append(dict(region=region,sequence=source['sequence'],qualificationForms=forms[region],glyphName=name,advance=advance,
                            removedZeroAreaInkContours=removed,layers=layer_reports,penTreatment=report))
        print(region, 'compiled', flush=True)
    variations = {}
    for entry in reports:
        for text in entry['qualificationForms']:
            bare = text.replace('\ufe0f','').replace('\ufe0e','')
            if len(bare)==1:
                cmap[ord(bare)] = entry['glyphName']
            for base,selector in zip(text,text[1:]):
                if ord(selector) in (0xfe0e,0xfe0f):
                    variations.setdefault(ord(selector),set()).add(ord(base))
    for entry in reports:
        for bare in sorted({text.replace('\ufe0f','').replace('\ufe0e','') for text in entry['qualificationForms']}):
            if len(bare)>1:
                rules.append((len(bare),'sub '+' '.join(cmap[ord(c)] for c in bare)+' by '+entry['glyphName']+';'))
    fb = FontBuilder(1000,isTTF=True)
    fb.setupGlyphOrder(list(glyphs));fb.setupCharacterMap(cmap);fb.setupGlyf(glyphs)
    for name, glyph in glyphs.items():
        glyph.recalcBounds(fb.font['glyf'])
        metrics[name] = (metrics[name][0], getattr(glyph, 'xMin', 0))
    fb.setupHorizontalMetrics(metrics);fb.setupHorizontalHeader(ascent=900,descent=-100)
    identifier=family_name.replace(' ','')
    fb.setupNameTable(dict(familyName=family_name,styleName='Regular',uniqueFontIdentifier=identifier,fullName=family_name,psName=identifier))
    fb.setupOS2(sTypoAscender=900,sTypoDescender=-100,usWinAscent=900,usWinDescent=100)
    fb.setupPost();fb.setupMaxp()
    if variations:
        uvs=CmapSubtable.newSubtable(14);uvs.platformID=0;uvs.platEncID=5;uvs.language=0;uvs.cmap={}
        uvs.uvsDict={selector:[(cp,None) for cp in sorted(points)] for selector,points in variations.items()}
        fb.font['cmap'].tables.append(uvs)
    fb.font['COLR'] = buildCOLR(layers,version=0)
    fb.font['CPAL'] = buildCPAL([[tuple(c/255 for c in rgb)+(1.0,) for rgb in palette]])
    addOpenTypeFeaturesFromString(fb.font,'languagesystem DFLT dflt; feature liga {\n'+'\n'.join(rule for _,rule in sorted(rules,key=lambda r:-r[0]))+'\n} liga;')
    fb.font['head'].created = fb.font['head'].modified = 2082844800
    fb.font.flavor='woff2'
    out=ROOT/'output/font-review/pen-translation'
    path=out/(prefix+'-candidate.woff2');fb.save(path)
    (out/(prefix+'-candidate.json')).write_text(json.dumps(dict(candidateOnly=True,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),flags=reports),indent=2)+'\n')
    from preview_region_flag_font import preview
    preview(prefix)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--regions', nargs='*', default=EXAMPLES)
    args = parser.parse_args()
    spec = json.loads((ROOT/'docs/flags-emoji-svg-source-probe.json').read_text())
    sources = {label(e['sequence']): e for e in spec['files'] if e.get('licenseFamily') == 'region-flags-public-domain'}
    if args.regions == ['all']:
        args.regions = sorted(sources)
        assert len(args.regions) == 262
        preflight = json.loads((ROOT/'output/font-review/pen-translation/region-flags-contour-preflight.json').read_text())
        assert len(preflight) == 262 and {e['region'] for e in preflight} == set(sources)
        assert not any('error' in e for e in preflight), 'Resolve regional preflight failures before compiling all flags'
    selected = [sources[region] for region in args.regions]
    compile_flags(list(zip(args.regions, selected)), prepare)


if __name__ == '__main__':
    main()
