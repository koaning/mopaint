import base64
from pathlib import Path
import anywidget
import traitlets
from io import BytesIO


def base64_to_pil(base64_string):
    """Convert a base64 string to PIL Image"""
    # Remove the data URL prefix if it exists
    from PIL import Image

    if 'base64,' in base64_string:
        base64_string = base64_string.split('base64,')[1]

    # Decode base64 string
    img_data = base64.b64decode(base64_string)

    # Create PIL Image from bytes
    return Image.open(BytesIO(img_data))


def pil_to_base64(img):
    """Convert a PIL Image to base64 string"""
    from io import BytesIO
    import base64
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def create_empty_image(width=500, height=500, background_color=(255, 255, 255, 255)):
    """Create an empty image with the specified dimensions and background color"""
    from PIL import Image
    return Image.new('RGBA', (width, height), background_color)


class Paint(anywidget.AnyWidget):
    """Initialize a Draw widget based on tldraw"""
    _esm = Path(__file__).parent / 'static' / 'draw.js'
    _css = Path(__file__).parent / 'static' / 'styles.css'
    base64 = traitlets.Unicode("").tag(sync=True)
    height = traitlets.Int(500).tag(sync=True)
    width = traitlets.Int(889).tag(sync=True)  # Default to 16:9 aspect ratio with height 500
    store_background = traitlets.Bool(True).tag(sync=True)
    
    def get_pil(self):
        from PIL import Image
        
        # If base64 is empty, return an empty image with the correct dimensions
        if not self.base64:
            return create_empty_image(width=self.width, height=self.height)
        
        # Get the original image
        img = base64_to_pil(self.base64)
        
        # If store_background is True, add a white background
        if self.store_background:
            # Create a new image with white background
            background = Image.new('RGBA', img.size, (255, 255, 255, 255))
            # Paste the original image onto the white background
            background.paste(img, (0, 0), img)
            return background
        
        return img

    def get_base64(self) -> str:
        return pil_to_base64(self.get_pil())