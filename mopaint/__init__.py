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
    show_grid : bool, optional
        Whether to show a grid overlay on the canvas. Default is False.
    store_grid : bool, optional
        Whether to include the grid in the exported image. Requires show_grid=True.
        Default is False.
    
    Examples
    --------
    >>> from mopaint import Paint
    >>> # Create widget with empty canvas
    >>> widget = Paint(height=400, width=600)
    >>> widget  # Display the widget
    >>> 
    >>> # Create widget with grid
    >>> widget = Paint(height=400, width=600, show_grid=True)
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
    show_grid = traitlets.Bool(False).tag(sync=True)
    store_grid = traitlets.Bool(False).tag(sync=True)
    
    def __init__(self, height=500, width=889, store_background=True, show_grid=False, store_grid=False):
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
        show_grid : bool, optional
            Whether to show a grid overlay on the canvas. Default is False.
        store_grid : bool, optional
            Whether to include the grid in the exported image. Requires show_grid=True.
            Default is False.
        """
        # Validate grid parameters
        if store_grid and not show_grid:
            raise ValueError("store_grid cannot be True when show_grid is False. "
                           "To include the grid in the output, you must first make it visible with show_grid=True.")
        
        super().__init__()
        self.height = height
        self.width = width
        self.store_background = store_background
        self.show_grid = show_grid
        self.store_grid = store_grid
        self.base64 = ""
    
    @traitlets.observe('store_grid', 'show_grid')
    def _validate_grid_params(self, change):
        """Validate grid parameters when they change."""
        if self.store_grid and not self.show_grid:
            # Reset store_grid to False if show_grid becomes False
            if change['name'] == 'show_grid' and not change['new']:
                self.store_grid = False
            # Prevent setting store_grid to True when show_grid is False
            elif change['name'] == 'store_grid' and change['new']:
                raise ValueError("store_grid cannot be True when show_grid is False. "
                               "To include the grid in the output, you must first make it visible with show_grid=True.")
    
    def get_pil(self):
        """Get the current drawing as a PIL Image.
        
        Returns
        -------
        PIL.Image.Image
            The current drawing as a PIL Image. If no drawing exists, returns an empty
            transparent image with the correct dimensions.
        """
        from PIL import Image
        
        # If base64 is empty, return an empty transparent image with the correct dimensions
        if not self.base64:
            return create_empty_image(width=self.width, height=self.height, background_color=(0, 0, 0, 0))
        
        # Get the image from base64
        return base64_to_pil(self.base64)
    
    def get_base64(self) -> str:
        # Return empty string if no image has been drawn
        if not self.base64:
            return ""
        return pil_to_base64(self.get_pil())