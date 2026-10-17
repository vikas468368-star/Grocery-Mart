import React, { useState, useEffect } from 'react';
import {
  X,
  CheckCircle,
  Banknote,
  CreditCard,
  QrCode,
  Split,
  User,
  AlertTriangle,
  ReceiptText,
  Check,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import { useCart } from '../context/CartContext';
import { processCheckout } from '../api/billingApi';

const PAYMENT_METHODS = [
  { id: 'CASH', label: 'Cash', icon: Banknote, desc: 'Paper currency & coin' },
  { id: 'CARD', label: 'Card', icon: CreditCard, desc: 'Debit / Credit / POS' },
  { id: 'UPI', label: 'UPI / QR', icon: QrCode, desc: 'GPay, PhonePe, Paytm' },
  { id: 'SPLIT', label: 'Split', icon: Split, desc: 'Multi-tender payment' },
];

export default function CheckoutModal({ isOpen, onClose }) {
  const {
    cart,
    totals,
    clearCart,
    discountPercent,
    discountFixed,
    setLastCompletedOrder,
    setIsReceiptModalOpen,
    customer,
  } = useCart();

  const [paymentMethod, setPaymentMethod] = useState('CASH');
  const [tenderedAmount, setTenderedAmount] = useState(totals.grandTotal);
  const [customerPhone, setCustomerPhone] = useState(customer.phone || '');
  const [customerName, setCustomerName] = useState(customer.name || 'Walk-in Customer');
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Card & UPI Reference Numbers
  const [cardRef, setCardRef] = useState('');
  const [upiRef, setUpiRef] = useState('');

  // Split Payment Allocations
  const [splitCash, setSplitCash] = useState(0);
  const [splitCard, setSplitCard] = useState(0);
  const [splitUpi, setSplitUpi] = useState(0);

  useEffect(() => {
    if (isOpen) {
      setTenderedAmount(totals.grandTotal);
      setErrorMsg('');
      setCardRef(`AUTH-${Math.floor(100000 + Math.random() * 900000)}`);
      setUpiRef(`UPI-${Date.now().toString().slice(-8)}`);

      // Initialize split default (50/50 Cash & Card)
      const half = Math.round((totals.grandTotal / 2) * 100) / 100;
      setSplitCash(half);
      setSplitCard(Math.round((totals.grandTotal - half) * 100) / 100);
      setSplitUpi(0);
    }
  }, [isOpen, totals.grandTotal]);

  if (!isOpen) return null;

  // Split Calculations
  const splitTotal = Math.round((Number(splitCash || 0) + Number(splitCard || 0) + Number(splitUpi || 0)) * 100) / 100;
  const splitRemaining = Math.round((totals.grandTotal - splitTotal) * 100) / 100;
  const isSplitBalanced = Math.abs(splitRemaining) < 0.01;

  // Cash change due
  const changeDue = Math.max(0, Number(tenderedAmount || 0) - totals.grandTotal);

  const handleQuickCash = (amt) => {
    setTenderedAmount(amt);
  };

  const handleSplitPreset = (type) => {
    if (type === '50_50_CARD') {
      const half = Math.round((totals.grandTotal / 2) * 100) / 100;
      setSplitCash(half);
      setSplitCard(Math.round((totals.grandTotal - half) * 100) / 100);
      setSplitUpi(0);
    } else if (type === '50_50_UPI') {
      const half = Math.round((totals.grandTotal / 2) * 100) / 100;
      setSplitCash(half);
      setSplitCard(0);
      setSplitUpi(Math.round((totals.grandTotal - half) * 100) / 100);
    } else if (type === 'BALANCE_CASH') {
      setSplitCash(Math.max(0, Math.round((totals.grandTotal - splitCard - splitUpi) * 100) / 100));
    } else if (type === 'BALANCE_CARD') {
      setSplitCard(Math.max(0, Math.round((totals.grandTotal - splitCash - splitUpi) * 100) / 100));
    } else if (type === 'BALANCE_UPI') {
      setSplitUpi(Math.max(0, Math.round((totals.grandTotal - splitCash - splitCard) * 100) / 100));
    }
  };

  const handleConfirmPayment = async () => {
    setErrorMsg('');

    // Validations
    if (paymentMethod === 'CASH' && Number(tenderedAmount || 0) < totals.grandTotal) {
      setErrorMsg(`Tendered cash (₹${Number(tenderedAmount || 0).toFixed(2)}) is less than total amount due (₹${totals.grandTotal.toFixed(2)}).`);
      return;
    }

    if (paymentMethod === 'SPLIT' && !isSplitBalanced) {
      setErrorMsg(`Split payments must equal total grand amount (₹${totals.grandTotal.toFixed(2)}). Currently allocated: ₹${splitTotal.toFixed(2)}.`);
      return;
    }

    setIsProcessing(true);
    try {
      // Build split breakdown if applicable
      const splitBreakdown = [];
      if (paymentMethod === 'SPLIT') {
        if (Number(splitCash) > 0) {
          splitBreakdown.push({
            method: 'CASH',
            amount: Number(splitCash),
            tendered_amount: Number(splitCash),
          });
        }
        if (Number(splitCard) > 0) {
          splitBreakdown.push({
            method: 'CARD',
            amount: Number(splitCard),
            transaction_reference: cardRef || 'CARD-POS',
          });
        }
        if (Number(splitUpi) > 0) {
          splitBreakdown.push({
            method: 'UPI',
            amount: Number(splitUpi),
            transaction_reference: upiRef || 'UPI-APP',
          });
        }
      }

      const orderPayload = {
        cashier_name: 'Cashier #01',
        customer_name: customerName,
        customer_phone: customerPhone,
        payment_method: paymentMethod,
        discount_percent: discountPercent || 0,
        discount_fixed: discountFixed || 0,
        subtotal: totals.subtotal,
        tax_amount: totals.taxTotal,
        discount_amount: totals.discountTotal,
        total_amount: totals.grandTotal,
        tendered_amount: paymentMethod === 'CASH' ? Number(tenderedAmount) : totals.grandTotal,
        change_amount: paymentMethod === 'CASH' ? changeDue : 0,
        split_breakdown: paymentMethod === 'SPLIT' ? splitBreakdown : undefined,
        notes: `Processed via ${paymentMethod} payment`,
        items: cart.map((item) => ({
          product_id: item.product_id,
          product_name: item.product_name,
          barcode: item.barcode,
          unit_price: item.unit_price,
          quantity: item.quantity,
          unit: item.unit,
          tax_rate: item.tax_rate,
          discount_amount: 0,
        })),
      };

      const result = await processCheckout(orderPayload);

      // Record for receipt modal view
      setLastCompletedOrder({
        ...result,
        items: cart,
        tendered_amount: paymentMethod === 'CASH' ? Number(tenderedAmount) : totals.grandTotal,
        change_amount: paymentMethod === 'CASH' ? changeDue : 0,
        payment_method: paymentMethod,
        split_breakdown: result.split_breakdown || (paymentMethod === 'SPLIT' ? splitBreakdown : null),
        status: 'Paid',
      });

      clearCart();
      onClose();
      setIsReceiptModalOpen(true);
    } catch (err) {
      setErrorMsg(err.message || 'Payment processing failed. Please check inventory stock.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card checkout-modal" style={{ maxWidth: '560px' }}>
        <div className="modal-header">
          <div>
            <h3>Payment & Receipt Checkout</h3>
            <span className="modal-subtitle">Total Due: ₹{totals.grandTotal.toFixed(2)}</span>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {errorMsg && (
            <div
              className="checkout-error-banner"
              style={{
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid #ef4444',
                color: '#fca5a5',
                padding: '12px 14px',
                borderRadius: '8px',
                marginBottom: '10px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontSize: '13px',
                lineHeight: '1.4',
              }}
            >
              <AlertTriangle size={20} style={{ color: '#ef4444', flexShrink: 0 }} />
              <div>
                <strong style={{ color: '#f87171' }}>Payment Error: </strong>
                {errorMsg}
              </div>
            </div>
          )}

          {/* Payment Method Selector Grid */}
          <div className="form-group">
            <label className="form-label">Select Payment Mode</label>
            <div className="payment-options-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
              {PAYMENT_METHODS.map((method) => {
                const IconComponent = method.icon;
                const isActive = paymentMethod === method.id;
                return (
                  <button
                    key={method.id}
                    className={`payment-method-card ${isActive ? 'active' : ''}`}
                    onClick={() => {
                      setPaymentMethod(method.id);
                      setErrorMsg('');
                    }}
                    style={{ padding: '12px 6px', textAlign: 'center' }}
                  >
                    <IconComponent size={22} />
                    <span style={{ fontSize: '13px', fontWeight: '700' }}>{method.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* CASH MODE */}
          {paymentMethod === 'CASH' && (
            <div className="cash-calculation-section">
              <label className="form-label">Tendered Cash Amount</label>
              <div className="cash-input-row">
                <span className="input-currency">₹</span>
                <input
                  type="number"
                  className="form-input cash-input"
                  value={tenderedAmount}
                  onChange={(e) => setTenderedAmount(Number(e.target.value))}
                  step="1"
                  autoFocus
                />
              </div>

              {/* Quick Cash Chips */}
              <div className="quick-bill-chips">
                <button className="bill-chip" onClick={() => handleQuickCash(totals.grandTotal)}>
                  Exact (₹{totals.grandTotal.toFixed(2)})
                </button>
                {[100, 200, 500, 1000, 2000].map((bill) => (
                  <button key={bill} className="bill-chip" onClick={() => handleQuickCash(bill)}>
                    ₹{bill}
                  </button>
                ))}
              </div>

              {/* Change Output */}
              <div className="change-display-box">
                <span className="change-label">Change to Return to Customer:</span>
                <span className="change-value">₹{changeDue.toFixed(2)}</span>
              </div>
            </div>
          )}

          {/* CARD MODE */}
          {paymentMethod === 'CARD' && (
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#60a5fa' }}>
                <ShieldCheck size={24} />
                <div>
                  <h4 style={{ margin: 0, fontSize: '14px', color: '#fff' }}>POS Card Terminal Ready</h4>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Swipe, Tap, or Insert Chip Card into Card Reader
                  </span>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Card Authorization / Approval Code</label>
                <input
                  type="text"
                  className="form-input"
                  value={cardRef}
                  onChange={(e) => setCardRef(e.target.value)}
                  placeholder="e.g. AUTH-982143"
                />
              </div>
              <div style={{ fontSize: '12px', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Check size={14} /> Ready to Charge ₹{totals.grandTotal.toFixed(2)}
              </div>
            </div>
          )}

          {/* UPI MODE */}
          {paymentMethod === 'UPI' && (
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                <div
                  style={{
                    background: '#fff',
                    padding: '8px',
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '100px',
                    height: '100px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                  }}
                >
                  <QrCode size={84} color="#111827" />
                </div>
                <div>
                  <h4 style={{ margin: 0, fontSize: '14px', color: '#fff' }}>Scan & Pay with Any UPI App</h4>
                  <p style={{ margin: '4px 0', fontSize: '12px', color: 'var(--accent-emerald)', fontWeight: 'bold' }}>
                    emeraldgrocery@icici
                  </p>
                  <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                    Supports Google Pay, PhonePe, Paytm, BHIM, CRED
                  </span>
                  <div style={{ marginTop: '6px', fontSize: '13px', fontWeight: 'bold', color: '#60a5fa' }}>
                    Amount: ₹{totals.grandTotal.toFixed(2)}
                  </div>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">UPI Reference / UTR Number</label>
                <input
                  type="text"
                  className="form-input"
                  value={upiRef}
                  onChange={(e) => setUpiRef(e.target.value)}
                  placeholder="e.g. 320194829182"
                />
              </div>
            </div>
          )}

          {/* SPLIT PAYMENT MODE */}
          {paymentMethod === 'SPLIT' && (
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-md)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '13px', fontWeight: '700', color: '#fff' }}>
                  Split Payment Breakdown
                </span>
                <span
                  style={{
                    fontSize: '11px',
                    padding: '3px 8px',
                    borderRadius: '12px',
                    background: isSplitBalanced ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    color: isSplitBalanced ? '#34d399' : '#f87171',
                    fontWeight: 'bold',
                  }}
                >
                  {isSplitBalanced ? '✓ Balanced' : `Pending: ₹${splitRemaining.toFixed(2)}`}
                </span>
              </div>

              {/* Split inputs */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                <div>
                  <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Banknote size={14} /> Cash (₹)
                  </label>
                  <input
                    type="number"
                    className="form-input"
                    value={splitCash}
                    onChange={(e) => setSplitCash(Number(e.target.value))}
                    step="1"
                    min="0"
                  />
                </div>
                <div>
                  <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <CreditCard size={14} /> Card (₹)
                  </label>
                  <input
                    type="number"
                    className="form-input"
                    value={splitCard}
                    onChange={(e) => setSplitCard(Number(e.target.value))}
                    step="1"
                    min="0"
                  />
                </div>
                <div>
                  <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <QrCode size={14} /> UPI (₹)
                  </label>
                  <input
                    type="number"
                    className="form-input"
                    value={splitUpi}
                    onChange={(e) => setSplitUpi(Number(e.target.value))}
                    step="1"
                    min="0"
                  />
                </div>
              </div>

              {/* Quick Split Presets */}
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                <button type="button" className="bill-chip" onClick={() => handleSplitPreset('50_50_CARD')}>
                  50/50 Cash + Card
                </button>
                <button type="button" className="bill-chip" onClick={() => handleSplitPreset('50_50_UPI')}>
                  50/50 Cash + UPI
                </button>
                <button type="button" className="bill-chip" onClick={() => handleSplitPreset('BALANCE_CARD')}>
                  Fill Rest to Card
                </button>
                <button type="button" className="bill-chip" onClick={() => handleSplitPreset('BALANCE_UPI')}>
                  Fill Rest to UPI
                </button>
              </div>

              {/* Allocation Summary */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '8px 12px',
                  background: 'var(--bg-input)',
                  borderRadius: '6px',
                  fontSize: '12px',
                }}
              >
                <span>Allocated: <strong>₹{splitTotal.toFixed(2)}</strong></span>
                <span>Total Due: <strong>₹{totals.grandTotal.toFixed(2)}</strong></span>
              </div>
            </div>
          )}

          {/* Customer Loyalty / Phone Section */}
          <div className="form-group customer-section">
            <label className="form-label">Customer Contact (For Loyalty Points & SMS Receipt)</label>
            <div className="customer-input-row">
              <User size={18} className="input-icon" />
              <input
                type="tel"
                placeholder="+91 98765 43210 (Optional)"
                className="form-input"
                value={customerPhone}
                onChange={(e) => setCustomerPhone(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose} disabled={isProcessing}>
            Cancel
          </button>
          <button
            className="btn-primary confirm-pay-btn"
            onClick={handleConfirmPayment}
            disabled={isProcessing}
            style={{
              background: 'linear-gradient(135deg, #10b981, #059669)',
              padding: '11px 22px',
              fontSize: '14px',
              fontWeight: '700',
            }}
          >
            {isProcessing ? (
              <span>Recording Payment...</span>
            ) : (
              <>
                <ReceiptText size={18} />
                <span>
                  Record Payment & Print Receipt (₹{totals.grandTotal.toFixed(2)})
                </span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
