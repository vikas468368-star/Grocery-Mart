import React, { useEffect } from 'react';
import { Trash2, Plus, Minus, Receipt, Percent, Tag, CreditCard, ShoppingCart, ReceiptText } from 'lucide-react';
import { useCart } from '../context/CartContext';

export default function CartPanel({ onOpenCheckout }) {
  const {
    cart,
    updateQuantity,
    removeFromCart,
    clearCart,
    discountPercent,
    setDiscountPercent,
    discountFixed,
    setDiscountFixed,
    totals,
  } = useCart();

  // Listen for F8 shortcut key to open bill checkout
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'F8' && cart.length > 0) {
        e.preventDefault();
        onOpenCheckout();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [cart, onOpenCheckout]);

  return (
    <aside className="pos-cart-panel">
      <div className="cart-header">
        <div className="cart-title">
          <Receipt size={20} className="title-icon" />
          <h3>Current Bill</h3>
          <span className="cart-count-badge">{totals.itemCount} items</span>
        </div>

        {cart.length > 0 && (
          <button className="clear-btn" onClick={clearCart} title="Clear all items">
            <Trash2 size={16} />
            <span>Reset</span>
          </button>
        )}
      </div>

      <div className="cart-items-list">
        {cart.length === 0 ? (
          <div className="empty-cart-state">
            <div className="cart-empty-icon">
              <ShoppingCart size={40} />
            </div>
            <h4>Cart is Empty</h4>
            <p>Scan a barcode or select items from the catalog on the left to start billing.</p>
          </div>
        ) : (
          cart.map((item) => {
            const lineTotal = item.unit_price * item.quantity;
            return (
              <div key={item.product_id || item.barcode} className="cart-item-row">
                <div className="item-main-info">
                  <span className="cart-item-name">{item.product_name}</span>
                  <span className="cart-item-sub">
                    ₹{item.unit_price.toFixed(2)} / {item.unit} • GST {Math.round(item.tax_rate * 100)}%
                  </span>
                </div>

                <div className="qty-controls">
                  <button
                    className="qty-btn"
                    onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                  >
                    <Minus size={13} />
                  </button>
                  <span className="qty-display">{item.quantity}</span>
                  <button
                    className="qty-btn"
                    onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                  >
                    <Plus size={13} />
                  </button>
                </div>

                <div className="item-price-col">
                  <span className="line-total">₹{lineTotal.toFixed(2)}</span>
                  <button
                    className="item-delete-btn"
                    onClick={() => removeFromCart(item.product_id)}
                    title="Remove item"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {cart.length > 0 && (
        <div className="cart-footer">
          {/* Quick Discount Selector */}
          <div className="discount-bar">
            <span className="discount-label">
              <Percent size={14} /> Discount:
            </span>
            <div className="discount-pills">
              {[0, 5, 10, 15].map((pct) => (
                <button
                  key={pct}
                  className={`disc-pill ${discountPercent === pct ? 'active' : ''}`}
                  onClick={() => {
                    setDiscountPercent(pct);
                    setDiscountFixed(0);
                  }}
                >
                  {pct === 0 ? 'None' : `${pct}%`}
                </button>
              ))}
              <button
                className={`disc-pill ${discountFixed === 50 ? 'active' : ''}`}
                onClick={() => {
                  setDiscountPercent(0);
                  setDiscountFixed(discountFixed === 50 ? 0 : 50);
                }}
              >
                ₹50 Off
              </button>
            </div>
          </div>

          {/* Totals Summary */}
          <div className="cart-summary">
            <div className="summary-row">
              <span>Subtotal ({totals.totalUnits} units)</span>
              <span>₹{totals.subtotal.toFixed(2)}</span>
            </div>
            <div className="summary-row">
              <span>Estimated Tax (GST)</span>
              <span>₹{totals.taxTotal.toFixed(2)}</span>
            </div>
            {totals.discountTotal > 0 && (
              <div className="summary-row discount-row">
                <span>Discount Applied</span>
                <span>-₹{totals.discountTotal.toFixed(2)}</span>
              </div>
            )}
            <div className="summary-row total-row">
              <span className="total-label">Grand Total</span>
              <span className="total-value">₹{totals.grandTotal.toFixed(2)}</span>
            </div>
          </div>

          {/* Checkout CTA */}
          <button
            className="checkout-cta-btn generate-bill-btn"
            onClick={onOpenCheckout}
            disabled={cart.length === 0}
          >
            <ReceiptText size={20} />
            <span>Generate Bill (F8) • ₹{totals.grandTotal.toFixed(2)}</span>
          </button>
        </div>
      )}
    </aside>
  );
}
