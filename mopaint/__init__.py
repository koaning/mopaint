import base64
from pathlib import Path
import anywidget
import traitlets
from io import BytesIO
from typing import Union
import urllib.request
import urllib.parse


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


def input_to_pil(input_data: Union[str, Path, 'Image.Image', bytes, None]) -> 'Image.Image':
    """Convert various input types to PIL Image.
    
    Parameters
    ----------
    input_data : str, Path, PIL.Image.Image, bytes, or None
        The input data to convert. Can be:
        - PIL Image object (returned as-is)
        - File path (string or Path object)
        - URL (string starting with http:// or https://)
        - Base64 encoded string (with or without data URL prefix)
        - Raw image bytes
        - None (returns None)
    
    Returns
    -------
    PIL.Image.Image or None
        The converted PIL Image, or None if input_data is None
        
    Raises
    ------
    ValueError
        If the input cannot be converted to a PIL Image
    FileNotFoundError
        If a file path is provided but the file doesn't exist
    urllib.error.URLError
        If a URL is provided but cannot be fetched
    """
    from PIL import Image
    
    if input_data is None:
        return None
        
    # If it's already a PIL Image, return as-is
    if hasattr(input_data, 'mode') and hasattr(input_data, 'size'):
        return input_data
    
    # Handle string inputs
    if isinstance(input_data, (str, Path)):
        input_str = str(input_data)
        
        # Check if it's a URL
        if input_str.startswith(('http://', 'https://')):
            try:
                with urllib.request.urlopen(input_str, timeout=10) as response:
                    img_data = response.read()
                    return Image.open(BytesIO(img_data))
            except Exception as e:
                raise ValueError(f"Failed to load image from URL '{input_str}': {e}")
        
        # Check if it's a base64 string (with or without data URL prefix)
        elif 'base64,' in input_str or (len(input_str) > 50 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in input_str.replace('\n', '').replace('\r', ''))):
            try:
                return base64_to_pil(input_str)
            except Exception as e:
                # If base64 decoding fails, treat as file path
                pass
        
        # Treat as file path
        file_path = Path(input_str)
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        try:
            return Image.open(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load image from file '{file_path}': {e}")
    
    # Handle bytes input
    if isinstance(input_data, bytes):
        try:
            return Image.open(BytesIO(input_data))
        except Exception as e:
            raise ValueError(f"Failed to load image from bytes data: {e}")
    
    raise ValueError(f"Unsupported input type: {type(input_data)}. Expected PIL Image, file path, URL, base64 string, or bytes.")


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
    init_image : str, Path, PIL.Image.Image, bytes, or None, optional
        Initial image to load into the canvas. Can be:
        - PIL Image object
        - File path (string or Path object)
        - URL (string starting with http:// or https://)
        - Base64 encoded string (with or without data URL prefix)
        - Raw image bytes
        - None (empty canvas). Default is None.
    
    Examples
    --------
    >>> from mopaint import Paint
    >>> from PIL import Image
    >>> 
    >>> # Create widget with empty canvas
    >>> widget = Paint(height=400, width=600)
    >>> widget  # Display the widget
    >>> 
    >>> # Create widget with grid
    >>> widget = Paint(height=400, width=600, show_grid=True)
    >>> 
    >>> # Create widget with initial image from file
    >>> widget = Paint(init_image="path/to/image.png")
    >>> 
    >>> # Create widget with initial image from URL
    >>> widget = Paint(init_image="https://example.com/image.jpg")
    >>> 
    >>> # Create widget with initial PIL Image
    >>> img = Image.open("image.png")
    >>> widget = Paint(init_image=img)
    >>> 
    >>> # Create widget with large image scaled to fit height=400
    >>> large_img = Image.open("large_image.png")  # e.g., 4000x2000
    >>> widget = Paint(init_image=large_img, height=400)  # Canvas: 800x400
    >>> 
    >>> # Create widget with initial base64 image
    >>> widget = Paint(init_image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
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
    
    def __init__(self, height=500, width=889, store_background=True, show_grid=False, store_grid=False, init_image=None):
        """Initialize the Paint widget.
        
        Parameters
        ----------
        height : int, optional
            Height of the drawing canvas in pixels. Default is 500.
            When used with init_image, scales the image to fit this height while preserving aspect ratio.
        width : int, optional
            Width of the drawing canvas in pixels. Default is 889 (16:9 aspect ratio).
            Cannot be used together with init_image (width is calculated from height and aspect ratio).
        store_background : bool, optional
            Whether to include a white background when exporting the image. 
            If False, the background will be transparent. Default is True.
        show_grid : bool, optional
            Whether to show a grid overlay on the canvas. Default is False.
        store_grid : bool, optional
            Whether to include the grid in the exported image. Requires show_grid=True.
            Default is False.
        init_image : str, Path, PIL.Image.Image, bytes, or None, optional
            Initial image to load into the canvas. When provided, canvas dimensions
            are automatically calculated based on the image aspect ratio. If height
            is specified, the image is scaled to fit that height. Can be:
            - PIL Image object
            - File path (string or Path object)
            - URL (string starting with http:// or https://)
            - Base64 encoded string (with or without data URL prefix)
            - Raw image bytes
            - None (empty canvas). Default is None.
        
        Raises
        ------
        ValueError
            If init_image is provided along with explicit width parameter.
        """
        # Check for defaults to determine if user explicitly provided width/height
        import inspect
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        
        # Get the signature to check which parameters were explicitly passed
        sig = inspect.signature(self.__init__)
        bound_args = sig.bind_partial(height, width, store_background, show_grid, store_grid, init_image)
        
        # Check if user provided explicit width when init_image is present
        user_provided_width = width != 889  # Default width
        user_provided_height = height != 500  # Default height
        
        if init_image is not None and user_provided_width:
            raise ValueError(
                "Cannot specify both init_image and explicit width parameter. "
                "Canvas width is automatically calculated from image aspect ratio and height. "
                f"Received: width={width}, init_image={type(init_image).__name__}"
            )
        
        # Validate grid parameters
        if store_grid and not show_grid:
            raise ValueError("store_grid cannot be True when show_grid is False. "
                           "To include the grid in the output, you must first make it visible with show_grid=True.")
        
        super().__init__()
        
        # Handle initial image and set dimensions
        if init_image is not None:
            pil_image = input_to_pil(init_image)
            if pil_image is not None:
                # Calculate canvas dimensions based on image aspect ratio
                image_width, image_height = pil_image.size
                aspect_ratio = image_width / image_height
                
                if user_provided_height:
                    # User specified height, calculate width from aspect ratio
                    self.height = height
                    self.width = int(height * aspect_ratio)
                else:
                    # No height specified, use original image dimensions
                    self.width = image_width
                    self.height = image_height
                
                base64_with_prefix = pil_to_base64(pil_image)
                self.base64 = base64_with_prefix.split(',')[1]  # Remove data URL prefix
            else:
                self.width = width
                self.height = height
                self.base64 = ""
        else:
            self.width = width
            self.height = height
            self.base64 = ""
        
        self.store_background = store_background
        self.show_grid = show_grid
        self.store_grid = store_grid
    
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