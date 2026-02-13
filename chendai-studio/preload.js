const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    generateMelam: (params) => ipcRenderer.invoke('generate-melam', params),
    saveProject: (projectData) => ipcRenderer.invoke('save-project', projectData),
    loadProject: (projectPath) => ipcRenderer.invoke('load-project', projectPath),

    // Subscribe to events
    onProgress: (callback) => {
        ipcRenderer.on('generation-progress', (event, data) => callback(data));
    },

    onError: (callback) => {
        ipcRenderer.on('error', (event, error) => callback(error));
    }
});
