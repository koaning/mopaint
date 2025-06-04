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
    """A paint widget for drawing and sketching in Jupyter notebooks.
    
    This widget provides a simple drawing interface similar to MS Paint, allowing
    users to draw with different tools (brush, thick marker, eraser) and colors.
    The drawing can be exported as a PIL Image or base64 string.
    
    Parameters
    ----------
    height : int, optional
        Height of the drawing canvas in pixels. Default is 500.
    width : int, optional
        Width of the drawing canvas in pixels. Default is 889 (16:9 aspect ratio).
    store_background : bool, optional
        Whether to include a white background when exporting the image. 
        If False, the background will be transparent. Default is True.
    initial_image : PIL.Image.Image, optional
        Initial image to load into the canvas. Must be a PIL Image object.
        If provided, it will be resized to fit the canvas dimensions if necessary.
        Default is None (empty canvas).
    
    Examples
    --------
    >>> from mopaint import Paint
    >>> from PIL import Image
    >>> 
    >>> # Create widget with empty canvas
    >>> widget = Paint(height=400, width=600)
    >>> widget  # Display the widget
    >>> 
    >>> # Create widget with initial image
    >>> img = Image.open('background.png')
    >>> widget = Paint(height=400, width=600, initial_image=img)
    >>> 
    >>> # Get the drawing as PIL Image
    >>> img = widget.get_pil()
    >>> 
    >>> # Get the drawing as base64 string
    >>> base64_str = widget.get_base64()
    """
    _esm = Path(__file__).parent / 'static' / 'draw.js'
    _css = Path(__file__).parent / 'static' / 'styles.css'
    base64 = traitlets.Unicode("").tag(sync=True)
    height = traitlets.Int(500).tag(sync=True)
    width = traitlets.Int(889).tag(sync=True)  # Default to 16:9 aspect ratio with height 500
    store_background = traitlets.Bool(True).tag(sync=True)
    
    def __init__(self, height=500, width=889, store_background=True, initial_image=None):
        """Initialize the Paint widget.
        
        Parameters
        ----------
        height : int, optional
            Height of the drawing canvas in pixels. Default is 500.
        width : int, optional
            Width of the drawing canvas in pixels. Default is 889 (16:9 aspect ratio).
        store_background : bool, optional
            Whether to include a white background when exporting the image. 
            If False, the background will be transparent. Default is True.
        initial_image : PIL.Image.Image or str, optional
            Initial image to load into the canvas. Can be either a PIL Image object
            or a base64 encoded string. If a PIL Image is provided, it will be resized
            to fit the canvas dimensions if necessary. Default is None (empty canvas).
        """
        super().__init__()
        self.height = height
        self.width = width
        self.store_background = store_background
        
        # Handle initial image
        if initial_image is None:
            self.base64 = ""
        elif isinstance(initial_image, str):
            # Assume it's already a base64 string
            self.base64 = initial_image
        else:
            # Assume it's a PIL Image
            from PIL import Image
            
            # Resize image to fit canvas if necessary
            if initial_image.size != (width, height):
                # Create a new image with the canvas size and white background
                canvas = Image.new('RGBA', (width, height), (255, 255, 255, 255))
                
                # Calculate scaling to fit image within canvas while maintaining aspect ratio
                img_ratio = initial_image.width / initial_image.height
                canvas_ratio = width / height
                
                if img_ratio > canvas_ratio:
                    # Image is wider, scale by width
                    new_width = width
                    new_height = int(width / img_ratio)
                else:
                    # Image is taller, scale by height
                    new_height = height
                    new_width = int(height * img_ratio)
                
                # Resize the image
                resized = initial_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Paste the resized image centered on the canvas
                x = (width - new_width) // 2
                y = (height - new_height) // 2
                
                # Handle images with alpha channel
                if resized.mode == 'RGBA':
                    canvas.paste(resized, (x, y), resized)
                else:
                    canvas.paste(resized, (x, y))
                
                self.base64 = pil_to_base64(canvas)
            else:
                self.base64 = pil_to_base64(initial_image)
    
    def get_pil(self):
        from PIL import Image
        
        # If base64 is empty, return an empty image with the correct dimensions
        if not self.base64:
            if self.store_background:
                # Return white background
                return create_empty_image(width=self.width, height=self.height, background_color=(255, 255, 255, 255))
            else:
                # Return transparent background
                return create_empty_image(width=self.width, height=self.height, background_color=(255, 255, 255, 0))
        
        # Get the original image
        img = base64_to_pil(self.base64)
        
        # If store_background is True, add a white background
        if self.store_background:
            # Create a new image with white background
            background = Image.new('RGBA', img.size, (255, 255, 255, 255))
            # Paste the original image onto the white background
            if img.mode == 'RGBA':
                # Use alpha channel as mask for RGBA images
                background.paste(img, (0, 0), img)
            else:
                # No mask needed for RGB images
                background.paste(img, (0, 0))
            return background
        
        return img

    def get_base64(self) -> str:
        # Return empty string if no image has been drawn
        if not self.base64:
            return ""
        return pil_to_base64(self.get_pil())