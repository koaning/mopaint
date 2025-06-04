import pytest
from PIL import Image
from mopaint import Paint, base64_to_pil, pil_to_base64, create_empty_image


def test_init_with_pil_image():
    """Test initializing Paint widget with a PIL image"""
    # Create a test image
    test_img = Image.new('RGB', (200, 100), color='red')
    
    # Create widget with the image
    widget = Paint(height=400, width=600, initial_image=test_img)
    
    # The widget should have a base64 representation
    assert widget.base64 != ""
    
    # Get the resulting image
    result_img = widget.get_pil()
    
    # Check dimensions match the widget size
    assert result_img.size == (600, 400)
    
    # The image should be centered on a white background
    # Check that corners are white (background)
    assert result_img.getpixel((0, 0))[:3] == (255, 255, 255)
    assert result_img.getpixel((599, 399))[:3] == (255, 255, 255)


def test_init_with_base64_string():
    """Test initializing Paint widget with a base64 string"""
    # Create a test image and convert to base64
    test_img = Image.new('RGB', (100, 100), color='blue')
    from mopaint import pil_to_base64
    base64_str = pil_to_base64(test_img)
    
    # Create widget with the base64 string
    widget = Paint(height=200, width=200, initial_image=base64_str)
    
    # The widget should have the same base64
    assert widget.base64 == base64_str


def test_init_with_exact_size_image():
    """Test initializing with an image that matches canvas dimensions"""
    # Create image with exact dimensions
    test_img = Image.new('RGB', (500, 300), color='green')
    
    # Create widget with matching dimensions
    widget = Paint(height=300, width=500, initial_image=test_img)
    
    # Get the resulting image
    result_img = widget.get_pil()
    
    # Should be the same size
    assert result_img.size == (500, 300)


def test_init_with_none():
    """Test initializing with no initial image"""
    widget = Paint(height=300, width=400)
    
    # Should have empty base64
    assert widget.base64 == ""
    
    # Should create an empty white image
    img = widget.get_pil()
    assert img.size == (400, 300)