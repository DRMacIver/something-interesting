"""Compile the registered, reviewed book and mail drawings into Dad Emoji."""
from emoji_svg_family import add_svg_family
from emoji_book_mail_svg import prepare


def add_book_mail(root,glyphs,metrics,cmap,layers,palette,review,outline):
    return add_svg_family(root,glyphs,metrics,cmap,layers,palette,review,outline,
                          'book-mail',prepare,30,4)
