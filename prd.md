# PRD: Initial Image Loading Feature for MoPaint Widget

## Problem Statement
Users want to load an initial image into the MoPaint widget to draw on top of, but currently face issues with:
- Image scaling/distortion when canvas dimensions don't match image dimensions
- Loss of original image when refreshing or resetting the canvas
- Unclear parameter behavior when both `init_image` and dimension parameters are provided

## Current Status
✅ **Working**: Image loads and displays  
❌ **Issues**: Image gets scaled to fit canvas, original image lost on refresh

## Requirements

### 1. Image Scaling & Canvas Sizing
- **When `init_image` is provided**: 
  - Canvas height is automatically set to image height
  - Canvas width adapts to browser/container width (user can resize by making browser bigger)
  - Image is NOT scaled - preserves original dimensions
  - If user provides `width` or `height` parameters with `init_image`, raise `ValueError`

### 2. Canvas Operations
- **Clear Canvas**: Resets to original image state (as if widget just started)
- **Reset Button**: Same as Clear Canvas - returns to initial image
- **Drawing**: User draws on top of original image, original remains underneath

### 3. Image Persistence
- **Original Image Storage**: Store original image separately from canvas state
- **State Management**: Always maintain reference to original image for reset operations
- **Browser Resize**: Canvas width can change, but original image dimensions preserved

### 4. Parameter Validation
- Raise `ValueError` if user provides both `init_image` and `width`/`height` parameters
- Error message should explain that dimensions are auto-determined from image

### 5. Technical Implementation
- Add validation in `Paint.__init__()` for conflicting parameters
- Store original image data separately from current canvas export
- Modify clear/reset operations to restore original image instead of empty canvas
- Canvas width responsive to container, height fixed to image height

### 6. User Experience
- Predictable behavior: original image always recoverable
- Responsive width while preserving image aspect ratio
- Clear distinction between "drawing state" and "original image state"
- Clear error messages for invalid parameter combinations

## Implementation Plan

### Phase 1: Parameter Validation (Python)
- Add validation in `Paint.__init__()`: if `init_image` is provided AND user specifies `width` or `height`, raise `ValueError`
- Automatically set `self.width` and `self.height` to image dimensions when `init_image` is used

### Phase 2: Original Image Storage (Frontend)
- Store original base64 image separately from current canvas state
- Add `originalImageRef` to track the initial image
- Ensure original image persists through canvas operations

### Phase 3: Canvas Sizing & Reset (Frontend)
- Respect image dimensions for canvas height
- Allow responsive width behavior in container
- Modify "Clear Canvas" button to restore original image instead of empty canvas
- Prevent image scaling - draw at original size

### Phase 4: Clean up
- Remove debug logging
- Add tests for new validation and auto-sizing behavior
- Update documentation

## Success Criteria
- User can load image without scaling distortion
- Clear/reset operations return to original image state
- Appropriate errors for invalid parameter combinations
- Responsive canvas width with fixed aspect ratio
- Original image always recoverable