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

__generated_with = "0.11.31"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from mopaint import Paint
    from mohtml import img
    return Paint, img, mo


@app.cell
def _(Paint, mo):
    widget = mo.ui.anywidget(Paint(width=1000, height=450))
    return (widget,)


@app.cell
def _(widget):
    widget
    return


@app.cell
def _(img, mo, widget):
    mo.hstack([
        img(src=widget.value["base64"]),  # Use base64 representation directly with mohtml
        widget.get_pil()                  # Retreive the Python PIL object instead
    ])
    return


if __name__ == "__main__":
    app.run()
