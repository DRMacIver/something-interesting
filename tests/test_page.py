"""Checks on the page itself."""

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parent.parent
SITE = "https://drmaciver.github.io/something-interesting/"


def meta(name):
    html = (ROOT / "index.html").read_text()
    match = re.search(rf'<meta\s+(?:property|name)="{re.escape(name)}"\s+content="([^"]*)"', html)
    return match and match.group(1)


def test_links_to_the_page_show_a_preview_of_the_comic():
    assert meta("og:title")
    assert meta("og:description")
    assert meta("og:url") == SITE
    assert meta("twitter:card") == "summary_large_image"
    # Previews need the image's full URL.
    image = meta("og:image")
    assert image and image.startswith(SITE + "assets/preview.png")
    assert meta("twitter:image") == image


def test_the_preview_image_is_the_comic_at_a_shareable_size():
    with Image.open(ROOT / "assets" / "preview.png") as image:
        assert image.width == 1200
        assert image.height > image.width
