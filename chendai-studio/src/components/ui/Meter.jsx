import React from 'react';
import { cn } from '../../utils/cn';

export function Meter({ value, segments = 20, className }) {
    // Value 0 to 1
    const activeSegments = Math.round(value * segments);

    return (
        <div className={cn("flex flex-col-reverse gap-[1px] bg-black/50 p-[1px] rounded overflow-hidden", className)}>
            {[...Array(segments)].map((_, i) => {
                const isActive = i < activeSegments;
                // Color scaling: Green -> Yellow -> Red
                let colorClass = "bg-green-500";
                if (i > segments * 0.6) colorClass = "bg-yellow-500";
                if (i > segments * 0.85) colorClass = "bg-red-500";

                return (
                    <div
                        key={i}
                        className={cn(
                            "w-full flex-1 rounded-[1px] transition-colors duration-75",
                            isActive ? colorClass : "bg-white/5"
                        )}
                        style={{ opacity: isActive ? 1 : 0.2 }}
                    />
                );
            })}
        </div>
    );
}
