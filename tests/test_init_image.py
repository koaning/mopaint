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


def test_pil_to_base64_rgb():
    """Test converting RGB PIL image to base64"""
    # Create a test RGB image
    img = Image.new('RGB', (50, 50), color='red')
    
    # Convert to base64
    base64_str = pil_to_base64(img)
    
    # Should start with data URL prefix
    assert base64_str.startswith('data:image/png;base64,')
    
    # Should be a valid base64 string
    assert len(base64_str) > len('data:image/png;base64,')
    
    # Convert back and verify
    recovered_img = base64_to_pil(base64_str)
    assert recovered_img.size == (50, 50)
    # Check a few pixels (might be RGBA after conversion)
    assert recovered_img.getpixel((25, 25))[:3] == (255, 0, 0)


def test_pil_to_base64_rgba():
    """Test converting RGBA PIL image to base64"""
    # Create a test RGBA image with transparency
    img = Image.new('RGBA', (30, 30), color=(0, 255, 0, 128))
    
    # Convert to base64
    base64_str = pil_to_base64(img)
    
    # Should start with data URL prefix
    assert base64_str.startswith('data:image/png;base64,')
    
    # Convert back and verify
    recovered_img = base64_to_pil(base64_str)
    assert recovered_img.size == (30, 30)
    assert recovered_img.mode == 'RGBA'
    assert recovered_img.getpixel((15, 15)) == (0, 255, 0, 128)


def test_base64_to_pil_with_prefix():
    """Test converting base64 with data URL prefix to PIL"""
    # Create image and convert to base64
    original_img = Image.new('RGB', (40, 40), color='blue')
    base64_str = pil_to_base64(original_img)
    
    # Convert back
    recovered_img = base64_to_pil(base64_str)
    
    assert recovered_img.size == (40, 40)
    assert recovered_img.getpixel((20, 20))[:3] == (0, 0, 255)


def test_base64_to_pil_without_prefix():
    """Test converting base64 without data URL prefix to PIL"""
    import base64
    from io import BytesIO
    
    # Create image and get raw base64 without prefix
    original_img = Image.new('RGB', (25, 25), color='yellow')
    buffered = BytesIO()
    original_img.save(buffered, format="PNG")
    raw_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Convert back
    recovered_img = base64_to_pil(raw_base64)
    
    assert recovered_img.size == (25, 25)
    assert recovered_img.getpixel((12, 12))[:3] == (255, 255, 0)


def test_create_empty_image_default():
    """Test creating empty image with default parameters"""
    img = create_empty_image()
    
    assert img.size == (500, 500)
    assert img.mode == 'RGBA'
    assert img.getpixel((250, 250)) == (255, 255, 255, 255)  # White opaque


def test_create_empty_image_custom():
    """Test creating empty image with custom parameters"""
    # Create transparent red image
    img = create_empty_image(width=100, height=200, background_color=(255, 0, 0, 128))
    
    assert img.size == (100, 200)
    assert img.mode == 'RGBA'
    assert img.getpixel((50, 100)) == (255, 0, 0, 128)


def test_create_empty_image_transparent():
    """Test creating fully transparent empty image"""
    img = create_empty_image(width=50, height=50, background_color=(0, 0, 0, 0))
    
    assert img.size == (50, 50)
    assert img.mode == 'RGBA'
    assert img.getpixel((25, 25)) == (0, 0, 0, 0)  # Fully transparent


def test_round_trip_conversion():
    """Test round-trip conversion between PIL and base64"""
    # Create a complex image with gradients
    img = Image.new('RGBA', (60, 60))
    pixels = img.load()
    for x in range(60):
        for y in range(60):
            pixels[x, y] = (x * 4, y * 4, 128, 255)
    
    # Convert to base64 and back
    base64_str = pil_to_base64(img)
    recovered_img = base64_to_pil(base64_str)
    
    # Verify the image is identical
    assert img.size == recovered_img.size
    assert img.mode == recovered_img.mode
    
    # Check a few sample pixels
    assert recovered_img.getpixel((0, 0)) == (0, 0, 128, 255)
    assert recovered_img.getpixel((30, 30)) == (120, 120, 128, 255)
    assert recovered_img.getpixel((59, 59)) == (236, 236, 128, 255)