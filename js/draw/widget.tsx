import { createRender, useModelState } from "@anywidget/react";
import React, { useRef, useState, useEffect } from 'react';
import './styles.css';


const Button = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: 'default' | 'ghost'
  }
>(({ className = '', variant = 'default', ...props }, ref) => {
  const baseStyles = 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50';
  const variantStyles = {
    default: 'bg-gray-200 hover:bg-gray-300',
    ghost: 'hover:bg-gray-100/50'
  };
  
  return (
    <button
      ref={ref}
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      {...props}
    />
  );
});
Button.displayName = 'Button';

const colors = [
  '#000000', '#FFFFFF', '#C0C0C0', '#FF0000', '#FFFF00', '#00FF00', '#00FFFF', '#0000FF', '#FF00FF', '#FFFF80', '#00FF80', '#80FFFF', '#8080FF', '#FF0080'
];

// Constants for canvas settings
const MAX_CANVAS_DIMENSION = 4096; // Most browsers support up to 4096x4096
const GRID_SIZE = 20;

function Component() {
  const drawingCanvasRef = useRef<HTMLCanvasElement>(null);
  const gridCanvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [color, setColor] = useState('#000000');
  const [tool, setTool] = useState('brush');
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  let [base64, setBase64] = useModelState<string>("base64");
  let [height, setHeight] = useModelState<number>("height");
  let [showGrid, setShowGrid] = useModelState<boolean>("show_grid");
  let [storeGrid, setStoreGrid] = useModelState<boolean>("store_grid");
  
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });

  // Utility function to ensure canvas context is available
  const getContexts = () => {
    const drawingContext = drawingCanvasRef.current?.getContext('2d');
    const gridContext = gridCanvasRef.current?.getContext('2d');
    return { drawingContext, gridContext };
  };

  // Utility function to ensure canvas sizes are in sync
  const syncCanvasSizes = (width: number, height: number) => {
    const { drawingContext, gridContext } = getContexts();
    if (!drawingContext || !gridContext) return false;

    // Scale down if dimensions are too large
    const scale = Math.min(1, MAX_CANVAS_DIMENSION / Math.max(width, height));
    const finalWidth = Math.floor(width * scale);
    const finalHeight = Math.floor(height * scale);

    try {
      drawingCanvasRef.current!.width = finalWidth;
      drawingCanvasRef.current!.height = finalHeight;
      gridCanvasRef.current!.width = finalWidth;
      gridCanvasRef.current!.height = finalHeight;
      return true;
    } catch (e) {
      console.error('Failed to resize canvases:', e);
      setError('Failed to resize canvas. Try reducing the window size.');
      return false;
    }
  };

  // Utility function to draw the grid programmatically on any context
  const drawGridOnContext = (context: CanvasRenderingContext2D, width: number, height: number, showGrid: boolean) => {
    if (!showGrid) return;
    context.save();
    context.strokeStyle = 'rgba(200, 200, 200, 0.5)';
    context.lineWidth = 1;
    context.setLineDash([]);
    for (let x = GRID_SIZE; x < width; x += GRID_SIZE) {
      context.beginPath();
      context.moveTo(x, 0);
      context.lineTo(x, height);
      context.stroke();
    }
    for (let y = GRID_SIZE; y < height; y += GRID_SIZE) {
      context.beginPath();
      context.moveTo(0, y);
      context.lineTo(width, y);
      context.stroke();
    }
    context.restore();
  };

  // Handle window resize with debouncing
  useEffect(() => {
    let resizeTimeout: number;
    
    const resizeCanvas = () => {
      const container = drawingCanvasRef.current?.parentElement;
      if (!container) return;

      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight;
      
      if (syncCanvasSizes(newWidth, newHeight)) {
        setCanvasSize({ width: newWidth, height: newHeight });
        const { gridContext } = getContexts();
        if (gridContext) {
          drawGridOnContext(gridContext, newWidth, newHeight, showGrid);
        }
      }
    };

    const debouncedResize = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(resizeCanvas, 250);
    };

    window.addEventListener('resize', debouncedResize);
    resizeCanvas(); // Initial sizing

    return () => {
      window.removeEventListener('resize', debouncedResize);
      clearTimeout(resizeTimeout);
    };
  }, [showGrid])

  // Effect to handle touch events
  useEffect(() => {
    const drawingCanvas = drawingCanvasRef.current;
    if (!drawingCanvas) return;

    const touchStart = (e: TouchEvent) => {
      e.preventDefault();
      const touch = e.touches[0];
      const rect = drawingCanvas.getBoundingClientRect();
      startDrawingAt(touch.clientX - rect.left, touch.clientY - rect.top);
    };

    const touchMove = (e: TouchEvent) => {
      e.preventDefault();
      const touch = e.touches[0];
      const rect = drawingCanvas.getBoundingClientRect();
      drawAt(touch.clientX - rect.left, touch.clientY - rect.top);
    };

    const touchEnd = (e: TouchEvent) => {
      e.preventDefault();
      stopDrawing();
    };

    drawingCanvas.addEventListener('touchstart', touchStart);
    drawingCanvas.addEventListener('touchmove', touchMove);
    drawingCanvas.addEventListener('touchend', touchEnd);

    return () => {
      drawingCanvas.removeEventListener('touchstart', touchStart);
      drawingCanvas.removeEventListener('touchmove', touchMove);
      drawingCanvas.removeEventListener('touchend', touchEnd);
    };
  }, []);

  // Effect to redraw grid when showGrid or canvasSize changes
  useEffect(() => {
    const { gridContext } = getContexts();
    if (gridContext && gridCanvasRef.current) {
      drawGridOnContext(gridContext, gridCanvasRef.current.width, gridCanvasRef.current.height, showGrid);
    }
  }, [showGrid, canvasSize]);

  // Drawing functions with coordinate handling
  const startDrawingAt = (x: number, y: number) => {
    const { drawingContext } = getContexts();
    if (!drawingContext) return;

    try {
      drawingContext.beginPath();
      drawingContext.moveTo(x, y);
      setIsDrawing(true);
    } catch (e) {
      console.error('Failed to start drawing:', e);
      setError('Failed to start drawing. Try refreshing the page.');
    }
  };

  const drawAt = (x: number, y: number) => {
    if (!isDrawing) return;
    
    const { drawingContext } = getContexts();
    if (!drawingContext) return;

    try {
      drawingContext.lineTo(x, y);
      drawingContext.strokeStyle = tool === 'eraser' ? 'rgba(0,0,0,0)' : color;
      drawingContext.lineWidth = tool === 'eraser' ? 20 : tool === 'marker' ? 8 : 2;
      drawingContext.lineCap = 'round';
      drawingContext.stroke();
    } catch (e) {
      console.error('Failed to draw:', e);
      setError('Failed to draw. Try refreshing the page.');
      setIsDrawing(false);
    }
  };

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    startDrawingAt(e.clientX - rect.left, e.clientY - rect.top);
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    drawAt(e.clientX - rect.left, e.clientY - rect.top);
  };

  // Update output image whenever storeGrid or showGrid changes
  useEffect(() => {
    if (!drawingCanvasRef.current) return;
    const width = drawingCanvasRef.current.width;
    const height = drawingCanvasRef.current.height;
    const drawingCanvas = drawingCanvasRef.current;

    // Create export canvas
    const exportCanvas = document.createElement('canvas');
    exportCanvas.width = width;
    exportCanvas.height = height;
    const exportContext = exportCanvas.getContext('2d');
    if (!exportContext) return;

    // Fill with white if background is enabled (assume always true for now)
    exportContext.fillStyle = '#FFFFFF';
    exportContext.fillRect(0, 0, width, height);

    // Draw grid if needed
    if (storeGrid && showGrid) {
      drawGridOnContext(exportContext, width, height, true);
    }
    // Draw drawing on top
    exportContext.drawImage(drawingCanvas, 0, 0);
    setBase64(exportCanvas.toDataURL('image/png'));
  }, [storeGrid, showGrid, canvasSize]);

  const stopDrawing = () => {
    setIsDrawing(false);
    if (!drawingCanvasRef.current) return;
    const width = drawingCanvasRef.current.width;
    const height = drawingCanvasRef.current.height;
    const drawingCanvas = drawingCanvasRef.current;

    try {
      // Create export canvas
      const exportCanvas = document.createElement('canvas');
      exportCanvas.width = width;
      exportCanvas.height = height;
      const exportContext = exportCanvas.getContext('2d');
      if (!exportContext) return;

      // Fill with white if background is enabled (assume always true for now)
      exportContext.fillStyle = '#FFFFFF';
      exportContext.fillRect(0, 0, width, height);

      // Draw grid if needed
      if (storeGrid && showGrid) {
        drawGridOnContext(exportContext, width, height, true);
      }
      // Draw drawing on top
      exportContext.drawImage(drawingCanvas, 0, 0);
      setBase64(exportCanvas.toDataURL('image/png'));
    } catch (e) {
      console.error('Failed to save drawing:', e);
      setError('Failed to save drawing. Try again or refresh the page.');
    }
  };

  const startDragging = (e: React.MouseEvent<HTMLDivElement>) => {
    setDragging(true);
    setPosition({
      x: e.clientX - (containerRef.current?.offsetLeft || 0),
      y: e.clientY - (containerRef.current?.offsetTop || 0)
    });
  };

  const onDrag = (e: React.MouseEvent<HTMLDivElement>) => {
    if (dragging) {
      const left = e.clientX - position.x;
      const top = e.clientY - position.y;
      if (containerRef.current) {
        containerRef.current.style.left = `${left}px`;
        containerRef.current.style.top = `${top}px`;
      }
    }
  };

  const stopDragging = () => {
    setDragging(false);
  };

  return (
    <div className="bg-teal-600 w-full overflow-hidden" style={{ height: `${height}px` }}>
      {error && (
        <div className="absolute top-0 left-0 right-0 bg-red-500 text-white p-2 text-center">
          {error}
          <button 
            className="ml-2 underline"
            onClick={() => setError(null)}
          >
            Dismiss
          </button>
        </div>
      )}
      <div 
        ref={containerRef}
        className="absolute bg-white border-2 border-gray-200 shadow-md" 
        style={{ 
          width: '90%', 
          height: '90%', 
          left: '50%', 
          top: '50%', 
          transform: 'translate(-50%, -50%)',
          minWidth: '400px',
          minHeight: '300px'
        }}
      >
        <div 
          className="bg-blue-900 text-white px-2 py-1 flex justify-between items-center cursor-move"
          onMouseDown={startDragging}
          onMouseMove={onDrag}
          onMouseUp={stopDragging}
          onMouseLeave={stopDragging}
        >
          <span className="text-white">untitled - Paint</span>
          <div className="flex gap-1">
            <Button variant="ghost" className="h-5 w-5 p-0 min-w-0 text-white hover:bg-blue-700">_</Button>
            <Button variant="ghost" className="h-5 w-5 p-0 min-w-0 text-white hover:bg-blue-700">□</Button>
            <Button variant="ghost" className="h-5 w-5 p-0 min-w-0 text-white hover:bg-blue-700">×</Button>
          </div>
        </div>
        <div className="bg-gray-300 px-2 py-1 text-sm text-black">
          <span className="mr-4 text-black">File</span>
          <span className="mr-4 text-black">Edit</span>
          <span className="mr-4 text-black">View</span>
          <span className="mr-4 text-black">Image</span>
          <span className="mr-4 text-black">Options</span>
          <span className="text-black">Help</span>
        </div>
        <div className="flex flex-1 flex-grow" style={{ height: 'calc(100% - 7.5rem)' }}>
          <div className="w-8 bg-gray-300 p-0.5 border-r border-gray-400">
            <Button
              variant="ghost"
              className={`w-7 h-7 p-0 min-w-0 mb-0.5 ${tool === 'brush' ? 'bg-gray-300 border border-gray-400 shadow-inner' : ''}`}
              onClick={() => setTool('brush')}
              title="Brush"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 text-black">
                <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
              </svg>
            </Button>
            <Button
              variant="ghost"
              className={`w-7 h-7 p-0 min-w-0 mb-0.5 ${tool === 'marker' ? 'bg-gray-300 border border-gray-400 shadow-inner' : ''}`}
              onClick={() => setTool('marker')}
              title="Thick Marker"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 text-black">
                <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
              </svg>
            </Button>
            <Button
              variant="ghost"
              className={`w-7 h-7 p-0 min-w-0 mb-0.5 ${tool === 'eraser' ? 'bg-gray-300 border border-gray-400 shadow-inner' : ''}`}
              onClick={() => setTool('eraser')}
              title="Eraser"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6 text-black">
                <path d="M7 21h10"/>
                <path d="M5.5 13.5L13 6c.83-.83 2.17-.83 3 0l2 2c.83.83.83 2.17 0 3l-7.5 7.5c-.83.83-2.17.83-3 0l-2-2c-.83-.83-.83-2.17 0-3z"/>
              </svg>
            </Button>
            <div className="w-7 h-0.5 bg-gray-400 my-1"></div>
            <Button
              variant="ghost"
              className={`w-7 h-7 p-0 min-w-0 mb-0.5 ${showGrid ? 'bg-gray-300 border border-gray-400 shadow-inner' : ''}`}
              onClick={() => {
                const newShowGrid = !showGrid;
                setShowGrid(newShowGrid);
                // If turning off grid, also turn off store_grid
                if (!newShowGrid && storeGrid) {
                  setStoreGrid(false);
                }
              }}
              title="Show Grid"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 text-black">
                <rect x="3" y="3" width="18" height="18" />
                <path d="M9 3v18" />
                <path d="M15 3v18" />
                <path d="M3 9h18" />
                <path d="M3 15h18" />
              </svg>
            </Button>
            <Button
              variant="ghost"
              className={`w-7 h-7 p-0 min-w-0 mb-0.5 ${storeGrid ? 'bg-gray-300 border border-gray-400 shadow-inner' : ''} ${!showGrid ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => {
                if (showGrid) {
                  setStoreGrid(!storeGrid);
                }
              }}
              disabled={!showGrid}
              title={showGrid ? "Keep Grid in Output" : "Enable 'Show Grid' first"}
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 text-black">
                <rect x="3" y="3" width="18" height="18" />
                <path d="M9 3v18" />
                <path d="M15 3v18" />
                <path d="M3 9h18" />
                <path d="M3 15h18" />
                <path d="M12 8l-4 4 4 4" />
                <path d="m8 12 4 0" />
              </svg>
            </Button>
            <div className="w-7 h-0.5 bg-gray-400 my-1"></div>
            <Button
              variant="ghost"
              className="w-7 h-7 p-0 min-w-0 mb-0.5"
              onClick={() => {
                // Clear the drawing canvas
                const drawingCanvas = drawingCanvasRef.current;
                if (drawingCanvas) {
                  const drawingContext = drawingCanvas.getContext('2d');
                  if (drawingContext) {
                    drawingContext.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height);
                  }
                }
                // Redraw the grid on the grid canvas
                const gridCanvas = gridCanvasRef.current;
                if (gridCanvas) {
                  const gridContext = gridCanvas.getContext('2d');
                  if (gridContext) {
                    drawGridOnContext(gridContext, gridCanvas.width, gridCanvas.height, showGrid);
                  }
                }
                // Update the output image
                if (storeGrid && showGrid && gridCanvasRef.current && drawingCanvasRef.current) {
                  const tempCanvas = document.createElement('canvas');
                  tempCanvas.width = drawingCanvasRef.current.width;
                  tempCanvas.height = drawingCanvasRef.current.height;
                  const tempContext = tempCanvas.getContext('2d');
                  if (tempContext) {
                    tempContext.drawImage(gridCanvasRef.current, 0, 0);
                    tempContext.drawImage(drawingCanvasRef.current, 0, 0);
                    setBase64(tempCanvas.toDataURL('image/png'));
                  }
                } else if (drawingCanvasRef.current) {
                  setBase64(drawingCanvasRef.current.toDataURL('image/png'));
                }
              }}
              title="Clear Canvas"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 text-black">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
                <path d="M21 3v5h-5"/>
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
                <path d="M8 16H3v5"/>
              </svg>
            </Button>
          </div>
          <div className="flex-grow overflow-hidden border border-gray-400 relative">
            <canvas
              ref={drawingCanvasRef}
              width={canvasSize.width}
              height={canvasSize.height}
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseOut={stopDrawing}
              style={{ 
                width: '100%', 
                height: '100%',
                position: 'absolute',
                left: 0,
                top: 0,
                zIndex: 1
              }}
            />
            <canvas
              ref={gridCanvasRef}
              width={canvasSize.width}
              height={canvasSize.height}
              style={{ 
                width: '100%', 
                height: '100%',
                position: 'absolute',
                left: 0,
                top: 0,
                zIndex: 2,
                pointerEvents: 'none'  // Allow drawing through the grid
              }}
            />
          </div>
        </div>
        <div className="flex bg-gray-300 p-1 border-t border-gray-400">
          <div className="flex flex-wrap gap-1">
            {colors.map((c) => (
              <Button
                key={c}
                variant="ghost"
                className={`w-6 h-6 p-0 min-w-0 ${color === c ? 'ring-1 ring-gray-600' : ''}`}
                style={{ backgroundColor: c }}
                onClick={() => setColor(c)}
              />
            ))}
          </div>
        </div>
        <div className="bg-gray-300 px-2 py-1 text-sm border-t border-gray-400 text-black">
          For Help, click Help Topics on the Help Menu.
        </div>
      </div>
    </div>
  );
}

const render = createRender(Component);

export default { render };
