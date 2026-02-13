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
    stems: {},
    metadata: null,
    logs: [],
    showLogs: false,

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
    setShowLogs: (showLogs) => set({ showLogs }),
    addLog: (message) => set((state) => ({ logs: [...state.logs.slice(-49), { id: Date.now(), text: message, time: new Date().toLocaleTimeString() }] })),
    clearLogs: () => set({ logs: [] }),
    setStems: (stems) => set({ stems }),

    generateMelam: async (naturalPrompt = null) => {
        set({ isGenerating: true, metadata: null, logs: [], showLogs: true });

        // Initialize WebSocket for logs
        const socket = new WebSocket('ws://localhost:8000/ws/logs');
        socket.onmessage = (event) => {
            useProjectStore.getState().addLog(event.data);
        };
        socket.onclose = () => console.log('Log WebSocket closed');

        try {
            const state = useProjectStore.getState();

            // Build parameters based on mode
            const playerParams = state.players.map(({ id, volume, pan, mute, solo }) => ({
                id, volume, pan, mute, solo
            }));

            const params = naturalPrompt ? {
                prompt: naturalPrompt,
                duration: state.duration,
                players: playerParams
            } : {
                pattern: state.pattern,
                duration: state.duration,
                strategy: state.strategy,
                players: playerParams
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
                // Extract filename from Windows path (handles both \ and /)
                const filename = result.audioPath.split('\\').pop().split('/').pop();
                const audioUrl = `http://localhost:8000/api/audio/${filename}`;

                // Process stems if available
                const stemUrls = {};
                if (result.stems) {
                    Object.entries(result.stems).forEach(([id, path]) => {
                        const stemFilename = path.split('\\').pop().split('/').pop();
                        stemUrls[id] = `http://localhost:8000/api/audio/${stemFilename}`;
                    });
                }

                console.log('✅ Audio filename:', filename);
                console.log('✅ Audio URL:', audioUrl);
                console.log('✅ Stems:', stemUrls);
                console.log('✅ Metadata:', result.metadata);

                set({
                    audioPath: audioUrl,
                    stems: stemUrls,
                    metadata: result.metadata,
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
    },

    exportAudio: async (exportParams) => {
        try {
            const state = useProjectStore.getState();
            if (!state.audioPath) throw new Error("No audio generated to export!");

            // Extract filename from current audio path
            // e.g., http://localhost:8000/api/audio/6player_Panchari_Melam_20260207.wav -> 6player_Panchari_Melam_20260207.wav
            const filename = state.audioPath.split('/').pop();

            console.log('Exporting audio:', { filename, ...exportParams });

            const response = await fetch('http://localhost:8000/api/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename,
                    ...exportParams
                })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || `Export failed: ${response.status}`);
            }

            const result = await response.json();
            console.log('Export success:', result);
            return result; // contains download_url

        } catch (error) {
            console.error('Export failed:', error);
            throw error;
        }
    }
}));

