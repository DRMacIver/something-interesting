"""Historical asteroid drawings retain identities and their internal counters."""
import hashlib
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linear_sum_assignment
from native_sfnt_loader import evidence_ttfont as TTFont
from font_baseline_checks import pinned_packaging_font
from test_font_scripts import manifest, ROOT, shape
from test_font_cuneiform import outline


def test_all_asteroid_drawings_preserve_topology_spacing_and_distinctions():
    entry=next(e for e in manifest()['fonts'] if e['source'].endswith('/UnicodiaFunky.ttf'))
    source=TTFont(ROOT/entry['source']);font=TTFont(ROOT/entry['file'])
    points=list(range(0x1cec0,0x1ced1))+list(range(0x1f777,0x1f77b))
    # Authenticate raw construction and the complete native/cache/current lineage.
    from alphabet_ink import adapt
    assert hashlib.sha256((ROOT/entry['source']).read_bytes()).hexdigest()==entry['sourceSha256']
    config=next(row for row in json.loads((ROOT/'data/font-sources/unicodia.json').read_text())['files'] if row['path']==entry['source'])
    assert ':alphabet-ink:'+json.dumps(config['ink_ranges'],separators=(',',':'))+':'+hashlib.sha256((ROOT/'tools/font/alphabet_ink.py').read_bytes()).hexdigest() in entry['recipe']
    native=pinned_packaging_font(entry)
    constructed=TTFont(ROOT/entry['source']);adapt(constructed,points)
    for cp in points:assert outline(constructed,cp)==outline(native,cp)
    drawings=[]
    for cp in points:
        before,after=outline(source,cp),outline(font,cp)
        assert after[0] and after[1] and after[2]>0,hex(cp)
        assert before[2]==after[2],hex(cp)
        assert before[0]!=after[0],hex(cp)
        assert max(abs(a-b) for a,b in zip(before[1],after[1]))<=4,hex(cp)
        # Pen perturbations must not remove counters, star components or strokes.
        original=source['glyf'][source.getBestCmap()[cp]]
        derived=font['glyf'][font.getBestCmap()[cp]]
        a,ends_a,flags_a=original.getCoordinates(source['glyf'])
        b,ends_b,flags_b=derived.getCoordinates(font['glyf'])
        assert len(ends_a)==len(ends_b),hex(cp)
        def contours(pts,ends):
            result=[];start=0
            for end in ends:
                contour=list(pts[start:end+1]);start=end+1
                bounds=(min(x for x,y in contour),min(y for x,y in contour),max(x for x,y in contour),max(y for x,y in contour))
                area=sum(x*v-y*u for (x,y),(u,v) in zip(contour,contour[1:]+contour[:1]))
                assert area!=0
                result.append((bounds,area))
            return result
        old,new=contours(a,ends_a),contours(b,ends_b)
        # Contour serialization order has no drawing semantics. Match spatial
        # roles bijectively, preserving winding and overlapping attachment area.
        cost=np.array([[sum((x-y)**2 for x,y in zip(i[0],j[0])) for j in new] for i in old])
        rows,cols=linear_sum_assignment(cost)
        assert len(rows)==len(old)==len(set(cols))
        for i,j in zip(rows,cols):
            ob,oa=old[i];nb,na=new[j]
            assert oa*na>0,hex(cp)
            assert max(ob[0],nb[0])<min(ob[2],nb[2]),hex(cp)
            assert max(ob[1],nb[1])<min(ob[3],nb[3]),hex(cp)
        def contains(a,b):return a[0]<=b[0] and a[1]<=b[1] and a[2]>=b[2] and a[3]>=b[3]
        for i,j in zip(rows,cols):
            for k,l in zip(rows,cols):
                assert contains(old[i][0],old[k][0])==contains(new[j][0],new[l][0]),hex(cp)
        drawings.append(repr(after[0]))
    assert len(set(drawings))==21
    text=''.join(map(chr,points))
    assert shape(ROOT/entry['source'],text)==shape(ROOT/entry['file'],text)


def test_complete_asteroid_field_preserves_native_components_and_counters():
    from check_supplemental_fields import check
    entry=next(e for e in manifest()['fonts'] if e['source'].endswith('/UnicodiaFunky.ttf'))
    pinned_packaging_font(entry)
    native=ROOT/'output/font-review/supplemental-production-baselines'/Path(entry['file']).name
    text=''.join(map(chr,list(range(0x1cec0,0x1ced1))+list(range(0x1f777,0x1f77b))))
    for size in (384,1024):
        result=check(native,ROOT/entry['file'],text,size)
        assert result['status']=='pass',result
