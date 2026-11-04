"""Extract original PDF ink and clip adjacent scenery into review sprites.

No character strokes are synthesized, reposed, or redrawn. Both surrounding
paper and interior paper are transparent, as for a monochrome font glyph.
"""
import json
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
from skimage.graph import route_through_array

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'assets/emoji-concepts/hobbes-source-v1'
# Coordinates are pixels in the source crop at five pixels per PDF point.
POSES = [
    dict(name='standing',page=12,box=(420,371,496,539),
         silhouette=[(145,40),(177,40),(198,45),(218,53),(248,56),(277,57),(315,69),(324,90),(318,115),(320,139),(310,159),(328,177),(318,202),(303,218),(292,236),(295,269),(307,293),(309,328),(317,363),(311,398),(319,436),(339,481),(319,509),(302,527),(289,573),(279,620),(284,662),(309,680),(339,680),(361,676),(374,689),(379,726),(379,757),(349,748),(317,754),(291,754),(263,756),(236,749),(212,754),(191,742),(173,723),(142,716),(117,716),(92,706),(68,705),(47,715),(31,702),(28,678),(32,652),(42,632),(66,619),(87,622),(107,637),(117,623),(124,595),(132,577),(133,564),(112,574),(97,568),(91,552),(93,524),(108,493),(119,469),(128,445),(137,424),(137,384),(143,356),(147,318),(155,285),(171,259),(169,247),(148,239),(130,229),(112,214),(96,191),(95,174),(99,151),(119,137),(128,115),(143,82)],
         head=(88,34,334,250)),
    dict(name='surprised',page=183,box=(512,719,569,866),
         silhouette=[(37,24),(50,18),(79,22),(117,14),(164,25),(219,22),(240,35),(238,89),(215,98),(249,123),(247,162),(229,181),(218,207),(206,220),(199,239),(207,264),(207,324),(211,376),(216,437),(210,474),(208,526),(206,591),(207,646),(236,657),(263,677),(267,701),(249,721),(211,728),(65,731),(35,720),(20,697),(19,654),(20,602),(18,571),(13,554),(12,520),(26,503),(30,471),(34,443),(34,402),(42,366),(45,328),(50,283),(59,246),(69,229),(81,217),(53,192),(29,180),(32,164),(26,155),(34,142),(25,131),(36,122),(59,106),(75,104),(69,91),(70,76),(57,69),(48,50)],
         head=(20,8,257,231)),
    dict(name='thinking',page=251,box=(184,437,247,577),
         silhouette=[(113,25),(140,26),(163,27),(185,25),(215,34),(236,52),(248,72),(265,94),(265,113),(279,130),(271,151),(260,172),(240,193),(229,211),(242,233),(253,247),(258,274),(273,297),(270,322),(252,344),(236,364),(232,400),(221,429),(212,446),(215,492),(219,535),(216,573),(232,594),(261,613),(274,635),(264,655),(239,668),(196,680),(148,683),(104,677),(80,657),(64,641),(50,655),(27,656),(17,639),(17,616),(17,598),(17,575),(23,567),(32,565),(51,573),(58,552),(61,516),(64,477),(69,442),(75,415),(72,402),(61,396),(58,377),(47,351),(32,345),(20,333),(16,317),(16,285),(30,267),(49,249),(67,232),(87,216),(100,202),(87,193),(90,177),(78,163),(77,150),(84,135),(97,117),(115,108),(113,90),(117,71),(118,61)],
         head=(69,17,289,220)),
]


def extract(doc, spec):
    page = doc[spec['page']-1]
    image = next(row for row in page.get_images(full=True) if row[1])
    mask = pymupdf.Pixmap(doc,image[1])
    ink = Image.frombytes('L',(mask.width,mask.height),mask.samples)
    rect = page.get_image_rects(image[0])[0]
    x0,y0,x1,y1 = spec['box']
    bounds = tuple(round(v) for v in ((x0-rect.x0)*mask.width/rect.width,
        (y0-rect.y0)*mask.height/rect.height,(x1-rect.x0)*mask.width/rect.width,
        (y1-rect.y0)*mask.height/rect.height))
    ink = ink.crop(bounds)
    if spec.get('combinedLayers'):
        pix=page.get_pixmap(matrix=pymupdf.Matrix(5,5),clip=pymupdf.Rect(spec['box']),colorspace=pymupdf.csGRAY)
        grey=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
        # Composite rendering retains dark detail stored in either PDF layer.
        # Remove the scan's grey paper; retain intermediate stroke coverage.
        ink=Image.fromarray(np.clip((170-grey.astype(float))*255/120,0,255).astype(np.uint8))
    stencil = Image.new('L',ink.size)
    points = [(round(x*ink.width/((x1-x0)*5)),round(y*ink.height/((y1-y0)*5)))
              for x,y in spec['silhouette']]
    black = np.asarray(ink)>127
    if spec['name'] in {'surprised','thinking'}:
        black[:,:13]=False  # Adjacent panel border, outside the character.
    if spec['name']=='thinking':
        black[:29,:]=False  # Speech-balloon line above the ears.
    from scipy.ndimage import binary_dilation
    # Snap the coarse hand-selection to original black pixels, then follow the
    # ink between adjacent points. This avoids polygonal white halos while
    # bridging the few intentional breaks in the original contour.
    ImageDraw.Draw(stencil).line(points+[points[0]],fill=255,width=1)
    original_points=points.copy()
    distance=distance_transform_edt(np.asarray(stencil)==0)
    cost=np.where(black,.1,8.)+.06*distance**2
    _,nearest=distance_transform_edt(~black,return_indices=True)
    points=[(int(nearest[1,y,x]),int(nearest[0,y,x])) for x,y in points]
    outline=[]
    for a,b in zip(points,points[1:]+points[:1]):
        x0=max(0,min(a[0],b[0])-15);x1=min(ink.width,max(a[0],b[0])+16)
        y0=max(0,min(a[1],b[1])-15);y1=min(ink.height,max(a[1],b[1])+16)
        route,_=route_through_array(cost[y0:y1,x0:x1],
            (a[1]-y0,a[0]-x0),(b[1]-y0,b[0]-x0),fully_connected=True)
        outline.extend((x+x0,y+y0) for y,x in route)
    stencil=Image.new('L',ink.size)
    ImageDraw.Draw(stencil).polygon(original_points if spec.get('selectionOnly') else outline,fill=255)
    selected=np.asarray(stencil)>0
    selected=binary_dilation(selected,iterations=spec.get('selectionMargin',2))
    black &= selected
    # Keep only the original black ink. Interior paper becomes transparent,
    # which is also the desired representation for a monochrome font glyph.
    # Do not synthesize white contour fills across the source's open strokes.
    rgba = np.zeros((*black.shape,4),dtype=np.uint8)
    rgba[:,:,3] = (np.where(selected,np.asarray(ink),0)
                   if spec.get('combinedLayers') else black.astype(np.uint8)*255)
    return Image.fromarray(rgba)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    doc = pymupdf.open(ROOT/'calvin-and-hobbes.pdf')
    sprites=[]
    for spec in POSES:
        sprite=extract(doc,spec)
        sprite.save(OUT/(spec['name']+'.png'))
        sprites.append(sprite)
    for spec,sprite in zip(POSES,sprites.copy()):
        head=sprite.crop(spec['head'])
        head.save(OUT/(spec['name']+'-face.png'))
        sprites.append(head)
    sheet=Image.new('RGBA',(1440,1120))
    for i,sprite in enumerate(sprites):
        sprite=sprite.crop(sprite.getbbox())
        sprite.thumbnail((392,460),Image.Resampling.LANCZOS)
        x=(i%3)*480+(480-sprite.width)//2
        y=(i//3)*560+(560-sprite.height)//2
        sheet.alpha_composite(sprite,(x,y))
    sheet.save(OUT/'sprite-sheet.png')
    preview=Image.new('RGBA',sheet.size,'white')
    preview.alpha_composite(sheet)
    preview.convert('RGB').save(OUT/'sprite-sheet-white-preview.png')
    (OUT/'provenance.json').write_text(json.dumps(dict(
        source='calvin-and-hobbes.pdf',method='Native PDF ink-mask extraction; manual clipping snapped to original ink; transparent interiors; no image generation or synthesized character strokes',
        poses=POSES,order=[s['name'] for s in POSES]+[s['name']+'-face' for s in POSES]),indent=2)+'\n')
    print(OUT/'sprite-sheet.png')


if __name__=='__main__':
    main()
