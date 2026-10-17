import React, { useState, useEffect } from 'react';
import { X, Save, Barcode, Sparkles, Layers, DollarSign, Calendar, Boxes } from 'lucide-react';
import { createProduct, updateProduct, getCategories } from '../api/productsApi';
import { getSuppliers } from '../api/suppliersApi';

const UNITS = ['pcs', 'kg', 'pack', 'litre', 'dozen', 'gm', 'box'];
const TAX_RATES = [
  { label: '0% (Exempt / Fresh produce)', value: 0.00 },
  { label: '5% (Essential groceries & dairy)', value: 0.05 },
  { label: '12% (Processed foods & beverages)', value: 0.12 },
  { label: '18% (Packaged snacks & household)', value: 0.18 },
];

export default function ProductModal({ isOpen, onClose, productToEdit, onSaved }) {
  const isEditMode = Boolean(productToEdit && productToEdit.id);

  const [categories, setCategories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    barcode: '',
    sku: '',
    category_id: 1,
    supplier_id: '',
    price: '',
    cost_price: '',
    stock_quantity: '',
    min_stock_alert: '15',
    unit: 'pcs',
    tax_rate: 0.05,
    expiry_date: '',
    batch_number: '',
    description: '',
  });

  useEffect(() => {
    if (isOpen) {
      loadDropdowns();
      if (productToEdit) {
        setFormData({
          name: productToEdit.name || '',
          barcode: productToEdit.barcode || '',
          sku: productToEdit.sku || '',
          category_id: productToEdit.category_id || 1,
          supplier_id: productToEdit.supplier_id || '',
          price: productToEdit.price !== undefined ? String(productToEdit.price) : '',
          cost_price: productToEdit.cost_price !== undefined ? String(productToEdit.cost_price) : '',
          stock_quantity: productToEdit.stock_quantity !== undefined ? String(productToEdit.stock_quantity) : '',
          min_stock_alert: productToEdit.min_stock_alert !== undefined ? String(productToEdit.min_stock_alert) : '15',
          unit: productToEdit.unit || 'pcs',
          tax_rate: productToEdit.tax_rate !== undefined ? productToEdit.tax_rate : 0.05,
          expiry_date: productToEdit.expiry_date ? String(productToEdit.expiry_date).split('T')[0] : '',
          batch_number: productToEdit.batch_number || '',
          description: productToEdit.description || '',
        });
      } else {
        // Default new product values
        generateBarcode();
      }
    }
  }, [isOpen, productToEdit]);

  const loadDropdowns = async () => {
    try {
      const [cats, supps] = await Promise.all([getCategories(), getSuppliers()]);
      setCategories(cats || []);
      setSuppliers(supps || []);
      if (cats && cats.length > 0 && !formData.category_id) {
        setFormData((prev) => ({ ...prev, category_id: cats[0].id }));
      }
    } catch (err) {
      console.warn('Failed to load modal dropdowns:', err.message);
    }
  };

  const generateBarcode = () => {
    // Generate standard 12-digit Indian retail barcode prefix 890...
    const randomSuffix = Math.floor(100000000 + Math.random() * 900000000);
    const code = `890${randomSuffix}`;
    setFormData((prev) => ({ ...prev, barcode: code }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!formData.name.trim()) {
      setErrorMsg('Product name is required.');
      return;
    }
    if (!formData.barcode.trim()) {
      setErrorMsg('Barcode is required.');
      return;
    }
    if (!formData.price || parseFloat(formData.price) <= 0) {
      setErrorMsg('Retail selling price must be greater than 0.');
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        name: formData.name.trim(),
        barcode: formData.barcode.trim(),
        sku: formData.sku.trim() || undefined,
        category_id: formData.category_id ? parseInt(formData.category_id, 10) : 1,
        supplier_id: formData.supplier_id ? parseInt(formData.supplier_id, 10) : undefined,
        price: parseFloat(formData.price),
        cost_price: parseFloat(formData.cost_price || 0),
        stock_quantity: parseFloat(formData.stock_quantity || 0),
        min_stock_alert: parseFloat(formData.min_stock_alert || 10),
        unit: formData.unit || 'pcs',
        tax_rate: parseFloat(formData.tax_rate),
        expiry_date: formData.expiry_date || null,
        batch_number: formData.batch_number.trim() || undefined,
        description: formData.description.trim() || undefined,
      };

      if (isEditMode) {
        await updateProduct(productToEdit.id, payload);
      } else {
        await createProduct(payload);
      }

      if (onSaved) onSaved();
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Operation failed. Please verify fields.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop">
      <div className="modal-card product-modal-dialog">
        <div className="modal-header">
          <div>
            <h3>{isEditMode ? `Edit Product: ${productToEdit.name}` : 'Add New Grocery Product'}</h3>
            <span className="modal-subtitle">
              {isEditMode ? `ID: #${productToEdit.id} • SKU: ${productToEdit.sku || 'N/A'}` : 'Catalog item with barcode and stock level'}
            </span>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {errorMsg && (
          <div className="modal-error-alert">
            <span>⚠️ {errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="modal-body">
          <div className="form-grid-2">
            {/* Product Name */}
            <div className="form-field full-width">
              <label>Product Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Amul Pure Cow Ghee 1L"
                required
              />
            </div>

            {/* Barcode & Generator */}
            <div className="form-field">
              <label>Barcode Number *</label>
              <div className="input-with-action">
                <input
                  type="text"
                  value={formData.barcode}
                  onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
                  placeholder="e.g. 890100000001"
                  required
                />
                <button
                  type="button"
                  className="btn-action-inline"
                  onClick={generateBarcode}
                  title="Generate Unique Barcode"
                >
                  <Sparkles size={14} /> Auto
                </button>
              </div>
            </div>

            {/* SKU */}
            <div className="form-field">
              <label>SKU (Stock Keeping Unit)</label>
              <input
                type="text"
                value={formData.sku}
                onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                placeholder="e.g. GHE-001"
              />
            </div>

            {/* Category / Department */}
            <div className="form-field">
              <label>Grocery Department / Category *</label>
              <select
                value={formData.category_id}
                onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
              >
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} (Tax: {Math.round(c.default_tax_rate * 100)}%)
                  </option>
                ))}
              </select>
            </div>

            {/* Supplier */}
            <div className="form-field">
              <label>Supplier / Distributor</label>
              <select
                value={formData.supplier_id}
                onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
              >
                <option value="">-- No Assigned Supplier --</option>
                {suppliers.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.contact_person || 'Distributor'})
                  </option>
                ))}
              </select>
            </div>

            {/* Selling Price */}
            <div className="form-field">
              <label>Retail Selling Price (₹) *</label>
              <input
                type="number"
                step="0.01"
                min="0.1"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                placeholder="0.00"
                required
              />
            </div>

            {/* Cost Price */}
            <div className="form-field">
              <label>Procurement Cost Price (₹)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.cost_price}
                onChange={(e) => setFormData({ ...formData, cost_price: e.target.value })}
                placeholder="0.00"
              />
            </div>

            {/* Stock Quantity */}
            <div className="form-field">
              <label>Current Stock Quantity *</label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={formData.stock_quantity}
                onChange={(e) => setFormData({ ...formData, stock_quantity: e.target.value })}
                placeholder="0"
                required
              />
            </div>

            {/* Min Stock Alert */}
            <div className="form-field">
              <label>Low Stock Warning Threshold</label>
              <input
                type="number"
                step="1"
                min="1"
                value={formData.min_stock_alert}
                onChange={(e) => setFormData({ ...formData, min_stock_alert: e.target.value })}
                placeholder="15"
              />
            </div>

            {/* Unit */}
            <div className="form-field">
              <label>Measurement Unit</label>
              <select
                value={formData.unit}
                onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
              >
                {UNITS.map((u) => (
                  <option key={u} value={u}>
                    {u.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            {/* Tax Rate (GST) */}
            <div className="form-field">
              <label>GST Tax Bracket</label>
              <select
                value={formData.tax_rate}
                onChange={(e) => setFormData({ ...formData, tax_rate: parseFloat(e.target.value) })}
              >
                {TAX_RATES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Expiry Date */}
            <div className="form-field">
              <label>Batch Expiry Date</label>
              <input
                type="date"
                value={formData.expiry_date}
                onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
              />
            </div>

            {/* Batch Number */}
            <div className="form-field">
              <label>Batch / Lot Code</label>
              <input
                type="text"
                value={formData.batch_number}
                onChange={(e) => setFormData({ ...formData, batch_number: e.target.value })}
                placeholder="e.g. BATCH-2026-X"
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>
            <button
              type="submit"
              className={`btn-primary ${isEditMode ? '' : 'add-product-action'}`}
              disabled={isSubmitting}
            >
              <Save size={16} />
              <span>{isSubmitting ? 'Saving...' : isEditMode ? 'Update Product' : 'Save New Product'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
