import React, { useEffect, useRef } from 'react';
import { useProjectStore } from '../store/projectStore';
import { Terminal, X, ChevronDown, ChevronUp, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../utils/cn';

function LogViewer() {
    const { logs, showLogs, setShowLogs, clearLogs } = useProjectStore();
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    if (!showLogs && logs.length === 0) return null;

    return (
        <div className={cn(
            "fixed bottom-24 right-6 w-80 z-40 transition-all duration-300",
            !showLogs ? "h-10" : "h-[400px]"
        )}>
            <div className="bg-black/90 backdrop-blur-md border border-white/10 rounded-xl flex flex-col h-full shadow-2xl overflow-hidden">
                {/* Header */}
                <div
                    className="flex items-center justify-between px-3 py-2 bg-white/5 border-b border-white/10 cursor-pointer hover:bg-white/10 transition-colors"
                    onClick={() => setShowLogs(!showLogs)}
                >
                    <div className="flex items-center gap-2">
                        <Terminal size={14} className="text-primary" />
                        <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">Model Logs</span>
                        {logs.length > 0 && (
                            <span className="bg-primary/20 text-primary px-1.5 py-0.5 rounded text-[8px]">{logs.length}</span>
                        )}
                    </div>
                    <div className="flex items-center gap-1">
                        <button
                            onClick={(e) => { e.stopPropagation(); clearLogs(); }}
                            className="p-1 hover:bg-white/10 rounded text-muted-foreground hover:text-red-400 transition-colors"
                        >
                            <Trash2 size={12} />
                        </button>
                        {showLogs ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
                    </div>
                </div>

                {/* Logs Content */}
                <AnimatePresence>
                    {showLogs && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex-1 overflow-y-auto p-3 font-mono text-[10px] space-y-1.5 selection:bg-primary/30"
                            ref={scrollRef}
                        >
                            {logs.length === 0 ? (
                                <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-50 space-y-2">
                                    <Terminal size={24} />
                                    <p>Waiting for generation...</p>
                                </div>
                            ) : (
                                logs.map((log) => (
                                    <div key={log.id} className="animate-in fade-in slide-in-from-left-1 duration-200">
                                        <span className="text-muted-foreground/40 mr-2">[{log.time}]</span>
                                        <span className={cn(
                                            "leading-relaxed",
                                            log.text.includes('🤖') || log.text.includes('🧠') ? "text-primary italic" :
                                                log.text.includes('⚠️') ? "text-red-400" :
                                                    log.text.includes('✅') ? "text-green-400 font-bold" :
                                                        "text-muted-foreground"
                                        )}>
                                            {log.text}
                                        </span>
                                    </div>
                                ))
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}

export default LogViewer;
