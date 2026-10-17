import React, { useState, useEffect } from 'react';
import {
  Truck,
  Plus,
  Package,
  Calendar,
  CheckCircle2,
  Clock,
  X,
  FileText,
  DollarSign,
  AlertCircle,
  Phone,
  Mail,
  MapPin,
  Building,
  RefreshCw,
  Trash2,
} from 'lucide-react';
import {
  getSuppliers,
  createSupplier,
  getPurchaseOrders,
  createPurchaseOrder,
  updatePurchaseOrderStatus,
} from '../api/suppliersApi';
import { getProducts } from '../api/productsApi';

export default function SupplierPage() {
  const [activeTab, setActiveTab] = useState('orders'); // 'orders' or 'suppliers'
  const [suppliers, setSuppliers] = useState([]);
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [productsList, setProductsList] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modals
  const [showAddSupplierModal, setShowAddSupplierModal] = useState(false);
  const [showCreatePOModal, setShowCreatePOModal] = useState(false);

  // Add Supplier Form
  const [supplierForm, setSupplierForm] = useState({
    name: '',
    contact_person: '',
    phone: '',
    email: '',
    address: '',
    tax_number: '',
  });

  // Create PO Form
  const [poSupplierId, setPoSupplierId] = useState('');
  const [poNotes, setPoNotes] = useState('');
  const [poExpectedDate, setPoExpectedDate] = useState('');
  const [poItems, setPoItems] = useState([
    { product_id: '', quantity_ordered: 50, unit_cost: 0 },
  ]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [supps, orders, prods] = await Promise.all([
        getSuppliers(),
        getPurchaseOrders(),
        getProducts('', 'All', 200),
      ]);
      setSuppliers(supps || []);
      setPurchaseOrders(orders || []);
      setProductsList(prods || []);
      if (supps && supps.length > 0 && !poSupplierId) {
        setPoSupplierId(String(supps[0].id));
      }
    } catch (err) {
      console.warn('Error loading suppliers data:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSupplier = async (e) => {
    e.preventDefault();
    try {
      await createSupplier(supplierForm);
      setShowAddSupplierModal(false);
      setSupplierForm({
        name: '',
        contact_person: '',
        phone: '',
        email: '',
        address: '',
        tax_number: '',
      });
      loadData();
    } catch (err) {
      alert(`Failed to add supplier: ${err.message}`);
    }
  };

  const handleAddPOLine = () => {
    setPoItems([...poItems, { product_id: '', quantity_ordered: 20, unit_cost: 0 }]);
  };

  const handleRemovePOLine = (index) => {
    setPoItems(poItems.filter((_, idx) => idx !== index));
  };

  const handlePOLineChange = (index, field, value) => {
    const updated = [...poItems];
    updated[index][field] = value;

    // If product selected, auto-populate unit cost from product cost_price
    if (field === 'product_id') {
      const found = productsList.find((p) => p.id === parseInt(value, 10));
      if (found) {
        updated[index].unit_cost = found.cost_price || Math.round(found.price * 0.75);
      }
    }

    setPoItems(updated);
  };

  const handleCreatePO = async (e) => {
    e.preventDefault();
    const validItems = poItems
      .filter((item) => item.product_id && item.quantity_ordered > 0)
      .map((item) => ({
        product_id: parseInt(item.product_id, 10),
        quantity_ordered: parseFloat(item.quantity_ordered),
        unit_cost: parseFloat(item.unit_cost || 0),
      }));

    if (validItems.length === 0) {
      alert('Please add at least one valid product line with quantity.');
      return;
    }

    try {
      await createPurchaseOrder({
        supplier_id: parseInt(poSupplierId, 10),
        notes: poNotes,
        expected_delivery_date: poExpectedDate ? new Date(poExpectedDate).toISOString() : null,
        items: validItems,
      });

      setShowCreatePOModal(false);
      setPoItems([{ product_id: '', quantity_ordered: 50, unit_cost: 0 }]);
      setPoNotes('');
      loadData();
    } catch (err) {
      alert(`Failed to create purchase order: ${err.message}`);
    }
  };

  const handleMarkReceived = async (po) => {
    if (window.confirm(`Mark Purchase Order ${po.po_number} as RECEIVED? This will automatically increment stock quantities for all items in the order.`)) {
      try {
        await updatePurchaseOrderStatus(po.id, 'RECEIVED');
        loadData();
      } catch (err) {
        alert(`Failed to update PO status: ${err.message}`);
      }
    }
  };

  const calculatePOTotal = () => {
    return poItems.reduce((sum, item) => sum + (parseFloat(item.quantity_ordered || 0) * parseFloat(item.unit_cost || 0)), 0);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'RECEIVED':
        return <span className="po-badge bg-green">🟢 RECEIVED</span>;
      case 'ORDERED':
        return <span className="po-badge bg-blue">🔵 ORDERED</span>;
      case 'CANCELLED':
        return <span className="po-badge bg-red">🔴 CANCELLED</span>;
      default:
        return <span className="po-badge bg-amber">🟡 PENDING</span>;
    }
  };

  return (
    <div className="supplier-page-container">
      {/* Top Header */}
      <div className="supplier-header-row">
        <div>
          <h2>Supplier Management & Procurement</h2>
          <p className="supplier-subtitle">
            Manage wholesale distributors, generate purchase orders, and receive restocking shipments.
          </p>
        </div>

        <div className="supplier-header-actions">
          <div className="supplier-subnav">
            <button
              className={`subnav-pill ${activeTab === 'orders' ? 'active' : ''}`}
              onClick={() => setActiveTab('orders')}
            >
              <Package size={16} />
              <span>Purchase Orders ({purchaseOrders.length})</span>
            </button>
            <button
              className={`subnav-pill ${activeTab === 'suppliers' ? 'active' : ''}`}
              onClick={() => setActiveTab('suppliers')}
            >
              <Truck size={16} />
              <span>Distributors ({suppliers.length})</span>
            </button>
          </div>

          <button className="refresh-icon-btn" onClick={loadData} title="Refresh records">
            <RefreshCw size={16} />
          </button>

          {activeTab === 'orders' ? (
            <button className="btn-primary" onClick={() => setShowCreatePOModal(true)}>
              <Plus size={16} />
              <span>New Purchase Order</span>
            </button>
          ) : (
            <button className="btn-primary" onClick={() => setShowAddSupplierModal(true)}>
              <Plus size={16} />
              <span>Add Supplier</span>
            </button>
          )}
        </div>
      </div>

      {/* Tab 1: Purchase Orders */}
      {activeTab === 'orders' && (
        <div className="po-section-wrapper">
          <div className="po-table-container">
            {loading ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <span>Loading purchase orders...</span>
              </div>
            ) : purchaseOrders.length === 0 ? (
              <div className="table-empty">
                <Package size={44} className="empty-icon" />
                <h4>No Purchase Orders Found</h4>
                <p>Click "New Purchase Order" to restock inventory from suppliers.</p>
              </div>
            ) : (
              <table className="inventory-table">
                <thead>
                  <tr>
                    <th>PO Number</th>
                    <th>Supplier / Distributor</th>
                    <th>Order Date</th>
                    <th>Status</th>
                    <th>Total Amount</th>
                    <th>Items</th>
                    <th className="text-right">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {purchaseOrders.map((po) => (
                    <tr key={po.id}>
                      <td className="po-number-cell">
                        <strong>{po.po_number}</strong>
                        {po.notes && <span className="po-note-sub">{po.notes}</span>}
                      </td>
                      <td>
                        <div className="supplier-cell-info">
                          <Building size={14} className="text-muted" />
                          <span>{po.supplier_name}</span>
                        </div>
                      </td>
                      <td>
                        <div className="date-cell">
                          <Calendar size={13} />
                          <span>{new Date(po.order_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
                        </div>
                      </td>
                      <td>{getStatusBadge(po.status)}</td>
                      <td className="price-cell">₹{Number(po.total_amount).toFixed(2)}</td>
                      <td>
                        <span className="items-count-pill">{po.items?.length || 0} line items</span>
                      </td>
                      <td className="text-right">
                        {po.status !== 'RECEIVED' && po.status !== 'CANCELLED' && (
                          <button
                            className="btn-receive-po"
                            onClick={() => handleMarkReceived(po)}
                            title="Mark as Received to restock product inventory"
                          >
                            <CheckCircle2 size={14} />
                            <span>Receive & Restock</span>
                          </button>
                        )}
                        {po.status === 'RECEIVED' && (
                          <span className="received-stamp">✓ Restocked</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Suppliers Directory */}
      {activeTab === 'suppliers' && (
        <div className="suppliers-grid-wrapper">
          <div className="suppliers-cards-grid">
            {suppliers.map((s) => (
              <div key={s.id} className="supplier-card">
                <div className="supplier-card-header">
                  <div className="supplier-icon-badge">
                    <Truck size={22} />
                  </div>
                  <div className="supplier-title-col">
                    <h3>{s.name}</h3>
                    <span className="contact-person">Rep: {s.contact_person || 'Representative'}</span>
                  </div>
                  <span className="supplier-product-count">{s.product_count || 0} Products</span>
                </div>

                <div className="supplier-details-list">
                  <div className="sup-detail">
                    <Phone size={14} />
                    <span>{s.phone || 'No phone provided'}</span>
                  </div>
                  <div className="sup-detail">
                    <Mail size={14} />
                    <span>{s.email || 'No email provided'}</span>
                  </div>
                  <div className="sup-detail">
                    <MapPin size={14} />
                    <span>{s.address || 'Address not listed'}</span>
                  </div>
                  {s.tax_number && (
                    <div className="sup-detail">
                      <FileText size={14} />
                      <span>GSTIN: {s.tax_number}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Create Purchase Order Modal */}
      {showCreatePOModal && (
        <div className="modal-backdrop">
          <div className="modal-card po-modal-dialog">
            <div className="modal-header">
              <div>
                <h3>Create Procurement Purchase Order</h3>
                <span className="modal-subtitle">Replenish supermarket inventory from distributors</span>
              </div>
              <button className="modal-close-btn" onClick={() => setShowCreatePOModal(false)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreatePO} className="modal-body">
              <div className="form-grid-2">
                <div className="form-field">
                  <label>Select Distributor *</label>
                  <select value={poSupplierId} onChange={(e) => setPoSupplierId(e.target.value)} required>
                    {suppliers.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.contact_person || 'Distributor'})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-field">
                  <label>Expected Delivery Date</label>
                  <input
                    type="date"
                    value={poExpectedDate}
                    onChange={(e) => setPoExpectedDate(e.target.value)}
                  />
                </div>

                <div className="form-field full-width">
                  <label>Order Notes / Reference</label>
                  <input
                    type="text"
                    value={poNotes}
                    onChange={(e) => setPoNotes(e.target.value)}
                    placeholder="e.g. Weekly replenishment shipment"
                  />
                </div>
              </div>

              {/* Line Items Builder */}
              <div className="po-lines-section">
                <div className="po-lines-header">
                  <h4>Procurement Items List</h4>
                  <button type="button" className="btn-add-line" onClick={handleAddPOLine}>
                    <Plus size={14} /> Add Line Item
                  </button>
                </div>

                <div className="po-lines-list">
                  {poItems.map((line, idx) => (
                    <div key={idx} className="po-line-row">
                      <div className="line-field-product">
                        <label>Product *</label>
                        <select
                          value={line.product_id}
                          onChange={(e) => handlePOLineChange(idx, 'product_id', e.target.value)}
                          required
                        >
                          <option value="">-- Choose Grocery Item --</option>
                          {productsList.map((p) => (
                            <option key={p.id} value={p.id}>
                              {p.name} (Stock: {p.stock_quantity} {p.unit})
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="line-field-qty">
                        <label>Qty</label>
                        <input
                          type="number"
                          step="1"
                          min="1"
                          value={line.quantity_ordered}
                          onChange={(e) => handlePOLineChange(idx, 'quantity_ordered', e.target.value)}
                          required
                        />
                      </div>

                      <div className="line-field-cost">
                        <label>Unit Cost (₹)</label>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={line.unit_cost}
                          onChange={(e) => handlePOLineChange(idx, 'unit_cost', e.target.value)}
                          required
                        />
                      </div>

                      <div className="line-field-total">
                        <label>Total</label>
                        <span className="line-total-calc">
                          ₹{(parseFloat(line.quantity_ordered || 0) * parseFloat(line.unit_cost || 0)).toFixed(2)}
                        </span>
                      </div>

                      {poItems.length > 1 && (
                        <button
                          type="button"
                          className="btn-remove-line"
                          onClick={() => handleRemovePOLine(idx)}
                          title="Remove line"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  ))}
                </div>

                <div className="po-total-bar">
                  <span>Estimated Total PO Cost:</span>
                  <span className="po-grand-total">₹{calculatePOTotal().toFixed(2)}</span>
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn-secondary" onClick={() => setShowCreatePOModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Generate Purchase Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Supplier Modal */}
      {showAddSupplierModal && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Register New Supplier</h3>
              <button className="modal-close-btn" onClick={() => setShowAddSupplierModal(false)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateSupplier} className="modal-body form-grid-2">
              <div className="form-field full-width">
                <label>Company / Supplier Name *</label>
                <input
                  type="text"
                  value={supplierForm.name}
                  onChange={(e) => setSupplierForm({ ...supplierForm, name: e.target.value })}
                  placeholder="e.g. Metro Wholesale Agrotech"
                  required
                />
              </div>

              <div className="form-field">
                <label>Contact Person</label>
                <input
                  type="text"
                  value={supplierForm.contact_person}
                  onChange={(e) => setSupplierForm({ ...supplierForm, contact_person: e.target.value })}
                  placeholder="e.g. Sunil Gupta"
                />
              </div>

              <div className="form-field">
                <label>Phone Number *</label>
                <input
                  type="text"
                  value={supplierForm.phone}
                  onChange={(e) => setSupplierForm({ ...supplierForm, phone: e.target.value })}
                  placeholder="+91 98111 22334"
                  required
                />
              </div>

              <div className="form-field">
                <label>Email Address</label>
                <input
                  type="email"
                  value={supplierForm.email}
                  onChange={(e) => setSupplierForm({ ...supplierForm, email: e.target.value })}
                  placeholder="orders@supplier.in"
                />
              </div>

              <div className="form-field">
                <label>GSTIN / Tax ID</label>
                <input
                  type="text"
                  value={supplierForm.tax_number}
                  onChange={(e) => setSupplierForm({ ...supplierForm, tax_number: e.target.value })}
                  placeholder="27AABCM1234F1Z1"
                />
              </div>

              <div className="form-field full-width">
                <label>Warehouse Address</label>
                <input
                  type="text"
                  value={supplierForm.address}
                  onChange={(e) => setSupplierForm({ ...supplierForm, address: e.target.value })}
                  placeholder="Yard 4, APMC Market, Vashi, Navi Mumbai"
                />
              </div>

              <div className="modal-footer full-width">
                <button type="button" className="btn-secondary" onClick={() => setShowAddSupplierModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Save Supplier
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
