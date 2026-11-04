"""Only eight proven source9 retained composites may lose empty point contours."""
import copy
import pytest
from font_baseline_checks import assert_retained_native_drawing

SOURCE='build/unicode-sources/unicodia/ArchaicCuneiformNumerals.ttf'
DRAWING=[('moveTo',((0,0),)),('lineTo',((10,0),)),('lineTo',((10,10),)),('closePath',())]


@pytest.mark.parametrize('gid',range(131,139))
def test_exact_proven_native_empty_contour_count(gid):
    row=dict(gid=gid,glyph=f'u{0x125d2+gid-131:X}',status='native-retained-guard')
    native=[command for i in range(gid-129) for command in [('moveTo',((i,i),)),('closePath',())]]+DRAWING
    assert_retained_native_drawing(SOURCE,row,native,DRAWING)
    for wrong in [native,DRAWING+[('moveTo',((1,1),)),('closePath',())]]:
        with pytest.raises(AssertionError):assert_retained_native_drawing(SOURCE,row,native,wrong)


@pytest.mark.parametrize('mutation',['line','curve','connectivity','wrong-source','policy-glyph'])
def test_real_drawing_or_scope_mutations_are_rejected(mutation):
    row=dict(gid=131,glyph='u125D2',status='native-retained-guard')
    native=[('moveTo',((1,1),)),('closePath',()),('moveTo',((2,2),)),('closePath',())]+DRAWING
    actual=copy.deepcopy(DRAWING);source=SOURCE
    if mutation=='line':actual[1]=('lineTo',((9,0),))
    if mutation=='curve':actual[1]=('qCurveTo',((5,3),(10,0)))
    if mutation=='connectivity':actual[0]=('lineTo',((0,0),))
    if mutation=='wrong-source':source='Other.ttf'
    if mutation=='policy-glyph':row['sourcePolicy']=True
    with pytest.raises(AssertionError):assert_retained_native_drawing(source,row,native,actual)
