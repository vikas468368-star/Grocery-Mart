const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const fs = require('fs');

let mainWindow;

function getProductionHtmlPath() {
  const localDist = path.join(__dirname, 'dist', 'index.html');
  if (fs.existsSync(localDist)) return localDist;
  const monorepoDist = path.join(__dirname, '..', 'frontend', 'dist', 'index.html');
  if (fs.existsSync(monorepoDist)) return monorepoDist;
  return localDist;
}

function createWindow() {
  const iconPath = path.join(__dirname, 'assets', 'icon.png');
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 1024,
    minHeight: 700,
    title: 'Grocery POS - Retail Terminal',
    backgroundColor: '#0b0f19',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
    },
    icon: fs.existsSync(iconPath) ? iconPath : undefined,
    show: false,
  });

  // Check whether we are in dev mode or production build
  const devServerUrl = process.env.VITE_DEV_SERVER_URL || 'http://127.0.0.1:5173';
  const isDev = process.env.NODE_ENV === 'development' || (!app.isPackaged && !process.env.ELECTRON_FORCE_PACKAGED);

  if (isDev) {
    mainWindow.loadURL(devServerUrl).catch(() => {
      console.log(`Dev server at ${devServerUrl} not reachable, falling back to local HTML.`);
      const staticHtml = getProductionHtmlPath();
      if (fs.existsSync(staticHtml)) {
        mainWindow.loadFile(staticHtml);
      }
    });
  } else {
    mainWindow.loadFile(getProductionHtmlPath());
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle IPC commands from POS React frontend
  ipcMain.on('toggle-kiosk', () => {
    if (mainWindow) {
      mainWindow.setKiosk(!mainWindow.isKiosk());
    }
  });

  ipcMain.handle('print-receipt', async (event, content) => {
    console.log('[Desktop POS] Receipt print request received for invoice');
    // Silently print or open native print preview
    if (mainWindow) {
      mainWindow.webContents.print({
        silent: false,
        printBackground: true,
      });
      return { success: true };
    }
    return { success: false, error: 'Window not found' };
  });

  ipcMain.handle('get-app-version', () => {
    return app.getVersion();
  });
}

// App lifecycle
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
