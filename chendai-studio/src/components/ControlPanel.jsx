import React, { useState } from 'react';
import { useProjectStore } from '../store/projectStore';
import { Play, Sparkles, Music, Mic2, Download, HelpCircle } from 'lucide-react';
import { cn } from '../utils/cn';

function ControlPanel() {
    const { pattern, duration, strategy, setPattern, setDuration, setStrategy, generateMelam } = useProjectStore();
    const [prompt, setPrompt] = useState('');
    const [usePrompt, setUsePrompt] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);

    const handleGenerate = async () => {
        setIsGenerating(true);
        try {
            await generateMelam(usePrompt ? prompt : null);
        } catch (error) {
            alert('Generation failed: ' + error.message);
            console.error('Generation error:', error);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="flex flex-col gap-6">
            {/* Composition Section */}
            <div className="space-y-4">
                <div className="flex items-center gap-2 text-primary">
                    <Music size={16} />
                    <h2 className="text-sm font-bold uppercase tracking-wider">Composition</h2>
                </div>

                <div className="p-4 rounded-xl bg-surface/50 border border-white/5 space-y-4">
                    {/* Mode Toggle */}
                    <div className="flex items-center gap-2 mb-4">
                        <button
                            onClick={() => setUsePrompt(false)}
                            className={cn(
                                "flex-1 text-xs font-medium py-2 rounded-lg transition-colors border",
                                !usePrompt ? "bg-primary/20 text-primary border-primary/20" : "bg-transparent text-muted-foreground border-transparent hover:bg-white/5"
                            )}
                        >
                            Pattern Mode
                        </button>
                        <button
                            onClick={() => setUsePrompt(true)}
                            className={cn(
                                "flex-1 text-xs font-medium py-2 rounded-lg transition-colors border",
                                usePrompt ? "bg-primary/20 text-primary border-primary/20" : "bg-transparent text-muted-foreground border-transparent hover:bg-white/5"
                            )}
                        >
                            AI Prompt
                        </button>
                    </div>

                    {usePrompt ? (
                        <div className="space-y-2 animate-in fade-in slide-in-from-top-2 duration-200">
                            <label className="text-[10px] uppercase text-muted-foreground font-bold">Describe Music</label>
                            <textarea
                                className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-primary/50 transition-colors resize-none"
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="E.g., High energy temple festival with heavy chenda rolls..."
                                rows={4}
                            />
                        </div>
                    ) : (
                        <div className="space-y-4 animate-in fade-in slide-in-from-top-2 duration-200">
                            <div className="space-y-1">
                                <label className="text-[10px] uppercase text-muted-foreground font-bold">Rhythm Style</label>
                                <select
                                    value={pattern}
                                    onChange={(e) => setPattern(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50"
                                >
                                    <option value="panchari">🥁 Panchari Melam (Temple)</option>
                                    <option value="pandi">⚡ Pandi Melam (Powerful)</option>
                                    <option value="thayambaka">🎯 Thayambaka (Solo)</option>
                                    <option value="panchavadyam">🎺 Panchavadyam</option>
                                </select>
                            </div>

                            <div className="space-y-1">
                                <label className="text-[10px] uppercase text-muted-foreground font-bold">Orchestration</label>
                                <select
                                    value={strategy}
                                    onChange={(e) => setStrategy(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50"
                                >
                                    <option value="traditional">🏛️ Traditional</option>
                                    <option value="dynamic">⚡ Dynamic Variations</option>
                                    <option value="unison">🤝 Unison</option>
                                    <option value="antiphonal">🔄 Call & Response</option>
                                    <option value="layered">📚 Progressive Layers</option>
                                </select>
                            </div>

                            <div className="space-y-1">
                                <label className="text-[10px] uppercase text-muted-foreground font-bold">Duration: {duration}s</label>
                                <input
                                    type="range"
                                    min="5"
                                    max="300"
                                    step="5"
                                    value={duration}
                                    onChange={(e) => setDuration(Number(e.target.value))}
                                    className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
                                />
                            </div>
                        </div>
                    )}

                    <button
                        onClick={handleGenerate}
                        disabled={isGenerating}
                        className="w-full py-3 bg-gradient-to-r from-primary to-accent rounded-lg text-black font-bold text-sm shadow-lg shadow-primary/20 hover:shadow-primary/40 hover:brightness-110 transition-all flex items-center justify-center gap-2 group"
                    >
                        <Sparkles size={16} className={cn("transition-transform", isGenerating ? "animate-spin" : "group-hover:scale-110")} />
                        {isGenerating ? 'Composing...' : 'Generate Music'}
                    </button>
                </div>
            </div>

            {/* AI Insights Display */}
            <MetadataDisplay />

            <ExportSection />

            {/* Pro Tips */}
            <div className="p-4 rounded-xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20">
                <div className="flex items-center gap-2 mb-2 text-indigo-400">
                    <HelpCircle size={14} />
                    <h3 className="text-xs font-bold uppercase">Pro Tips</h3>
                </div>
                <ul className="text-xs text-muted-foreground space-y-1 list-disc pl-4">
                    <li>Use headphones for spatial audio</li>
                    <li>Try "Dynamic" mode for variety</li>
                    <li>Export to FLAC for mastering</li>
                </ul>
            </div>
        </div>
    );
}

function MetadataDisplay() {
    const metadata = useProjectStore(state => state.metadata);

    if (!metadata) return null;

    return (
        <div className="space-y-2 animate-in slide-in-from-left-4 duration-300">
            <div className="flex items-center gap-2 text-primary">
                <Sparkles size={16} />
                <h2 className="text-sm font-bold uppercase tracking-wider">AI Insights</h2>
            </div>
            <div className="p-4 rounded-xl bg-surface/50 border border-white/5 space-y-2">
                <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Style</span>
                    <span className="text-foreground font-medium">{metadata.style}</span>
                </div>
                <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Orchestration</span>
                    <span className="text-foreground font-medium">{metadata.orchestration}</span>
                </div>
                <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">BPM</span>
                    <span className="text-foreground font-medium">{metadata.bpm}</span>
                </div>
                <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Total Events</span>
                    <span className="text-foreground font-medium">{metadata.total_events} notes</span>
                </div>
            </div>
        </div>
    );
}

function ExportSection() {
    const { audioPath, exportAudio } = useProjectStore(state => ({
        audioPath: state.audioPath,
        exportAudio: state.exportAudio
    }));
    const [format, setFormat] = useState('mp3');
    const [isExporting, setIsExporting] = useState(false);

    if (!audioPath) return null;

    const handleExport = async () => {
        setIsExporting(true);
        try {
            const result = await exportAudio({
                format,
                normalize: true
            });
            const link = document.createElement('a');
            link.href = result.download_url;
            link.download = result.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (err) {
            alert(err.message);
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <div className="space-y-2 animate-in slide-in-from-left-4 duration-300">
            <div className="flex items-center gap-2 text-primary">
                <Download size={16} />
                <h2 className="text-sm font-bold uppercase tracking-wider">Export</h2>
            </div>

            <div className="p-4 rounded-xl bg-surface/50 border border-white/5 space-y-3">
                <select
                    value={format}
                    onChange={e => setFormat(e.target.value)}
                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50"
                >
                    <option value="mp3">MP3 (High Quality)</option>
                    <option value="wav">WAV (Lossless)</option>
                    <option value="flac">FLAC (Lossless)</option>
                </select>
                <button
                    onClick={handleExport}
                    disabled={isExporting}
                    className="w-full py-2 bg-surface hover:bg-white/5 border border-white/10 rounded-lg text-xs font-medium transition-colors flex items-center justify-center gap-2"
                >
                    {isExporting ? 'Converting...' : 'Download File'}
                </button>
            </div>
        </div>
    );
}

export default ControlPanel;
