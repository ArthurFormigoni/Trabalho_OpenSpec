from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

try:
    import pillow_avif  # noqa: F401
except ImportError:  # pragma: no cover
    pillow_avif = None

MAX_OUTPUT_BYTES = 1_048_576
MIN_ASPECT_RATIO = 0.5


class ImageValidationError(ValueError):
    pass


class ImageEncodingError(RuntimeError):
    pass


def _encode(image: Image.Image, quality: int) -> bytes:
    output = BytesIO()
    try:
        image.save(output, format="AVIF", quality=quality, speed=8)
    except (KeyError, OSError) as exc:
        raise ImageEncodingError("O ambiente não possui suporte para conversão AVIF") from exc
    return output.getvalue()


def process_image(source: bytes) -> tuple[int, int, bytes]:
    try:
        with Image.open(BytesIO(source)) as opened:
            opened.verify()
        with Image.open(BytesIO(source)) as opened:
            width, height = opened.size
            if width <= 0 or height <= 0:
                raise ImageValidationError("A imagem não possui dimensões válidas")
            aspect_ratio = min(width, height) / max(width, height)
            if aspect_ratio < MIN_ASPECT_RATIO:
                raise ImageValidationError("A proporção da imagem não é adequada para o mosaico da galeria")
            image = ImageOps.exif_transpose(opened).convert("RGBA" if "A" in opened.getbands() else "RGB")
            image.load()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        if isinstance(exc, ImageValidationError):
            raise
        raise ImageValidationError("O arquivo enviado não é uma imagem válida") from exc

    for quality in (80, 65, 50, 35, 25, 15):
        encoded = _encode(image, quality)
        if len(encoded) <= MAX_OUTPUT_BYTES:
            return width, height, encoded

    current = image
    while max(current.size) > 256:
        next_size = (max(1, int(current.width * 0.8)), max(1, int(current.height * 0.8)))
        current = current.resize(next_size, Image.Resampling.LANCZOS)
        encoded = _encode(current, 20)
        if len(encoded) <= MAX_OUTPUT_BYTES:
            return current.width, current.height, encoded

    raise ImageEncodingError("Não foi possível comprimir a imagem para 1 MiB")

