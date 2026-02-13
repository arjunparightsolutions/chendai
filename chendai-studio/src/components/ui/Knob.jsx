import React, { useState, useEffect, useRef } from 'react';
import { cn } from '../../utils/cn';

export function Knob({
    label,
    value,
    min = 0,
    max = 100,
    step = 1,
    onChange,
    unit = '',
    format,
    size = 40,
    className
}) {
    const [dragging, setDragging] = useState(false);
    const startY = useRef(null);
    const startValue = useRef(null);

    const handleMouseDown = (e) => {
        setDragging(true);
        startY.current = e.clientY;
        startValue.current = value;
        document.body.style.cursor = 'ns-resize';
        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('mouseup', handleMouseUp);
    };

    const handleMouseMove = (e) => {
        if (startY.current === null) return;

        const deltaY = startY.current - e.clientY;
        const range = max - min;
        // Sensitivity: full range in 200px
        const deltaValue = (deltaY / 200) * range;

        let newValue = startValue.current + deltaValue;

        // Snap to step
        if (step) {
            newValue = Math.round(newValue / step) * step;
        }

        // Clamp
        newValue = Math.max(min, Math.min(max, newValue));

        onChange(newValue);
    };

    const handleMouseUp = () => {
        setDragging(false);
        startY.current = null;
        startValue.current = null;
        document.body.style.cursor = '';
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
    };

    useEffect(() => {
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, []);

    // Visual calculation
    const percentage = (value - min) / (max - min);
    const rotation = -135 + (percentage * 270); // -135 to +135 degrees

    return (
        <div className={cn("flex flex-col items-center gap-1 select-none group", className)}>
            <div
                className="relative cursor-ns-resize group-hover:scale-105 transition-transform"
                style={{ width: size, height: size }}
                onMouseDown={handleMouseDown}
            >
                {/* Background Ring */}
                <svg width={size} height={size} viewBox="0 0 100 100" className="overflow-visible">
                    <circle
                        cx="50" cy="50" r="40"
                        fill="none"
                        stroke="#333"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray="200" // Approx 75% of circle
                        strokeDashoffset="50" // Rotate to open at bottom
                        transform="rotate(135 50 50)"
                    />
                    {/* Value Arc */}
                    <circle
                        cx="50" cy="50" r="40"
                        fill="none"
                        stroke="var(--primary, #fbbf24)"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={200}
                        strokeDashoffset={200 - (percentage * 200)}
                        transform="rotate(135 50 50)"
                        className="transition-all duration-75"
                    />
                </svg>

                {/* Pointer / Knob Body */}
                <div
                    className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full shadow-lg shadow-black/50 border border-white/10 flex items-center justify-center bg-gradient-to-br from-zinc-700 to-zinc-900"
                    style={{
                        width: size * 0.7,
                        height: size * 0.7,
                        transform: `translate(-50%, -50%) rotate(${rotation}deg)`
                    }}
                >
                    <div className="w-1 h-3 bg-white/80 rounded-full absolute top-1 shadow-[0_0_5px_rgba(255,255,255,0.8)]"></div>
                </div>
            </div>

            <div className="text-center space-y-0.5">
                <div className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider group-hover:text-white transition-colors">
                    {label}
                </div>
                <div className="text-[9px] font-mono text-primary font-bold">
                    {format ? format(value) : Math.round(value * 10) / 10}
                    {unit && <span className="text-muted-foreground/50 ml-0.5 text-[8px]">{unit}</span>}
                </div>
            </div>
        </div>
    );
}
