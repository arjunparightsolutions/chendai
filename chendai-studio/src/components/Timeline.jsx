import React, { useRef, useEffect } from 'react';
import { useProjectStore } from '../store/projectStore';
import WaveSurfer from 'wavesurfer.js';
import { cn } from '../utils/cn';

import PatternTrack from './PatternTrack';
import { AlignJustify, Activity } from 'lucide-react';

function Timeline() {
    const { audioPath, stems, players, currentTime } = useProjectStore();
    const waveformRefs = useRef({});
    const wavesurferInstances = useRef({});
    const [viewMode, setViewMode] = React.useState('waveform'); // 'waveform' or 'pattern'

    // Waveform Cleanup / Init logic
    useEffect(() => {
        if (viewMode !== 'waveform') return; // Only init waveforms in waveform mode
        if (!audioPath && Object.keys(stems).length === 0) return;

        // Initialize WaveSurfer
        players.forEach((player) => {
            if (waveformRefs.current[player.id]) {
                if (wavesurferInstances.current[player.id]) {
                    wavesurferInstances.current[player.id].destroy();
                }

                const ws = WaveSurfer.create({
                    container: waveformRefs.current[player.id],
                    waveColor: '#52525b', // zinc-600
                    progressColor: '#fbbf24', // primary (amber-400)
                    cursorColor: '#f59e0b',
                    barWidth: 2,
                    barGap: 1,
                    height: 50,
                    normalize: true,
                    interact: false,
                    hideScrollbar: true
                });

                const source = stems[player.id] || audioPath;
                if (source) ws.load(source);

                wavesurferInstances.current[player.id] = ws;
            }
        });

        return () => {
            Object.values(wavesurferInstances.current).forEach(ws => ws?.destroy());
            wavesurferInstances.current = {};
        };
    }, [audioPath, stems, players, viewMode]);

    // Sync Cursor
    useEffect(() => {
        if (viewMode !== 'waveform') return;
        Object.values(wavesurferInstances.current).forEach(ws => {
            if (ws) {
                const duration = ws.getDuration();
                if (duration > 0) {
                    ws.seekTo(Math.min(currentTime / duration, 1));
                }
            }
        });
    }, [currentTime, viewMode]);

    return (
        <div className="h-full flex flex-col">
            {/* Timeline Ruler */}
            <div className="h-8 bg-surface border-b border-white/5 flex items-end">
                <div className="w-[200px] flex-shrink-0 border-r border-white/5 bg-surface/50 h-full flex items-center justify-between px-3">
                    <span className="text-xs text-muted-foreground font-bold">Tracks</span>
                    <div className="flex gap-1">
                        <button
                            className={cn("p-1 rounded", viewMode === 'waveform' ? "bg-white/10 text-white" : "text-muted-foreground hover:bg-white/5")}
                            onClick={() => setViewMode('waveform')}
                            title="Waveform View"
                        >
                            <Activity className="w-4 h-4" />
                        </button>
                        <button
                            className={cn("p-1 rounded", viewMode === 'pattern' ? "bg-white/10 text-white" : "text-muted-foreground hover:bg-white/5")}
                            onClick={() => setViewMode('pattern')}
                            title="Pattern View"
                        >
                            <AlignJustify className="w-4 h-4" />
                        </button>
                    </div>
                </div>
                <div className="flex-1 flex justify-between px-2 text-[10px] text-muted-foreground font-mono select-none">
                    <span>00:00</span><span>00:15</span><span>00:30</span><span>00:45</span><span>01:00</span><span>01:15</span><span>01:30</span>
                </div>
            </div>

            {/* Tracks */}
            <div className="flex-1 overflow-y-auto">
                {players.map((player) => (
                    <div key={player.id} className="h-20 flex border-b border-white/5 bg-surface/30 hover:bg-surface/50 transition-colors">
                        {/* Track Header */}
                        <div className="w-[200px] flex-shrink-0 bg-surface border-r border-white/5 p-3 flex flex-col justify-center relative">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-lg">{player.role.includes('elathaalam') ? '🔔' : '🥁'}</span>
                                <span className="text-xs font-bold text-foreground truncate">{player.name}</span>
                            </div>
                            <div className="flex gap-1">
                                <span className={cn("text-[9px] px-1 rounded border", player.solo ? "bg-primary text-black border-primary" : "text-muted-foreground border-white/10")}>S</span>
                                <span className={cn("text-[9px] px-1 rounded border", player.mute ? "bg-red-500 text-white border-red-500" : "text-muted-foreground border-white/10")}>M</span>
                            </div>
                            {/* Color strip */}
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary/20"></div>
                        </div>

                        {/* Track Content Lane */}
                        <div className="flex-1 relative flex items-center bg-black/20 overflow-hidden">
                            {/* Grid lines (common) */}
                            <div className="absolute inset-0 w-full h-full pointer-events-none" style={{
                                backgroundImage: 'linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px)',
                                backgroundSize: '10% 100%'
                            }}></div>

                            {viewMode === 'waveform' ? (
                                <div
                                    ref={(el) => (waveformRefs.current[player.id] = el)}
                                    className="w-full opacity-80"
                                />
                            ) : (
                                <PatternTrack player={player} />
                            )}
                        </div>
                    </div>
                ))}

                {!audioPath && (
                    <div className="h-full flex items-center justify-center flex-col text-muted-foreground gap-2">
                        <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center">
                            <WaveSurferIcon className="w-8 h-8 opacity-20" />
                        </div>
                        <p className="text-xs">Generate a composition to see {viewMode}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

// Simple icon for empty state
const WaveSurferIcon = ({ className }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M2 12h2l2-6 4 12 4-12 4 6h2" />
    </svg>
);

export default Timeline;
