"""Extend the original lettering with Latin compositions and combining anchors.

Base letters and their contextual alternates remain unchanged. Mark outlines
come from the pinned OFL Noto source and are normalised to the original cap
height. The derivative is a separate OFL font; the original stays available.
"""
from copy import deepcopy
from pathlib import Path
import sys
import json
import hashlib

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/unicode"))
from audit import DATA, records
from optical_anchors import accent_centres


def bounds(glyph, glyphs):
    pen = BoundsPen(glyphs)
    glyph.draw(pen)
    return pen.bounds


def append_features(font, code):
    temporary = deepcopy(font)
    addOpenTypeFeaturesFromString(temporary, code, tables=["GPOS", "GDEF"])
    old, new = font["GPOS"].table, temporary["GPOS"].table
    offset = len(old.LookupList.Lookup)
    old.LookupList.Lookup.extend(new.LookupList.Lookup)
    old.LookupList.LookupCount = len(old.LookupList.Lookup)
    indices = []
    for record in new.FeatureList.FeatureRecord:
        record.Feature.LookupListIndex = [i + offset for i in record.Feature.LookupListIndex]
        indices.append(len(old.FeatureList.FeatureRecord))
        old.FeatureList.FeatureRecord.append(record)
    old.FeatureList.FeatureCount = len(old.FeatureList.FeatureRecord)
    for script in old.ScriptList.ScriptRecord:
        systems = [script.Script.DefaultLangSys] + [r.LangSys for r in script.Script.LangSysRecord]
        for language in systems:
            if language is not None:
                language.FeatureIndex.extend(indices)
                language.FeatureCount = len(language.FeatureIndex)
    font["GDEF"] = temporary["GDEF"]


def build(output):
    font = TTFont(ROOT / "data/font-sources/dad-lettering-base.woff2")
    donor = TTFont(ROOT / "build/unicode-sources/noto/NotoSans-Regular.ttf")
    donor_cmap = donor.getBestCmap()
    donor_glyphs = donor.getGlyphSet()
    extra_path = ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf'
    entry = next(e for e in json.loads((ROOT/'data/font-sources/unicodia.json').read_text())['files'] if e['path']==extra_path.relative_to(ROOT).as_posix())
    assert hashlib.sha256(extra_path.read_bytes()).hexdigest() == entry['sha256']
    extra = TTFont(extra_path)
    extra_cmap = extra.getBestCmap()
    extra_glyphs = extra.getGlyphSet()
    permitted = {cp for a,b in entry['include_ranges'] for cp in range(a,b+1)}
    glyphs = font.getGlyphSet()
    cmap = dict(font.getBestCmap())
    original_names = font.getGlyphOrder()[:]
    original_bounds = {n: bounds(glyphs[n], glyphs) for n in original_names}
    original_centres = {n: accent_centres(glyphs[n], glyphs, box,
                        top_fraction=.05 if n=='A' or n.startswith('A.') else .2)
                        for n, box in original_bounds.items() if box is not None}
    top = font["CFF "].cff.topDictIndex[0]
    strings = top.CharStrings
    strings.charStrings = {n: strings[n] for n in original_names}
    strings.charStringsAreIndexed = False
    names = original_names[:]
    fields_by_cp = {int(f[0], 16): f for f in records(DATA / "UnicodeData.txt")}
    marks = {}
    scale = 700 / donor["OS/2"].sCapHeight

    def draw_donor(glyph, pen, transform, source_glyphs=None):
        # Decompose before reversing: addComponent otherwise bypasses the
        # reversal wrapper and leaves composite accents with opposite winding.
        recording = DecomposingRecordingPen(source_glyphs or donor_glyphs)
        glyph.draw(recording)
        recording.replay(TransformPen(ReverseContourPen(pen), transform))

    def add(name, pen, advance, lsb):
        strings[name] = pen.getCharString(private=top.Private, globalSubrs=font["CFF "].cff.GlobalSubrs)
        font["hmtx"].metrics[name] = (round(advance), round(lsb))
        names.append(name)

    for cp, f in fields_by_cp.items():
        if f[2] not in {"Mn", "Me"}:
            continue
        # Start with the general combining-mark blocks; script-specific marks
        # must be kept with their own shaping font.
        if not any(a <= cp <= b for a, b in [(0x300, 0x36F), (0x1AB0, 0x1AFF),
                                           (0x1DC0, 0x1DFF), (0x20D0, 0x20FF), (0xFE20, 0xFE2F)]):
            continue
        if cp in donor_cmap:
            mark_font, mark_glyphs, mark_cmap = donor, donor_glyphs, donor_cmap
        elif cp in permitted and cp in extra_cmap:
            mark_font, mark_glyphs, mark_cmap = extra, extra_glyphs, extra_cmap
        else:
            continue
        mark_scale = 700 / mark_font['OS/2'].sCapHeight
        glyph = mark_glyphs[mark_cmap[cp]]
        box = bounds(glyph, mark_glyphs)
        if not box:
            continue
        x0, y0, x1, y1 = [v * mark_scale for v in box]
        ccc = int(f[3])
        cls = "overlay" if ccc == 1 else "below" if ccc in {202, 216, 218, 220, 222, 224, 226, 228} or "BELOW" in f[1] else "above"
        shift_y = -y0 if cls == "above" else -y1 if cls == "below" else -(y0+y1)/2
        side = {0x1ac1:'above_left',0x1ac2:'above_right',0x1ac3:'below_left',0x1ac4:'below_right'}.get(cp)
        shift_x = -(x0+x1)/2
        if side:
            # Side parentheses enclose a diacritic, not the base letter. The
            # 170-unit side clearance surrounds the normal voicing-ring width.
            shift_x = -x1-170 if side.endswith('left') else -x0+170
            cls = side
        name = f"uni{cp:04X}"
        pen = T2CharStringPen(0, mark_glyphs)
        draw_donor(glyph, pen, (mark_scale, 0, 0, mark_scale, shift_x, shift_y), mark_glyphs)
        add(name, pen, 0, x0+shift_x)
        cmap[cp] = name
        marks[cp] = {"name": name, "class": cls, "height": y1-y0,
                     "left": x0+shift_x, "attach": ccc in {202, 216}}

    # Joined capitals reuse the actual reference lettering, including its
    # uneven edges. Lean E's spine along A's right leg; overlap O's right
    # stroke with E's spine. Lowercase follows this font's capital lettering.
    for chars, base_char, transform in [
        ("Ææ", "A", (0.8, 0, -0.32, 1, 350, 0)),
        ("Œœ", "O", (0.8, 0, 0, 0.94, 365, 8)),
    ]:
        for char in chars:
            name = f"uni{ord(char):04X}"
            drawing = RecordingPen()
            glyphs[cmap[ord(base_char)]].draw(drawing)
            glyphs[cmap[ord("E")]].draw(TransformPen(drawing, transform))
            # Match E's right side bearing instead of leaving a fixed extra
            # 45–62 units after these narrower joined forms.
            bpen = BoundsPen(None)
            drawing.replay(bpen)
            e = cmap[ord('E')]
            advance = bpen.bounds[2]+font['hmtx'][e][0]-original_bounds[e][2]
            pen = T2CharStringPen(round(advance), None)
            drawing.replay(pen)
            add(name, pen, advance, original_bounds[cmap[ord(base_char)]][0])
            cmap[ord(char)] = name

    # These letters do not have canonical base+mark decompositions. Keep them
    # identifiable using donor outlines pending their custom glyph review.
    for char in "ÆæØøŒœŁłĐđÐðÞþßẞı":
        cp = ord(char)
        source = char.upper() if len(char.upper()) == 1 else char
        if cp in cmap or ord(source) not in donor_cmap:
            continue
        glyph = donor_glyphs[donor_cmap[ord(source)]]
        advance, lsb = donor["hmtx"].metrics[donor_cmap[ord(source)]]
        pen = T2CharStringPen(round(advance*scale), donor_glyphs)
        draw_donor(glyph, pen, (scale, 0, 0, scale, 0, 0))
        name = f"uni{cp:04X}"
        add(name, pen, advance*scale, lsb*scale)
        cmap[cp] = name
    for char, base_char in [("¿", "?"), ("¡", "!")]:
        base = cmap[ord(base_char)]
        x0, y0, x1, y1 = original_bounds[base]
        advance, lsb = font["hmtx"].metrics[base]
        pen = T2CharStringPen(advance, None)
        glyphs[base].draw(TransformPen(pen, (-1, 0, 0, -1, x0+x1, y0+y1)))
        name = f"uni{ord(char):04X}"
        add(name, pen, advance, lsb)
        cmap[ord(char)] = name

    def decomposition(cp):
        f = fields_by_cp.get(cp)
        if not f or not f[5] or f[5].startswith("<"):
            return [cp]
        return [part for value in f[5].split() for part in decomposition(int(value, 16))]

    # Compositions are drawn from the same base and same anchors as decomposed
    # strings. Canonical equivalents therefore have matching ink and advances.
    for cp, f in fields_by_cp.items():
        if cp in cmap or not f[1].startswith("LATIN "):
            continue
        parts = decomposition(cp)
        if len(parts) < 2 or parts[0] not in cmap or any(p not in marks for p in parts[1:]):
            continue
        base = cmap[parts[0]]
        if base not in original_bounds or original_bounds[base] is None:
            continue
        x0, y0, x1, y1 = original_bounds[base]
        advance, lsb = font["hmtx"].metrics[base]
        pen = T2CharStringPen(advance, None)
        glyphs[base].draw(pen)
        positions = {"above": y1+45, "below": y0-25, "overlay": (y0+y1)/2}
        for part in parts[1:]:
            mark = marks[part]
            cls = mark["class"]
            above_x, below_x = original_centres[base]
            x = above_x if cls == "above" else below_x if cls == "below" else (x0+x1)/2
            strings[mark["name"]].draw(TransformPen(pen, (1, 0, 0, 1, x, positions[cls])))
            if cls != "overlay":
                positions[cls] += (mark["height"] + 25) * (1 if cls == "above" else -1)
        name = f"uni{cp:04X}"
        add(name, pen, advance, lsb)
        cmap[cp] = name

    font.setGlyphOrder(names)
    top.charset = names
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap.update({cp: name for cp, name in cmap.items() if cp <= 0xFFFF or table.format == 12})
    # Compute bounds for compositions too, so later marks attach above their
    # existing accents rather than colliding unintentionally.
    glyphs = font.getGlyphSet()
    code = ["languagesystem DFLT dflt;", "languagesystem latn dflt;"]
    for mark in marks.values():
        code.append(f'markClass {mark["name"]} <anchor 0 0> @MC_{mark["class"]};')
    code.append("feature mark {")
    for name in names:
        if name in {m["name"] for m in marks.values()}:
            continue
        box = bounds(glyphs[name], glyphs)
        if box is None:
            continue
        x0, y0, x1, y1 = box
        x = round((x0+x1)/2)
        above_x, below_x = (round(v) for v in accent_centres(glyphs[name], glyphs, box,
                            top_fraction=.05 if name=='A' or name.startswith('A.') else .2))
        code.append(f"pos base {name} <anchor {above_x} {round(y1+45)}> mark @MC_above "
                    f"<anchor {below_x} {round(y0-25)}> mark @MC_below "
                    f"<anchor {x} {round((y0+y1)/2)}> mark @MC_overlay "
                    f"<anchor {x} {round(y1+45)}> mark @MC_above_left "
                    f"<anchor {x} {round(y1+45)}> mark @MC_above_right "
                    f"<anchor {x} {round(y0-25)}> mark @MC_below_left "
                    f"<anchor {x} {round(y0-25)}> mark @MC_below_right;")
    code.append("} mark;\nfeature mkmk {")
    for mark in marks.values():
        cls = mark["class"]
        if '_' in cls:
            continue  # Side parentheses are not another vertical stacking level.
        y = round((mark["height"]+25)*(1 if cls == "above" else -1)) if cls != "overlay" else 0
        code.append(f'pos mark {mark["name"]} <anchor 0 {y}> mark @MC_{cls};')
        if cls in {'above','below'}:
            code.append(f'pos mark {mark["name"]} <anchor 0 0> mark @MC_{cls}_left <anchor 0 0> mark @MC_{cls}_right;')
    code.append("} mkmk;")
    append_features(font, "\n".join(code))
    # A new derivative family keeps licensing/provenance separate from the
    # original extracted lettering. This source will supersede it at runtime.
    family = "Dad Lettering Unicode"
    for nid, value in [(1, family), (3, family+" Regular 1.0"), (4, family),
                       (6, "DadLetteringUnicode-Regular"), (13, "SIL Open Font License, Version 1.1"),
                       (14, "https://openfontlicense.org/")]:
        font["name"].setName(value, nid, 3, 1, 0x409)
    font["name"].setName("Combining marks: Copyright 2022 The Noto Project Authors. "
                         "Additional combining marks: Copyright (c) 2021-2026 Mikhail Merkuryev; Google Noto, SIL OFL. "
                         "Original lettering extracted from the supplied comic reference; see project provenance.", 0, 3, 1, 0x409)
    top.FullName = family
    font["CFF "].cff.fontNames = ["DadLetteringUnicode-Regular"]
    font["OS/2"].usWinAscent = 1500
    font["OS/2"].usWinDescent = 800
    font.flavor = "woff2"
    font.recalcTimestamp = False
    output.parent.mkdir(parents=True, exist_ok=True)
    font.save(output)
    print(f"{len(cmap)} code points, {len(marks)} combining marks: {output}")


if __name__ == "__main__":
    build(ROOT / "assets/fonts/dad-lettering-unicode.woff2")
