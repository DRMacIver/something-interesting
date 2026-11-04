"""Record why Sharada Supplement needs native attachment work, not a cmap shard.

This diagnostic deliberately does not add source glyphs to delivered coverage.
Run from the repository root with the project's Python environment.
"""
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb

ROOT=Path(__file__).resolve().parents[2]
NATIVE=ROOT/'build/unicode-sources/noto/NotoSansSharada-Regular.ttf'
DONOR=ROOT/'build/unicode-sources/unicodia/UnicodiaFunky.ttf'


def glyph_record(font, cp):
    name=font.getBestCmap().get(cp)
    if name is None:return None
    glyphs=font.getGlyphSet();pen=BoundsPen(glyphs);glyphs[name].draw(pen)
    return {'name':name,'advance':font['hmtx'][name][0],'bounds':pen.bounds}


def shaped(path, text):
    font=hb.Font(hb.Face(path.read_bytes()));buf=hb.Buffer()
    buf.add_str(text);buf.guess_segment_properties();hb.shape(font,buf)
    return [{'gid':i.codepoint,'cluster':i.cluster,'advance':p.x_advance,
             'offset':[p.x_offset,p.y_offset]}
            for i,p in zip(buf.glyph_infos,buf.glyph_positions)]


def review():
    native,donor=TTFont(NATIVE),TTFont(DONOR)
    placements=['top','right','bottom','bottom','top','right','top','right']
    records=[]
    for cp,position in zip(range(0x11b60,0x11b68),placements):
        text=chr(0x11191)+chr(cp)
        records.append({'codepoint':f'{cp:05X}','position':position,
                        'native':glyph_record(native,cp),'donor':glyph_record(donor,cp),
                        'native_ka_sequence':shaped(NATIVE,text)})
    anchors=[]
    references=['E','AA','U','UU','VowelModifier','ChandrabinduInv']
    for index,lookup in enumerate(native['GPOS'].table.LookupList.Lookup):
        if lookup.LookupType!=4:continue
        for table in lookup.SubTable:
            for name in references:
                if name not in table.MarkCoverage.glyphs:continue
                record=table.MarkArray.MarkRecord[table.MarkCoverage.glyphs.index(name)]
                anchors.append({'lookup':index,'glyph':name,'class':record.Class,
                                'anchor':[record.MarkAnchor.XCoordinate,record.MarkAnchor.YCoordinate]})
    return {'status':'source-only diagnosis; native attachment implemented in sharada_vowels.py and verified separately' ,
            'reference':'https://www.unicode.org/L2/L2023/23122-kashmiri-sharada.pdf',
            'native_source':str(NATIVE.relative_to(ROOT)),
            'native_version':native['name'].getDebugName(5),
            'donor_source':str(DONOR.relative_to(ROOT)),
            'donor_has_sharada_layout':any(r.ScriptTag=='shrd' for tag in ['GSUB','GPOS']
                                         for r in donor[tag].table.ScriptList.ScriptRecord),
            'official_source_checked':{'repository':'https://github.com/notofonts/sharada',
                                      'commit':'5860efa605f4c81084090479feab9b99f838af37',
                                      'file':'sources/NotoSansSharada.glyphs',
                                      'supplement_glyphs_found':False},
            'marks':records,'native_mark_anchors':anchors,
            'integration_gates':['Import the licensed drawings into the native Sharada font, retaining notices.',
                             'Use zero advance for all Mn signs, including donor U+11B66 (currently 231).',
                             'Preserve native syllable shaping and contextual below-vowel variants.',
                             'Verify above/below/right attachment on consonants, conjuncts and independent vowels.',
                             'Check older browser shaping engines; add scoped compatibility only if needed.',
                             'Validate actual composite forms against the proposal, then review at dialogue size.']}


if __name__=='__main__':
    result=review()
    (ROOT/'docs/sharada-vowel-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f"{len(result['marks'])} donor marks; native coverage 0; donor Sharada layout {result['donor_has_sharada_layout']}")
