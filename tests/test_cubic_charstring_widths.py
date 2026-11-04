"""Type2 width operands are deltas from private nominalWidthX, not advances."""
from types import SimpleNamespace
import pytest
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.recordingPen import RecordingPen
from font_baseline_checks import assert_cubic_charstring_advance


def glyph(width,nominal=1046,default=200):
    private=SimpleNamespace(nominalWidthX=nominal,defaultWidthX=default,Subrs=[])
    pen=T2CharStringPen(width,None,roundTolerance=0)
    pen.moveTo((10,20));pen.lineTo((110,20));pen.lineTo((110,120));pen.closePath()
    return pen.getCharString(private=private,globalSubrs=[])


@pytest.mark.parametrize('advance',[0,200,1000,1600])
def test_correct_encoded_operand_keeps_native_advance(advance):
    encoded=None if advance==200 else advance-1046
    charstring=glyph(encoded)
    assert_cubic_charstring_advance(charstring,advance)
    charstring.compile()
    assert_cubic_charstring_advance(charstring,advance)


def test_absolute_operand_is_rejected_despite_identical_drawn_geometry():
    wrong=glyph(1000);correct=glyph(-46)
    p,q=RecordingPen(),RecordingPen();wrong.draw(p);correct.draw(q)
    assert p.value==q.value
    assert wrong.width==2046 and correct.width==1000
    with pytest.raises(AssertionError):assert_cubic_charstring_advance(wrong,1000)
    assert_cubic_charstring_advance(correct,1000)


def test_changed_private_nominal_width_is_not_hidden_by_hmtx():
    charstring=glyph(-46,nominal=1047)
    with pytest.raises(AssertionError):assert_cubic_charstring_advance(charstring,1000)


def repaired_pair():
    native=glyph(642);current=glyph(642-1046)
    row=dict(gid=1210,glyph='u1D253',status='native-retained-guard',widthRepair=dict(method='explicit-type2-width-operand-only',nativeDecodedAdvance=1688,hmtxAdvance=642,encodedOperandBefore=642,encodedOperandAfter=-404,nominalWidthX=1046,defaultWidthX=200))
    return native,current,row


def test_only_explicit_legacy_retained_width_operand_is_normalized():
    from font_baseline_checks import assert_cubic_retained_charstring
    native,current,row=repaired_pair()
    assert_cubic_retained_charstring(native,current,642,row)
    with pytest.raises(AssertionError):assert_cubic_retained_charstring(native,current,642,{k:v for k,v in row.items() if k!='widthRepair'})


@pytest.mark.parametrize('mutation',['curve','operand-metadata','native-advance-metadata','wrong-gid','protected-policy'])
def test_retained_width_repair_does_not_waive_curves_or_provenance(mutation):
    from font_baseline_checks import assert_cubic_retained_charstring
    native,current,row=repaired_pair()
    if mutation=='curve':
        current.decompile();current.program[1]+=1
    if mutation=='operand-metadata':row['widthRepair']['encodedOperandAfter']=-403
    if mutation=='native-advance-metadata':row['widthRepair']['nativeDecodedAdvance']=1687
    if mutation=='wrong-gid':row['gid']=1213
    if mutation=='protected-policy':row['sourcePolicy']=True
    with pytest.raises(AssertionError):assert_cubic_retained_charstring(native,current,642,row)
