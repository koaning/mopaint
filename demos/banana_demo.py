# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "anywidget==0.9.18",
#     "marimo",
#     "google-genai",
#     "mohtml==0.1.4",
#     "pillow==11.3.0",
#     "python-dotenv==1.1.1",
#     "replicate==1.0.7",
# ]
# ///

import marimo

__generated_with = "0.15.5"
app = marimo.App(width="columns")


@app.cell(column=0)
def _(mo):
    mo.md(r"""## Draw""")
    return


@app.cell
def _(Image):
    init_img = Image.open("dog.png")
    return


@app.cell
def _(Paint, mo):
    widget = mo.ui.anywidget(
        Paint(init_image="https://i.insider.com/5df14d0ee94e860668396b82?width=700", height=700)
    )
    return (widget,)


@app.cell
def _(widget):
    widget
    return


@app.cell
def _():
    import marimo as mo
    from mopaint import Paint
    from mohtml import img, div, tailwind_css

    tailwind_css()
    return Paint, mo


@app.cell
def _(widget):
    widget.value
    return


@app.cell
def _():
    from PIL import Image, ImageDraw
    return (Image,)


@app.cell(column=1, hide_code=True)
def _(mo):
    run_btn = mo.ui.run_button(label="generate image")
    run_btn
    return (run_btn,)


@app.cell(hide_code=True)
def _(mo):
    prompt_input = mo.ui.text_area(
        value="Make this image loop hyper realistic, but keep the background transparant, like a png.",
        label="prompt",
        full_width=True,
    )
    prompt_input
    return (prompt_input,)


@app.cell
def _(image):
    image
    return


@app.cell(hide_code=True)
def _(Image, mo, prompt_input, run_btn, widget):
    from google import genai
    from google.genai import types
    from io import BytesIO
    from dotenv import load_dotenv
    import os

    load_dotenv(".env")

    mo.stop(not run_btn.value)

    client = genai.Client()

    response = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=[prompt_input.value, widget.get_pil()],
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save("generated_image.png")
    return (image,)


@app.cell
def _():
    return


@app.cell(column=2)
def _(mo):
    bg_btn = mo.ui.run_button(label="remove background")
    bg_btn
    return (bg_btn,)


@app.cell
def _(mo, output):
    mo.image(src=output.url)
    return


@app.cell
def _():
    import replicate
    return (replicate,)


@app.cell
def _():
    import io
    import base64


    def pil_to_data_uri(image, format="JPEG"):
        img_bytes = io.BytesIO()
        image.save(img_bytes, format=format)
        b64 = base64.b64encode(img_bytes.getvalue()).decode()
        return f"data:image/{format.lower()};base64,{b64}"
    return (pil_to_data_uri,)


@app.cell
def _(bg_btn, image, mo, pil_to_data_uri, replicate):
    mo.stop(not bg_btn.value)

    output = replicate.run(
        "851-labs/background-remover:a029dff38972b5fda4ec5d75d7d1cd25aeff621d2cf4946a41055d7db66b80bc",
        input={"image": pil_to_data_uri(image)},
    )

    print(output.url)
    return (output,)


@app.cell
def _():
    return


@app.cell(column=4)
def _():
    return


if __name__ == "__main__":
    app.run()
