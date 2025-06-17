# /// script
# requires-python = ">=3.12"
# dependencies = 
#     "anywidget==0.9.18",
#     "marimo",
#     "mohtml==0.1.4",
#     "pillow==11.1.0",
# ]
# ///

import marimo
from PIL import Image
from mopaint import Paint
import marimo as mo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from mopaint import Paint
    from mohtml import img
    return Paint, img, mo


@app.cell
def _(Paint, mo):
    widget = mo.ui.anywidget(Paint(height=450, store_background=True))
    return (widget,)


@app.cell
def _(widget):
    widget
    return


@app.cell
def _(img, widget):
    img(src=widget.get_base64())  # Use base64 representation directly with mohtml
    return


@app.cell
def _(widget):
    widget.get_pil()
    return


@app.cell
def _():
    return


def create_sample_image():
    """Create a sample image for demonstration"""
    # Create a simple gradient image
    img = Image.new('RGB', (400, 300), color='white')
    pixels = img.load()
    
    for x in range(400):
        for y in range(300):
            # Create a gradient effect
            r = min(255, x // 2)
            g = min(255, y // 2)
            b = 128
            pixels[x, y] = (r, g, b)
    
    return img


def demo_basic_widget():
    """Demo of basic paint widget"""
    print("Basic Paint Widget (no initial image):")
    widget = Paint(width=600, height=400)
    return widget


def demo_with_initial_image():
    """Demo of paint widget with initial image"""
    print("Paint Widget with Initial Image:")
    
    # Create or load an image
    img = create_sample_image()
    
    # Create widget with initial image (using the API from user's example)
    widget = Paint(width=1000, height=1000, initial_image=img)
    
    return widget


def demo_with_loaded_image():
    """Demo of paint widget loading an image from file"""
    print("Paint Widget with Loaded Image:")
    
    try:
        # This would be the user's example:
        # img_ = Image.open("/marimo/path/to/png.png")
        
        # For demo, create a test image
        img_ = Image.new('RGBA', (300, 200))
        pixels = img_.load()
        for x in range(300):
            for y in range(200):
                # Create a checkerboard pattern
                if (x // 20 + y // 20) % 2:
                    pixels[x, y] = (255, 0, 0, 255)  # Red
                else:
                    pixels[x, y] = (0, 0, 255, 255)  # Blue
        
        widget = Paint(width=1000, height=1000, initial_image=img_)
        return widget
        
    except Exception as e:
        print(f"Error loading image: {e}")
        return demo_basic_widget()


if __name__ == "__main__":
    print("Mopaint Widget Demo")
    print("=" * 40)
    
    # Demo 1: Basic widget
    widget1 = demo_basic_widget()
    print(f"Widget created: {widget1.width}x{widget1.height}")
    
    print()
    
    # Demo 2: Widget with initial image
    widget2 = demo_with_initial_image()
    print(f"Widget with initial image: {widget2.width}x{widget2.height}")
    print(f"Has initial image: {widget2.base64 != ''}")
    
    print()
    
    # Demo 3: Widget with loaded image
    widget3 = demo_with_loaded_image()
    print(f"Widget with loaded image: {widget3.width}x{widget3.height}")
    print(f"Has initial image: {widget3.base64 != ''}")
    
    print()
    print("Demo completed successfully!")
    
    # Save example images for testing
    print("Saving example images...")
    sample_img = create_sample_image()
    sample_img.save('sample_gradient.png')
    print("Saved sample_gradient.png")
    
    # Example of getting the image back
    result_img = widget2.get_pil()
    result_img.save('widget_output.png')
    print("Saved widget_output.png")
