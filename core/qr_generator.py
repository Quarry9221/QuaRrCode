import qrcode
from qrcode.image.svg import SvgImage
from io import BytesIO
from dataclasses import dataclass
from typing import Literal


@dataclass
class QRResult:
    file: BytesIO
    format: str
    caption: str


class QRGenerator:
    @staticmethod
    def generate(
        text: str,
        size: int = 10,
        fg_color: str = "black",
        bg_color: str = "white",
        fmt: Literal["PNG", "SVG"] = "PNG",
    ) -> QRResult:
        """Генерація QR коду"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=size,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        fmt_upper = fmt.upper()
        if fmt_upper == "PNG":
            img = qr.make_image(fill_color=fg_color, back_color=bg_color)
            filename = "qr.png"
        elif fmt_upper == "SVG":
            img = qr.make_image(
                image_factory=SvgImage, fill_color=fg_color, back_color=bg_color
            )
            filename = "qr.svg"
        else:
            raise ValueError(f"Непідтримуваний формат: {fmt}")

        bio = BytesIO()
        bio.name = filename
        img.save(bio)
        bio.seek(0)

        return QRResult(
            file=bio, format=fmt_upper, caption=f"✅ QR код готовий! ({fmt_upper})"
        )
