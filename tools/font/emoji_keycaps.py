"""Original keycap borders around the project's existing comic lettering."""
import hashlib
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen

KEYS = '#*0123456789'


def add_keycaps(root, glyphs, metrics, cmap, layers):
    source = root/'data/font-sources/dad-lettering-base.woff2'
    font = TTFont(source); gs = font.getGlyphSet()
    # Two independently drawn, slightly asymmetric rounded contours. The
    # inner contour runs backwards to leave white space in monochrome ink.
    outer = [('moveTo',[(112,0)]),('qCurveTo',[(44,1),(43,73)]),
             ('lineTo',[(48,658)]),('qCurveTo',[(48,736),(123,737)]),
             ('lineTo',[(723,733)]),('qCurveTo',[(802,732),(800,656)]),
             ('lineTo',[(797,78)]),('qCurveTo',[(798,-3),(722,-2)]),('closePath',[])]
    inner = [('moveTo',[(116,35)]),('lineTo',[(718,33)]),
             ('qCurveTo',[(763,33),(763,81)]),('lineTo',[(767,653)]),
             ('qCurveTo',[(768,698),(719,699)]),('lineTo',[(126,702)]),
             ('qCurveTo',[(82,701),(82,655)]),('lineTo',[(78,76)]),
             ('qCurveTo',[(77,35),(116,35)]),('closePath',[])]
    def draw(pen, commands):
        for method, points in commands: getattr(pen,method)(*points)
    backing=TTGlyphPen(None);draw(backing,outer)
    glyphs['keycap.white']=backing.glyph();metrics['keycap.white']=(850,43)
    sequences=[]
    for char in KEYS:
        cp=ord(char); component=f'key{cp:X}'; name=component+'.cap'
        cmap[cp]=component;glyphs[component]=TTGlyphPen(None).glyph();metrics[component]=(0,0)
        original=gs[font.getBestCmap()[cp]]
        bounds=BoundsPen(gs);original.draw(bounds);x0,y0,x1,y1=bounds.bounds
        scale=min(440/(x1-x0),480/(y1-y0))
        transform=(scale,0,0,scale,425-(x0+x1)*scale/2,368-(y0+y1)*scale/2)
        pen=TTGlyphPen(None);draw(pen,outer);draw(pen,inner)
        recording=DecomposingRecordingPen(gs);original.draw(recording)
        recording.replay(TransformPen(Cu2QuPen(pen,max_err=0.5,reverse_direction=False),transform))
        glyphs[name]=pen.glyph();metrics[name]=(850,43)
        layers[name]=[('keycap.white',0),(name+'.ink',1)]
        glyphs[name+'.ink']=glyphs[name];metrics[name+'.ink']=(850,43)
        sequences.extend([char+'\u20e3',char+'\ufe0f\u20e3'])
    cmap[0x20e3]='keycap.mark';glyphs['keycap.mark']=TTGlyphPen(None).glyph();metrics['keycap.mark']=(0,0)
    rules='\n'.join(f'sub key{ord(c):X} keycap.mark by key{ord(c):X}.cap;' for c in KEYS)
    return sequences, [ord(c) for c in KEYS]+[0x20e3], rules, {'source':str(source.relative_to(root)), 'sha256':hashlib.sha256(source.read_bytes()).hexdigest(), 'keys':KEYS,'design':'original asymmetrical rounded border; centered existing comic glyphs; white and black ink'}
