"""Image helpers: validation limits and WebP optimisation for uploads."""

from io import BytesIO
from pathlib import PurePosixPath

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageOps

MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8 MB raw upload limit
MAX_WIDTH = 1600
WEBP_QUALITY = 82


def validate_image_size(file):
    if file.size > MAX_UPLOAD_BYTES:
        raise ValidationError(
            f"Image is too large ({file.size / 1024 / 1024:.1f} MB). "
            f"Maximum is {MAX_UPLOAD_BYTES // 1024 // 1024} MB."
        )


def to_webp(source, name, max_width=MAX_WIDTH, quality=WEBP_QUALITY):
    """Return (new_name, ContentFile) for a resized WebP version of `source`."""
    with Image.open(source) as img:
        img = ImageOps.exif_transpose(img)
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, round(img.height * ratio)), Image.LANCZOS)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.mode else "RGB")
        buffer = BytesIO()
        img.save(buffer, "WEBP", quality=quality, method=6)
    stem = PurePosixPath(name).stem
    return f"{stem}.webp", ContentFile(buffer.getvalue())
