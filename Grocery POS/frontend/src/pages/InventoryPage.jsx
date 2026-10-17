import React, { useState, useEffect, useMemo } from 'react';
import {
  Package,
  Plus,
  Search,
  AlertTriangle,
  DollarSign,
  Edit2,
  Trash2,
  Barcode,
  Layers,
  Calendar,
  Filter,
  CheckCircle2,
  Boxes,
  RefreshCw,
  Copy,
  ScanBarcode,
} from 'lucide-react';
import { getProducts, deleteProduct, getCategories } from '../api/productsApi';
import ProductModal from '../components/ProductModal';
import { useBarcodeScanner } from '../hooks/useBarcodeScanner';

const ITEMS_PER_PAGE = 25;

export default function InventoryPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [stockFilter, setStockFilter] = useState('all'); // all, low, out, in_stock
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [productToEdit, setProductToEdit] = useState(null);
  const [copiedBarcode, setCopiedBarcode] = useState(null);
  const [scannedFeedback, setScannedFeedback] = useState('');

  // Hardware Barcode Scanner listener
  useBarcodeScanner((scannedCode) => {
    setSearch(scannedCode);
    setScannedFeedback(`Scanned barcode: ${scannedCode}`);
    setTimeout(() => setScannedFeedback(''), 3000);
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [prods, cats] = await Promise.all([getProducts('', 'All', 1000), getCategories()]);
      setProducts(prods || []);
      setCategories(cats || []);
    } catch (err) {
      console.warn('Failed loading inventory:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenAdd = () => {
    setProductToEdit(null);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (prod) => {
    setProductToEdit(prod);
    setIsModalOpen(true);
  };

  const handleDelete = async (prod) => {
    if (window.confirm(`Are you sure you want to deactivate "${prod.name}" (Barcode: ${prod.barcode})?`)) {
      try {
        await deleteProduct(prod.id);
        setProducts((prev) => prev.filter((p) => p.id !== prod.id));
      } catch (err) {
        alert(`Failed to delete product: ${err.message}`);
      }
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard?.writeText(text);
    setCopiedBarcode(text);
    setTimeout(() => setCopiedBarcode(null), 2000);
  };

  // Filter products locally for instant responsive UI across 655 items
  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      // Search
      const searchLower = search.toLowerCase();
      const matchSearch =
        !search ||
        p.name.toLowerCase().includes(searchLower) ||
        (p.barcode && p.barcode.includes(search)) ||
        (p.sku && p.sku.toLowerCase().includes(searchLower));

      // Category
      const catName = p.category_name || p.category || '';
      const matchCategory =
        selectedCategory === 'All' || catName.toLowerCase() === selectedCategory.toLowerCase();

      // Stock Status
      const qty = p.stock_quantity || 0;
      const threshold = p.min_stock_alert || 15;
      let matchStock = true;
      if (stockFilter === 'low') matchStock = qty <= threshold && qty > 0;
      else if (stockFilter === 'out') matchStock = qty === 0;
      else if (stockFilter === 'in_stock') matchStock = qty > threshold;

      return matchSearch && matchCategory && matchStock;
    });
  }, [products, search, selectedCategory, stockFilter]);

  // Pagination
  const totalPages = Math.ceil(filteredProducts.length / ITEMS_PER_PAGE) || 1;
  const paginatedProducts = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredProducts.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredProducts, currentPage]);

  // Overall Statistics
  const totalValue = products.reduce((sum, p) => sum + (p.price * (p.stock_quantity || 0)), 0);
  const lowStockItems = products.filter((p) => (p.stock_quantity || 0) <= (p.min_stock_alert || 15));
  const outOfStockItems = products.filter((p) => (p.stock_quantity || 0) === 0);

  return (
    <div className="inventory-page-container">
      {/* Top Stat Cards */}
      <div className="inventory-stats-grid">
        <div className="stat-card">
          <div className="stat-icon-wrapper blue">
            <Package size={22} />
          </div>
          <div>
            <span className="stat-title">Catalog Inventory</span>
            <h3 className="stat-number">{products.length} Products</h3>
          </div>
        </div>

        <div
          className={`stat-card cursor-pointer ${stockFilter === 'low' ? 'stat-active-filter' : ''}`}
          onClick={() => setStockFilter(stockFilter === 'low' ? 'all' : 'low')}
          title="Click to toggle low stock filter"
        >
          <div className="stat-icon-wrapper amber">
            <AlertTriangle size={22} />
          </div>
          <div>
            <span className="stat-title">Low Stock Alerts</span>
            <h3 className="stat-number text-amber">{lowStockItems.length} Items</h3>
          </div>
        </div>

        <div
          className={`stat-card cursor-pointer ${stockFilter === 'out' ? 'stat-active-filter' : ''}`}
          onClick={() => setStockFilter(stockFilter === 'out' ? 'all' : 'out')}
          title="Click to toggle out of stock filter"
        >
          <div className="stat-icon-wrapper red">
            <Boxes size={22} />
          </div>
          <div>
            <span className="stat-title">Out of Stock</span>
            <h3 className="stat-number text-red">{outOfStockItems.length} Items</h3>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper green">
            <DollarSign size={22} />
          </div>
          <div>
            <span className="stat-title">Retail Valuation</span>
            <h3 className="stat-number">₹{totalValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</h3>
          </div>
        </div>
      </div>

      {/* Barcode scanner scan alert */}
      {scannedFeedback && (
        <div className="scanned-feedback-toast">
          <ScanBarcode size={16} />
          <span>{scannedFeedback}</span>
        </div>
      )}

      {/* Action Toolbar */}
      <div className="inventory-toolbar">
        <div className="toolbar-left">
          {/* Search Bar */}
          <div className="search-box">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              className="scanner-input"
              placeholder="Search product name, barcode gun, or SKU..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setCurrentPage(1);
              }}
            />
            {search && (
              <button className="clear-search" onClick={() => setSearch('')}>
                ✕
              </button>
            )}
          </div>

          {/* Department Filter */}
          <div className="select-wrapper">
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setCurrentPage(1);
              }}
            >
              <option value="All">All Departments (12)</option>
              {categories.map((c) => (
                <option key={c.id} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Stock Filter */}
          <div className="select-wrapper">
            <select
              value={stockFilter}
              onChange={(e) => {
                setStockFilter(e.target.value);
                setCurrentPage(1);
              }}
            >
              <option value="all">All Stock Statuses</option>
              <option value="low">⚠️ Low Stock Alerts Only ({lowStockItems.length})</option>
              <option value="out">🔴 Out of Stock Only ({outOfStockItems.length})</option>
              <option value="in_stock">🟢 Healthy Stock Only</option>
            </select>
          </div>
        </div>

        <div className="toolbar-right">
          <button className="refresh-icon-btn" onClick={loadData} title="Reload catalog">
            <RefreshCw size={16} />
          </button>
          <button className="btn-primary add-product-btn add-product-action" onClick={handleOpenAdd}>
            <Plus size={16} />
            <span>Add Product</span>
          </button>
        </div>
      </div>

      {/* Low Stock Warning Banner if Low items exist */}
      {lowStockItems.length > 0 && stockFilter !== 'low' && (
        <div className="low-stock-alert-strip" onClick={() => setStockFilter('low')}>
          <AlertTriangle size={16} />
          <span>
            <strong>Inventory Alert:</strong> {lowStockItems.length} products have reached or dropped
            below their reorder threshold. <u>Click here to review low stock items.</u>
          </span>
        </div>
      )}

      {/* Main Data Table */}
      <div className="inventory-table-container">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <span>Loading product catalog data...</span>
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="table-empty">
            <Package size={44} className="empty-icon" />
            <h4>No products match your filter criteria</h4>
            <p>Try searching for a different keyword or resetting filters.</p>
          </div>
        ) : (
          <table className="inventory-table">
            <thead>
              <tr>
                <th>Product & SKU</th>
                <th>Department</th>
                <th>Barcode</th>
                <th>Stock Quantity</th>
                <th>Retail Price</th>
                <th>Cost Price</th>
                <th>Margin</th>
                <th>Expiry Date</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {paginatedProducts.map((p) => {
                const stockQty = p.stock_quantity || 0;
                const minThreshold = p.min_stock_alert || 15;
                const isOutOfStock = stockQty === 0;
                const isLowStock = !isOutOfStock && stockQty <= minThreshold;

                const cost = p.cost_price || 0;
                const price = p.price || 0;
                const margin = price > 0 ? Math.round(((price - cost) / price) * 100) : 0;

                return (
                  <tr key={p.id} className={isLowStock ? 'row-low-stock' : isOutOfStock ? 'row-out-stock' : ''}>
                    <td className="product-col">
                      <div className="product-title-cell">
                        <span className="product-table-name">{p.name}</span>
                        <span className="product-table-sku">SKU: {p.sku || 'N/A'}</span>
                      </div>
                    </td>

                    <td>
                      <span className="table-cat-badge">{p.category_name || p.category || 'General'}</span>
                    </td>

                    <td>
                      <div className="barcode-cell">
                        <Barcode size={14} className="barcode-icon" />
                        <span className="barcode-code">{p.barcode}</span>
                        <button
                          className="copy-barcode-btn"
                          onClick={() => copyToClipboard(p.barcode)}
                          title="Copy Barcode to Clipboard"
                        >
                          {copiedBarcode === p.barcode ? <CheckCircle2 size={12} className="text-green" /> : <Copy size={12} />}
                        </button>
                      </div>
                    </td>

                    <td>
                      <div className="stock-level-cell">
                        <span
                          className={`stock-badge ${
                            isOutOfStock ? 'stock-out' : isLowStock ? 'stock-low' : 'stock-good'
                          }`}
                        >
                          {isOutOfStock ? '🔴 ' : isLowStock ? '🟡 ' : '🟢 '}
                          {stockQty} {p.unit || 'pcs'}
                        </span>
                        <span className="min-alert-text">Min: {minThreshold}</span>
                      </div>
                    </td>

                    <td className="price-cell">₹{Number(p.price).toFixed(2)}</td>

                    <td className="cost-cell">₹{Number(p.cost_price || 0).toFixed(2)}</td>

                    <td>
                      <span className={`margin-badge ${margin >= 20 ? 'margin-good' : 'margin-fair'}`}>
                        {margin}%
                      </span>
                    </td>

                    <td>
                      <div className="expiry-cell">
                        <Calendar size={13} />
                        <span>{p.expiry_date ? String(p.expiry_date).split('T')[0] : 'N/A'}</span>
                      </div>
                    </td>

                    <td className="text-right">
                      <div className="table-actions">
                        <button
                          className="action-btn-subtle edit-btn"
                          onClick={() => handleOpenEdit(p)}
                          title="Edit product"
                        >
                          <Edit2 size={15} />
                        </button>
                        <button
                          className="action-btn-subtle delete-btn"
                          onClick={() => handleDelete(p)}
                          title="Deactivate product"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination Footer */}
      {filteredProducts.length > ITEMS_PER_PAGE && (
        <div className="inventory-pagination">
          <span className="pagination-info">
            Showing {(currentPage - 1) * ITEMS_PER_PAGE + 1} to{' '}
            {Math.min(currentPage * ITEMS_PER_PAGE, filteredProducts.length)} of {filteredProducts.length} items
          </span>

          <div className="pagination-controls">
            <button
              className="page-btn"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
            >
              Previous
            </button>
            <span className="current-page-indicator">
              Page {currentPage} of {totalPages}
            </span>
            <button
              className="page-btn"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Add / Edit Product Modal */}
      <ProductModal
        isOpen={isModalOpen}
        productToEdit={productToEdit}
        onClose={() => setIsModalOpen(false)}
        onSaved={loadData}
      />
    </div>
  );
}
