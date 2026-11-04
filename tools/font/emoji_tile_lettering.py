"""Place existing comic capitals/digits into reviewed emoji tile letter cells."""
import hashlib
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.svgLib.path import parse_path

TEXT={'1f520':'ABCD','1f522':'1234','1f170':'A','1f18e':'AB','1f171':'B','1f191':'CL','1f192':'COOL','1f193':'FREE','1f194':'ID','24c2':'M','1f195':'NEW','1f196':'NG','1f17e':'O','1f197':'OK','1f17f':'P','1f198':'SOS','1f199':'UP!','1f19a':'VS'}

def replace_letters(root,key,shapes,indices,text=None):
    """Keep source placement, fit authentic lettering without changing case."""
    text=TEXT.get(key) if text is None else text
    if text is None:return None
    path=root/'data/font-sources/dad-lettering-base.woff2'
    font=TTFont(path);gs=font.getGlyphSet();cmap=font.getBestCmap()
    cells=[]
    for i in indices:
        element=shapes[i]
        assert element.tag.split('}')[-1]=='path'
        pen=BoundsPen(None);parse_path(element.attrib['d'],pen)
        cells.append((i,pen.bounds))
    if key in {'1f520','1f522'}:
        rows=sorted(cells,key=lambda cell:(cell[1][1]+cell[1][3])/2)
        cells=sorted(rows[:2],key=lambda cell:cell[1][0])+sorted(rows[2:],key=lambda cell:cell[1][0])
    else:cells.sort(key=lambda cell:cell[1][0])
    assert len(cells)==len(text)
    mapping=[]
    for char,(i,(x0,y0,x1,y1)) in zip(text,cells):
        glyph=gs[cmap[ord(char)]];bounds=BoundsPen(gs);glyph.draw(bounds);a,b,c,d=bounds.bounds
        # Preserve each source letter's cell while keeping the donor aspect ratio.
        scale=min((x1-x0)/(c-a),(y1-y0)/(d-b))
        transform=(scale,0,0,-scale,(x0+x1)/2-(a+c)*scale/2,(y0+y1)/2+(b+d)*scale/2)
        pen=SVGPathPen(None);record=DecomposingRecordingPen(gs);glyph.draw(record);record.replay(TransformPen(pen,transform))
        shapes[i].set('d',pen.getCommands())
        mapping.append(dict(sourcePath=i,character=char,glyph=cmap[ord(char)],sourceBounds=[x0,y0,x1,y1]))
    return dict(path=str(path.relative_to(root)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),letters=mapping,programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
