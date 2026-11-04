"""Reviewed monochrome emoji from pinned OFL Noto Emoji, with pen treatment."""
import hashlib
import json
import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from pen_translate import Settings, translate

MUSIC = [ord(c) for c in '🥁🎷🎺🎸🎻🎹🎵🎶🎼🎤🎧📻']
CLOCKS = list(range(0x1F550, 0x1F568))
TRANSPORT = [ord(c) for c in '🚗🚕🚙🚌🚎🚐🚚🚛🚜🛺🚂🚃🚄🚅🚆🚇🚈🚝🚢⛵🚤🛥🛶⛴']
TOOLS = [ord(c) for c in '🛠⚒🔨⛏🔧🪛🔩⚙🗜⚖🔗⛓🪝🧰🧲🪜🪚🪓🪤🧯🔑🗝🔒🔓']
EXPRESSIONS = [ord(c) for c in '🤣🫠😇🥰😍🤩😘😗😚😙🥲🤑🤗🤭🫢🫣🤫🫡🫥🤥🫨😌🥴🤠🥳🥸🫤🥹😨😰😥😱😓😺😸😹😻😼😽🙀😿😾🙈🙉🙊']
MAMMALS = [ord(c) for c in '🐵🐒🦍🦧🐶🐕🦮🐩🐺🦊🦝🐱🐈🦁🐯🐅🐆🐴🫎🫏🐎🦄🦓🦌🦬🐮🐂🐃🐄🐷🐖🐗🐽🐏🐑🐐🐪🐫🦙🦒🐘🦣🦏🦛🐭🐁🐀🐹🐰🐇🐿🦫🦔🦇🐻🐨🐼🦥🦦🦨🦘🦡🐾']
BIRDS = [ord(c) for c in '🦃🐔🐓🐣🐤🐥🐦🐧🕊🦅🦆🦢🦉🦤🪶🦩🦚🦜🪽🪿']
WILDLIFE = [ord(c) for c in '🐸🐊🐢🦎🐍🐲🐉🦕🦖🐳🐋🐬🦭🐟🐠🐡🦈🐙🐚🪸🪼🦀🦞🦐🦑🦪🐌🦋🐛🐜🐝🪲🐞🦗🪳🕷🕸🦂🦟🪰🪱🦠']
PLANTS = [ord(c) for c in '💐🌸💮🪷🏵🌹🥀🌺🌻🌼🌷🪻🌱🪴🌲🌳🌴🌵🌾🌿☘🍀🍁🍂🍃🪹🪺🍄']
SPORTS = [ord(c) for c in '⚽⚾🥎🏀🏐🏈🏉🎾🥏🎳🏏🏑🏒🥍🏓🏸🥊🥋🥅⛳⛸🎣🤿🎽🎿🛷🥌']
FOOD = [ord(c) for c in '🍞🥐🥖🫓🥨🥯🥞🧇🧀🍖🍗🥩🥓🍔🍟🍕🌭🥪🌮🌯🫔🥙🧆🥚🍳🥘🍲🫕🥣🥗🍿🧈🧂🥫🍱🍘🍙🍚🍛🍜🍝🍠🍢🍣🍤🍥🥮🍡🥟🥠🥡']
DINING = [ord(c) for c in '🍦🍧🍨🍩🍪🎂🍰🧁🥧🍫🍬🍭🍮🍯🍼🥛☕🫖🍵🍶🍾🍷🍸🍹🍺🍻🥂🥃🫗🥤🧋🧃🧉🧊🥢🍽🍴🥄🔪🫙🏺']
SKY = [ord(c) for c in '🌑🌒🌓🌔🌕🌖🌗🌘🌙🌚🌛🌜🌝🌞⭐🌟🌠🌌☀☁⛅⛈🌤🌥🌦🌧🌨🌩🌪🌫🌬🌀🌂☂☔⛱⚡❄☃⛄☄💧🌊']
BUILDINGS = [ord(c) for c in '🏠🏡🏢🏣🏤🏥🏦🏨🏩🏪🏫🏬🏭🏯🏰💒⛪🕌🛕🕍⛩🕋⛲🛖']
PLACES = [ord(c) for c in '🏔⛰🌋🗻🏕🏖🏜🏝🏞🏟🏛🏗🏘🏚🌁🌃🏙🌄🌅🌆🌇🌉♨🎠🎡🎢🗼🗽🗾🗺🌐🧭']
TIMEPIECES = [ord(c) for c in '⌚⏰⏱⏲🕰⌛⏳']
STATIONERY = [ord(c) for c in '✏✒🖋🖊🖌🖍📝💼📁📂🗂📅📆🗒🗓📇📋📌📍📎🖇📏📐✂🗃🗄🗑']
PRODUCE = [ord(c) for c in '🍇🍈🍉🍊🍋🍌🍍🥭🍐🍑🍒🍓🫐🥝🍅🫒🥥🥑🍆🥔🥕🌽🌶🫑🥒🥬🥦🧄🧅🥜🫘🌰🫚🫛']
CLOTHING = [ord(c) for c in '👑👒🎩🎓🧢🪖⛑🧣🧤🧥🧦👔👕👖👗👘🥻🩱🩲🩳👙👚👛👜👝🎒🩴👞👟🥾🥿👠👡🩰👢🥼🦺🥽']
ELECTRONICS = [ord(c) for c in '📱📲☎📞📟📠🔋🪫🔌💻🖥🖨⌨🖱🖲💽💾💿📀🧮🎥🎞📽🎬📺📷📸📹📼🔍🔎🕯💡🔦🏮🪔']
CELEBRATIONS = [ord(c) for c in '🎀🎁🎃🎄🎆🎇🧨🎈🎉🎊🎋🎍🎎🎏🎐🎑🎟🎫']
RECREATION = [ord(c) for c in '🎯🪀🪁🎱🔮🪄🎮🕹🎰🎲🧩🧸🪅🪩🪆🃏🎴🎭🖼🎨🧵🪡🧶🪢🎪']
HOUSEHOLD = [ord(c) for c in '🚪🛗🪞🪟🛏🛋🪑🚽🪠🚿🛁🪒🧴🧷🧹🧺🧻🪣🧼🫧🪥🧽🛒🧳']
SCIENCE = [ord(c) for c in '⚗🧪🧫🧬🔬🔭📡🩺🩻🩼💊💉']
TRANSPORT_EXTRA = [ord(c) for c in '🚀🚁🚉🚊🚋🚏🚒🚓🚖🚞🚟🚠🚡🛴🛵🛫🛬🛝🛞🛟🛢']
MOBILITY_EQUIPMENT = [ord(c) for c in '🦯🦼🦽']
BODY_PARTS = [ord(c) for c in '🧠🦷🦴👀👁👅👄🫦🫀🫁🦾🦿']
CATEGORIES = dict(body_parts=BODY_PARTS,mobility_equipment=MOBILITY_EQUIPMENT,transport_extra=TRANSPORT_EXTRA,household=HOUSEHOLD, science=SCIENCE, recreation=RECREATION, celebrations=CELEBRATIONS, electronics=ELECTRONICS, clothing=CLOTHING, produce=PRODUCE, timepieces=TIMEPIECES, stationery=STATIONERY, places=PLACES, buildings=BUILDINGS, music=MUSIC, clocks=CLOCKS, transport=TRANSPORT, tools=TOOLS,
                  expressions=EXPRESSIONS, mammals=MAMMALS, birds=BIRDS, wildlife=WILDLIFE, plants=PLANTS, sports=SPORTS, food=FOOD, dining=DINING, sky=SKY)
POINTS = [cp for points in CATEGORIES.values() for cp in points]
assert len(POINTS) == len(set(POINTS))


def raster(glyphs, name, pixels=384):
    bounds = BoundsPen(glyphs); glyphs[name].draw(bounds)
    x0, y0, x1, y1 = bounds.bounds
    size = max(x1-x0, y1-y0)/.80
    cx, cy = (x0+x1)/2, (y0+y1)/2
    pen = SVGPathPen(glyphs); glyphs[name].draw(pen)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{pixels}" height="{pixels}" '
           f'viewBox="{cx-size/2} {-cy-size/2} {size} {size}">'
           f'<rect x="{cx-size/2}" y="{-cy-size/2}" width="{size}" height="{size}" fill="white"/>'
           f'<path transform="scale(1 -1)" fill="black" d="{pen.getCommands()}"/></svg>')
    doc = pymupdf.open(stream=svg.encode(), filetype='svg')
    pdf = pymupdf.open('pdf', doc.convert_to_pdf())
    pix = pdf[0].get_pixmap(alpha=False)
    return np.asarray(Image.frombytes('RGB', (pix.width, pix.height), pix.samples)).max(axis=2) < 128


def add_licensed(root, glyphs, metrics, cmap, layers, review, outline):
    manifest = json.loads((root/'data/font-sources/noto-emoji.json').read_text())
    for entry in manifest['files']:
        assert hashlib.sha256((root/entry['path']).read_bytes()).hexdigest() == entry['sha256']
    source = root/manifest['files'][0]['path']
    font = TTFont(source)
    source_glyphs = font.getGlyphSet(location={'wght':400})
    for cp in POINTS:
        existing_name=cmap.get(cp)
        assert existing_name is None or (cp==0x1F680 and glyphs[existing_name].numberOfContours==0)
        source_name = font.getBestCmap()[cp]
        # Source-specific resolution/weight choices preserve fine wheel spokes,
        # windows, screw threads, star tips and forehead hatching without
        # relaxing the topology guard.
        weight, pixels = {0x1F696:(350,384),0x2697:(400,768), 0x1F387:(400,768), 0x1F4BB:(400,768), 0x1F5A5:(350,768), 0x1F4FD:(400,512), 0x1F4CD:(400,512), 0x1F682:(350,512), 0x1F6A2:(400,768),
                          0x1F5DC:(400,768), 0x1F929:(400,768),
                          0x1F628:(350,512), 0x1F630:(350,512),
                          0x1F417:(400,512), 0x1F992:(350,512),
                          0x1F9A7:(400,512), 0x1F99A:(400,768),
                          0x1F40A:(400,512), 0x1F433:(400,512),
                          0x1F421:(400,512), 0x1F577:(400,512),
                          0x1F338:(400,512), 0x1F9C7:(400,512),
                          0x1FAD4:(400,512), 0x1F372:(400,512),
                          0x1F9C6:(350,512), 0x1F957:(350,512),
                          0x1F368:(350,512), 0x1F30C:(400,512),
                          0x1F54D:(350,512), 0x1F54B:(400,512),
                          0x1F3DC:(400,512), 0x1F3DA:(400,512),
                          0x1F307:(400,512), 0x1F309:(350,512),
                          0x1F3A1:(350,512), 0x1F5FE:(400,512),
                          0x1F5FA:(350,512)}.get(cp, (400,384))
        selected_glyphs = source_glyphs if weight == 400 else font.getGlyphSet(location={'wght':weight})
        ink = raster(selected_glyphs, source_name, pixels)
        source_transform = {}
        if cp == 0x1F387:
            # The knockout sparkler has six one-pixel raster islands along
            # diagonal white rays at this reviewed resolution. They are
            # antialiasing debris, not separate sparks; retain the large tile.
            labels, count = ndimage.label(ink)
            sizes = np.bincount(labels.ravel()); sizes[0] = 0
            main = sizes.argmax()
            assert count == 7 and sorted(sizes[1:])[:6] == [1]*6
            ink = labels == main
            source_transform = dict(sourceTransform='remove-six-single-pixel-raster-islands')
        if cp == 0x1F31A:
            # The monochrome donor uses white disks for both moon faces.
            # Reverse the interior features of the new moon so dark/light
            # meaning survives without introducing an arbitrary colour.
            labels, count = ndimage.label(ink)
            sizes = np.bincount(labels.ravel()); sizes[0] = 0
            border = labels == sizes.argmax()
            disk = ndimage.binary_fill_holes(border)
            features = ink & ~border
            assert count == 6 and not (features & ~disk).any()
            ink = disk & ~features
            source_transform = dict(sourceTransform='dark-face-inversion')
        # Shift orangutan's pressure field away from its small enclosed details.
        # This reviewed phase choice is deterministic and still uses the same
        # preservation guard and pressure magnitude as every other drawing.
        seed = 129448 if cp == 0x1F9A7 else cp
        # A solid new-moon disk has no representative narrow stroke radius:
        # applying the usual radius-scaled pressure distorts its silhouette.
        # The star-filled Milky Way needs gentler fields to retain white stars.
        adjustments = {0x1F387:dict(pressure=.02, taper=0), 0x1F311:dict(pressure=.02, taper=0),
                       0x1F30C:dict(pressure=.2, bend=.006),
                       0x1F31A:dict(pressure=.15, taper=0),
                       # The Kaaba's broad solid body surrounds fine white
                       # ornament: limit pressure without weakening its guard.
                       0x1F54B:dict(pressure=.1, taper=0)}.get(cp, {})
        treated, treatment = translate(ink, Settings(strength=1.7, seed=seed, **adjustments))
        assert treatment["appliedStrength"] > 0 and not treatment["fallback"], f"No safe expressive treatment for U+{cp:04X}"
        ink = np.asarray(treated) < 128
        white = ndimage.binary_fill_holes(ink)
        yy, xx = np.nonzero(white)
        x0, y0, x1, y1 = map(int, (xx.min(), yy.min(), xx.max(), yy.max()))
        factor = 760/max(x1-x0+1, y1-y0+1)
        transform = x0, y0, factor
        name = existing_name or f'u{cp:X}'
        advance = round((x1-x0+1)*factor)+100
        glyphs[name] = outline(ink, transform)
        # Raster preservation is insufficient if polygon simplification then
        # discards an enclosed detail. Reject that drawing during compilation.
        assert glyphs[name].numberOfContours >= treatment['sourceComponents'] + treatment['sourceHoles'], f'Tracing lost a detail in U+{cp:04X}'
        metrics[name] = advance, 50
        cmap[cp] = name
        layers[name] = []
        for i, mask in enumerate((white, ink)):
            layer = f'{name}.layer{i}'
            glyphs[layer] = outline(mask, transform)
            metrics[layer] = advance, 50
            layers[name].append((layer, i))
        review.append(dict(codepoint=f'U+{cp:04X}', source=str(source.relative_to(root)),
                           sourceGlyph=source_name, sourceWeight=weight, sourcePixels=pixels, advance=advance,
                           bounds=[x0,y0,x1,y1], penTreatment=treatment,
                           **source_transform, license='NotoEmoji-OFL.txt', category=next(category for category,points in CATEGORIES.items() if cp in points)))
    variants = []
    path = root/'data/unicode/18.0.0/emoji/emoji-variation-sequences.txt'
    for line in path.read_text().splitlines():
        fields = line.split('#')[0].strip().split(';')
        if len(fields) < 2:
            continue
        seq = [int(s, 16) for s in fields[0].split()]
        if len(seq) == 2 and seq[0] in POINTS:
            variants.append(tuple(seq))
    return variants
