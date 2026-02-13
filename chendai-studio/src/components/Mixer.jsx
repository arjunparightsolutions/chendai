import React from 'react';
import ChannelStrip from './ChannelStrip';
import { useProjectStore } from '../store/projectStore';
import { VolumeX } from 'lucide-react';

function Mixer() {
    const { players } = useProjectStore();

    return (
        <div className="flex flex-col h-full bg-surface">
            <div className="flex-1 overflow-y-auto overflow-x-hidden p-2 space-y-2">
                {players.map(player => (
                    <ChannelStrip key={player.id} player={player} />
                ))}
            </div>

            <div className="mt-auto border-t border-white/5 bg-background/50 p-4 sticky bottom-0 backdrop-blur-sm">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Master Out</span>
                    <VolumeX size={14} className="text-muted-foreground hover:text-red-500 cursor-pointer" />
                </div>
                {/* Master Meter Placeholder */}
                <div className="flex gap-1 h-32 justify-center">
                    <div className="w-4 bg-black rounded-full overflow-hidden relative border border-white/10">
                        <div className="absolute bottom-0 w-full bg-gradient-to-t from-green-500 via-yellow-500 to-red-500 h-[70%] opacity-80"></div>
                    </div>
                    <div className="w-4 bg-black rounded-full overflow-hidden relative border border-white/10">
                        <div className="absolute bottom-0 w-full bg-gradient-to-t from-green-500 via-yellow-500 to-red-500 h-[70%] opacity-80"></div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Mixer;
