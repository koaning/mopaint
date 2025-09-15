import pytest
from unittest.mock import patch, Mock
from io import BytesIO
from pathlib import Path
import tempfile
import os

from PIL import Image
from mopaint import Paint, input_to_pil, pil_to_base64


def create_test_image(width=100, height=100, color=(255, 0, 0, 255)):
    """Create a test PIL Image."""
    return Image.new('RGBA', (width, height), color)


def create_test_image_bytes():
    """Create test image as bytes."""
    img = create_test_image()
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def test_input_to_pil_with_none():
    """Test input_to_pil with None input."""
    result = input_to_pil(None)
    assert result is None


def test_input_to_pil_with_pil_image():
    """Test input_to_pil with PIL Image input."""
    img = create_test_image()
    result = input_to_pil(img)
    assert result is img  # Should return the same object
    assert result.size == (100, 100)


def test_input_to_pil_with_bytes():
    """Test input_to_pil with bytes input."""
    img_bytes = create_test_image_bytes()
    result = input_to_pil(img_bytes)
    assert isinstance(result, Image.Image)
    assert result.size == (100, 100)


def test_input_to_pil_with_file_path():
    """Test input_to_pil with file path input."""
    # Create a temporary image file
    img = create_test_image()
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img.save(f.name)
        temp_path = f.name
    
    try:
        # Test with string path
        result = input_to_pil(temp_path)
        assert isinstance(result, Image.Image)
        assert result.size == (100, 100)
        
        # Test with Path object
        result = input_to_pil(Path(temp_path))
        assert isinstance(result, Image.Image)
        assert result.size == (100, 100)
    finally:
        os.unlink(temp_path)


def test_input_to_pil_with_nonexistent_file():
    """Test input_to_pil with non-existent file path."""
    with pytest.raises(FileNotFoundError) as exc_info:
        input_to_pil("/path/that/does/not/exist.png")
    assert "Image file not found" in str(exc_info.value)


def test_input_to_pil_with_base64_string():
    """Test input_to_pil with base64 string input."""
    img = create_test_image()
    base64_str = pil_to_base64(img)
    
    # Test with data URL prefix
    result = input_to_pil(base64_str)
    assert isinstance(result, Image.Image)
    assert result.size == (100, 100)
    
    # Test without data URL prefix
    base64_only = base64_str.split(',')[1]
    result = input_to_pil(base64_only)
    assert isinstance(result, Image.Image)
    assert result.size == (100, 100)


def test_input_to_pil_with_invalid_base64():
    """Test input_to_pil with invalid base64 string that looks like a filename."""
    with pytest.raises(FileNotFoundError):
        input_to_pil("this_is_invalid_base64_but_looks_like_filename.png")


@patch('urllib.request.urlopen')
def test_input_to_pil_with_url(mock_urlopen):
    """Test input_to_pil with URL input."""
    # Mock the URL response
    img_bytes = create_test_image_bytes()
    mock_response = Mock()
    mock_response.read.return_value = img_bytes
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)
    mock_urlopen.return_value = mock_response
    
    result = input_to_pil("https://example.com/image.png")
    assert isinstance(result, Image.Image)
    assert result.size == (100, 100)
    mock_urlopen.assert_called_once_with("https://example.com/image.png", timeout=10)


@patch('urllib.request.urlopen')
def test_input_to_pil_with_invalid_url(mock_urlopen):
    """Test input_to_pil with URL that fails to load."""
    mock_urlopen.side_effect = Exception("Network error")
    
    with pytest.raises(ValueError) as exc_info:
        input_to_pil("https://invalid.url/image.png")
    assert "Failed to load image from URL" in str(exc_info.value)


def test_input_to_pil_with_invalid_bytes():
    """Test input_to_pil with invalid bytes data."""
    invalid_bytes = b"not an image"
    with pytest.raises(ValueError) as exc_info:
        input_to_pil(invalid_bytes)
    assert "Failed to load image from bytes data" in str(exc_info.value)


def test_input_to_pil_with_unsupported_type():
    """Test input_to_pil with unsupported input type."""
    with pytest.raises(ValueError) as exc_info:
        input_to_pil(123)  # Integer is not supported
    assert "Unsupported input type" in str(exc_info.value)


def test_paint_with_init_image_pil():
    """Test Paint widget initialization with PIL Image."""
    img = create_test_image()
    widget = Paint(init_image=img)
    
    # The widget should have base64 set
    assert widget.base64 != ""
    
    # The base64 should be valid
    reconstructed = widget.get_pil()
    assert reconstructed.size == img.size


def test_paint_with_init_image_file():
    """Test Paint widget initialization with file path."""
    # Create a temporary image file
    img = create_test_image()
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        img.save(f.name)
        temp_path = f.name
    
    try:
        widget = Paint(init_image=temp_path)
        assert widget.base64 != ""
        
        reconstructed = widget.get_pil()
        assert reconstructed.size == img.size
    finally:
        os.unlink(temp_path)


def test_paint_with_init_image_base64():
    """Test Paint widget initialization with base64 string."""
    img = create_test_image()
    base64_str = pil_to_base64(img)
    
    widget = Paint(init_image=base64_str)
    assert widget.base64 != ""
    
    reconstructed = widget.get_pil()
    assert reconstructed.size == img.size


@patch('urllib.request.urlopen')
def test_paint_with_init_image_url(mock_urlopen):
    """Test Paint widget initialization with URL."""
    # Mock the URL response
    img_bytes = create_test_image_bytes()
    mock_response = Mock()
    mock_response.read.return_value = img_bytes
    mock_response.__enter__ = Mock(return_value=mock_response)
    mock_response.__exit__ = Mock(return_value=None)
    mock_urlopen.return_value = mock_response
    
    widget = Paint(init_image="https://example.com/image.png")
    assert widget.base64 != ""
    
    reconstructed = widget.get_pil()
    assert reconstructed.size == (100, 100)


def test_paint_with_init_image_none():
    """Test Paint widget initialization with None init_image (default behavior)."""
    widget = Paint(init_image=None)
    assert widget.base64 == ""
    
    # get_pil should return empty transparent image
    result = widget.get_pil()
    assert result.size == (889, 500)  # Default dimensions


def test_paint_with_invalid_init_image():
    """Test Paint widget initialization with invalid init_image."""
    with pytest.raises(FileNotFoundError):
        Paint(init_image="/path/that/does/not/exist.png")


def test_paint_init_image_with_grid_parameters():
    """Test Paint widget initialization with init_image and grid parameters."""
    img = create_test_image()
    widget = Paint(init_image=img, show_grid=True, store_grid=True)
    
    assert widget.base64 != ""
    assert widget.show_grid is True
    assert widget.store_grid is True
    
    reconstructed = widget.get_pil()
    assert reconstructed.size == img.size


def test_paint_init_image_with_explicit_width_only_raises_error():
    """Test that providing both init_image and explicit width raises ValueError."""
    img = create_test_image(width=200, height=100)
    
    with pytest.raises(ValueError) as exc_info:
        Paint(init_image=img, width=500)
    
    error_msg = str(exc_info.value)
    assert "Cannot specify both init_image and explicit width parameter" in error_msg
    assert "width=500" in error_msg


def test_paint_init_image_with_explicit_height_works():
    """Test that providing both init_image and explicit height works (scales image)."""
    img = create_test_image(width=200, height=100)  # 2:1 aspect ratio
    
    # Should work and scale the image to fit height=300, width should be 600
    widget = Paint(init_image=img, height=300)
    
    assert widget.height == 300
    assert widget.width == 600  # 300 * (200/100) = 600
    assert widget.base64 != ""


def test_paint_init_image_with_explicit_width_raises_error():
    """Test that providing both init_image and explicit width raises ValueError (even with height)."""
    img = create_test_image(width=200, height=100)
    
    with pytest.raises(ValueError) as exc_info:
        Paint(init_image=img, width=500, height=300)
    
    error_msg = str(exc_info.value)
    assert "Cannot specify both init_image and explicit width parameter" in error_msg
    assert "width=500" in error_msg


def test_paint_init_image_auto_sets_dimensions():
    """Test that init_image automatically sets canvas dimensions to match image."""
    img = create_test_image(width=300, height=200)
    widget = Paint(init_image=img)
    
    # Canvas dimensions should match image dimensions
    assert widget.width == 300
    assert widget.height == 200
    
    # Base64 should be set
    assert widget.base64 != ""
    
    # get_pil should return image with correct dimensions
    reconstructed = widget.get_pil()
    assert reconstructed.size == (300, 200)


def test_paint_init_image_with_defaults_works():
    """Test that init_image works with default width/height (no explicit values)."""
    img = create_test_image(width=150, height=75)
    
    # This should work fine - no explicit width/height provided
    widget = Paint(init_image=img)
    
    # Dimensions should match image, not defaults
    assert widget.width == 150
    assert widget.height == 75
    assert widget.base64 != ""


def test_paint_without_init_image_uses_provided_dimensions():
    """Test that without init_image, explicit width/height are used normally."""
    widget = Paint(width=400, height=300)
    
    assert widget.width == 400
    assert widget.height == 300
    assert widget.base64 == ""  # No image loaded


def test_paint_with_exact_size_image():
    """Test that canvas dimensions exactly match image dimensions with no scaling."""
    # Create a specific size image
    test_width, test_height = 123, 456
    img = create_test_image(width=test_width, height=test_height)
    
    widget = Paint(init_image=img)
    
    # Verify exact dimension matching
    assert widget.width == test_width
    assert widget.height == test_height
    
    # Verify image is loaded
    assert widget.base64 != ""
    
    # Verify reconstructed image has exact same dimensions
    reconstructed = widget.get_pil()
    assert reconstructed.size == (test_width, test_height)


def test_paint_init_image_scaled_height_preserves_aspect_ratio():
    """Test that scaling with height preserves aspect ratio correctly."""
    # Create image with 3:2 aspect ratio
    img = create_test_image(width=300, height=200)
    
    # Scale to height 100
    widget = Paint(init_image=img, height=100)
    
    # Width should be 150 (100 * 3/2 = 150)
    assert widget.height == 100
    assert widget.width == 150
    assert widget.base64 != ""


def test_paint_init_image_large_image_scaled_down():
    """Test that a large image can be scaled down to fit screen."""
    # Create a very large image
    img = create_test_image(width=4000, height=2000)  # 2:1 aspect ratio
    
    # Scale down to height 400
    widget = Paint(init_image=img, height=400)
    
    # Width should be 800 (400 * 2 = 800)
    assert widget.height == 400
    assert widget.width == 800
    assert widget.base64 != ""


def test_paint_init_image_tall_image_handling():
    """Test handling of very tall (portrait) images."""
    # Create a tall image (portrait orientation)
    img = create_test_image(width=100, height=400)  # 1:4 aspect ratio
    
    # Scale to height 200
    widget = Paint(init_image=img, height=200)
    
    # Width should be 50 (200 * 1/4 = 50)
    assert widget.height == 200
    assert widget.width == 50
    assert widget.base64 != ""