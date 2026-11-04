"""Extract matched enclosure ends and connecting strips from native shaping."""
import hashlib
import json
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from review_egyptian_insertions import ROOT,CACHE,build as review

STARTS=[0x13258,0x13259,0x1325a,0x13286,0x13288,0x13379,0x1342f]
ENDS=[0x1325b,0x1325c,0x1325d,0x13287,0x13289,0x1337a,0x1337b]


def build():
    review() # source hash verification
    raw=(CACHE/'eot.ttf').read_bytes();font=TTFont(CACHE/'eot.ttf');gs=font.getGlyphSet()
    native=hb.Font(hb.Face(raw));entries={}
    for cp in [None,*STARTS,*ENDS]:
        control=0x1343e if cp in [0x13286,0x13287,0x13288,0x13289] else 0x1343c
        for control in ([0x1343c,0x1343e] if cp is None else [control]):
            cps=([cp] if cp in STARTS else [])+[control,0x13441,control+1]+([cp] if cp in ENDS else [])
            b=hb.Buffer();b.add_str(''.join(map(chr,cps)));b.guess_segment_properties();hb.shape(native,b)
            visible=[]
            for info,pos in zip(b.glyph_infos,b.glyph_positions):
                name=font.getGlyphName(info.codepoint);extent=native.get_glyph_extents(info.codepoint)
                if not extent or not extent.width or not extent.height:continue
                if cp is not None and name.startswith('Q'):continue
                pen=SVGPathPen(gs);bp=BoundsPen(gs)
                transform=(1,0,0,-1,pos.x_offset,1576-pos.y_offset)
                gs[name].draw(TransformPen(pen,transform));gs[name].draw(TransformPen(bp,transform))
                visible.append({'path':pen.getCommands(),'bounds':list(bp.bounds),'advance':pos.x_advance,'sourceGlyph':name})
            if len(visible)!=1:raise ValueError((cps,visible))
            entries[f'{cp or control:X}']=visible[0]
    return {'source':'Egyptian Text','sha256':hashlib.sha256(raw).hexdigest(),
            'license':'SIL OFL 1.1; see assets/fonts/licenses','contentHeight':1860,
            'starts':STARTS,'ends':ENDS,'entries':entries}

if __name__=='__main__':
    manifest=build()
    (ROOT/'js/egyptian-enclosure-manifest.js').write_text('// Derived from pinned OFL Egyptian Text.\nexport default '+json.dumps(manifest,separators=(',',':'))+';\n')
    print({'parts':len(manifest['entries'])})
