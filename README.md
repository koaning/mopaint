# mopaint

MSPaint, for marimo. Borrows heavily from [this project](https://v0.dev/chat/community/microsoft-paint-T58xe0hGtYx).

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

