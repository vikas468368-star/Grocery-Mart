const { contextBridge, ipcRenderer } = require('electron');

// Expose safe, isolated APIs to the renderer process (React frontend)
contextBridge.exposeInMainWorld('electronAPI', {
  isElectron: true,
  platform: process.platform,
  
  // Thermal receipt printer bridge
  printReceipt: (content) => ipcRenderer.invoke('print-receipt', content),
  
  // Fullscreen / POS Kiosk mode
  toggleKiosk: () => ipcRenderer.send('toggle-kiosk'),
  
  // Barcode scanner hardware hook listener
  onBarcodeScan: (callback) => {
    const handler = (_event, barcode) => callback(barcode);
    ipcRenderer.on('barcode-scanned', handler);
    return () => ipcRenderer.removeListener('barcode-scanned', handler);
  },
  
  // App metadata
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
});
