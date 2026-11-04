"""Original page-129 pounce and face, using both PDF layers."""
import json
from pathlib import Path
import pymupdf
from PIL import Image
from extract_hobbes import extract, ROOT

OUT=ROOT/'assets/emoji-concepts/hobbes-source-v4'

def pose(name,box,points):
    # Selection coordinates were inspected on the 4x composite page crops.
    return dict(name=name,page=129,box=box,combinedLayers=True,selectionOnly=True,selectionMargin=12 if name=='pounce' else 3,
                silhouette=[(x*5/4,y*5/4) for x,y in points])

POSES=[
    pose('face',(522,438,629,522),[
        (251,24),(275,20),(296,31),(309,44),(331,44),(353,48),
        (376,61),(376,76),(373,94),(378,113),(373,139),(377,153),
        (387,171),(380,186),(369,201),(377,217),(359,218),(350,232),
        (335,222),(323,231),(307,229),(292,223),(277,215),(263,205),
        (251,195),(240,187),(230,187),(228,182),(219,183),(211,179),
        (225,173),(206,167),(216,154),(198,151),(218,139),(201,134),
        (219,121),(210,112),(229,110),(225,97),(246,104),(253,91),
        (260,80),(250,66),(244,47)]),
    pose('pounce',(238,350,516,577),[
        (21,746),(26,731),(43,718),(78,724),(126,741),(160,708),(195,685),(239,662),
        (264,660),(267,641),(281,616),(300,596),(317,582),(350,571),
        (366,550),(392,548),(407,555),(428,551),(450,537),(475,522),
        (510,500),(550,477),(590,450),(630,425),(655,410),(675,405),(682,418),
        (704,418),(720,404),(718,386),(733,357),(744,348),(722,337),
        (704,328),(704,316),(729,308),(754,304),(777,306),
        (858,263),(949,218),(1040,177),(1110,149),(1110,185),
        (1043,216),(957,256),(873,300),(824,329),(848,332),
        (877,337),(895,347),(894,361),(875,382),(856,396),
        (869,405),(850,430),(857,451),(833,470),(806,485),(780,493),(758,497),(744,475),(740,482),
        (709,510),(645,556),(572,606),(506,655),(425,710),
        (359,754),(305,788),(245,831),(209,850),(196,874),
        (175,890),(157,887),(150,869),(143,854),(128,865),
        (115,855),(120,833),(101,821),(93,811),(91,796),
        (105,787),(123,782),(143,792),(167,791),(188,800),
        (250,757),(250,747),(241,738),(224,731),(196,735),
        (167,746),(154,764),(154,783),(136,781),(108,771),
        (86,769),(63,780),(41,778),(28,767)])
]

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    doc=pymupdf.open(ROOT/'calvin-and-hobbes.pdf')
    previews=[]
    for spec in POSES:
        im=extract(doc,spec);im=im.crop(im.getbbox())
        im.save(OUT/(spec['name']+'.png'))
        preview=Image.new('RGBA',im.size,'white');preview.alpha_composite(im)
        preview.convert('RGB').save(OUT/(spec['name']+'-white-preview.png'))
    (OUT/'provenance.json').write_text(json.dumps(dict(
        source='calvin-and-hobbes.pdf',page=129,strip='middle',
        facePanel=3,pouncePanel=2,poses=POSES,
        method='Composite PDF render at 5 pixels/point; grey-paper removal and original-contour clipping. No generated artwork.',
        limitation='Pounce tail ends at the original panel boundary; no continuation is invented.'),indent=2)+'\n')

if __name__=='__main__':main()
