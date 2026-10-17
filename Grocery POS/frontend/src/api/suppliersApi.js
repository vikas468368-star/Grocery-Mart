import { apiFetch } from './client';

export async function getSuppliers() {
  try {
    return await apiFetch('/suppliers/');
  } catch {
    return [];
  }
}

export async function getSupplier(id) {
  return await apiFetch(`/suppliers/${id}`);
}

export async function createSupplier(supplierData) {
  return await apiFetch('/suppliers/', {
    method: 'POST',
    body: JSON.stringify(supplierData),
  });
}

export async function updateSupplier(id, supplierData) {
  return await apiFetch(`/suppliers/${id}`, {
    method: 'PUT',
    body: JSON.stringify(supplierData),
  });
}

export async function deleteSupplier(id) {
  return await apiFetch(`/suppliers/${id}`, {
    method: 'DELETE',
  });
}

// Purchase Orders API
export async function getPurchaseOrders(supplierId = null) {
  try {
    const query = supplierId ? `?supplier_id=${supplierId}` : '';
    return await apiFetch(`/purchase-orders/${query}`);
  } catch {
    return [];
  }
}

export async function getPurchaseOrder(id) {
  return await apiFetch(`/purchase-orders/${id}`);
}

export async function createPurchaseOrder(poData) {
  return await apiFetch('/purchase-orders/', {
    method: 'POST',
    body: JSON.stringify(poData),
  });
}

export async function updatePurchaseOrderStatus(poId, status) {
  return await apiFetch(`/purchase-orders/${poId}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  });
}
