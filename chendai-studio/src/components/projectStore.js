import { create } from 'zustand';

export const useProjectStore = create((set) => ({
    // Project state
    projectName: 'Untitled Project',
    isDirty: false,

    // Generation parameters
    pattern: 'panchari',
    duration: 30,
    strategy: 'traditional',

    // Players
    players: [
        { id: 'P1', name: 'Lead Player', role: 'lead', volume: 0.8, pan: -0.3, solo: false, mute: false },
        { id: 'P2', name: 'Rhythm Player', role: 'rhythm', volume: 0.7, pan: 0.3, solo: false, mute: false },
        { id: 'P3', name: 'Elathaalam 1', role: 'elathaalam_1', volume: 0.6, pan: -0.5, solo: false, mute: false },
        { id: 'P4', name: 'Elathaalam 2', role: 'elathaalam_2', volume: 0.6, pan: 0.5, solo: false, mute: false },
    ],

    // Playback state
    isPlaying: false,
    isGenerating: false,
    currentTime: 0,
    audioPath: null,
    audioFilename: null,

    // Actions
    setPattern: (pattern) => set({ pattern, isDirty: true }),
    setDuration: (duration) => set({ duration, isDirty: true }),
    setStrategy: (strategy) => set({ strategy, isDirty: true }),

    updatePlayer: (id, updates) => set((state) => ({
        players: state.players.map(p => p.id === id ? { ...p, ...updates } : p),
        isDirty: true
    })),

    setIsPlaying: (isPlaying) => set({ isPlaying }),
    setIsGenerating: (isGenerating) => set({ isGenerating }),
    setCurrentTime: (currentTime) => set({ currentTime }),
    setAudioPath: (audioPath) => set({ audioPath }),

    generateMelam: async (naturalPrompt = null) => {
        set({ isGenerating: true });
        try {
            const state = useProjectStore.getState();

            // Build parameters based on mode
            const params = naturalPrompt ? {
                prompt: naturalPrompt,
                duration: state.duration
            } : {
                pattern: state.pattern,
                duration: state.duration,
                strategy: state.strategy
            };

            console.log('Generating with params:', params);

            // Call backend API directly (web version)
            const response = await fetch('http://localhost:8000/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Generation result:', result);

            if (result && result.success) {
                // Extract filename from path
                const filename = result.audioPath.split('\\').pop().split('/').pop();
                const audioUrl = `http://localhost:8000/api/audio/${filename}`;

                console.log('Audio URL:', audioUrl);

                set({
                    audioPath: audioUrl,
                    audioFilename: filename,
                    isGenerating: false
                });
                return result;
            } else {
                throw new Error(result?.error || 'Generation failed');
            }
        } catch (error) {
            console.error('Generation failed:', error);
            set({ isGenerating: false });
            throw error;
        }
    }
}));
