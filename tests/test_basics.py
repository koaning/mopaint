from mopaint import Paint
import pytest

def test_basics_no_drawn_image():
    """Test behavior when no image is drawn."""
    widget = Paint()
    
    assert widget.get_base64() == ""
    # Should return an empty white image when store_background is True (default)
    img = widget.get_pil()
    assert img.size == (889, 500)  # Default dimensions
    assert img.getpixel((0, 0)) == (255, 255, 255, 255)  # White background
