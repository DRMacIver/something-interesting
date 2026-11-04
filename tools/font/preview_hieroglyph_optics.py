"""Review runtime optical stroke constants on unchanged native shaped outlines.
No font mutation. This tests native ink only, not app layout or canvas export.
"""
import json
from pathlib import Path
from render_specimen import Font, render

original = Font.shape

def optical_shape(self, text, size, **options):
    result = original(self, text, size, **options)
    if getattr(self, 'optical', False):
        ratio = .010 if any(0x14400 <= ord(c) <= 0x1467f for c in text) else .014
        stroke = self.upem * ratio
        result['paths'] = [p.replace('<path ', f'<path stroke="#111" stroke-width="{stroke}" stroke-linejoin="round" ') for p in result['paths']]
        pad = size * ratio / 2
        a,b,c,d = result['bounds']; result['bounds'] = [a-pad,b-pad,c+pad,d+pad]
        result['opticalStrokeEm'] = ratio
    return result

# The renderer caches by path; use a synthetic suffix resolved only here.
init = Font.__init__
def optical_init(self, path):
    self.optical = str(path).endswith('.optical')
    init(self, str(path).removesuffix('.optical'))
Font.__init__ = optical_init
Font.shape = optical_shape

if __name__ == '__main__':
    atlas = json.loads(Path('output/font-review/source-style-atlas.json').read_text())
    samples = []
    for row in atlas['samples']:
        if row['index'] not in (5,24): continue
        font = row['fonts'][0]['file']
        text = row['text'].removeprefix('‗')
        for candidate in (False,True):
            samples.append({'label': ('OPTICAL ' if candidate else 'SOURCE ') + ('EGYPTIAN' if row['index']==5 else 'ANATOLIAN'),
                'font': font + ('.optical' if candidate else ''), 'text':text})
    for label,font,text in [
        ('EXTENDED EGYPTIAN','assets/fonts/scripts/5f5f565fbefa.woff2','𓑠𓑡𓑢𔃿'),
        ('NATIVE GROUPS','assets/fonts/scripts/90fcad2ecf0c.woff2','𓀀\U00013430𓀁 𓆓\U00013433𓀀'),
    ]:
        for candidate in (False,True):
            samples.append({'label':('OPTICAL ' if candidate else 'SOURCE ')+label,
                'font':font+('.optical' if candidate else ''),'text':text})
    render(samples,Path('output/font-review/hieroglyph-optics/native-comparison'))
