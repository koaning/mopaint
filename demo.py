# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "anthropic==0.49.0",
#     "anywidget==0.9.18",
#     "marimo",
#     "mohtml==0.1.4",
#     "pillow==11.1.0",
# ]
# ///

import marimo

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
    widget = mo.ui.anywidget(Paint(height=450, store_background=True, background_color="#000000"))
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


if __name__ == "__main__":
    app.run()
