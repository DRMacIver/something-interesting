"""Validate and render an already built regional flag candidate font."""
import hashlib
import io
import json
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont
ROOT = Path(__file__).resolve().parents[2]


def shape(font, text):
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)
    return [(i.codepoint,p.x_advance) for i,p in zip(buffer.glyph_infos,buffer.glyph_positions)]


def harfbuzz(path):
    font = TTFont(path)
    font.flavor = None
    output = io.BytesIO()
    font.save(output)
    return hb.Font(hb.Face(output.getvalue()))


def preview(prefix='region-flags'):
    folder = ROOT/'output/font-review/pen-translation'
    path = folder/(prefix+'-candidate.woff2')
    report_path = path.with_suffix('.json')
    report = json.loads(report_path.read_text())
    assert hashlib.sha256(path.read_bytes()).hexdigest() == report['sha256']
    font = TTFont(path,recalcTimestamp=False)
    for tag in ['COLR','CPAL']:
        del font[tag]
    for record in font['name'].names:
        if record.nameID in {1,3,4,6,16}:
            text=record.toUnicode()
            text=text.replace(' Candidate',' Candidate Ink') if ' Candidate' in text else text.replace('Candidate','CandidateInk')
            record.string=text.encode(record.getEncoding())
    ink_path = folder/(prefix+'-candidate-ink.woff2')
    font.save(ink_path)
    for target in [path,ink_path]:
        check = TTFont(target)
        for name in check.getGlyphOrder():
            glyph = check['glyf'][name]
            glyph.recalcBounds(check['glyf'])
            assert check['hmtx'][name][1] == getattr(glyph,'xMin',0),(target,name)
            start = 0
            if glyph.numberOfContours <= 0:
                continue
            for last in glyph.endPtsOfContours:
                points=list(glyph.coordinates[start:last+1]);start=last+1
                assert sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1])) != 0,(target,name)
    coloured = harfbuzz(path)
    monochrome = harfbuzz(ink_path)
    expected = {}
    colour_font = TTFont(path)
    for entry in report['flags']:
        text = entry['sequence']
        actual = shape(coloured,text)
        assert len(actual)==1 and colour_font.getGlyphName(actual[0][0])==entry['glyphName']
        assert actual[0][1]==entry['advance']
        assert shape(monochrome,text)==actual
        for alias in entry.get('qualificationForms',[text]):
            assert shape(coloured,alias)==actual,(entry['region'],alias)
            assert shape(monochrome,alias)==actual,(entry['region'],alias)
            expected[alias]=actual
    for first,a in expected.items():
        for second,b in expected.items():
            assert shape(coloured,first+second)==a+b
            assert shape(monochrome,first+second)==a+b
    ink_hash=hashlib.sha256(ink_path.read_bytes()).hexdigest()
    template=(ROOT/'tools/font/templates/region-flags.html').read_text()
    template=template.replace('region-flags-candidate',prefix+'-candidate')
    data=[dict(region=e['region']+(f' alias {i}' if i else ''),sequence=text) for e in report['flags'] for i,text in enumerate(e.get('qualificationForms',[e['sequence']]))]
    if prefix=='general-flags':
        template=template.replace('Regional flag','General flag')
    html=template.replace('__FLAGS__',json.dumps(data)).replace('__FONT_HASH__',report['sha256'][:12]).replace('__INK_HASH__',ink_hash[:12])
    (folder/(prefix+'-candidate.html')).write_text(html)
    result=dict(sequences=len(expected),adjacencyPairs=len(expected)**2,colourSha256=report['sha256'],inkSha256=ink_hash,
                actualBearings=True,positiveAreaContours=True,companionShapingIdentical=True)
    (folder/(prefix+'-candidate-validation.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    preview()
