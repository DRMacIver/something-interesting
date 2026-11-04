"""Foreign vowel fragments keep their actual native shaping and split forms."""
import json
import subprocess
from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import ROOT,shape
from test_outline_audit import drawn_glyph


def test_spacing_fallback_fragments_shape_exactly_like_their_licensed_sources():
    script=r'''
      import {nativeSpacingVariationPlan,variationFontContains} from './js/font-variations.js';
      import {requiredFonts} from './js/fonts.js';
      import {fontRuns} from './js/emoji-routing.js';
      const texts=['𝓏\ufe02ি','豈\ufe00ि','𝓏\ufe02ெ','豈\ufe00ொ','𝓏\ufe02ើ','豈\ufe00ើ'];
      console.log(JSON.stringify(texts.map(text=>{
        const plan=nativeSpacingVariationPlan(text),fonts=requiredFonts([text]).fonts;
        const donor=fonts.find(f=>f.family!==plan.font.family&&f.source&&[...plan.tail].every(c=>variationFontContains(f.ranges,c.codePointAt(0))));
        return {text,body:plan.body,tail:plan.tail,runs:fontRuns(text),donor};
      })));
    '''
    rows=json.loads(subprocess.check_output(['node','--input-type=module','-e',script],cwd=ROOT,text=True))
    for row in rows:
        assert [r['text'] for r in row['runs']]==[row['body'],row['tail']]
        assert row['runs'][0]['fontFamily'] and 'fontFamily' not in row['runs'][1]
        donor=row['donor'];font=TTFont(ROOT/donor['file'])
        output=shape(ROOT/donor['file'],row['tail'],True)
        assert output and all(g[0]>0 for g in output),row
        assert any(drawn_glyph(font,font.getGlyphName(g[0])) for g in output)
        assert shape(ROOT/donor['file'],row['tail'])==shape(ROOT/donor['source'],row['tail']),row
        if row['tail']=='ொ':
            # Tamil O decomposes into the left E and right AA drawings, with
            # the native dotted-circle carrier between them in this context.
            assert len(output)>=3
