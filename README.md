# mopaint

MSPaint, for marimo. Borrows heavily from [this project](https://v0.dev/chat/community/microsoft-paint-T58xe0hGtYx).

![CleanShot 2025-03-31 at 11 25 41](https://github.com/user-attachments/assets/3b474757-9a11-4ce0-a1f7-40349e478dd7)

## Demo 

To give this project a spin, check out the interactive [docs](https://koaning.github.io/mopaint/).

## Installation

```bash
uv pip install mopaint
```

## Usage

```python
from mopaint import Paint
import marimo as mo

paint = mo.ui.anywidget(Paint())
paint
```

