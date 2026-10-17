import { useEffect, useRef } from 'react';

/**
 * Custom hook to capture hardware barcode scanner gun input.
 * Hardware scanners send characters rapidly (<35ms apart) ending with an 'Enter' key.
 */
export function useBarcodeScanner(onScan, options = {}) {
  const {
    minChars = 4,
    maxIntervalMs = 50,
    disabled = false,
  } = options;

  const bufferRef = useRef([]);
  const lastTimeRef = useRef(0);

  useEffect(() => {
    if (disabled || typeof onScan !== 'function') return;

    // Listen to native Electron hardware bridge if present
    if (window.electronAPI?.onBarcodeScan) {
      const unsubscribe = window.electronAPI.onBarcodeScan((scannedCode) => {
        if (scannedCode) onScan(scannedCode.trim());
      });
      return () => unsubscribe();
    }

    const handleKeyDown = (e) => {
      // Ignore if user is editing inside a regular text input/textarea UNLESS it's superhumanly fast
      const activeEl = document.activeElement;
      const isInput = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA');

      const currentTime = Date.now();
      const timeDiff = currentTime - lastTimeRef.current;
      lastTimeRef.current = currentTime;

      // Enter key marks end of barcode scan
      if (e.key === 'Enter') {
        if (bufferRef.current.length >= minChars) {
          const barcode = bufferRef.current.join('').trim();
          bufferRef.current = [];
          if (barcode) {
            e.preventDefault();
            onScan(barcode);
          }
          return;
        }
        bufferRef.current = [];
        return;
      }

      // If characters come in too slowly (> maxIntervalMs) and user is in an input, reset buffer
      if (timeDiff > maxIntervalMs && isInput && !activeEl.classList.contains('scanner-input')) {
        bufferRef.current = [];
        return;
      }

      // If it's a printable character
      if (e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
        // Reset buffer if idle time was too long (> 200ms)
        if (timeDiff > 200) {
          bufferRef.current = [];
        }
        bufferRef.current.push(e.key);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onScan, disabled, minChars, maxIntervalMs]);
}
