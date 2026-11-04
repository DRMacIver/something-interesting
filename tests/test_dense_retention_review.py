"""Retention review must distinguish nominal encodings from painted glyphs."""
import sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/font'))
import dense_native_adapter as adapter
import review_dense_retention as review
import render_specimen
import verify_dense_warm as verify
from test_dense_warm_verification import warm,dump


@pytest.fixture
def retained_warm(monkeypatch,request):
    def reject(*args,**kwargs):raise ValueError('Fixture native fine-feature guard')
    monkeypatch.setattr(adapter,'contrast',reject);monkeypatch.setattr(adapter,'flex',reject)
    root,work,group,kernel,complete=request.getfixturevalue('warm')
    proof=verify.verify_plan(root);dump(root/'verified.json',proof)
    monkeypatch.setattr(review,'ROOT',verify.ROOT);monkeypatch.setattr(render_specimen,'ROOT',verify.ROOT)
    return root


def test_full_report_inventory_and_actual_selected_encoded_specimen(retained_warm,tmp_path):
    output=tmp_path/'review';summary=review.collect(output,retained_warm)
    assert summary['glyphCounts']=={'native-blank':1,'native-retained-guard':1}
    assert summary['uniqueEncodedCandidates']==1
    assert summary['cases'][0]['assignedCodepoints']==[72]
    assert summary['cases'][0]['visualDisposition']=='review pending; no automatic style approval'
    review.specimens(summary,output,1)
    corpus=review.read(output/'encoded-review-corpus.json')
    assert len(corpus['selected'])==1
    assert corpus['selected'][0]['sourceGlyphIds']==corpus['selected'][0]['derivedGlyphIds']==[1]
    assert (output/'encoded-retentions-01.png').exists()


def test_nominal_encoding_not_selected_by_shaping_is_deferred(retained_warm,tmp_path,monkeypatch):
    output=tmp_path/'review';summary=review.collect(output,retained_warm)
    class DifferentGlyph:
        def __init__(self,path):pass
        def shape(self,text,size):return {'glyphs':[{'gid':2}]}
    monkeypatch.setattr(review,'Font',DifferentGlyph)
    review.specimens(summary,output,1)
    corpus=review.read(output/'encoded-review-corpus.json')
    assert corpus['selected']==[] and len(corpus['needsContext'])==1
    assert not (output/'encoded-retentions-01.png').exists()


def test_encoded_later_alias_replaces_unencoded_representative_without_cross_font_union():
    common={'cacheKey':'same','status':'native-retained-guard','profile':'Jigmo.ttf','inkBoxAreaEm2':1,'variationPairs':[]}
    first=common|{'family':'closure','gid':9,'assignedCodepoints':[],'baseline':'closure-source','derived':'closure-derived'}
    encoded=common|{'family':'encoded','gid':2,'assignedCodepoints':[72],'baseline':'encoded-source','derived':'encoded-derived'}
    cases={};review.add_case(cases,first);review.add_case(cases,encoded)
    chosen=cases['same']
    assert chosen['family']=='encoded' and chosen['gid']==2
    assert chosen['baseline']=='encoded-source' and chosen['assignedCodepoints']==[72]
    assert len(chosen['aliases'])==2
    assert chosen['aliases'][0]['baseline']=='closure-source' and chosen['aliases'][0]['codepoints']==[]
    assert chosen['aliases'][1]['baseline']=='encoded-source' and chosen['aliases'][1]['codepoints']==[72]


def test_specimen_uses_correct_later_alias_font_and_gid(tmp_path,monkeypatch):
    common={'cacheKey':'same','status':'native-retained-guard','profile':'Jigmo.ttf','inkBoxAreaEm2':1,'variationPairs':[]}
    a=common|{'family':'a','gid':1,'assignedCodepoints':[72],'baseline':'a-source','derived':'a-derived'}
    b=common|{'family':'b','gid':2,'assignedCodepoints':[73],'baseline':'b-source','derived':'b-derived'}
    cases={};review.add_case(cases,a);review.add_case(cases,b)
    class Paints:
        def __init__(self,path):self.path=path
        def shape(self,text,size):return {'glyphs':[{'gid':2 if self.path.startswith('b-') else 9}]}
    rendered=[];monkeypatch.setattr(review,'Font',Paints);monkeypatch.setattr(review,'render',lambda samples,path:rendered.extend(samples))
    review.specimens({'rankedEncoded':[cases['same']]},tmp_path,1)
    selected=review.read(tmp_path/'encoded-review-corpus.json')['selected'][0]
    assert selected['family']=='b' and selected['gid']==2 and selected['reviewText']=='I'
    assert selected['baseline']=='b-source' and selected['derived']=='b-derived'
    assert [sample['font'] for sample in rendered]==['b-source','b-derived']


def test_pinned_public_inventory_keeps_variation_selectors():
    assigned=review.inventory()
    assert 0xfe00 in assigned and 0xe0100 in assigned
