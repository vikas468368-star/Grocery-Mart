import React, { useState, useEffect } from 'react';
import { X, RotateCcw, AlertTriangle, CheckCircle, PackagePlus, Banknote, CreditCard, QrCode } from 'lucide-react';
import { processReturn } from '../api/billingApi';

const RETURN_REASONS = [
  'Customer Changed Mind / Unopened',
  'Defective / Damaged Goods',
  'Expired / Spoiled Item',
  'Wrong Item Scanned by Cashier',
  'Price Discrepancy / Dissatisfied',
];

export default function ReturnModal({ sale, isOpen, onClose, onSuccess }) {
  if (!isOpen || !sale) return null;

  const [selectedItems, setSelectedItems] = useState({});
  const [refundMethod, setRefundMethod] = useState(sale.payment_method || 'CASH');
  const [commonReason, setCommonReason] = useState(RETURN_REASONS[0]);
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Initialize selectable items
  useEffect(() => {
    const initial = {};
    (sale.items || []).forEach((item) => {
      const alreadyReturned = item.returned_quantity || 0;
      const remaining = Math.max(0, item.quantity - alreadyReturned);
      if (remaining > 0) {
        initial[item.id] = {
          selected: false,
          sale_item_id: item.id,
          product_id: item.product_id,
          product_name: item.product_name,
          unit: item.unit || 'pcs',
          unit_price: item.unit_price,
          quantity: remaining,
          maxQuantity: remaining,
          reason: commonReason,
        };
      }
    });
    setSelectedItems(initial);
    setErrorMsg('');
  }, [sale, commonReason]);

  const handleToggleSelect = (itemId) => {
    setSelectedItems((prev) => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        selected: !prev[itemId].selected,
      },
    }));
  };

  const handleQtyChange = (itemId, newQty) => {
    const val = Math.max(1, Math.min(prevMax(itemId), Number(newQty)));
    setSelectedItems((prev) => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        quantity: val,
      },
    }));
  };

  const handleReasonChange = (itemId, reason) => {
    setSelectedItems((prev) => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        reason,
      },
    }));
  };

  const prevMax = (itemId) => {
    return selectedItems[itemId]?.maxQuantity || 1;
  };

  // Compute Refund Total
  const activeReturnList = Object.values(selectedItems).filter((it) => it.selected);
  const totalRefundAmount = activeReturnList.reduce(
    (sum, it) => sum + (it.unit_price * it.quantity),
    0
  );

  const handleSubmitReturn = async () => {
    setErrorMsg('');
    if (activeReturnList.length === 0) {
      setErrorMsg('Please select at least one item from the bill to return.');
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        sale_id: sale.id,
        invoice_number: sale.invoice_number,
        refund_method: refundMethod,
        notes: notes || `Customer return for ${sale.invoice_number}`,
        items: activeReturnList.map((it) => ({
          sale_item_id: it.sale_item_id,
          product_id: it.product_id,
          quantity: it.quantity,
          reason: it.reason || commonReason,
        })),
      };

      const result = await processReturn(payload);
      if (onSuccess) {
        onSuccess(result);
      }
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to process return.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card return-modal" style={{ maxWidth: '620px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <RotateCcw size={20} style={{ color: '#f59e0b' }} />
            <div>
              <h3 style={{ margin: 0 }}>Process Return & Refund</h3>
              <span className="modal-subtitle" style={{ color: '#cbd5e1' }}>
                Invoice: <strong>{sale.invoice_number}</strong> • Original Total: ₹{Number(sale.total_amount).toFixed(2)}
              </span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body" style={{ maxHeight: '65vh', overflowY: 'auto' }}>
          {errorMsg && (
            <div
              className="checkout-error-banner"
              style={{
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid #ef4444',
                color: '#fca5a5',
                padding: '10px 14px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '13px',
              }}
            >
              <AlertTriangle size={18} style={{ color: '#ef4444' }} />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Quick Info Bar */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '10px 14px',
              display: 'flex',
              justifyContent: 'space-between',
              fontSize: '12px',
              color: 'var(--text-muted)',
            }}
          >
            <span>Customer: <strong style={{ color: '#fff' }}>{sale.customer_name || 'Walk-in'}</strong></span>
            <span>Date: <strong style={{ color: '#fff' }}>{new Date(sale.created_at).toLocaleDateString()}</strong></span>
            <span>Payment Mode: <strong style={{ color: '#60a5fa' }}>{sale.payment_method}</strong></span>
          </div>

          {/* Selectable Items Table */}
          <div className="form-group">
            <label className="form-label">Select Items to Return from this Invoice</label>
            <div
              style={{
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                overflow: 'hidden',
                background: 'var(--bg-input)',
              }}
            >
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                <thead>
                  <tr style={{ background: 'rgba(255, 255, 255, 0.05)', textAlign: 'left', borderBottom: '1px solid var(--border-color)' }}>
                    <th style={{ padding: '8px 10px', width: '36px' }}>Select</th>
                    <th style={{ padding: '8px 10px' }}>Product</th>
                    <th style={{ padding: '8px 10px', width: '90px' }}>Return Qty</th>
                    <th style={{ padding: '8px 10px', textAlign: 'right' }}>Unit Rate</th>
                    <th style={{ padding: '8px 10px', textAlign: 'right' }}>Refund</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.keys(selectedItems).length === 0 ? (
                    <tr>
                      <td colSpan="5" style={{ padding: '16px', textAlign: 'center', color: 'var(--text-dim)' }}>
                        All items from this invoice have already been returned.
                      </td>
                    </tr>
                  ) : (
                    Object.values(selectedItems).map((it) => {
                      const isChecked = it.selected;
                      const lineRefund = it.unit_price * it.quantity;
                      return (
                        <React.Fragment key={it.sale_item_id}>
                          <tr
                            style={{
                              borderBottom: '1px solid rgba(255,255,255,0.05)',
                              background: isChecked ? 'rgba(245, 158, 11, 0.08)' : 'transparent',
                            }}
                          >
                            <td style={{ padding: '10px' }}>
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => handleToggleSelect(it.sale_item_id)}
                                style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                              />
                            </td>
                            <td style={{ padding: '10px' }}>
                              <strong style={{ color: '#fff' }}>{it.product_name}</strong>
                              <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                                Max returnable: {it.maxQuantity} {it.unit}
                              </div>
                            </td>
                            <td style={{ padding: '10px' }}>
                              <input
                                type="number"
                                className="form-input"
                                disabled={!isChecked}
                                min="1"
                                max={it.maxQuantity}
                                value={it.quantity}
                                onChange={(e) => handleQtyChange(it.sale_item_id, e.target.value)}
                                style={{
                                  padding: '4px 8px',
                                  fontSize: '13px',
                                  textAlign: 'center',
                                  width: '70px',
                                  opacity: isChecked ? 1 : 0.4,
                                }}
                              />
                            </td>
                            <td style={{ padding: '10px', textAlign: 'right' }}>
                              ₹{it.unit_price.toFixed(2)}
                            </td>
                            <td style={{ padding: '10px', textAlign: 'right', fontWeight: 'bold', color: isChecked ? '#f59e0b' : 'inherit' }}>
                              ₹{lineRefund.toFixed(2)}
                            </td>
                          </tr>
                          {isChecked && (
                            <tr style={{ background: 'rgba(245, 158, 11, 0.04)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                              <td colSpan="5" style={{ padding: '6px 12px 10px 42px' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
                                  <span style={{ color: 'var(--text-muted)' }}>Reason:</span>
                                  <select
                                    className="form-input"
                                    value={it.reason}
                                    onChange={(e) => handleReasonChange(it.sale_item_id, e.target.value)}
                                    style={{ padding: '4px 8px', fontSize: '12px', flex: 1 }}
                                  >
                                    {RETURN_REASONS.map((r) => (
                                      <option key={r} value={r}>
                                        {r}
                                      </option>
                                    ))}
                                  </select>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Refund Method & Inventory Notification */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="form-group">
              <label className="form-label">Refund Payment Mode</label>
              <select
                className="form-input"
                value={refundMethod}
                onChange={(e) => setRefundMethod(e.target.value)}
              >
                <option value="CASH">Cash Drawer Outflow</option>
                <option value="CARD">Reverse to Card (Card Refund)</option>
                <option value="UPI">Reverse to UPI / Bank Account</option>
                <option value="STORE_CREDIT">Issue Store Credit Voucher</option>
              </select>
            </div>

            <div
              style={{
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.25)',
                borderRadius: '8px',
                padding: '10px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '12px',
                color: '#34d399',
              }}
            >
              <PackagePlus size={20} style={{ flexShrink: 0 }} />
              <span>
                Inventory stock will be <strong>automatically added back</strong> to the Product table upon return confirmation.
              </span>
            </div>
          </div>

          {/* Refund Summary Bar */}
          <div
            style={{
              background: 'rgba(245, 158, 11, 0.15)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              borderRadius: '8px',
              padding: '12px 16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Selected Items for Return:</span>
              <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#fff' }}>
                {activeReturnList.length} items ({activeReturnList.reduce((acc, it) => acc + it.quantity, 0)} units)
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Total Reversal Amount:</span>
              <div style={{ fontSize: '20px', fontWeight: '900', color: '#f59e0b' }}>
                ₹{totalRefundAmount.toFixed(2)}
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </button>
          <button
            className="btn-primary"
            onClick={handleSubmitReturn}
            disabled={isSubmitting || activeReturnList.length === 0}
            style={{
              background: 'linear-gradient(135deg, #f59e0b, #d97706)',
              padding: '10px 20px',
              fontWeight: '700',
            }}
          >
            {isSubmitting ? (
              <span>Processing Return...</span>
            ) : (
              <>
                <RotateCcw size={16} />
                <span>Confirm Return & Refund (₹{totalRefundAmount.toFixed(2)})</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
