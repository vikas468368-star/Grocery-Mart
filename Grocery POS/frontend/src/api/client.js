const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Initial fallback catalog in case backend is offline during early development
export const MOCK_PRODUCTS = [
  { id: 1, name: "Fresh Farm Whole Milk 1L", barcode: "890100000131", sku: "DAI-001", category: "Dairy & Eggs", price: 62.00, stock_quantity: 45.0, unit: "pcs", tax_rate: 0.05 },
  { id: 2, name: "Artisan Sourdough Bread", barcode: "890100000161", sku: "BAK-001", category: "Bakery & Breads", price: 45.00, stock_quantity: 20.0, unit: "pcs", tax_rate: 0.05 },
  { id: 3, name: "Organic Farm Brown Eggs (Pack of 12)", barcode: "890100000135", sku: "DAI-005", category: "Dairy & Eggs", price: 95.00, stock_quantity: 30.0, unit: "pack", tax_rate: 0.05 },
  { id: 4, name: "Crisp Royal Gala Apples 1kg", barcode: "890100000001", sku: "FRU-001", category: "Fresh Fruits", price: 190.00, stock_quantity: 50.5, unit: "kg", tax_rate: 0.00 },
  { id: 5, name: "Cavendish Bananas 1kg", barcode: "890100000007", sku: "FRU-007", category: "Fresh Fruits", price: 55.00, stock_quantity: 40.0, unit: "kg", tax_rate: 0.00 },
  { id: 6, name: "Premium Basmati Rice 5kg", barcode: "890100000186", sku: "GRA-001", category: "Rice & Flours", price: 480.00, stock_quantity: 25.0, unit: "pack", tax_rate: 0.05 },
  { id: 7, name: "Fortune Sunlite Refined Oil 1L", barcode: "890100000296", sku: "OIL-001", category: "Cooking Oils & Ghee", price: 135.00, stock_quantity: 35.0, unit: "pcs", tax_rate: 0.05 },
  { id: 8, name: "Tata Tea Gold 500g", barcode: "890100000416", sku: "BEV-001", category: "Beverages & Tea", price: 325.00, stock_quantity: 40.0, unit: "pcs", tax_rate: 0.12 },
  { id: 9, name: "Britannia Good Day Butter Cookies", barcode: "890100000471", sku: "SNK-001", category: "Snacks & Biscuits", price: 45.00, stock_quantity: 60.0, unit: "pcs", tax_rate: 0.18 },
  { id: 10, name: "Surf Excel Matic Front Load 1kg", barcode: "890100000551", sku: "HOU-001", category: "Cleaning & Household", price: 230.00, stock_quantity: 22.0, unit: "pcs", tax_rate: 0.18 },
];

export async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Attach stored JWT token if present
  const token = localStorage.getItem('pos_token');
  const authHeader = token ? { Authorization: `Bearer ${token}` } : {};

  try {
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...authHeader,
        ...(options.headers || {}),
      },
      ...options,
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP Error ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.warn(`[API] ${endpoint} request error:`, error.message);
    throw error;
  }
}

export { API_BASE_URL };
