import React, { useState, useRef, useEffect } from 'react';
import { cn } from '../../utils/cn';

export function Fader({
    label,
    value,
    min = 0,
    max = 1,
    step = 0.01,
    onChange,
    orientation = 'vertical',
    height = 200,
    width = 40,
    className
}) {
    const trackRef = useRef(null);
    const [dragging, setDragging] = useState(false);

    const handleInteract = (clientY) => {
        if (!trackRef.current) return;
        const rect = trackRef.current.getBoundingClientRect();

        let percentage;
        if (orientation === 'vertical') {
            const relativeY = clientY - rect.top;
            percentage = 1 - (relativeY / rect.height);
        } else {
            // Horizontal not implemented fully yet but similar logic
            percentage = 0;
        }

        // Clamp 0-1
        percentage = Math.max(0, Math.min(1, percentage));

        let newValue = min + percentage * (max - min);

        // Step
        if (step) {
            newValue = Math.round(newValue / step) * step;
        }

        onChange(newValue);
    };

    const handleMouseDown = (e) => {
        setDragging(true);
        handleInteract(e.clientY);
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = 'ns-resize'; // or ew-resize
    };

    const handleMouseMove = (e) => {
        handleInteract(e.clientY);
    };

    const handleMouseUp = () => {
        setDragging(false);
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
    };

    useEffect(() => {
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, []);

    const percentage = (value - min) / (max - min);

    return (
        <div className={cn("flex flex-col items-center gap-2 select-none group", className)}>
            <div className="flex-1 relative flex justify-center py-2" style={{ height }}>
                {/* Track Background */}
                <div
                    ref={trackRef}
                    className="w-1.5 h-full bg-black/40 rounded-full overflow-hidden border border-white/5 relative cursor-pointer"
                    onMouseDown={handleMouseDown}
                >
                    {/* Fill */}
                    <div
                        className="absolute bottom-0 w-full bg-primary/20 transition-all duration-75"
                        style={{ height: `${percentage * 100}%` }}
                    ></div>
                </div>

                {/* Tick Marks */}
                <div className="absolute right-1/2 mr-3 h-full flex flex-col justify-between py-2 opacity-30 pointer-events-none">
                    {[...Array(11)].map((_, i) => (
                        <div key={i} className={cn("w-1.5 bg-white", i % 5 === 0 ? "h-0.5 w-2.5" : "h-px")} />
                    ))}
                </div>

                {/* Fader Handle */}
                <div
                    className="absolute left-1/2 -translate-x-1/2 w-8 h-12 rounded-sm shadow-xl shadow-black border border-white/10 bg-gradient-to-b from-zinc-600 via-zinc-700 to-zinc-800 cursor-grab active:cursor-grabbing flex items-center justify-center group-hover:border-primary/50 transition-colors"
                    style={{
                        bottom: `calc(${percentage * 100}% - 24px)`,
                        zIndex: 10
                    }}
                    onMouseDown={handleMouseDown}
                >
                    <div className="w-full h-[1px] bg-black/50 absolute top-1/2 -translate-y-1/2"></div>
                    <div className="w-full h-[1px] bg-white/20 absolute top-1/2 -translate-y-1/2 translate-y-px"></div>
                </div>
            </div>

            {/* Label */}
            <div className="bg-black/40 px-2 py-1 rounded border border-white/5 text-center min-w-[3rem]">
                <div className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider">{label}</div>
                <div className="text-[10px] font-mono font-bold text-primary">
                    {Math.round(value * 100)}%
                </div>
            </div>
        </div>
    );
}
