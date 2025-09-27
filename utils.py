import qrcode
from qrcode.image.svg import SvgImage
from io import BytesIO
from typing import Literal

def generate_qr_image(
    text: str,
    size: int = 10,
    fg_color: str = "black",
    bg_color: str = "white",
    fmt: Literal["PNG", "SVG"] = "PNG"
) -> BytesIO:
    """
    Генерує QR-код з тексту.
    Підтримує PNG та SVG, кольори та розмір.
    """
    qr = qrcode.QRCode(box_size=size, border=4)
    qr.add_data(text)
    qr.make(fit=True)

    fmt_upper = fmt.upper()
    if fmt_upper == "PNG":
        img = qr.make_image(fill_color=fg_color, back_color=bg_color)
        filename = "qr.png"
    elif fmt_upper == "SVG":
        img = qr.make_image(image_factory=SvgImage, fill_color=fg_color, back_color=bg_color)
        filename = "qr.svg"
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    bio = BytesIO()
    bio.name = filename
    img.save(bio)
    bio.seek(0)
    return bio
