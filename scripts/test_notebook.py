import marimo

__generated_with = "0.12.8"
app = marimo.App(width="columns")


@app.cell(column=0)
def _(widget1, widget2, widget3):
    def test_transparent_grid():
        r, g, b, a = widget1.get_pil().resize((1, 1)).getpixel((0, 0))

        assert r == 212
        assert g == 212
        assert b == 212
        assert a == 12

    def test_white_bg():
        r, g, b, a = widget2.get_pil().resize((1, 1)).getpixel((0, 0))
        assert r == 255
        assert g == 255
        assert b == 255
        assert a == 255

    def test_white_bg_grid():
        r, g, b, a = widget3.get_pil().resize((1, 1)).getpixel((0, 0))
        assert r == 253
        assert g == 253
        assert b == 253
        assert a == 255
    return test_transparent_grid, test_white_bg, test_white_bg_grid


@app.cell
def _():
    import marimo as mo
    from mopaint import Paint
    from mohtml import img, div, tailwind_css

    tailwind_css()
    return Paint, div, img, mo, tailwind_css


@app.cell
def _():
    return


@app.cell(column=1)
def _(Paint, div, mo):
    widget1 = mo.ui.anywidget(
        Paint(
            height=550,
            store_background=False,
            show_grid=True,
            store_grid=True
        )
    )
    div(widget1, id="yo")
    return (widget1,)


@app.cell
def _(widget1):
    widget1.get_pil().resize((1, 1)).getpixel((0, 0))
    return


@app.cell
def _(div, img, widget1):
    div(
        img(src=widget1.get_base64()), klass="bg-gray-200 p-4"
    )
    return


@app.cell
def _():
    return


@app.cell(column=2)
def _(Paint, mo):
    widget2 = mo.ui.anywidget(
        Paint(
            height=550,
            store_background=True,
            show_grid=True,
            store_grid=False
        )
    )
    widget2
    return (widget2,)


@app.cell
def _(widget2):
    widget2.get_pil().resize((1, 1)).getpixel((0, 0))
    return


@app.cell
def _(div, img, widget2):
    div(
        img(src=widget2.get_base64()), klass="bg-gray-200 p-4"
    )
    return


@app.cell(column=3)
def _(Paint, mo):
    widget3 = mo.ui.anywidget(
        Paint(
            height=550,
            store_background=True,
            show_grid=True,
            store_grid=True
        )
    )
    widget3
    return (widget3,)


@app.cell
def _(widget3):
    widget3.get_pil().resize((1, 1)).getpixel((0, 0))
    return


@app.cell
def _(div, img, widget3):
    div(
        img(src=widget3.get_base64()), klass="bg-gray-200 p-4"
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
