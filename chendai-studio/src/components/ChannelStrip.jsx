import React, { useState } from 'react';
import { useProjectStore } from '../store/projectStore';
import { ChevronRight, ChevronDown } from 'lucide-react';
import { cn } from '../utils/cn';
import { Knob } from './ui/Knob';
import { Fader } from './ui/Fader';
import { Meter } from './ui/Meter';
import { motion, AnimatePresence } from 'framer-motion';

function ChannelStrip({ player }) {
    const { updatePlayer, isPlaying } = useProjectStore();
    const [expanded, setExpanded] = useState(false);

    // Simulated Meter Value (Random for demo if playing)
    // In production, this would come from an AudioAnalyzer node
    const [meterValue, setMeterValue] = useState(0);

    React.useEffect(() => {
        if (!isPlaying) {
            setMeterValue(0);
            return;
        }

        const interval = setInterval(() => {
            // Simulate audio signal (random noise + volume envelope)
            const noise = Math.random() * 0.8 + 0.2;
            setMeterValue(noise * player.volume);
        }, 100);

        return () => clearInterval(interval);
    }, [isPlaying, player.volume]);

    const handleChange = (param, value) => {
        updatePlayer(player.id, { [param]: value });
    };

    return (
        <div className={cn(
            "rounded-lg border transition-all duration-300 overflow-hidden",
            expanded ? "bg-card border-primary/20 shadow-lg shadow-black/50" : "bg-card/50 border-white/5 hover:border-white/10"
        )}>
            {/* Header - Always Visible */}
            <div
                className="flex items-center gap-2 p-2 cursor-pointer select-none hover:bg-white/5 active:bg-white/10"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="w-8 h-8 rounded-md bg-black/40 flex items-center justify-center text-lg border border-white/5 relative overflow-hidden">
                    {/* Background Meter in Icon */}
                    <div className="absolute bottom-0 left-0 right-0 bg-primary/20 transition-all duration-75" style={{ height: `${meterValue * 100}%` }}></div>
                    <span className="relative z-10">{player.role === 'lead' ? '🥁' : player.role === 'rhythm' ? '🎯' : '🔔'}</span>
                </div>
                <div className="flex-1 min-w-0">
                    <div className="text-xs font-bold text-foreground truncate">{player.name}</div>
                    <div className="flex items-center gap-2 mt-1 h-2">
                        {/* Horizontal Meter */}
                        <div className="flex-1 h-full bg-black/50 rounded-full overflow-hidden flex gap-[1px]">
                            <div className="h-full bg-primary transition-all duration-75" style={{ width: `${meterValue * 100}%`, opacity: 0.8 }}></div>
                        </div>
                    </div>
                </div>

                <div className="flex gap-1" onClick={e => e.stopPropagation()}>
                    <motion.button
                        whileTap={{ scale: 0.9 }}
                        className={cn("w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold border transition-colors", player.solo ? "bg-primary text-black border-primary" : "bg-black/40 text-muted-foreground border-white/10 hover:bg-white/10")}
                        onClick={() => handleChange('solo', !player.solo)}
                        title="Solo"
                    >S</motion.button>
                    <motion.button
                        whileTap={{ scale: 0.9 }}
                        className={cn("w-6 h-6 rounded flex items-center justify-center text-[10px] font-bold border transition-colors", player.mute ? "bg-red-500 text-white border-red-500" : "bg-black/40 text-muted-foreground border-white/10 hover:bg-white/10")}
                        onClick={() => handleChange('mute', !player.mute)}
                        title="Mute"
                    >M</motion.button>
                </div>

                <div className="text-muted-foreground">
                    <motion.div
                        animate={{ rotate: expanded ? 90 : 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        <ChevronRight size={14} />
                    </motion.div>
                </div>
            </div>

            {/* Expanded View - All Controls */}
            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                    >
                        <div className="p-3 border-t border-white/5 space-y-6 bg-black/20">

                            {/* Main Sliders and Fader */}
                            <div className="flex gap-4">
                                {/* Left Side: Knobs for Pan & EQ */}
                                <div className="flex-1 space-y-4">

                                    {/* Pan & Stereo */}
                                    <div className="flex justify-between px-2">
                                        <Knob label="Pan" value={player.pan || 0} min={-1} max={1} step={0.05} onChange={v => handleChange('pan', v)} size={36}
                                            format={v => v === 0 ? 'C' : v < 0 ? `L${Math.abs(Math.round(v * 100))}` : `R${Math.round(v * 100)}`}
                                        />
                                        <Knob label="Width" value={player.stereo_width || 1} min={0} max={2} step={0.1} onChange={v => handleChange('stereo_width', v)} size={36} unit="%" format={v => Math.round(v * 100)} />
                                    </div>

                                    {/* EQ Section */}
                                    <div className="space-y-2">
                                        <h4 className="text-[9px] font-bold text-primary/50 uppercase tracking-wider text-center border-b border-primary/10 pb-1">Equalizer</h4>
                                        <div className="grid grid-cols-3 gap-1">
                                            <Knob label="Low" value={player.eq_low || 0} min={-15} max={15} onChange={v => handleChange('eq_low', v)} unit="dB" size={32} />
                                            <Knob label="Mid" value={player.eq_mid || 0} min={-15} max={15} onChange={v => handleChange('eq_mid', v)} unit="dB" size={32} />
                                            <Knob label="High" value={player.eq_high || 0} min={-15} max={15} onChange={v => handleChange('eq_high', v)} unit="dB" size={32} />
                                        </div>
                                    </div>

                                    {/* Sends */}
                                    <div className="space-y-2">
                                        <h4 className="text-[9px] font-bold text-primary/50 uppercase tracking-wider text-center border-b border-primary/10 pb-1">Sends</h4>
                                        <div className="grid grid-cols-2 gap-2">
                                            <Knob label="Reverb" value={player.reverb || 0} min={0} max={1} step={0.01} onChange={v => handleChange('reverb', v)} unit="%" format={v => Math.round(v * 100)} size={32} />
                                            <Knob label="Delay" value={player.delay || 0} min={0} max={1} step={0.01} onChange={v => handleChange('delay', v)} unit="%" format={v => Math.round(v * 100)} size={32} />
                                        </div>
                                    </div>
                                </div>

                                {/* Right Side: Main Fader */}
                                <div className="w-16 flex justify-center border-l border-white/5 pl-2 gap-2">
                                    <Meter value={meterValue} className="w-2 h-[200px]" />
                                    <Fader
                                        label="Vol"
                                        value={player.volume}
                                        onChange={v => handleChange('volume', v)}
                                        height={200}
                                        min={0} max={1} step={0.01}
                                    />
                                </div>
                            </div>

                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

export default ChannelStrip;
