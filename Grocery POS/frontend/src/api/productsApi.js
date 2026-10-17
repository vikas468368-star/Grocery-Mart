import { apiFetch, MOCK_PRODUCTS } from './client';

export async function getProducts(search = '', category = '', limit = 700, skip = 0) {
  try {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (category && category !== 'All') params.append('category', category);
    params.append('limit', limit);
    params.append('skip', skip);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    return await apiFetch(`/products/${queryString}`);
  } catch {
    // Graceful offline mock fallback
    return MOCK_PRODUCTS.filter(p => {
      const matchSearch = !search || p.name.toLowerCase().includes(search.toLowerCase()) || p.barcode.includes(search);
      const matchCategory = !category || category === 'All' || (p.category_name || p.category || '').toLowerCase() === category.toLowerCase();
      return matchSearch && matchCategory;
    });
  }
}

export async function getProductByBarcode(barcode) {
  try {
    return await apiFetch(`/products/barcode/${barcode}`);
  } catch {
    const found = MOCK_PRODUCTS.find(p => p.barcode === barcode);
    if (found) return found;
    throw new Error(`Product with barcode ${barcode} not found`);
  }
}

export async function getLowStockProducts(threshold = null) {
  try {
    const query = threshold !== null ? `?threshold=${threshold}` : '';
    return await apiFetch(`/products/low-stock${query}`);
  } catch {
    return [];
  }
}

export async function createProduct(productData) {
  return await apiFetch('/products/', {
    method: 'POST',
    body: JSON.stringify(productData),
  });
}

export async function updateProduct(id, productData) {
  return await apiFetch(`/products/${id}`, {
    method: 'PUT',
    body: JSON.stringify(productData),
  });
}

export async function deleteProduct(id) {
  return await apiFetch(`/products/${id}`, {
    method: 'DELETE',
  });
}

// Categories API
export async function getCategories() {
  try {
    return await apiFetch('/categories/');
  } catch {
    return [
      { id: 1, name: "Fresh Fruits", code: "CAT-FRUITS", default_tax_rate: 0.00 },
      { id: 2, name: "Fresh Vegetables", code: "CAT-VEG", default_tax_rate: 0.00 },
      { id: 3, name: "Dairy & Eggs", code: "CAT-DAIRY", default_tax_rate: 0.05 },
      { id: 4, name: "Bakery & Breads", code: "CAT-BAKERY", default_tax_rate: 0.05 },
      { id: 5, name: "Rice & Flours", code: "CAT-GRAINS", default_tax_rate: 0.05 },
      { id: 6, name: "Pulses & Dals", code: "CAT-PULSES", default_tax_rate: 0.00 },
      { id: 7, name: "Cooking Oils & Ghee", code: "CAT-OILS", default_tax_rate: 0.05 },
      { id: 8, name: "Spices & Seasonings", code: "CAT-SPICES", default_tax_rate: 0.05 },
      { id: 9, name: "Beverages & Tea", code: "CAT-BEV", default_tax_rate: 0.12 },
      { id: 10, name: "Snacks & Biscuits", code: "CAT-SNACKS", default_tax_rate: 0.18 },
      { id: 11, name: "Cleaning & Household", code: "CAT-HOUSEHOLD", default_tax_rate: 0.18 },
      { id: 12, name: "Personal Care", code: "CAT-CARE", default_tax_rate: 0.18 },
    ];
  }
}

export async function createCategory(categoryData) {
  return await apiFetch('/categories/', {
    method: 'POST',
    body: JSON.stringify(categoryData),
  });
}

export async function updateCategory(id, categoryData) {
  return await apiFetch(`/categories/${id}`, {
    method: 'PUT',
    body: JSON.stringify(categoryData),
  });
}

export async function deleteCategory(id) {
  return await apiFetch(`/categories/${id}`, {
    method: 'DELETE',
  });
}
