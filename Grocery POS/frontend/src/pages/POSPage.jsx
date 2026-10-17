import React, { useState } from 'react';
import BarcodeScanner from '../components/BarcodeScanner';
import ProductCatalog from '../components/ProductCatalog';
import CartPanel from '../components/CartPanel';
import CheckoutModal from '../components/CheckoutModal';
import ReceiptModal from '../components/ReceiptModal';

export default function POSPage() {
  const [isCheckoutOpen, setIsCheckoutOpen] = useState(false);

  return (
    <div className="pos-page-layout">
      <div className="pos-main-column">
        {/* Top Rapid Barcode Scanner Bar */}
        <BarcodeScanner />

        {/* Product Catalog Grid */}
        <ProductCatalog />
      </div>

      {/* Right Billing Cart & Checkout Summary */}
      <CartPanel onOpenCheckout={() => setIsCheckoutOpen(true)} />

      {/* Checkout Modal */}
      <CheckoutModal
        isOpen={isCheckoutOpen}
        onClose={() => setIsCheckoutOpen(false)}
      />

      {/* Receipt Thermal Modal */}
      <ReceiptModal />
    </div>
  );
}
