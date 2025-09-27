import pytest
from utils import generate_qr_image

@pytest.mark.parametrize("text,fmt", [
    ("hello", "PNG"),
    ("https://example.com", "PNG"),
    ("hello", "SVG"),
    ("https://example.com", "SVG"),
])
def test_generate_qr_image_basic(text, fmt):
    img = generate_qr_image(text, fmt=fmt)
    assert img is not None
    assert hasattr(img, 'read')
    assert img.name.endswith(fmt.lower())

@pytest.mark.parametrize("size,fg,bg", [
    (5, "black", "white"),
    (15, "red", "yellow"),
    (10, "blue", "gray"),
])
def test_generate_qr_image_colors_and_size(size, fg, bg):
    img = generate_qr_image("test", size=size, fg_color=fg, bg_color=bg)
    assert img is not None
    assert hasattr(img, 'read')

# Edge case: empty text
@pytest.mark.parametrize("text", ["", " "])
def test_generate_qr_image_empty(text):
    img = generate_qr_image(text)
    assert img is not None
    assert hasattr(img, 'read')

# Edge case: unsupported format
import pytest

def test_generate_qr_image_unsupported_format():
    with pytest.raises(ValueError):
        generate_qr_image("test", fmt="JPG")
