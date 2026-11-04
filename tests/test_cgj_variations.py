"""CGJ is invisible: retaining it in a native prefix must preserve UVS ink."""
import json
import subprocess

import pytest

from native_sfnt_loader import evidence_ttfont as TTFont
from test_font_scripts import ROOT,shape
from test_outline_audit import drawn_glyph
from test_contextual_variants import assert_context_identity


def assert_cgj_identity(with_cgj,without_cgj):
    assert_context_identity(with_cgj[0],without_cgj[0])
    assert with_cgj[1]==without_cgj[1],'Invisible CGJ changed total advance'


def test_cgj_native_prefix_keeps_variant_glyphs_positions_and_advance():
    script=r'''
      import {annotationPlan} from './js/combining-annotations.js';
      import {requiredFonts} from './js/fonts.js';
      const bases=['𝓏\ufe02','豈\ufe00'];
      console.log(JSON.stringify(bases.flatMap(base=>[base+'͏゙',base+'́͏゙'].map(text=>{
        const plan=annotationPlan(text),fonts=requiredFonts([text]).fonts;
        return {text,body:plan.body,file:fonts.find(f=>f.family===plan.variantFamily).file};
      }))));
    '''
    rows=json.loads(subprocess.check_output(['node','--input-type=module','-e',script],cwd=ROOT,text=True))
    for row in rows:
        font=TTFont(ROOT/row['file'])
        def ink(text):
            output=shape(ROOT/row['file'],text,True)
            assert all(g[0]>0 for g in output)
            visible=[g for g in output if drawn_glyph(font,font.getGlyphName(g[0]))]
            return visible,sum(g[1] for g in output)
        with_cgj=ink(row['body']);without_cgj=ink(row['body'].replace('\u034f',''))
        assert_cgj_identity(with_cgj,without_cgj)
        assert with_cgj[0]


@pytest.mark.parametrize('mutation',['selector_gid','mark_offset','invisible_advance'])
def test_cgj_identity_rejects_visible_variant_or_advance_changes(mutation):
    native=([(8,1000,0,0,0),(19,0,0,-200,300)],1000)
    changed=(list(native[0]),native[1])
    if mutation=='selector_gid':changed[0][0]=(9,1000,0,0,0)
    elif mutation=='mark_offset':changed[0][1]=(19,0,0,-199,300)
    else:changed=(changed[0],1001)
    with pytest.raises(AssertionError):assert_cgj_identity(native,changed)
