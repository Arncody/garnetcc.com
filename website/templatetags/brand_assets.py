"""Geometry for uploaded footer brand assets."""

from hashlib import sha256

from django import template
from django.core.cache import cache
from PIL import Image

register = template.Library()


def _horizontal_padding(logo):
    try:
        with logo.storage.open(logo.name, "rb") as source, Image.open(source) as image:
            if "A" not in image.getbands() and "transparency" not in image.info:
                return (0, 0)
            image.thumbnail((512, 512))
            alpha = image.convert("RGBA").getchannel("A")
            bounds = alpha.point([0] * 17 + [255] * 239).getbbox()
            if bounds:
                left, _, right, _ = bounds
                return left / image.width, (image.width - right) / image.width
    except (OSError, ValueError, Image.DecompressionBombError):
        pass
    return (0, 0)


@register.simple_tag
def footer_wordmark_offset(logo, is_en):
    """Return a percentage offset toward the visible wordmark's leading edge."""
    if not logo:
        return "0%"
    # Uploaded replacements get a new storage name. Expiry also covers same-name replacements.
    digest = sha256(logo.name.encode()).hexdigest()
    left, right = cache.get_or_set(f"footer-wordmark-padding:{digest}", lambda: _horizontal_padding(logo), 3600)
    return f"{(-left if is_en else right) * 100:.4f}%"
