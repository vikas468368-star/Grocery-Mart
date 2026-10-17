import React, { createContext, useContext, useState, useMemo } from 'react';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [cart, setCart] = useState([]);
  const [discountPercent, setDiscountPercent] = useState(0);
  const [discountFixed, setDiscountFixed] = useState(0);
  const [customer, setCustomer] = useState({ name: 'Walk-in Customer', phone: '', points: 0 });
  const [lastCompletedOrder, setLastCompletedOrder] = useState(null);
  const [isReceiptModalOpen, setIsReceiptModalOpen] = useState(false);

  // Add item to cart
  const addToCart = (product, qty = 1) => {
    setCart((prev) => {
      const existingIndex = prev.findIndex((item) => item.product_id === product.id || item.barcode === product.barcode);
      if (existingIndex > -1) {
        const updated = [...prev];
        const newQty = updated[existingIndex].quantity + qty;
        updated[existingIndex] = {
          ...updated[existingIndex],
          quantity: Math.round(newQty * 100) / 100,
        };
        return updated;
      }
      return [
        ...prev,
        {
          product_id: product.id,
          product_name: product.name,
          unit_price: product.price,
          quantity: qty,
          unit: product.unit || 'pcs',
          tax_rate: product.tax_rate ?? 0.05,
          barcode: product.barcode,
          category: product.category_name || product.category || 'General',
        },
      ];
    });
  };

  // Update item quantity
  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart((prev) =>
      prev.map((item) =>
        item.product_id === productId ? { ...item, quantity: Math.round(newQuantity * 100) / 100 } : item
      )
    );
  };

  // Remove single line item
  const removeFromCart = (productId) => {
    setCart((prev) => prev.filter((item) => item.product_id !== productId));
  };

  // Clear entire cart
  const clearCart = () => {
    setCart([]);
    setDiscountPercent(0);
    setDiscountFixed(0);
  };

  // Calculations
  const totals = useMemo(() => {
    const subtotal = cart.reduce((acc, item) => acc + item.unit_price * item.quantity, 0);
    const taxTotal = cart.reduce((acc, item) => acc + item.unit_price * item.quantity * item.tax_rate, 0);
    const percentAmount = (subtotal * discountPercent) / 100;
    const discountTotal = percentAmount + Number(discountFixed);
    const grandTotal = Math.max(0, subtotal + taxTotal - discountTotal);
    const totalUnits = cart.reduce((acc, item) => acc + item.quantity, 0);

    return {
      subtotal: Math.round(subtotal * 100) / 100,
      taxTotal: Math.round(taxTotal * 100) / 100,
      discountTotal: Math.round(discountTotal * 100) / 100,
      grandTotal: Math.round(grandTotal * 100) / 100,
      itemCount: cart.length,
      totalUnits: Math.round(totalUnits * 100) / 100,
    };
  }, [cart, discountPercent, discountFixed]);

  return (
    <CartContext.Provider
      value={{
        cart,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        discountPercent,
        setDiscountPercent,
        discountFixed,
        setDiscountFixed,
        customer,
        setCustomer,
        totals,
        lastCompletedOrder,
        setLastCompletedOrder,
        isReceiptModalOpen,
        setIsReceiptModalOpen,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
