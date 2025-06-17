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

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from mopaint import Paint
    from mohtml import img, div, tailwind_css

    tailwind_css()
    return Paint, div, img, mo, tailwind_css


@app.cell
def _(Paint, mo):
    widget = mo.ui.anywidget(
        Paint(
            height=550,
            store_background=False,
            show_grid=True,
        )
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
def _():
    return


if __name__ == "__main__":
    app.run()
