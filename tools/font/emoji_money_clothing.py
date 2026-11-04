"""Compile reviewed money/accessory families without changing earlier glyphs."""
import importlib
from emoji_svg_family import add_svg_family


def add_money_clothing(root,glyphs,metrics,cmap,layers,palette,review,outline):
    sequences=[]
    variations=[]
    for family,count,aliases in [('money',10,0),('clothing',9,2)]:
        module=importlib.import_module(f'emoji_{family}_svg')
        forms,pairs=add_svg_family(root,glyphs,metrics,cmap,layers,palette,review,
                                   outline,family,module.prepare,count,aliases)
        sequences+=forms
        variations+=pairs
    return sequences,sorted(set(variations))
