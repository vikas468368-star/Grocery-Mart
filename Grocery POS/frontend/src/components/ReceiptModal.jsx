import React, { useRef, useEffect } from 'react';
import { Printer, ArrowLeft, CheckCircle2 } from 'lucide-react';
import { useReactToPrint } from 'react-to-print';
import { useCart } from '../context/CartContext';

export default function ReceiptModal() {
  const { isReceiptModalOpen, setIsReceiptModalOpen, lastCompletedOrder } = useCart();
  const receiptRef = useRef(null);

  const handlePrint = useReactToPrint({
    contentRef: receiptRef,
    documentTitle: `Receipt-${lastCompletedOrder?.invoice_number || 'Sale'}`,
    pageStyle: `
      @page {
        size: 80mm auto;
        margin: 3mm;
      }
      @media print {
        body {
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .thermal-receipt {
          box-shadow: none !important;
          margin: 0 !important;
          padding: 8px !important;
          width: 100% !important;
        }
      }
    `,
  });

  const handleClose = () => {
    setIsReceiptModalOpen(false);
  };

  // Keyboard shortcut: Press Enter or P to print, Esc to close
  useEffect(() => {
    if (!isReceiptModalOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'p' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        handlePrint();
      } else if (e.key === 'Escape') {
        handleClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isReceiptModalOpen, handlePrint]);

  if (!isReceiptModalOpen || !lastCompletedOrder) return null;

  const order = lastCompletedOrder;
  const items = order.items || [];
  const splitBreakdown = order.split_breakdown || [];

  // Compute CGST and SGST splits for tax transparency
  const totalTax = Number(order.tax_amount || 0);
  const cgst = Math.round((totalTax / 2) * 100) / 100;
  const sgst = Math.round((totalTax - cgst) * 100) / 100;

  return (
    <div className="modal-backdrop">
      <div className="modal-card receipt-modal" style={{ maxWidth: '440px' }}>
        <div className="receipt-actions-header">
          <button className="btn-secondary" onClick={handleClose}>
            <ArrowLeft size={16} />
            <span>New Sale (Esc)</span>
          </button>
          <button
            className="btn-primary"
            onClick={handlePrint}
            style={{
              background: 'linear-gradient(135deg, #10b981, #059669)',
              gap: '8px',
              fontWeight: '700',
            }}
          >
            <Printer size={16} />
            <span>Print Receipt</span>
          </button>
        </div>

        {/* Printable Thermal Receipt Container */}
        <div className="thermal-receipt" id="printable-receipt" ref={receiptRef}>
          {/* Store Header Details */}
          <div className="receipt-center">
            <h2 className="receipt-store-title">EMERALD GROCERY MART</h2>
            <p className="receipt-store-sub">124 Market Avenue, Suite #4, Metro City</p>
            <p className="receipt-store-sub">GSTIN: 27AABCE1234F1Z8 | FSSAI: 11518018000452</p>
            <p className="receipt-store-sub">Tel: +91 98200 12345 | Web: emeraldgrocery.in</p>
            <div className="receipt-divider">================================</div>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '11px',
                fontWeight: '900',
                letterSpacing: '1px',
                padding: '2px 8px',
                border: '1px solid #111827',
                borderRadius: '3px',
                margin: '4px 0',
              }}
            >
              <CheckCircle2 size={12} />
              <span>TAX INVOICE - PAID</span>
            </div>
            <div className="receipt-divider">================================</div>
          </div>

          {/* Invoice Metadata Grid */}
          <div className="receipt-meta-grid">
            <div>
              <span>Invoice: </span>
              <strong>{order.invoice_number || 'INV-2026-001'}</strong>
            </div>
            <div>
              <span>Date: </span>
              <span>{new Date(order.created_at || Date.now()).toLocaleDateString()}</span>
            </div>
            <div>
              <span>Cashier: </span>
              <span>{order.cashier_name || 'Cashier #01'}</span>
            </div>
            <div>
              <span>Time: </span>
              <span>{new Date(order.created_at || Date.now()).toLocaleTimeString()}</span>
            </div>
            {order.customer_name && (
              <div style={{ gridColumn: 'span 2' }}>
                <span>Customer: </span>
                <span>{order.customer_name}</span>
                {order.customer_phone ? ` (${order.customer_phone})` : ''}
              </div>
            )}
          </div>

          <div className="receipt-divider">--------------------------------</div>

          {/* Items Table */}
          <table className="receipt-items-table">
            <thead>
              <tr>
                <th className="th-item">Item Description</th>
                <th className="th-qty">Qty</th>
                <th className="th-rate">Rate</th>
                <th className="th-total">Total</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, idx) => {
                const lineTotal = item.unit_price * item.quantity;
                return (
                  <tr key={idx}>
                    <td className="td-item">
                      <div>{item.product_name}</div>
                      <div style={{ fontSize: '9px', color: '#6b7280' }}>
                        Tax: {Math.round((item.tax_rate ?? 0.05) * 100)}%
                      </div>
                    </td>
                    <td className="td-qty">
                      {item.quantity} {item.unit || 'pcs'}
                    </td>
                    <td className="td-rate">₹{Number(item.unit_price).toFixed(2)}</td>
                    <td className="td-total">₹{Number(lineTotal).toFixed(2)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          <div className="receipt-divider">--------------------------------</div>

          {/* Totals & Tax Breakdowns */}
          <div className="receipt-totals-list">
            <div className="receipt-line">
              <span>Subtotal:</span>
              <span>₹{Number(order.subtotal || 0).toFixed(2)}</span>
            </div>

            {Number(order.discount_amount || 0) > 0 && (
              <div className="receipt-line" style={{ fontWeight: 'bold' }}>
                <span>Discount Savings:</span>
                <span>-₹{Number(order.discount_amount).toFixed(2)}</span>
              </div>
            )}

            <div className="receipt-line">
              <span>CGST:</span>
              <span>₹{cgst.toFixed(2)}</span>
            </div>

            <div className="receipt-line">
              <span>SGST:</span>
              <span>₹{sgst.toFixed(2)}</span>
            </div>

            <div className="receipt-divider">================================</div>

            <div className="receipt-line receipt-grand-total">
              <strong>TOTAL GRAND AMOUNT:</strong>
              <strong>₹{Number(order.total_amount).toFixed(2)}</strong>
            </div>

            <div className="receipt-divider">================================</div>

            {/* Payment Method & Payment Breakdown */}
            <div className="receipt-line">
              <span>Payment Mode:</span>
              <strong>{order.payment_method || 'CASH'}</strong>
            </div>

            {/* Split Payment Breakdown */}
            {order.payment_method === 'SPLIT' && splitBreakdown.length > 0 && (
              <div
                style={{
                  background: '#f8fafc',
                  border: '1px dashed #94a3b8',
                  padding: '6px',
                  borderRadius: '4px',
                  margin: '4px 0',
                }}
              >
                <div style={{ fontSize: '10px', fontWeight: 'bold', marginBottom: '3px' }}>
                  Split Payment Breakdown:
                </div>
                {splitBreakdown.map((part, i) => (
                  <div
                    key={i}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '10px',
                    }}
                  >
                    <span>• {part.method}:</span>
                    <span>
                      ₹{Number(part.amount).toFixed(2)}
                      {part.transaction_reference ? ` (Ref: ${part.transaction_reference})` : ''}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Cash Tendered & Change Returned */}
            {(order.payment_method === 'CASH' || order.tendered_amount) && (
              <>
                <div className="receipt-line">
                  <span>Amount Tendered:</span>
                  <span>₹{Number(order.tendered_amount || order.total_amount).toFixed(2)}</span>
                </div>
                <div className="receipt-line">
                  <span>Change Returned:</span>
                  <span>₹{Number(order.change_amount || 0).toFixed(2)}</span>
                </div>
              </>
            )}

            <div className="receipt-line" style={{ marginTop: '2px' }}>
              <span>Payment Status:</span>
              <strong style={{ color: '#059669' }}>PAID IN FULL</strong>
            </div>
          </div>

          {/* Receipt Footer */}
          <div className="receipt-center receipt-footer-section">
            <p className="barcode-mockup">||| ||||| ||| |||| |||||| |||| ||</p>
            <p className="barcode-digits">*{order.invoice_number || 'INV-2026-001'}*</p>
            <p className="thank-you-text">Thank you for shopping at Emerald Grocery!</p>
            <p className="receipt-policy">
              Exchange within 7 days with original invoice. GST inclusive prices.
            </p>
            <p style={{ fontSize: '9px', color: '#9ca3af', marginTop: '4px' }}>
              System Powered by Antigravity POS Engine
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
