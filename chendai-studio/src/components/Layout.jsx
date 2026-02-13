import React from 'react';
import { Settings, Play, Square, Mic, Volume2, Save, FolderOpen, MoreVertical } from 'lucide-react';
import { cn } from '../utils/cn'; // We need to create this utility

const Layout = ({ children }) => {
    return (
        <div className="flex flex-col h-screen w-screen bg-background text-foreground overflow-hidden font-sans select-none">
            {/* App Header */}
            <header className="h-[50px] bg-surface/50 border-b border-white/5 flex items-center justify-between px-4 backdrop-blur-sm z-50">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
                        <span className="text-black font-bold text-lg">C</span>
                    </div>
                    <div>
                        <h1 className="text-sm font-bold tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent/80 text-glow">
                            CHENDAI STUDIO
                        </h1>
                        <div className="text-[10px] text-muted-foreground tracking-wider font-mono">PRO EDITON V2.0</div>
                    </div>
                </div>

                <div className="flex items-center gap-1">
                    {['File', 'Edit', 'View', 'Track', 'Help'].map((item) => (
                        <button key={item} className="px-3 py-1 text-xs text-muted-foreground hover:text-primary hover:bg-white/5 rounded-md transition-colors">
                            {item}
                        </button>
                    ))}
                </div>

                <div className="flex items-center gap-2">
                    <button className="p-2 hover:bg-white/5 rounded-full text-muted-foreground hover:text-primary transition-colors">
                        <Settings size={16} />
                    </button>
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-zinc-700 to-zinc-800 border border-white/10"></div>
                </div>
            </header>

            {/* Main Workspace */}
            <main className="flex-1 flex overflow-hidden relative">
                {children}
            </main>

            {/* StatusBar / Footer */}
            <footer className="h-[28px] bg-black border-t border-white/5 flex items-center justify-between px-4 text-[10px] text-muted-foreground">
                <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-emerald-500"></span> ENGINE READY</span>
                    <span>CPU: 12%</span>
                    <span>RAM: 1.2GB</span>
                </div>
                <div className="flex items-center gap-4">
                    <span>MIDI: ONLINE</span>
                    <span>AUDIO: 48kHz / 24bit</span>
                </div>
            </footer>
        </div>
    );
};

export default Layout;
