import React from 'react';
import { useProjectStore } from '../store/projectStore';
import { cn } from '../utils/cn';

function PatternTrack({ player, width_px_per_sec = 100 }) {
    const { metadata, duration } = useProjectStore();

    const events = metadata?.tracks?.[player.id] || [];
    const totalWidth = duration * width_px_per_sec;

    return (
        <div className="relative h-full w-full bg-black/20 overflow-hidden group">
            {/* Grid Background */}
            <div className="absolute inset-0 w-full h-full pointer-events-none" style={{
                backgroundImage: 'linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px)',
                backgroundSize: `${width_px_per_sec}px 100%`,
                width: `${totalWidth}px`
            }}></div>

            {/* Sub-beat Grid (16th notes approx) */}
            <div className="absolute inset-0 w-full h-full pointer-events-none" style={{
                backgroundImage: 'linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px)',
                backgroundSize: `${width_px_per_sec / 4}px 100%`,
                width: `${totalWidth}px`
            }}></div>

            <div className="absolute inset-0 h-full" style={{ width: `${totalWidth}px` }}>
                {events.map((event, idx) => {
                    const left = event.time * width_px_per_sec;
                    const width = Math.max(4, event.duration * width_px_per_sec);

                    // Color based on stroke type/category
                    let color = "bg-primary";
                    let height = "h-4/6";
                    let top = "top-1/6"; // Centered

                    // Visual differentiation
                    if (event.category.includes("THAAM") || event.category === "Chapu") {
                        color = "bg-amber-500";
                        height = "h-5/6"; // Taller
                    }
                    if (event.category.includes("DHEEM") || event.category === "Dheem") {
                        color = "bg-orange-600";
                        height = "h-full"; // Full height
                    }
                    if (event.category.includes("NAM") || event.category === "Ilathaalam") {
                        color = "bg-yellow-300";
                        height = "h-3/6"; // Shorter
                    }

                    return (
                        <div
                            key={idx}
                            className={cn(
                                "absolute rounded-sm border border-black/20 shadow-sm transition-all hover:brightness-125 cursor-pointer top-1/2 -translate-y-1/2",
                                color,
                                height
                            )}
                            style={{
                                left: `${left}px`,
                                width: `${width}px`,
                                opacity: 0.6 + (event.velocity * 0.4)
                            }}
                            title={`${event.type} (${event.category}) - Vel: ${event.velocity.toFixed(2)}`}
                        >
                            <div className="hidden group-hover:block absolute -top-5 left-0 text-[10px] bg-black/90 text-white px-1.5 py-0.5 rounded whitespace-nowrap z-50 pointer-events-none">
                                {event.type}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default PatternTrack;
