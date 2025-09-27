import pytest
from io import BytesIO
from utils import generate_qr_image

def test_generate_qr_image_returns_bytesio():
    text = "Hello QR"
    result = generate_qr_image(text)

    assert isinstance(result, BytesIO)
    assert result.name == "qr.png"
    assert result.getbuffer().nbytes > 0  # файл не пустий

def test_generate_qr_image_different_inputs():
    inputs = ["simple text", "1234567890", "https://example.com", ""]
    results = [generate_qr_image(text) for text in inputs]

    # Усі повертають BytesIO
    assert all(isinstance(r, BytesIO) for r in results)
    # Файли різні за розміром
    sizes = [r.getbuffer().nbytes for r in results]
    assert len(set(sizes)) == len(sizes)

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