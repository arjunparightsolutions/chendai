import React, { useMemo } from 'react';
import { useProjectStore } from '../store/projectStore';
import { cn } from '../utils/cn';

function PatternView({ width_px_per_sec = 100 }) {
    const { players, metadata, duration } = useProjectStore();

    // If no metadata or tracks, show empty state
    if (!metadata?.tracks) {
        return (
            <div className="h-full flex items-center justify-center text-muted-foreground text-xs">
                Generate a pattern to view events
            </div>
        );
    }

    const tracks = metadata.tracks;
    const totalWidth = duration * width_px_per_sec;

    return (
        <div className="flex-1 overflow-auto relative bg-black/20">
            <div className="min-w-full" style={{ width: `${totalWidth}px` }}>
                {players.map((player) => {
                    const playerEvents = tracks[player.id] || [];

                    return (
                        <div key={player.id} className="h-20 border-b border-white/5 relative group">
                            {/* Grid Background */}
                            <div className="absolute inset-0 w-full h-full pointer-events-none" style={{
                                backgroundImage: 'linear-gradient(to right, rgba(255,255,255,0.05) 1px, transparent 1px)',
                                backgroundSize: `${width_px_per_sec}px 100%`
                            }}></div>

                            {/* Sub-beat Grid (16th notes approx) */}
                            <div className="absolute inset-0 w-full h-full pointer-events-none" style={{
                                backgroundImage: 'linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px)',
                                backgroundSize: `${width_px_per_sec / 4}px 100%`
                            }}></div>

                            {/* Events */}
                            {playerEvents.map((event, idx) => {
                                const left = event.time * width_px_per_sec;
                                const width = Math.max(4, event.duration * width_px_per_sec);

                                // Color based on stroke type/category
                                let color = "bg-primary";
                                if (event.category.includes("THAAM") || event.category === "Chapu") color = "bg-amber-500";
                                if (event.category.includes("DHEEM") || event.category === "Dheem") color = "bg-orange-600";
                                if (event.category.includes("NAM") || event.category === "Ilathaalam") color = "bg-yellow-300";

                                return (
                                    <div
                                        key={idx}
                                        className={cn(
                                            "absolute top-2 bottom-2 rounded-sm border border-black/20 shadow-sm transition-all hover:brightness-125 cursor-pointer",
                                            color
                                        )}
                                        style={{
                                            left: `${left}px`,
                                            width: `${width}px`,
                                            opacity: 0.6 + (event.velocity * 0.4)
                                        }}
                                        title={`${event.type} (${event.category}) - Vel: ${event.velocity.toFixed(2)}`}
                                    >
                                        <div className="hidden group-hover:block absolute -top-4 left-0 text-[9px] bg-black/80 px-1 rounded whitespace-nowrap z-10">
                                            {event.type}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default PatternView;
