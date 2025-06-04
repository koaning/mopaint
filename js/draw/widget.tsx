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

function Component() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [color, setColor] = useState('#000000');
  const [tool, setTool] = useState('brush');
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  let [base64, setBase64] = useModelState<string>("base64");
  let [height, setHeight] = useModelState<number>("height");
  

  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const resizeCanvas = () => {
      const canvas = canvasRef.current;
      const container = canvas?.parentElement;
      if (canvas && container) {
        const newWidth = container.clientWidth;
        const newHeight = container.clientHeight;
        
        // Update canvas size
        setCanvasSize({ width: newWidth, height: newHeight });
        canvas.width = newWidth;
        canvas.height = newHeight;
        
        // Reset the canvas to an empty state with white background
        const context = canvas.getContext('2d');
        if (context) {
          context.fillStyle = '#FFFFFF';
          context.fillRect(0, 0, canvas.width, canvas.height);
          
          // Update the base64 representation to reflect the empty state
          const emptyBase64 = canvas.toDataURL('image/png');
          setBase64(emptyBase64);
        }
      }
    };

    // Create resize observer
    const resizeObserver = new ResizeObserver(resizeCanvas);
    if (canvasRef.current?.parentElement) {
      resizeObserver.observe(canvasRef.current.parentElement);
    }

    // Initial resize
    resizeCanvas();

    return () => resizeObserver.disconnect();
  }, []);

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const context = canvas.getContext('2d');
    if (context) {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      context.beginPath();
      context.moveTo(x, y);
      setIsDrawing(true);
    }
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const context = canvas.getContext('2d');
    if (context) {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      context.lineTo(x, y);
      context.strokeStyle = tool === 'eraser' ? '#FFFFFF' : color;
      context.lineWidth = tool === 'eraser' ? 20 : tool === 'marker' ? 8 : 2;
      context.lineCap = 'round';
      context.stroke();
    }
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    const canvas = canvasRef.current;
    if (canvas) {
      base64 = canvas.toDataURL('image/png');
    }
    setBase64(base64 as string);
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
              className="w-7 h-7 p-0 min-w-0 mb-0.5"
              onClick={() => {
                const canvas = canvasRef.current;
                if (canvas) {
                  const context = canvas.getContext('2d');
                  if (context) {
                    context.fillStyle = '#FFFFFF';
                    context.fillRect(0, 0, canvas.width, canvas.height);
                    setBase64(canvas.toDataURL('image/png'));
                  }
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
          <div className="flex-grow overflow-hidden border border-gray-400">
            <canvas
              ref={canvasRef}
              width={canvasSize.width}
              height={canvasSize.height}
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseOut={stopDrawing}
              style={{ width: '100%', height: '100%' }}
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
