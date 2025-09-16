# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MoPaint is an MSPaint-like drawing widget for marimo notebooks. It bridges Python and TypeScript/React using AnyWidget to provide an interactive painting interface.

## Key Architecture

The project has a hybrid architecture:
- **Python backend** (`mopaint/__init__.py`): Widget class inheriting from `anywidget.AnyWidget`, handles image conversion and configuration
- **TypeScript frontend** (`js/draw/widget.tsx`): React component implementing the paint interface with canvas, tools, and color palette
- **Build system**: Uses esbuild to compile TypeScript/React into static assets stored in `mopaint/static/`

The widget communicates between Python and JavaScript using AnyWidget's traitlets system. The frontend exports drawings as base64 images that Python converts to PIL Images.

## Essential Commands

### Development
```bash
# Install all dependencies (Python and JavaScript)
make install

# Build JavaScript assets (required after frontend changes)
make js
# or directly:
npm run build-draw

# Development mode with hot reloading for frontend changes
make dev
# or directly:
npm run dev-draw

# Clean build artifacts
make clean
```

### Testing
```bash
# Run all tests
pytest

# Run with uv
uv run pytest

# Run specific test
python -m pytest tests/test_basics.py::test_basics_no_drawn_image -v
```

### Documentation
```bash
# Generate documentation site
make docs

# Run demo notebook
marimo run demo.py
```

### Publishing
```bash
# Publish to PyPI
make pypi
```

## Important Development Notes

### Frontend Development
When modifying the React component (`js/draw/widget.tsx`):
1. The component uses a dual-canvas system - one for drawing and one for grid overlay
2. Changes require rebuilding with `make js` or `npm run build-draw`
3. Use `make dev` for hot reloading during development
4. The built assets go to `mopaint/static/` and must be committed

### Widget State Management
The widget uses these key traitlets for state synchronization:
- `image`: Base64-encoded drawing data
- `height`/`width`: Canvas dimensions
- `grid`: Whether to show grid overlay
- `store_grid`: Whether to include grid in exported image
- `store_bg`: Whether to include white background in export

### Grid Validation Rules
- `store_grid=True` requires `grid=True` (enforced in Python)
- Grid spacing is fixed at 20px in the frontend
- Grid lines are rendered on a separate canvas for performance

### Testing Considerations
- Tests focus on grid parameter validation and state management
- New drawing features should include tests for state synchronization
- Canvas operations should handle browser limitations (max 4096x4096)

## Project Structure Highlights

Critical files for understanding the codebase:
- `mopaint/__init__.py`: Core widget implementation and image utilities
- `js/draw/widget.tsx`: Complete frontend implementation
- `package.json`: Frontend build scripts and dependencies
- `pyproject.toml`: Python package configuration
- `Makefile`: Build automation commands