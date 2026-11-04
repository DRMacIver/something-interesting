"""Subset explicit licensed NewCM variation mappings, preserving native layout."""
import hashlib
import json
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from native_variations import variation_ranges
from math_unicode_marks import repair_marks,unicode_categories
from math_historical_variants import install as install_historical,REFERENCES

ROOT=Path(__file__).resolve().parents[2]


def build():
    spec=json.loads((ROOT/'data/font-sources/newcm.json').read_text())
    for entry in spec['files']:
        assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256']
    source=spec['files'][0]
    font=TTFont(ROOT/source['path'],recalcTimestamp=False)
    wanted={tuple(map(ord,text)) for text in source['include_sequences']}
    assert len(wanted)==27
    data=ROOT/'data/unicode/18.0.0/StandardizedVariants.txt'
    pin=next(e['sha256'] for e in json.loads((ROOT/'data/unicode/sources.json').read_text())['files'] if e['path']=='18.0.0/StandardizedVariants.txt')
    assert hashlib.sha256(data.read_bytes()).hexdigest()==pin
    standardized={tuple(int(c,16) for c in line.split(';')[0].split()) for row in data.read_text().splitlines() if (line:=row.split('#')[0].strip())}
    assert wanted<=standardized
    native={(cp,s):name or font.getBestCmap()[cp] for t in font['cmap'].tables if t.format==14 for s,rows in t.uvsDict.items() for cp,name in rows}
    assert wanted<=native.keys()
    original_wanted=set(wanted)
    historical=install_historical(font,include_kurrent=True)
    native.update({(r['base'],r['selector']):r['glyph'] for r in historical})
    wanted.update((r['base'],r['selector']) for r in historical)
    assert len(wanted)==37 and wanted<=standardized
    # Do not let the donor's unrelated UVS override existing source choices.
    for table in font['cmap'].tables:
        if table.format==14:
            table.uvsDict={s:[(cp,name) for cp,name in rows if (cp,s) in wanted]
                           for s,rows in table.uvsDict.items()}
            table.uvsDict={s:rows for s,rows in table.uvsDict.items() if rows}
    # Retain native mark attachment for accented variant clusters too.
    marks={int(f[0],16) for line in (ROOT/'data/unicode/18.0.0/UnicodeData.txt').read_text().splitlines()
           if (f:=line.split(';'))[2].startswith('M')}
    points=({cp for cp,_ in wanted}|marks)&font.getBestCmap().keys()
    options=subset.Options()
    options.layout_features=['*']
    options.name_IDs=['*'];options.name_languages=['*'];options.name_legacy=True
    options.glyph_names=True
    sub=subset.Subsetter(options=options)
    sub.populate(unicodes=points|{s for _,s in wanted})
    sub.subset(font)
    bases={native[pair] for pair in wanted}|{font.getBestCmap()[cp] for cp,_ in wanted}
    mark_repair=repair_marks(font,bases,unicode_categories(ROOT))
    family='Dad Math Variants'
    for record in font['name'].names:
        if record.nameID in {1,2,3,4,6,16,17}:
            value='Regular' if record.nameID in {2,17} else family.replace(' ','') if record.nameID==6 else family
            record.string=value.encode(record.getEncoding())
    font['name'].setName('Modified subset for 37 standardized variation sequences. Renamed Dad Math Variants; 27 native variants, nine historical relation adaptations and an original kurrent z; Unicode combining attachment added from MATH optical points. See licenses/README-DadMathVariants.txt.',10,3,1,0x409)
    font['name'].setName('GUST Font License 1.0 and LPPL 1.3c. See licenses/NewCM-GUST.txt and licenses/NewCM-LPPL.txt.',13,3,1,0x409)
    cff=font['CFF '].cff
    cff.fontNames=['DadMathVariants']
    for top in cff.topDictIndex:
        top.FamilyName=top.FullName=family
    font['head'].created=font['head'].modified=2082844800
    font.recalcTimestamp=False;font.flavor='woff2'
    path=ROOT/'assets/fonts/dad-math-variants.woff2'
    font.save(path)
    from build_scripts import ranges
    result=dict(family=family,variationOnly=True,file=path.relative_to(ROOT).as_posix(),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size,
                source=source['path'],sourceSha256=source['sha256'],ranges=ranges(font.getBestCmap()),
                nativeVariations=variation_ranges(font),variationSequences=source['include_sequences']+[chr(r['base'])+chr(r['selector']) for r in historical],
                variationDerivations=historical,variationReferences=REFERENCES,
                markAttachmentRepair=mark_repair,
                licence='assets/fonts/licenses/NewCM-GUST.txt',
                notices=['assets/fonts/licenses/NewCM-Package-License.txt','assets/fonts/licenses/NewCM-GUST.txt','assets/fonts/licenses/NewCM-LPPL.txt','assets/fonts/licenses/README-DadMathVariants.txt'],
                style='27 native calligraphic variants, nine reviewed historical relations and original kurrent z; all 37 pairs visually retained at dialogue size; specialist review provisional',
                styleReview='docs/math-variant-style-review.json')
    (ROOT/'js/math-variant-manifest.js').write_text('// Generated by tools/font/build_math_variants.py\nexport default '+json.dumps(result,separators=(',',':'))+';\n')
    review=dict(source=source['path'],sourceSha256=source['sha256'],dataSha256=pin,
                variants=[dict(base=cp,selector=s,sourceGlyph=native[(cp,s)]) for cp,s in sorted(original_wanted)],
                derivedVariants=historical,variationReferences=REFERENCES,
                markAttachmentRepair=mark_repair,styleReview='docs/math-variant-style-review.json',status='27 native source variants, nine historical relation adaptations and original kurrent z; Unicode mark attachment repaired; all 37 pairs visually retained at 22/44 px; specialist review provisional')
    (ROOT/'docs/math-variant-review.json').write_text(json.dumps(review,indent=2)+'\n')
    print(f'{len(wanted)} explicit math variants; {result["bytes"]} bytes')


if __name__=='__main__':build()
