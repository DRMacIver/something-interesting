"""Reject treating a native stroke-only primitive as a filled silhouette."""
import xml.etree.ElementTree as ET
SHAPES={'path','circle','ellipse','polygon','rect','line','polyline'}


def selected_strokes(root,recipe,stroke_paths=(),letter_paths=()):
    parents={c:p for p in root.iter() for c in p}
    shapes=[e for e in root.iter() if e.tag.split('}')[-1] in SHAPES]
    count,paper,ink,cutouts,colours=recipe
    assert len(shapes)==count
    selected=set(paper)|set(ink)|set(cutouts)|set(colours)|set(stroke_paths)
    def property_value(element,name,default):
        while True:
            style={key.strip():value.strip() for key,value in (rule.split(':',1) for rule in element.get('style','').split(';') if ':' in rule)}
            if name in style:return style[name].strip()
            if name in element.attrib:return element.attrib[name].strip()
            if element not in parents:return default
            element=parents[element]
    checked=[]
    for index in sorted(selected-set(letter_paths)):
        element=shapes[index];parent=element;definition=False
        while parent in parents:
            parent=parents[parent]
            if parent.tag.split('}')[-1] in {'defs','clipPath','mask','pattern'}:definition=True;break
        if definition:continue
        if element.tag.split('}')[-1]=='line' or property_value(element,'fill','black')=='none':
            assert index in stroke_paths,('Native stroke would become a filled shape',index,element.attrib)
            checked.append(index)
    return checked
