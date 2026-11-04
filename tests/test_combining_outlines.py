"""All outline drawing identities, geometry and licences have real donors."""
import hashlib,json
import sys
from functools import lru_cache

from native_sfnt_loader import evidence_ttfont as TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from font_baseline_checks import assert_catalog_equal_or_optical, evidence_identity
from test_font_scripts import ROOT
from test_font_scripts import shape


@lru_cache(maxsize=128)
def _font(path,identity):return TTFont(ROOT/path)


def font(path):return _font(path,evidence_identity(ROOT/path))


def test_numeric_enclosures_export_exact_native_parts_without_changing_catalog_drawings():
    sys.path.insert(0,str(ROOT/'tools/font'))
    from build_combining_outlines import numeric_enclosure
    data=json.loads((ROOT/'js/combining-outline-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    baseline=json.loads((ROOT/'output/font-review/pre-numeric-enclosures/combining-outline-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    for cp in [0x488,0x489,0xa670,0xa671,0xa672]:
        row=data['marks'][str(cp)];source=font(data['sources'][row['source']]['file'])
        expected=numeric_enclosure(source.getGlyphSet(),row['glyph'],1/source['head'].unitsPerEm,cp)
        assert row.pop('numericEnclosure')==expected
        # Complete decomposition has the same ink area as the source;
        # no omitted ray, added circle, replacement bracket or carrier.
        from fontTools.pens.areaPen import AreaPen
        native=AreaPen(None);parse_path(row['path'],native)
        total=0
        for part in expected['parts']:
            area=AreaPen(None);parse_path(part['path'],area);total+=area.value
        assert abs(native.value-total)<.000001
        assert all(part['path'] and part['bounds'][2]>part['bounds'][0] for part in expected['parts'])
    assert_catalog_equal_or_optical(baseline,data)


def test_combining_outline_catalog_preserves_source_identities_and_geometry():
    data=json.loads((ROOT/'js/combining-outline-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    assert len(data['marks'])==1840
    assert set(data['nativeContextOnly'])=={0x11d45,0x11d97}
    for source in data['sources']:
        assert hashlib.sha256((ROOT/source['file']).read_bytes()).hexdigest()==source['sha256']
        assert source['licence'] or source['suppliedNotice']
    for cp,row in data['marks'].items():
        original=font(data['sources'][row['source']]['file']);name=original.getBestCmap()[int(cp)]
        assert name==row['glyph'] and original.getGlyphID(name)>0
        bounds=BoundsPen(original.getGlyphSet());original.getGlyphSet()[name].draw(bounds)
        if not row['bounds']:
            assert int(cp) in data['nativeContextOnly'] and bounds.bounds is None
            continue
        parsed=BoundsPen(None);parse_path(row['path'],parsed)
        assert all(abs(a-b)<.00001 for a,b in zip(parsed.bounds,row['bounds'])),cp
        unit=original['head'].unitsPerEm
        x0,y0,x1,y1=bounds.bounds
        assert all(abs(a-b)<.000001 for a,b in zip(row['bounds'],[x0/unit,-y1/unit,x1/unit,-y0/unit])),cp
    assert str(0xe0100) not in data['marks']
    assert str(0xe0100) in data['behaviouralMarks']
    assert {int(cp) for cp,e in data['marks'].items() if 'ring' in e}=={0x20dd,0x20de,0x20df,0x20e2,0x20e4}
    for row in data['marks'].values():
        if not row.get('ring'):continue
        outer,inner=row['ring']['outer'],row['ring']['inner']
        assert abs(outer['area'])>abs(inner['area']) and outer['area']*inner['area']<0
        for contour in [outer,inner]:
            parsed=BoundsPen(None);parse_path(contour['path'],parsed)
            assert all(abs(a-b)<.00001 for a,b in zip(parsed.bounds,contour['bounds']))


def test_empty_native_context_records_select_real_contextual_letter_forms():
    data=json.loads((ROOT/'js/combining-outline-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    for mark,base in [(0x11d45,0x11d0c),(0x11d97,0x11d6c)]:
        row=data['marks'][str(mark)];path=ROOT/data['sources'][row['source']]['file']
        plain=shape(path,chr(base),True)
        suppressed=shape(path,chr(base)+chr(mark),True)
        joined=shape(path,chr(base)+chr(mark)+chr(base),True)
        assert len(suppressed)==1 and suppressed[0][0]!=plain[0][0]
        assert all(g[0]>0 for g in joined) and joined!=plain+plain


def test_variant_mark_drawings_are_exactly_from_each_selected_native_font():
    data=json.loads((ROOT/'js/combining-outline-manifest.js').read_text().split('export default ',1)[1].rstrip(';\n'))
    assert 'Dad Math Variants' in data['variationMarks']
    assert len(data['variationMarks'])>=93
    checked=0
    for family,entry in data['variationMarks'].items():
        source=data['sources'][entry['source']]
        original=font(source['file']);cmap=original.getBestCmap();gs=original.getGlyphSet()
        unit=1/original['head'].unitsPerEm
        for cp,row in entry['marks'].items():
            assert row['glyph']==cmap[int(cp)],(family,cp)
            drawing=data['variantDrawings'][row['drawing']]
            pen=SVGPathPen(gs,ntos=lambda n:f'{n:.6f}'.rstrip('0').rstrip('.') if n else '0')
            gs[cmap[int(cp)]].draw(TransformPen(pen,(unit,0,0,-unit,0,0)))
            assert drawing['path']==pen.getCommands(),(family,cp)
            if drawing['bounds']:
                parsed=BoundsPen(None);parse_path(drawing['path'],parsed)
                assert all(abs(a-b)<.00001 for a,b in zip(parsed.bounds,drawing['bounds'])),(family,cp)
            checked+=1
    assert checked>20000
