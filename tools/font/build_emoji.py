"""Prepare changed glyph assets, then assemble the single production emoji font.

The reviewed legacy vector font is a prepared source, not a generated runtime
fallback. New artwork is compiled into per-glyph content-addressed artifacts.
Font assembly never rasterizes or retraces unchanged legacy artwork.
"""
import argparse
import copy
import hashlib
import gzip
import io
import json
from pathlib import Path
import time

from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.colorLib.builder import buildCOLR,buildCPAL

from emoji_glyph_cache import GlyphCache
from build_adventure_emoji import POINTS,SELECTIONS,prepare_glyph
from build_emoji_ink import build_ink
from emoji_font_assembly import save_webfont

ROOT=Path(__file__).resolve().parents[2]


def outline(mask,transform):
    """Compatibility for historical source-preparation/review utilities."""
    from prepare_legacy_emoji import outline as trace
    return trace(mask,transform)


def glyph_from_commands(commands):
    recording=RecordingPen();recording.value=commands
    pen=TTGlyphPen(None);recording.replay(pen)
    return pen.glyph()


def prepared_font(source):
    path=ROOT/source['file'];raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==source['sha256'],'Prepared source changed without provenance update'
    sfnt=gzip.decompress(raw) if path.suffix=='.gz' else raw
    if 'sfntSha256' in source:
        assert hashlib.sha256(sfnt).hexdigest()==source['sfntSha256'],'Prepared SFNT checksum mismatch'
    return TTFont(io.BytesIO(sfnt),recalcTimestamp=False,recalcBBoxes=False)


def build(output_root=None,cache_dir=None):
    started=time.monotonic()
    destination=ROOT if output_root is None else Path(output_root)
    source=json.loads((ROOT/'data/font-sources/dad-emoji-prepared.json').read_text())
    assert hashlib.sha256((ROOT/source['preparationRecipe']).read_bytes()).hexdigest()==source['preparationRecipeSha256'],'Legacy preparation recipe changed; refresh its prepared vector input before assembling'
    font=prepared_font(source)
    entry=copy.deepcopy(source['manifest'])
    cache=GlyphCache(cache_dir or ROOT/'build/font-cache/emoji-glyphs')
    layers={name:[(l.name,l.colorID) for l in values] for name,values in font['COLR'].ColorLayers.items()}
    palettes=[[(c.red,c.green,c.blue,c.alpha) for c in row] for row in font['CPAL'].palettes]
    colours=palettes[0]
    order=font.getGlyphOrder();cmap=font.getBestCmap();records=[];updated=set()
    for index,cp in enumerate(POINTS):
        prepared,record=prepare_glyph(index,cp,cache);records.append(record)
        names={cmap[cp]}
        for table in font['cmap'].tables:
            if table.format==14:
                names.update(name for pairs in table.uvsDict.values() for base,name in pairs if base==cp and name)
        def install(name,commands):
            updated.add(name)
            glyph=glyph_from_commands(commands);font['glyf'][name]=glyph
            glyph.recalcBounds(font['glyf'])
            font['hmtx'][name]=(prepared['advance'],glyph.xMin if glyph.numberOfContours else 0)
            if name not in order:order.append(name)
        new_layers=[]
        for j,layer in enumerate(prepared['layers']):
            colour=tuple(layer['rgb'])+(255,)
            if colour not in colours:
                for palette in palettes:palette.append(colour)
            name=f'custom.{cp:X}.layer{j}';install(name,layer['outline'])
            new_layers.append((name,colours.index(colour)))
        for name in sorted(names):
            install(name,prepared['base']);layers[name]=new_layers.copy()
    prepared_at=time.monotonic()
    print(f'Prepared glyphs in {prepared_at-started:.3f}s ({cache.hits} reused, {cache.misses} compiled)',flush=True)
    font.setGlyphOrder(order)
    # Existing SFNT glyph records already contain reviewed bounds/bytecode.
    # Keep their compiled bytes instead of unpacking and recompiling them.
    for name in updated:
        glyph=font['glyf'][name]
        if glyph.numberOfContours:
            for axis in ('x','y'):
                for edge,op in [('Min',min),('Max',max)]:
                    attr=axis+edge
                    setattr(font['head'],attr,op(getattr(font['head'],attr),getattr(glyph,attr)))
            advance,lsb=font['hmtx'][name];width=glyph.xMax-glyph.xMin
            font['hhea'].minLeftSideBearing=min(font['hhea'].minLeftSideBearing,lsb)
            font['hhea'].minRightSideBearing=min(font['hhea'].minRightSideBearing,advance-lsb-width)
            font['hhea'].xMaxExtent=max(font['hhea'].xMaxExtent,lsb+width)
            font['maxp'].maxPoints=max(font['maxp'].maxPoints,len(glyph.coordinates))
            font['maxp'].maxContours=max(font['maxp'].maxContours,glyph.numberOfContours)
    font['hhea'].advanceWidthMax=max(advance for advance,_ in font['hmtx'].metrics.values())
    font['COLR']=buildCOLR(layers,version=0)
    font['CPAL']=buildCPAL([[tuple(v/255 for v in colour) for colour in palette] for palette in palettes])
    # Keep existing source notices, and identify the added artwork separately.
    old=font['name'].getDebugName(0) or ''
    font['name'].setName(old+'\nIncludes custom adventure artwork and restored Hobbes drawings; see assets/emoji-concepts for source and review records.',0,3,1,0x409)
    font['head'].created=font['head'].modified=2082844800
    font.recalcTimestamp=False;font.flavor='woff2'
    output=destination/'assets/fonts/dad-emoji.woff2';output.parent.mkdir(parents=True,exist_ok=True)
    save_webfont(font,output)
    print(f'Wrote colour font in {time.monotonic()-prepared_at:.3f}s',flush=True)
    entry.update(sha256=hashlib.sha256(output.read_bytes()).hexdigest(),bytes=output.stat().st_size)
    entry['companions']=[build_ink(destination,source_font=font)]
    entry['preparedSourceSha256']=source['sha256']
    entry['customArtwork']=[dict(codepoint=r['codepoint'],artifactKey=r['artifactKey']) for r in records]
    entry['customOptics']={chr(int(cp,16)):{key:spec[key] for key in ('strokeRatio','scale') if key in spec}
                           for cp,spec in SELECTIONS.items() if any(key in spec for key in ('strokeRatio','scale'))}
    manifest=destination/'js/emoji-manifest.js';manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_text('// Generated by tools/font/build_emoji.py\nexport default '+json.dumps(entry,separators=(',',':'))+';\n')
    review=destination/'assets/emoji-concepts/production-review.json';review.parent.mkdir(parents=True,exist_ok=True)
    review.write_text(json.dumps(dict(font=entry,drawings=records,recipeSha256=hashlib.sha256((ROOT/'tools/font/build_adventure_emoji.py').read_bytes()).hexdigest()),ensure_ascii=False,indent=2)+'\n')
    receipt=dict(cacheHits=cache.hits,cacheMisses=cache.misses,keys=cache.keys,
                 preparationSeconds=prepared_at-started,assemblySeconds=time.monotonic()-prepared_at,
                 elapsedSeconds=time.monotonic()-started,outputSha256=entry['sha256'])
    report=destination/'output/font-review/emoji-build.json';report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root',type=Path)
    parser.add_argument('--cache-dir',type=Path)
    args=parser.parse_args();build(args.output_root,args.cache_dir)
