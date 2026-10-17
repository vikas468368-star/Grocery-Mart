import { apiFetch } from './client';

export async function calculateBill(items, discountPercent = 0, discountFixed = 0, taxRateOverride = null) {
  try {
    return await apiFetch('/billing/calculate', {
      method: 'POST',
      body: JSON.stringify({
        items,
        discount_percent: discountPercent,
        discount_fixed: discountFixed,
        tax_rate_override: taxRateOverride,
      }),
    });
  } catch {
    // Client-side fallback calculation
    const subtotal = items.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
    const taxTotal = items.reduce((sum, item) => sum + (item.unit_price * item.quantity * (taxRateOverride ?? item.tax_rate ?? 0.05)), 0);
    const discount = (subtotal * (discountPercent / 100)) + discountFixed;
    const grandTotal = Math.max(0, subtotal + taxTotal - discount);
    const totalQty = items.reduce((sum, item) => sum + item.quantity, 0);

    return {
      subtotal: Math.round(subtotal * 100) / 100,
      tax_total: Math.round(taxTotal * 100) / 100,
      discount_total: Math.round(discount * 100) / 100,
      grand_total: Math.round(grandTotal * 100) / 100,
      item_count: items.length,
      total_quantity: Math.round(totalQty * 100) / 100,
    };
  }
}

export async function generateBill(billData) {
  return await apiFetch('/billing/generate-bill', {
    method: 'POST',
    body: JSON.stringify(billData),
  });
}

export async function processCheckout(orderData) {
  try {
    return await generateBill(orderData);
  } catch (err) {
    // If it's an insufficient stock error, re-throw immediately so user is notified
    if (err.message && (err.message.includes('Insufficient stock') || err.message.includes('unavailable'))) {
      throw err;
    }
    // Fallback to orders checkout
    return await apiFetch('/orders/checkout', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  }
}

export async function getOrders() {
  try {
    return await apiFetch('/orders/');
  } catch {
    return [];
  }
}

export async function recordPayment(paymentData) {
  return await apiFetch('/payments/record', {
    method: 'POST',
    body: JSON.stringify(paymentData),
  });
}

export async function getPayments() {
  try {
    return await apiFetch('/payments/');
  } catch {
    return [];
  }
}

export async function getSalePayments(saleId) {
  try {
    return await apiFetch(`/payments/sale/${saleId}`);
  } catch {
    return [];
  }
}

export async function getSalesHistory(search = '', statusFilter = '') {
  try {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (statusFilter) params.append('status_filter', statusFilter);
    const queryStr = params.toString() ? `?${params.toString()}` : '';
    return await apiFetch(`/sales/${queryStr}`);
  } catch {
    return [];
  }
}

export async function getSaleDetail(saleId) {
  return await apiFetch(`/sales/${saleId}`);
}

export async function processReturn(returnData) {
  return await apiFetch('/returns/process', {
    method: 'POST',
    body: JSON.stringify(returnData),
  });
}

export async function getReturnHistory() {
  try {
    return await apiFetch('/returns/');
  } catch {
    return [];
  }
}


