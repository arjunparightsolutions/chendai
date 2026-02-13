import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Layout from './components/Layout';
import Timeline from './components/Timeline';
import Mixer from './components/Mixer';
import Transport from './components/Transport';
import ControlPanel from './components/ControlPanel';
import LogViewer from './components/LogViewer';
import { useProjectStore } from './store/projectStore';

function App() {
    const { isGenerating } = useProjectStore();

    return (
        <Layout>
            <div className="flex w-full h-full">
                {/* Left Panel - Browser/Controls */}
                <aside className="w-[280px] bg-surface border-r border-white/5 flex flex-col">
                    <div className="h-8 flex items-center px-4 border-b border-white/5 bg-white/5 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                        Library & Controls
                    </div>
                    <div className="flex-1 overflow-y-auto p-4">
                        <ControlPanel />
                    </div>
                </aside>

                {/* Center Panel - Arrangement */}
                <main className="flex-1 flex flex-col bg-background/50 relative">
                    <div className="h-8 flex items-center px-4 border-b border-white/5 bg-white/5 text-[10px] font-bold text-muted-foreground uppercase tracking-widest justify-between">
                        <span>Arrangement</span>
                        <span className="text-primary">120 BPM</span>
                    </div>
                    <div className="flex-1 overflow-hidden relative">
                        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
                        <Timeline />
                    </div>
                    <div className="h-[80px] border-t border-white/5 bg-surface z-10">
                        <Transport />
                    </div>
                </main>

                {/* Right Panel - Mixer/Inspector */}
                <aside className="w-[300px] bg-surface border-l border-white/5 flex flex-col">
                    <div className="h-8 flex items-center px-4 border-b border-white/5 bg-white/5 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                        Mixer & FX
                    </div>
                    <div className="flex-1 overflow-y-auto">
                        <Mixer />
                    </div>
                </aside>
            </div>

            {/* Generation Overlay */}
            <AnimatePresence>
                {isGenerating && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-surface border border-primary/20 p-8 rounded-xl shadow-2xl shadow-primary/10 flex flex-col items-center gap-6"
                        >
                            {/* Beating Drum Animation */}
                            <div className="relative flex items-center justify-center w-24 h-24">
                                <motion.div
                                    animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                                    transition={{ repeat: Infinity, duration: 1.5, ease: "easeOut" }}
                                    className="absolute inset-0 rounded-full border-2 border-primary/50"
                                />
                                <motion.div
                                    animate={{ scale: [1, 1.25, 1], opacity: [0.8, 0, 0.8] }}
                                    transition={{ repeat: Infinity, duration: 1.5, ease: "easeOut", delay: 0.2 }}
                                    className="absolute inset-2 rounded-full border border-primary/50"
                                />
                                <motion.div
                                    animate={{ scale: [1, 1.1, 1] }}
                                    transition={{ repeat: Infinity, duration: 0.4, ease: "easeInOut", repeatType: "reverse" }} // Fast beat
                                    className="relative z-10 w-16 h-16 rounded-full bg-gradient-to-br from-primary to-orange-600 shadow-lg shadow-primary/50 flex items-center justify-center text-3xl select-none"
                                >
                                    🥁
                                </motion.div>
                            </div>

                            <div className="text-center space-y-1">
                                <h3 className="text-xl font-bold text-white tracking-tight">Composing Ensemble...</h3>
                                <p className="text-muted-foreground text-sm">AI is orchestrating traditional patterns</p>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* AI Model Logs */}
            <LogViewer />
        </Layout>
    );
}

export default App;
