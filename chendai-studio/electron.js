const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

// Check if running in development
const isDev = !app.isPackaged;

// Python backend server
let serverReady = false;
let serverReadyTimeout = null;

function startPythonServer() {
  return new Promise((resolve, reject) => {
    let scriptPath;
    let command;
    let args;

    if (isDev) {
      command = 'python';
      scriptPath = path.join(__dirname, '..', 'chendai_server.py');
      args = [scriptPath];
      console.log('🐍 Starting Python server (DEV):', scriptPath);
    } else {
      // In production, use the bundled executable
      scriptPath = path.join(process.resourcesPath, 'chendai_engine', 'chendai_engine.exe');
      command = scriptPath;
      args = [];
      console.log('🐍 Starting Python server (PROD):', scriptPath);
    }

    // Set timeout for server readiness (15 seconds)
    serverReadyTimeout = setTimeout(() => {
      if (!serverReady) {
        console.error('⚠️ Server did not respond with READY signal in time');
        reject(new Error('Backend server startup timeout'));
      }
    }, 15000);

    pythonProcess = spawn(command, args);

    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`[Backend] ${output}`);

      // Check for READY signal
      if (output.includes('ChendAI Studio API Server') || output.includes('Uvicorn running')) {
        console.log('✅ Backend server is READY!');
        serverReady = true;
        clearTimeout(serverReadyTimeout);
        resolve();
      }
    });

    pythonProcess.stderr.on('data', (data) => {
      const error = data.toString();
      console.error(`[Backend Error] ${error}`);

      // Check for critical errors
      if (error.includes('ModuleNotFoundError') || error.includes('ImportError')) {
        console.error('❌ Missing Python dependencies! Run: pip install -r requirements.txt');
        reject(new Error('Missing Python dependencies'));
      }
    });

    pythonProcess.on('close', (code) => {
      console.log(`Backend process exited with code ${code}`);
      serverReady = false;
      if (code !== 0) {
        reject(new Error(`Backend exited with code ${code}`));
      }
    });

    pythonProcess.on('error', (err) => {
      console.error('❌ Failed to start backend process:', err);

      if (err.code === 'ENOENT') {
        console.error('Python not found! Please install Python 3.8+ and add to PATH');
        reject(new Error('Python not found in system PATH'));
      } else {
        reject(err);
      }
    });
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    backgroundColor: '#1a1a2e',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'public', 'icon.png'),
    title: 'ChendAI Studio',
    show: false  // Don't show until ready
  });

  // Load React app
  if (isDev) {
    console.log('Loading dev URL: http://localhost:5173');
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    const indexPath = path.join(__dirname, 'dist', 'index.html');
    console.log('Loading production build:', indexPath);
    mainWindow.loadFile(indexPath);
  }

  console.log('ChendAI Studio - Running in', isDev ? 'DEVELOPMENT' : 'PRODUCTION', 'mode');

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Log when page loads
  mainWindow.webContents.on('did-finish-load', () => {
    console.log('Page loaded successfully');
  });
}

function createLoadingWindow() {
  const loadingWindow = new BrowserWindow({
    width: 600,
    height: 400,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  loadingWindow.loadFile(path.join(__dirname, 'loading.html'));
  loadingWindow.center();

  return loadingWindow;
}

// IPC Handlers
ipcMain.handle('generate-melam', async (event, params) => {
  try {
    console.log('IPC: Generating melam with params:', params);

    const response = await fetch('http://localhost:8000/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });

    const result = await response.json();
    console.log('IPC: Generation result:', result);
    return result;
  } catch (error) {
    console.error('IPC: Generation error:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('save-project', async (event, projectData) => {
  console.log('IPC: Saving project:', projectData.name);
  return { success: true };
});

ipcMain.handle('load-project', async (event, projectPath) => {
  console.log('IPC: Loading project:', projectPath);
  return { success: true };
});

// App lifecycle
app.whenReady().then(async () => {
  console.log('🚀 App is ready, starting Python server...');

  // Show loading screen
  let loadingWindow = null;
  try {
    loadingWindow = createLoadingWindow();
  } catch (err) {
    console.log('Could not create loading window:', err);
  }

  try {
    // Start Python server and wait for READY signal
    await startPythonServer();

    // Additional buffer to ensure server is fully initialized
    await new Promise(resolve => setTimeout(resolve, 2000));

    console.log('✅ Backend ready, creating window...');

    // Close loading window
    if (loadingWindow && !loadingWindow.isDestroyed()) {
      loadingWindow.close();
    }

    createWindow();
  } catch (error) {
    console.error('❌ Failed to start backend:', error);

    // Close loading window
    if (loadingWindow && !loadingWindow.isDestroyed()) {
      loadingWindow.close();
    }

    // Show error dialog to user
    const { dialog } = require('electron');
    const choice = await dialog.showMessageBox({
      type: 'error',
      title: 'Backend Startup Failed',
      message: 'ChendAI Studio failed to start the audio engine.',
      detail: error.message + '\n\nPossible solutions:\n' +
        '1. Install Python 3.8+: python.org/downloads\n' +
        '2. Install dependencies: pip install -r requirements.txt\n' +
        '3. Check if port 8000 is already in use\n\n' +
        'Would you like to try starting the app anyway?',
      buttons: ['Quit', 'Start Without Backend'],
      defaultId: 0
    });

    if (choice.response === 0) {
      app.quit();
    } else {
      // Start app without backend (limited functionality)
      console.log('⚠️ Starting in offline mode...');
      createWindow();
    }
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  console.log('All windows closed');
  if (pythonProcess) {
    pythonProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', () => {
  console.log('App quitting, killing Python process...');
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

app.on('will-quit', () => {
  console.log('App will quit');
  if (pythonProcess) {
    pythonProcess.kill();
  }
});
