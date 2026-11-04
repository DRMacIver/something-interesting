"""Candidate colour-preserving flag treatment with a shared gentle warp.

Keeps native emblems and proportions. Only the exterior ink receives pressure
variation; all colours follow the same displacement, preserving their alignment.
This is not registered in the production build.
"""
import hashlib,io,json,re,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageColor
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from pen_translate import Settings,translate
ROOT=Path(__file__).resolve().parents[2]
EXAMPLES=['GB','US','JP','NP','RO','TD','CA','ZA','BR','EU','KR','gbwls']


def label(text):
    if len(text)==2 and all(0x1f1e6<=ord(c)<=0x1f1ff for c in text):
        return ''.join(chr(ord(c)-0x1f1e6+65) for c in text)
    return ''.join(chr(ord(c)-0xe0000) for c in text if 0xe0000<=ord(c)<0xe007f)


def prepare(region):
    spec=json.loads((ROOT/'data/font-sources/noto-emoji-regional-flags-svg.json').read_text())
    source=next(e for e in spec['files'] if label(e['sequence'])==region)
    raw=(ROOT/source['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==source['sha256']
    root=ET.fromstring(raw);removed=[]
    # The upstream waved flags add a translucent perimeter bevel. Replace only
    # that exact decorative path with the pen outline; keep emblem gradients.
    children=list(root)
    if children and children[-1].tag.endswith('path') and children[-1].get('opacity')=='0.2' and children[-1].get('fill','').lower()=='#1a1a1a':
        removed.append(hashlib.sha256(ET.tostring(children[-1])).hexdigest());root.remove(children[-1])
    png=subprocess.run(['rsvg-convert','-w','1536','-h','1536'],input=ET.tostring(root),stdout=subprocess.PIPE,check=True).stdout
    rgba=Image.open(io.BytesIO(png)).convert('RGBA');alpha=np.asarray(rgba)[:,:,3]>=128
    # Quantize unassociated RGB: compositing partially opaque edge pixels on
    # white invents pale materials along the flag perimeter.
    rgb=rgba.convert('RGB')
    # Reconstruct antialiased edges from actual source paints, rather than
    # treating their blended edge pixels as dozens of extra colour materials.
    source_colours={(255,255,255)}
    for element in root.iter():
        paints=[element.get('fill',''),element.get('stop-color','')]
        paints+=re.findall(r'(?:fill|stop-color):([^;]+)',element.get('style',''))
        if element.tag.endswith('path') and not element.get('fill') and 'fill:' not in element.get('style',''):paints.append('#000000')
        for paint in paints:
            if not paint or paint=='none' or paint.startswith('url('):continue
            source_colours.add(ImageColor.getrgb(paint.strip()))
    source_colours=sorted(source_colours)
    if len(source_colours)<=64:
        # Pillow's fixed-palette quantizer caches reduced RGB cells. Use
        # exact nearest paints so antialiased borders cannot acquire speckles
        # from a different colour in the same reduced cell.
        colours=np.asarray(source_colours,dtype=np.uint8)
        _,indices=cKDTree(colours.astype(float)).query(np.asarray(rgb).reshape(-1,3))
        labels=indices.reshape(alpha.shape).astype(np.int16)
        quantization_mode='exact nearest source paints'
    else:
        quantized=rgb.quantize(colors=64,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE);quantization_mode='64-colour emblem palette'

        colours=np.array(quantized.getpalette(),dtype=np.uint8).reshape(-1,3)
        labels=np.asarray(quantized,dtype=np.int16)
    labels=np.where(alpha,labels,-1)
    error=np.abs(np.asarray(rgb,dtype=float)-colours[np.maximum(labels,0)]).mean(axis=2)
    quantization_error=float(error[alpha].mean());assert quantization_error<4, (region,quantization_error)
    # Native margins can be narrower than the pen: pad before tracing the edge.
    alpha=np.pad(alpha,16);labels=np.pad(labels,16,constant_values=-1)
    border=ndi.binary_dilation(alpha,iterations=10)&~ndi.binary_erosion(alpha,iterations=10)
    seed=int.from_bytes(hashlib.sha256(region.encode()).digest()[:4],'big')
    settings=Settings(strength=1.7,seed=seed,pressure=.2,taper=0,bend=.003)
    treated,report=translate(border,settings);ink=np.asarray(treated)<128
    assert report['appliedStrength']>0 and not report['fallback'],region
    # Recreate the exact correlated coordinate field used by pen_translate.
    pad=report['padding'];ys,xs=np.nonzero(border);size=max(np.ptp(xs)+1,np.ptp(ys)+1)
    y,x=np.mgrid[:ink.shape[0],:ink.shape[1]];xn=(x-pad-xs.min())/size;yn=(y-pad-ys.min())/size
    phase=np.random.default_rng(seed).uniform(0,2*np.pi,6)
    dx=size*settings.bend*(.7*np.sin(2*np.pi*yn+phase[0])+.3*np.sin(2*np.pi*(xn+yn)+phase[1]))
    dy=size*settings.bend*(.7*np.sin(2*np.pi*xn+phase[2])+.3*np.sin(2*np.pi*(xn-yn)+phase[3]))
    amount=report['appliedStrength'];warped=ndi.map_coordinates(np.pad(labels,pad,constant_values=-1),[y+amount*dy,x+amount*dx],order=0,mode='constant',cval=-1)
    paper=ndi.binary_fill_holes(ink);warped[~paper]=-1
    palette_path=ROOT/'output/imagegen/emoji-production/heart-palette-source.json';palette_raw=palette_path.read_bytes();palette=json.loads(palette_raw)
    assert hashlib.sha256((ROOT/palette['pdf']).read_bytes()).hexdigest()==palette['pdfSha256']
    anchors=np.array([s['rgb'] for s in palette['samples']],dtype=float)
    masks=[];rgbs=[];regions=[]
    for index in sorted(set(labels.ravel())-{-1}):
        mask=warped==index;before=int((labels==index).sum());after=int(mask.sum())
        if before>=100:assert .85<after/before<1.15,(region,index,before,after)
        if not after:continue
        colour=colours[index].astype(float)
        if colour.min()>245:styled=(255,255,255)
        elif colour.max()<32:styled=(17,17,17)
        else:
            nearest=anchors[np.square(anchors-colour).sum(axis=1).argmin()]
            styled=tuple(map(int,np.rint(.75*colour+.25*nearest)))
        masks.append(mask);rgbs.append(styled);regions.append(dict(sourcePaletteIndex=int(index),sourceRGB=list(map(int,colour)),sourcePixels=before,treatedPixels=after))
    report.update(region=region,source=source,sourcePixels=1536,rgbs=rgbs,regions=regions,
        sourceColourCount=len(source_colours),quantizationMode=quantization_mode,quantizationColours=len(masks),meanQuantizationError=quantization_error,removedPerimeterBevels=removed,
        paletteSource=str(palette_path.relative_to(ROOT)),paletteSha256=hashlib.sha256(palette_raw).hexdigest(),
        nativeColourFraction=.75,comicColourFraction=.25,
        rasterizer=subprocess.check_output(['rsvg-convert','--version'],text=True).strip(),
        programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
    return (paper,*masks,ink),report

