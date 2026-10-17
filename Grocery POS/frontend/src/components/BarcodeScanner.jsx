import React, { useState, useRef, useEffect } from 'react';
import { ScanBarcode, Plus, Zap, AlertCircle } from 'lucide-react';
import { getProductByBarcode } from '../api/productsApi';
import { useCart } from '../context/CartContext';

const QUICK_SAMPLE_BARCODES = [
  { barcode: '890100000001', name: 'Gala Apples 1kg', price: 190 },
  { barcode: '890100000007', name: 'Bananas 1kg', price: 55 },
  { barcode: '890100000061', name: 'Country Tomatoes', price: 35 },
  { barcode: '890100000131', name: 'Amul Milk 1L', price: 54 },
  { barcode: '890100000186', name: 'Basmati Rice 1kg', price: 215 },
  { barcode: '890100000296', name: 'Fortune Oil 1L', price: 135 },
  { barcode: '890100000416', name: 'Tata Tea Gold', price: 325 },
  { barcode: '890100000471', name: 'Good Day Cookies', price: 45 },
];

export default function BarcodeScanner() {
  const [barcodeInput, setBarcodeInput] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [scanFlash, setScanFlash] = useState(false);
  const inputRef = useRef(null);
  const { addToCart } = useCart();

  useEffect(() => {
    // Keep focus ready for barcode scanner hardware guns
    inputRef.current?.focus();

    // Listen for hardware barcode event from Electron if active
    if (window.electronAPI?.onBarcodeScan) {
      const unsubscribe = window.electronAPI.onBarcodeScan((scannedCode) => {
        handleLookupAndAdd(scannedCode);
      });
      return () => unsubscribe();
    }
  }, []);

  const handleLookupAndAdd = async (code) => {
    const trimmed = (code || barcodeInput).trim();
    if (!trimmed) return;

    setErrorMsg('');
    try {
      const product = await getProductByBarcode(trimmed);
      addToCart(product, 1);
      setBarcodeInput('');
      setScanFlash(true);
      setTimeout(() => setScanFlash(false), 300);
      inputRef.current?.focus();
    } catch (err) {
      setErrorMsg(`Barcode "${trimmed}" not recognized in database catalog.`);
      setTimeout(() => setErrorMsg(''), 3500);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleLookupAndAdd();
    }
  };

  return (
    <div className={`barcode-scanner-bar ${scanFlash ? 'scan-flash' : ''}`}>
      <div className="scanner-input-wrapper">
        <ScanBarcode className="scanner-icon" size={24} />
        <input
          ref={inputRef}
          type="text"
          className="scanner-input"
          placeholder="Scan barcode gun or type code and press Enter (e.g. 890100000001)..."
          value={barcodeInput}
          onChange={(e) => setBarcodeInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className="scanner-submit-btn"
          onClick={() => handleLookupAndAdd()}
        >
          <Plus size={18} />
          <span>Add Item</span>
        </button>
      </div>

      {errorMsg && (
        <div className="scanner-error">
          <AlertCircle size={14} />
          <span>{errorMsg}</span>
        </div>
      )}

      <div className="quick-scan-chips">
        <span className="chips-label">
          <Zap size={13} /> Quick Barcode Scan:
        </span>
        {QUICK_SAMPLE_BARCODES.map((item) => (
          <button
            key={item.barcode}
            className="chip-btn"
            onClick={() => handleLookupAndAdd(item.barcode)}
            title={`Scan ${item.name} (${item.barcode})`}
          >
            {item.name} <span className="chip-price">₹{item.price}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
