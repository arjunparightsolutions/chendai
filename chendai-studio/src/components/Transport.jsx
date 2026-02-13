import React, { useRef, useEffect } from 'react';
import { useProjectStore } from '../store/projectStore';
import { Play, Pause, Square, Circle, SkipBack, SkipForward, Repeat } from 'lucide-react';
import { cn } from '../utils/cn';
import { motion } from 'framer-motion';

function Transport() {
    const { isPlaying, currentTime, duration, setIsPlaying, setCurrentTime, audioPath } = useProjectStore();
    const audioRef = useRef(null);

    // Create audio element when audioPath changes
    useEffect(() => {
        if (audioPath) {
            console.log('🎵 Loading audio from:', audioPath);

            // Clean up previous audio if exists
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current.src = '';
            }

            audioRef.current = new Audio();

            audioRef.current.addEventListener('timeupdate', () => {
                setCurrentTime(audioRef.current.currentTime);
            });

            audioRef.current.addEventListener('ended', () => {
                setIsPlaying(false);
                setCurrentTime(0);
            });

            audioRef.current.addEventListener('error', (e) => {
                console.error('❌ Audio loading failed:', audioRef.current.error);
                alert(`Failed to load audio. Connection refused?`);
            });

            // Set the source after adding listeners
            audioRef.current.src = audioPath;
            audioRef.current.load();
        }

        // Cleanup on unmount
        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current.src = '';
            }
        };
    }, [audioPath]);

    const handlePlay = () => {
        if (!audioPath || !audioRef.current) {
            alert('No audio loaded. Generate some music first!');
            return;
        }
        audioRef.current.play()
            .then(() => setIsPlaying(true))
            .catch(err => alert('Failed to play audio: ' + err.message));
    };

    const handlePause = () => {
        if (audioRef.current) {
            audioRef.current.pause();
            setIsPlaying(false);
        }
    };

    const handleStop = () => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
            setIsPlaying(false);
            setCurrentTime(0);
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="w-full h-full flex items-center justify-between px-6 bg-surface border-t border-white/5 shadow-2xl z-50">
            {/* Transport Controls */}
            <div className="flex items-center gap-4">
                <button className="text-muted-foreground hover:text-white transition-colors" disabled={!audioPath}>
                    <SkipBack size={20} />
                </button>
                <button
                    className="w-10 h-10 flex items-center justify-center rounded-full bg-surface border border-white/10 text-white hover:bg-white/5 transition-all"
                    onClick={handleStop}
                    disabled={!audioPath}
                >
                    <Square size={14} fill="currentColor" />
                </button>
                <motion.button
                    whileTap={{ scale: 0.95 }}
                    animate={isPlaying ? { scale: [1, 1.1, 1], boxShadow: ["0 0 0 0px rgba(251, 191, 36, 0)", "0 0 0 4px rgba(251, 191, 36, 0.2)", "0 0 0 0px rgba(251, 191, 36, 0)"] } : {}}
                    transition={isPlaying ? { repeat: Infinity, duration: 1.5, ease: "easeInOut" } : {}}
                    className={cn(
                        "w-12 h-12 flex items-center justify-center rounded-full transition-colors shadow-lg",
                        isPlaying
                            ? "bg-primary text-black"
                            : "bg-primary text-black hover:brightness-110 hover:shadow-primary/20"
                    )}
                    onClick={isPlaying ? handlePause : handlePlay}
                    disabled={!audioPath}
                >
                    {isPlaying ? <Pause size={24} fill="currentColor" /> : <Play size={24} fill="currentColor" className="ml-1" />}
                </motion.button>
                <button className="w-10 h-10 flex items-center justify-center rounded-full bg-surface border border-white/10 text-red-500 hover:bg-red-500/10 transition-all">
                    <Circle size={14} fill="currentColor" />
                </button>
                <button className="text-muted-foreground hover:text-white transition-colors" disabled={!audioPath}>
                    <Repeat size={18} />
                </button>
            </div>

            {/* Time Display */}
            <div className="flex flex-col items-center bg-black/40 px-6 py-2 rounded-lg border border-white/5 shadow-inner">
                <div className="text-2xl font-mono font-bold text-primary tracking-widest text-glow">
                    {formatTime(currentTime)}
                </div>
                <div className="text-[10px] text-muted-foreground font-mono tracking-wide">
                    / {formatTime(duration)}
                </div>
            </div>

            {/* Metronome / Settings Placeholder */}
            <div className="flex items-center gap-4 text-xs font-mono text-muted-foreground">
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-primary/50 animate-pulse"></span>
                    120.00 BPM
                </div>
                <div className="text-white/20">|</div>
                <div>4/4</div>
            </div>
        </div>
    );
}

export default Transport;
