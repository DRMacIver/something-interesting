"""Handwritten Greek, including polytonic vowels, from retained OFL sources.

Keep WenKai's native Greek letters. Extend its missing canonical compositions
with Noto's actual accent arrangements, positioned against the new letter's
upper/lower profile. Breathing/acute combinations keep their native side-by-side
arrangement rather than becoming a generic vertical accent stack.
"""
import hashlib
import json
from pathlib import Path
import unicodedata

from fontTools import subset
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables
from fontTools.misc.transform import Transform

from math_unicode_marks import repair_marks, unicode_categories
from optical_anchors import accent_centres
from extend_latin import bounds

ROOT = Path(__file__).resolve().parents[2]


def build(output, manifest):
    main = json.loads((ROOT/'js/font-manifest.js').read_text().split('export default ', 1)[1].rstrip(';\n'))
    source = next(e for e in main['fonts'] if e['source'].endswith('/LXGWWenKai-Regular.ttf')
                  and any(a <= 0x3b1 <= b for a, b in e['ranges']))
    font = TTFont(ROOT/source['file'], recalcTimestamp=False)
    native_path = ROOT/'build/unicode-sources/noto/NotoSans-Regular.ttf'
    native = TTFont(native_path)
    notices = [font['name'].getDebugName(0), native['name'].getDebugName(0)]
    gs, ngs = font.getGlyphSet(), native.getGlyphSet()
    cmap, ncmap = dict(font.getBestCmap()), native.getBestCmap()
    scale = font['head'].unitsPerEm/native['head'].unitsPerEm
    names = font.getGlyphOrder()[:]
    records = []

    def add(cp, pen, advance):
        name = f'greek{cp:04X}'
        glyph = pen.glyph()
        font['glyf'][name] = glyph
        glyph.recalcBounds(font['glyf'])
        font['hmtx'][name] = (advance, getattr(glyph, 'xMin', 0))
        if 'vmtx' in font:
            font['vmtx'][name] = (font['head'].unitsPerEm, 0)
        names.append(name)
        cmap[cp] = name

    # Capital kappa has the same skeleton as Latin K. Use the actual comic's
    # inked K, fitting the native Greek capital height and retaining its advance.
    lettering_path = ROOT/'assets/fonts/dad-lettering-unicode.woff2'
    lettering = TTFont(lettering_path)
    lgs = lettering.getGlyphSet()
    k = lettering.getBestCmap()[ord('K')]
    old_k = cmap[0x39a]
    a,b,c,d = bounds(lgs[k],lgs)
    x0,y0,x1,y1 = bounds(gs[old_k],gs)
    factor = (y1-y0)/(d-b)
    dx = (x0+x1-factor*(a+c))/2
    dy = y0-factor*b
    pen = TTGlyphPen(None)
    lgs[k].draw(TransformPen(Cu2QuPen(pen,max_err=.05,reverse_direction=True),
                           (factor,0,0,factor,dx,dy)))
    add(0x39a,pen,font['hmtx'][old_k][0])
    records.append({'codepoint':0x39a,'method':'reference-lettering K fitted to native kappa capital height',
                    'scale':factor,'offset':[dx,dy]})
    notices.append(lettering['name'].getDebugName(0))

    canonical_parts = {ord(c) for cp in range(0x1f00, 0x2000) if cp in ncmap
                       for c in unicodedata.normalize('NFD', chr(cp))}
    targets = [*sorted(canonical_parts), *range(0x300, 0x370), *range(0x370, 0x400), *range(0x1f00, 0x2000)]
    for cp in dict.fromkeys(targets):
        if cp in cmap or cp not in ncmap:
            continue
        text = chr(cp)
        canonical = unicodedata.normalize('NFC', text)
        if canonical != text and len(canonical) == 1 and ord(canonical) in cmap:
            cmap[cp] = cmap[ord(canonical)]
            records.append({'codepoint': cp, 'canonical': ord(canonical), 'method': 'existing native canonical alias'})
            continue
        parts = unicodedata.normalize('NFD', text)
        base_cp = ord(parts[0])
        base_name = ncmap.get(base_cp)
        replacement = cmap.get(base_cp) if 0x370 <= base_cp <= 0x3ff else None
        pieces, bases = [], []

        def visit(name, transform=Transform()):
            if name == base_name and replacement:
                bases.append(transform)
                return
            glyph = native['glyf'][name]
            if glyph.isComposite():
                for component in glyph.components:
                    child, matrix = component.getComponentInfo()
                    visit(child, transform.transform(Transform(*matrix)))
            else:
                pieces.append((name, transform))

        if replacement and cp >= 0x1f00:
            visit(ncmap[cp])
        pen = TTGlyphPen(None)
        if replacement and len(bases) == 1:
            rec = DecomposingRecordingPen(gs)
            gs[replacement].draw(rec)
            rec.replay(pen)
            old_box = bounds(ngs[base_name], ngs)
            new_box = bounds(gs[replacement], gs)
            old_top, old_bottom = accent_centres(ngs[base_name], ngs, old_box)
            new_top, new_bottom = accent_centres(gs[replacement], gs, new_box)
            base_transform = bases[0]
            assert base_transform[:4] == (1, 0, 0, 1), 'Unexpected native base transform'
            bx, by = base_transform[4:]
            for name, transform in pieces:
                box = bounds(ngs[name], ngs)
                if box is None:
                    continue
                below = transform.transformPoint((0, box[3]))[1] < old_box[1]+by+10
                dx = (new_bottom if below else new_top)-scale*((old_bottom if below else old_top)+bx)
                dy = (new_box[1] if below else new_box[3])-scale*((old_box[1] if below else old_box[3])+by)
                rec = DecomposingRecordingPen(ngs)
                ngs[name].draw(rec)
                rec.replay(TransformPen(pen, Transform(scale, 0, 0, scale, dx, dy).transform(transform)))
            advance = font['hmtx'][replacement][0]
            records.append({'codepoint': cp, 'base': base_cp, 'method': 'native handwritten base and native accent arrangement'})
        else:
            rec = DecomposingRecordingPen(ngs)
            ngs[ncmap[cp]].draw(rec)
            rec.replay(TransformPen(pen, (scale, 0, 0, scale, 0, 0)))
            advance = round(native['hmtx'][ncmap[cp]][0]*scale)
            records.append({'codepoint': cp, 'method': 'native supplementary mark or symbol'})
        add(cp, pen, advance)

    font.setGlyphOrder(names)
    for table in font['cmap'].tables:
        if table.isUnicode() and table.format in {4, 12}:
            table.cmap.update(cmap)
    greek = {cp for cp in cmap if 0x370 <= cp <= 0x3ff or 0x1f00 <= cp <= 0x1fff}
    if 'GDEF' not in font:
        font['GDEF'] = newTable('GDEF')
        gdef = font['GDEF'].table = otTables.GDEF()
        gdef.Version = 0x00010000
        gdef.GlyphClassDef = otTables.ClassDef()
        gdef.GlyphClassDef.classDefs = {cmap[cp]: 1 for cp in greek}
        gdef.AttachList = gdef.LigCaretList = gdef.MarkAttachClassDef = None
    repair_marks(font, {cmap[cp] for cp in greek}, unicode_categories(ROOT))
    options = subset.Options()
    options.glyph_names = True
    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=greek | canonical_parts | {cp for cp in cmap if 0x300 <= cp < 0x370} | {0x20})
    sub.subset(font)
    family = 'Dad Handwritten Greek'
    for record in font['name'].names:
        if record.nameID in {1, 2, 3, 4, 6, 16, 17}:
            value = 'Regular' if record.nameID in {2, 17} else family.replace(' ', '') if record.nameID == 6 else family
            record.string = value.encode(record.getEncoding(), errors='replace')
    font['name'].setName('\n'.join(n for n in notices if n)+'\nGreek letters from LXGW WenKai; supplementary accents from Noto Sans; capital kappa from the comic lettering. Modified for the comic; WenKai and Noto sources SIL Open Font License 1.1.', 0, 3, 1, 0x409)
    font['head'].created = font['head'].modified = 2082844800
    font.flavor = 'woff2'
    output.parent.mkdir(parents=True, exist_ok=True)
    font.save(output)
    points = sorted(font.getBestCmap())
    ranges = []
    for cp in points:
        if ranges and cp == ranges[-1][1]+1:
            ranges[-1][1] = cp
        else:
            ranges.append([cp, cp])
    entry = dict(family=family, file=output.relative_to(ROOT).as_posix(), ranges=ranges,
                 source=source['source'], sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                 sources=[source['file'], native_path.relative_to(ROOT).as_posix(),lettering_path.relative_to(ROOT).as_posix()],
                 licences=['assets/fonts/licenses/WenKai-OFL.txt', 'assets/fonts/licenses/Noto-OFL.txt'])
    entry['sourceHashes'] = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in entry['sources']}
    entry['recipeSha256'] = hashlib.sha256(b''.join(p.read_bytes() for p in
        [Path(__file__), Path(__file__).with_name('optical_anchors.py'), Path(__file__).with_name('math_unicode_marks.py')])).hexdigest()
    assert all((ROOT/p).is_file() for p in entry['licences'])
    manifest.write_text('export default '+json.dumps(entry, ensure_ascii=False, separators=(',', ':'))+';\n')
    output.with_suffix('.review.json').write_text(json.dumps({'records': records, 'source': source, 'nativeSha256': hashlib.sha256(native_path.read_bytes()).hexdigest()}, ensure_ascii=False, indent=2)+'\n')
    print(f'{len(greek)} Greek characters: {output}')


if __name__ == '__main__':
    build(ROOT/'assets/fonts/dad-greek.woff2', ROOT/'js/greek-manifest.js')
