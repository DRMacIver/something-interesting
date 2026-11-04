"""Offline font specimens: native HarfBuzz shaping, exact SVG outlines, PNG.

No browser, server, network, system-font fallback, or image generation service.
This is a font review tool, not a replacement for the app's bidi/layout renderer.
Input JSON: {"samples": [{"label": "...", "font": "path", "text": "..."}]}.
Rows can instead specify ordered `runs`, each with font/text and optional
HarfBuzz direction/script/language. Run order is explicit, not paragraph bidi.
Use --atlas-page N for one page of the existing source inventory (1-based).
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess

import pymupdf
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[2]
DAD = ROOT / 'assets/fonts/dad-lettering-unicode.woff2'


def local_path(value):
    p = Path(value)
    return p if p.is_absolute() else ROOT / p


class Font:
    def __init__(self, path):
        self.path = local_path(path)
        self.sha256 = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.tt = TTFont(self.path,recalcBBoxes=False,recalcTimestamp=False)
        # HarfBuzz needs decoded sfnt bytes, not the browser's WOFF2 wrapper.
        self.tt.flavor = None
        stream = io.BytesIO(); self.tt.save(stream)
        self.hb = hb.Font(hb.Face(stream.getvalue()))
        if not self.hb.face.glyph_count:
            raise ValueError(f'No decoded font glyphs: {path}')
        self.upem = self.hb.face.upem
        self.gs = self.tt.getGlyphSet()
        self.cmap = self.tt.getBestCmap()
        if 'COLR' in self.tt and self.tt['COLR'].version != 0:
            raise ValueError(f'COLRv1 is not supported by this specimen tool: {path}')

    def layers(self, name):
        colr = self.tt.get('COLR')
        layers = colr.ColorLayers.get(name, []) if colr else []
        if not layers:
            return [(name, '#111111', 1)]
        palette = self.tt['CPAL'].palettes[0]
        result = []
        for layer in layers:
            if layer.colorID == 0xffff:
                result.append((layer.name, '#111111', 1))
            else:
                c = palette[layer.colorID]
                result.append((layer.name, f'#{c.red:02x}{c.green:02x}{c.blue:02x}', c.alpha / 255))
        return result

    def shape(self, text, size, **options):
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        for key in ('direction', 'script', 'language'):
            if options.get(key): setattr(buf, key, options[key])
        hb.shape(self.hb, buf)
        scale = size / self.upem
        x = y = 0; paths = []; glyphs = []; bounds = []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            if info.codepoint == 0:
                raise ValueError(f'Missing shaped glyph in {self.path}: {text!r}, cluster {info.cluster}')
            name = self.tt.getGlyphName(info.codepoint)
            tx = (x + pos.x_offset) * scale
            ty = -(y + pos.y_offset) * scale
            for layer, color, opacity in self.layers(name):
                pen = SVGPathPen(self.gs); self.gs[layer].draw(pen)
                bp = BoundsPen(self.gs); self.gs[layer].draw(bp)
                if bp.bounds:
                    a,b,c,d = bp.bounds
                    bounds.append((tx+a*scale,ty-d*scale,tx+c*scale,ty-b*scale))
                if pen.getCommands():
                    paths.append(f'<path fill="{color}" fill-opacity="{opacity}" d="{pen.getCommands()}" transform="translate({tx} {ty}) scale({scale} {-scale})"/>')
            glyphs.append({'name': name, 'gid': info.codepoint, 'cluster': info.cluster,
                'advance': [pos.x_advance, pos.y_advance], 'offset': [pos.x_offset, pos.y_offset]})
            x += pos.x_advance; y += pos.y_advance
        ink = [min(b[0] for b in bounds),min(b[1] for b in bounds),max(b[2] for b in bounds),max(b[3] for b in bounds)] if bounds else [0,0,0,0]
        return {'paths': paths, 'bounds': ink, 'advance': x*scale, 'glyphs': glyphs,
            'direction': str(buf.direction), 'script':str(buf.script), 'language':str(buf.language),
            'font': str(self.path), 'sha256': self.sha256, 'text': text}


def atlas_samples(page):
    data = json.loads((ROOT/'output/font-review/source-style-atlas.json').read_text())
    pages = math.ceil(len(data['samples'])/12)
    if not 1 <= page <= pages: raise ValueError(f'Atlas page must be 1–{pages}')
    rows = data['samples'][(page-1)*12:page*12]
    # Reuse the project's pinned grapheme boundaries and shaping aliases locally.
    script = """import {graphemes} from './js/unicode.js';
import {nativeShapingText} from './js/native-shaping.js';
let input='';for await(const chunk of process.stdin)input+=chunk;
console.log(JSON.stringify(JSON.parse(input).map(t=>graphemes(t).map(nativeShapingText))));"""
    clusters = json.loads(subprocess.run(['node','--input-type=module','-e',script],cwd=ROOT,
        input=json.dumps([r['text'] for r in rows]),text=True,capture_output=True,check=True,timeout=20).stdout)
    cache = {}; result = []
    for row, pieces in zip(rows, clusters):
        fonts = [(f,cache.setdefault(f['file'],set())) for f in row['fonts']]
        for f, points in fonts:
            if not points: points.update(TTFont(ROOT/f['file']).getBestCmap())
        # Prefer one complete source face before per-grapheme shard routing.
        needed = {ord(c) for c in ''.join(pieces) if not c.isspace() and not is_selector(ord(c))}
        complete = next((f for f,points in fonts if needed <= points),None)
        runs = []
        for piece in pieces:
            cps = {ord(c) for c in piece if not c.isspace() and not is_selector(ord(c))}
            f = complete or next((f for f,points in fonts if cps <= points),None)
            if f is None: raise ValueError(f'No complete native grapheme font for source {row["source"]}: {piece!r}')
            if runs and runs[-1]['font'] == f['file']: runs[-1]['text'] += piece
            else: runs.append({'font':f['file'],'text':piece})
        result.append({'label':f'{row["index"]+1}. {Path(row["source"]).name} — {row["role"]}',
                       'runs':runs, 'logicalText':row['text']})
    return result


def is_selector(cp):
    return 0xfe00 <= cp <= 0xfe0f or 0xe0100 <= cp <= 0xe01ef


def render(samples, output, sizes=(22,44)):
    if not samples or not sizes or any(s <= 0 or not math.isfinite(s) for s in sizes):
        raise ValueError('At least one sample and positive finite sizes are required')
    cache = {}; parts = []; reports = []; top = 20; width = 1180
    def shaped(run, size):
        p = str(local_path(run['font']))
        if p not in cache: cache[p] = Font(p)
        return cache[p].shape(run['text'],size,**{k:run[k] for k in ('direction','script','language') if k in run})
    for row in samples:
        label = row.get('label','Specimen')
        # Labels are also outlined: exported SVG never needs a system font.
        heading = shaped({'font':str(DAD),'text':label},12)
        parts.append(f'<g transform="translate(18 {top+14})">'+''.join(heading['paths'])+'</g>')
        top += 28; records = []
        runs = row.get('runs') if 'runs' in row else [{k:row[k] for k in ('font','text','direction','script','language') if k in row}]
        for size in sizes:
            lines = [shaped(r,size) for r in runs]
            asc = max([size*.75]+[-s['bounds'][1] for s in lines]); desc = max([4]+[s['bounds'][3] for s in lines])
            baseline = top+asc
            dad = shaped({'font':str(DAD),'text':'BESIDE DAD:'},size if size == sizes[0] else 12)
            parts.append(f'<g transform="translate(18 {baseline})">'+''.join(dad['paths'])+'</g>')
            x = 200
            for s in lines:
                x += max(0,-s['bounds'][0])
                parts.append(f'<g transform="translate({x} {baseline})">'+''.join(s.pop('paths'))+'</g>')
                width = max(width,math.ceil(x+max(s['advance'],s['bounds'][2])+20))
                x += s['advance']; records.append({'size':size,**s})
            top = baseline+desc+14
        parts.append(f'<path d="M18 {top} H{width-18}" stroke="#ddd"/>'); top += 14
        reports.append({'label':label,'logicalText':row.get('logicalText'), 'runs':records})
    output = Path(output); output.parent.mkdir(parents=True,exist_ok=True)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{math.ceil(top)}"><rect width="100%" height="100%" fill="white"/>'+''.join(parts)+'</svg>'
    svg_path = output.with_suffix('.svg'); svg_path.write_text(svg)
    with pymupdf.open(stream=svg.encode(),filetype='svg') as doc:
        doc[0].get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False).save(output.with_suffix('.png'))
    report = {'renderer':'offline HarfBuzz + fontTools SVG outlines + PyMuPDF',
        'limitations':['Explicit native runs, not full app paragraph bidi/layout, custom combining/Egyptian composition, emoji optical treatment, or browser equivalence.','COLRv0 palette 0 supported; COLRv1 rejected. No system fallback.','Atlas uses project grapheme segmentation/native aliases, then native font shaping; inventory samples remain glyph studies where labelled.'],
        'width':width,'height':math.ceil(top),'samples':reports}
    output.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--spec',type=Path,help='JSON with explicit font/text samples or ordered runs')
    source.add_argument('--atlas-page',type=int,help='Existing source atlas page, 1-based')
    p.add_argument('--output',type=Path,required=True,help='Output stem; writes .png, .svg, .json')
    args = p.parse_args()
    samples = atlas_samples(args.atlas_page) if args.atlas_page else json.loads(args.spec.read_text())['samples']
    report = render(samples,args.output)
    print(f'{args.output.with_suffix(".png").resolve()} ({len(report["samples"])} samples)')


if __name__ == '__main__': main()
