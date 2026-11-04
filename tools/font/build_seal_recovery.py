"""Trace reviewed public-domain scan crops; charts are verification only."""
import hashlib
import json
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage
from skimage.filters import threshold_otsu
from skimage.morphology import disk
from skimage.measure import find_contours, approximate_polygon
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT/'data/font-sources/seal-recovery.json'
OUTPUT = ROOT/'build/unicode-sources/seal-recovery/DadSealRecovery-Regular.ttf'


SOURCE_PROPERTIES = {'kSEAL_CCZSrc', 'kSEAL_DYCSrc', 'kSEAL_QJZSrc', 'kSEAL_THXSrc'}


def validate_reference(record, references):
    source_property = record.get('sourceProperty', 'kSEAL_CCZSrc')
    assert source_property in SOURCE_PROPERTIES
    assert references[record['codepoint'], source_property] == record['sequence']
    # TH-Y is a unified index for other editions, not a THX scan source.
    assert not (source_property == 'kSEAL_THXSrc' and record['sequence'].startswith('TH-Y'))


def source_image(record):
    path=ROOT/record['scan']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==record['scanSha256']
    if 'pdfImage' in record:
        import pymupdf
        spec=record['pdfImage']
        with pymupdf.open(path) as doc:
            assert spec['xref'] in {item[0] for item in doc[spec['page']-1].get_images()}
            raw=doc.extract_image(spec['xref'])
        image=Image.open(BytesIO(raw['image'])).convert('L')
        assert list(image.size)==spec['size']
        assert hashlib.sha256(image.tobytes()).hexdigest()==spec['pixelSha256']
        # A PDF stencil image can store white mask bits for printed black ink.
        # Its reviewed polarity is explicit rather than guessed from brightness.
        if spec.get('invert',False):image=ImageOps.invert(image)
        image=image.resize((image.width*2,image.height*2),Image.Resampling.LANCZOS)
    else:
        image=Image.open(path).convert('L')
        assert image.size==(3840,3767)
    return image


def mask(record):
    image=source_image(record)
    left,right=record['half']
    image=image.crop((left*2,0,right*2,image.height)).rotate(record['rotation'],resample=Image.Resampling.BICUBIC)
    x,y,w,h=[v*2 for v in record['crop']]
    image=image.crop((x,y,x+w,y+h))
    grey=ndimage.gaussian_filter(np.asarray(image).astype(float),1)
    # Dark binding shadows can otherwise fill the spaces between thin strokes.
    # Keep any reviewed threshold adjustment in the per-glyph source recipe.
    ink=grey<threshold_otsu(grey)+record.get('thresholdOffset',20)
    ink=ndimage.binary_closing(ink,structure=disk(1))
    ink=ndimage.binary_opening(ink,structure=disk(record.get('openingRadius',3)))
    labels,_=ndimage.label(ink);sizes=np.bincount(labels.ravel());sizes[0]=0
    # Dense glyphs can contain meaningful dots smaller than the default debris cutoff.
    # Lower this only for an explicitly reviewed source crop.
    ink &= sizes[labels]>=record.get('minimumComponentArea',70)
    if record['codepoint']=='3F5F1':
        # A later thin pencil line crosses the lower stems. Remove horizontal
        # bridges only in its reviewed band, retaining the long vertical ink.
        vertical=ndimage.binary_opening(ink,structure=np.ones((11,1),bool))
        ink[160:196]=vertical[160:196]
    # Explicitly reviewed pencil remnants; coordinates are in doubled scan
    # crop pixels. Keep these decisions in the provenance recipe.
    for x0,y0,x1,y1 in record.get('clearRects',[]):
        ink[y0:y1,x0:x1]=False
    for x0,y0,x1,y1 in record.get('verticalOpeningBands',[]):
        vertical=ndimage.binary_opening(ink,structure=np.ones((11,1),bool))
        ink[y0:y1,x0:x1]=vertical[y0:y1,x0:x1]
    # A local closing can reconnect a documented short break in a worn stem
    # without thickening the whole drawing or merging unrelated components.
    for x0,y0,x1,y1,radius in record.get('closingRects',[]):
        closed=ndimage.binary_closing(ink,structure=disk(radius))
        ink[y0:y1,x0:x1]=closed[y0:y1,x0:x1]
    # Explicit per-scan repair of tiny paper/printing pits inside solid ink.
    # Eight-connected background matches tracing: never fill an open counter
    # or a gap between strokes, and leave larger enclosed spaces untouched.
    if maximum_area := record.get('fillSmallHoles',0):
        background=np.ones((3,3),bool)
        holes=ndimage.binary_fill_holes(ink,structure=background)&~ink
        labels,_=ndimage.label(holes,structure=background)
        sizes=np.bincount(labels.ravel())
        selected=(sizes<=maximum_area)&(sizes>0);selected[0]=False
        ink |= selected[labels]
    return image,ink


def trace(ink):
    ys,xs=np.nonzero(ink);scale=760/max(np.ptp(xs)+1,np.ptp(ys)+1)
    cx=(xs.min()+xs.max())/2;cy=(ys.min()+ys.max())/2
    pen=TTGlyphPen(None)
    for contour in find_contours(np.pad(ink.astype(float),1),.5):
        contour=approximate_polygon(contour,tolerance=.35)
        points=[(round(500+(x-1-cx)*scale),round(380-(y-1-cy)*scale)) for y,x in contour]
        if len(points)<4:continue
        pen.moveTo(points[0])
        for point in points[1:-1]:pen.lineTo(point)
        pen.closePath()
    return pen.glyph()


def build(source=None):
    source=source or json.loads(SPEC.read_text())
    inputs=SPEC.read_bytes()+Path(__file__).read_bytes()+(ROOT/'data/unicode/18.0.0/SealSources.txt').read_bytes()
    for entry in source['files']:
        raw=(ROOT/entry['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==entry['sha256']
        inputs+=raw
    licence=ROOT/source['licence'];inputs+=licence.read_bytes()
    key=hashlib.sha256(inputs).hexdigest();cache=OUTPUT.with_suffix('.built.json')
    if OUTPUT.exists() and cache.exists():
        saved=json.loads(cache.read_text())
        if saved['input']==key and saved['output']==hashlib.sha256(OUTPUT.read_bytes()).hexdigest():return OUTPUT
    refs={}
    for line in (ROOT/'data/unicode/18.0.0/SealSources.txt').read_text().splitlines():
        fields=line.split('\t')
        if len(fields)==3 and fields[1] in SOURCE_PROPERTIES:
            cp,prop,seq=fields;refs[cp[2:],prop]=seq
    glyphs={'.notdef':TTGlyphPen(None).glyph()};cmap={}
    for record in source['glyphs']:
        validate_reference(record, refs)
        _,ink=mask(record);name='u'+record['codepoint'];glyphs[name]=trace(ink);cmap[int(record['codepoint'],16)]=name
    font=FontBuilder(1000,isTTF=True);font.setupGlyphOrder(list(glyphs));font.setupCharacterMap(cmap);font.setupGlyf(glyphs)
    for glyph in font.font['glyf'].glyphs.values():glyph.recalcBounds(font.font['glyf'])
    font.setupHorizontalMetrics({n:(1000,getattr(g,'xMin',0)) for n,g in glyphs.items()})
    font.setupHorizontalHeader(ascent=880,descent=-120)
    font.setupOS2(sTypoAscender=880,sTypoDescender=-120,usWinAscent=880,usWinDescent=120,fsType=0)
    font.setupNameTable(dict(familyName='Dad Seal Recovery',styleName='Regular',uniqueFontIdentifier='DadSealRecovery-1',fullName='Dad Seal Recovery Regular',psName='DadSealRecovery-Regular',version='Version 1.000',copyright='Copyright (c) 2026 calvins-dad contributors. Drawings traced from public-domain historical scans.',licenseDescription=licence.read_text(),licenseInfoURL='https://openfontlicense.org'))
    font.setupPost();font.font['head'].created=font.font['head'].modified=3876336000;font.font.recalcTimestamp=False
    font.save(OUTPUT);cache.write_text(json.dumps(dict(input=key,output=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()))+'\n')
    return OUTPUT


if __name__=='__main__':print(build())
