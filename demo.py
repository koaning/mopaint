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

__generated_with = "0.15.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from mopaint import Paint
    from mohtml import img, div, tailwind_css

    tailwind_css()
    return Paint, div, img, mo


@app.cell
def _(Paint, mo):
    widget = mo.ui.anywidget(
        Paint(init_image="https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/025.png", height=700)
    )
    return (widget,)


@app.cell
def _(widget):
    widget
    return


@app.cell
def _(widget):
    widget.value
    return


@app.cell
def _(div, img, widget):
    div(
        img(src=widget.get_base64()), klass="bg-gray-200 p-4"
    )  # Use base64 representation directly with mohtml
    return


@app.cell
def _(widget):
    widget.get_pil()
    return


@app.cell
def _(Paint, mo):
    # Demo: Create a simple test image to use as initial image
    from PIL import Image, ImageDraw

    # Create a simple test image
    test_img = Image.new('RGBA', (200, 150), (255, 255, 255, 255))
    draw = ImageDraw.Draw(test_img)
    draw.rectangle([10, 10, 190, 140], fill=(100, 150, 255, 255), outline=(0, 0, 0, 255))
    draw.text((20, 60), "Initial Image", fill=(0, 0, 0, 255))

    # Create widget with initial image
    widget_with_init = mo.ui.anywidget(Paint(height=400, init_image=test_img))
    return (widget_with_init,)


@app.cell
def _(widget_with_init):
    widget_with_init
    return


@app.cell
def _(Paint, mo):
    # Demo: Load image from URL (commented out as it requires internet)
    # widget_from_url = mo.ui.anywidget(Paint(
    #     height=300, 
    #     init_image="https://picsum.photos/300/200"
    # ))

    # Demo: Create widget with base64 image (1x1 red pixel)
    red_pixel_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    widget_from_base64 = mo.ui.anywidget(Paint(init_image=red_pixel_base64, height=100))
    return (widget_from_base64,)


@app.cell
def _(widget_from_base64):
    widget_from_base64
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
