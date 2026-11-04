"""Colour-semantic heart variants using the existing custom ink drawing."""
import hashlib
import json
from copy import deepcopy

HEARTS = {0x1F499:'blue',0x1F49A:'green',0x1F49B:'yellow',0x1F49C:'purple',
          0x1F5A4:'black',0x1F90D:'white',0x1F90E:'brown',0x1F9E1:'orange',
          0x1FA75:'light blue',0x1FA76:'grey',0x1FA77:'pink'}


def add_hearts(root,glyphs,metrics,cmap,layers,palette,review):
    record=json.loads((root/'output/imagegen/emoji-production/heart-palette-source.json').read_text())
    assert hashlib.sha256((root/record['pdf']).read_bytes()).hexdigest()==record['pdfSha256']
    colours={s['colour']:tuple(s['rgb']) for s in record['samples']}
    colours.update(black=(17,17,17),white=(255,255,255))
    # Keep the red heart tied to the new full-resolution sample too.
    palette[2]=colours['red']
    for cp,colour in HEARTS.items():
        rgb=colours[colour]
        if rgb not in palette: palette.append(rgb)
        name=f'u{cp:X}'
        glyphs[name]=deepcopy(glyphs['u2764']);metrics[name]=metrics['u2764'];cmap[cp]=name
        layers[name]=[(layer,palette.index(rgb) if i==1 else index)
                      for i,(layer,index) in enumerate(layers['u2764'])]
        review.append({'codepoint':f'U+{cp:04X}','sourceGlyph':'u2764','colour':colour,'rgb':rgb,
                       'advance':metrics[name][0],'design':'shared custom ink outline and highlight; semantic fill colour'})
    return record
