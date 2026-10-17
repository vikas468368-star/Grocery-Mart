import React, { useState, useEffect } from 'react';
import {
  ReceiptText,
  Printer,
  CheckCircle,
  Search,
  RefreshCw,
  RotateCcw,
  Calendar,
  AlertCircle,
  DollarSign,
  TrendingUp,
  Tag,
  CheckCircle2,
  Filter
} from 'lucide-react';
import { getSalesHistory } from '../api/billingApi';
import { useCart } from '../context/CartContext';
import ReturnModal from '../components/ReturnModal';

export default function TransactionsPage() {
  const [sales, setSales] = useState([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedSaleForReturn, setSelectedSaleForReturn] = useState(null);
  const [returnSuccessToast, setReturnSuccessToast] = useState(null);

  const { setLastCompletedOrder, setIsReceiptModalOpen } = useCart();

  useEffect(() => {
    loadSales();
  }, [statusFilter]);

  const loadSales = async () => {
    setLoading(true);
    try {
      const data = await getSalesHistory(search, statusFilter);
      setSales(data || []);
    } catch {
      setSales([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadSales();
  };

  const handleReprint = (sale) => {
    setLastCompletedOrder({
      ...sale,
      total_amount: sale.total_amount,
      items: sale.items || [],
      split_breakdown: sale.payments?.length > 1 ? sale.payments : undefined,
    });
    setIsReceiptModalOpen(true);
  };

  const handleOpenReturn = (sale) => {
    setSelectedSaleForReturn(sale);
  };

  const handleReturnSuccess = (result) => {
    setReturnSuccessToast({
      returnNumber: result.return_number,
      refundAmount: result.refund_amount,
      message: result.message,
    });
    setTimeout(() => setReturnSuccessToast(null), 6000);
    loadSales(); // reload sales to reflect updated status and quantities
  };

  // KPI Computations
  const totalInvoices = sales.length;
  const totalRevenue = sales.reduce((sum, s) => sum + (Number(s.total_amount) || 0), 0);
  const totalPaid = sales.filter((s) => s.status === 'Paid' || s.status === 'COMPLETED').length;
  const totalRefunded = sales.filter((s) => s.status === 'REFUNDED' || s.status?.includes('REFUND')).length;

  return (
    <div className="transactions-page">
      {/* Return Success Toast Alert */}
      {returnSuccessToast && (
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.3))',
            border: '1.5px solid #10b981',
            borderRadius: '10px',
            padding: '14px 18px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            color: '#34d399',
            boxShadow: '0 4px 14px rgba(16, 185, 129, 0.2)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <CheckCircle2 size={22} style={{ color: '#10b981' }} />
            <div>
              <strong style={{ color: '#fff' }}>Return #{returnSuccessToast.returnNumber} Processed!</strong>
              <div style={{ fontSize: '13px', color: '#a7f3d0' }}>
                {returnSuccessToast.message}
              </div>
            </div>
          </div>
          <button
            onClick={() => setReturnSuccessToast(null)}
            style={{ background: 'transparent', border: 'none', color: '#a7f3d0', cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Top Sales KPI Cards */}
      <div className="inventory-stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>
            <ReceiptText size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Invoices</span>
            <span className="stat-value">{totalInvoices}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
            <DollarSign size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Gross Sales</span>
            <span className="stat-value">₹{totalRevenue.toFixed(2)}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            <CheckCircle size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Completed Sales</span>
            <span className="stat-value">{totalPaid}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#f87171' }}>
            <RotateCcw size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Refunds / Returns</span>
            <span className="stat-value">{totalRefunded}</span>
          </div>
        </div>
      </div>

      {/* Main Sales History Table Card */}
      <div className="inventory-table-card">
        <div className="inventory-toolbar">
          <form onSubmit={handleSearchSubmit} className="search-box">
            <Search size={18} className="search-icon" />
            <input
              type="text"
              placeholder="Search by invoice number, customer name, or phone..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            {search && (
              <button
                type="button"
                className="clear-search"
                onClick={() => {
                  setSearch('');
                  loadSales();
                }}
              >
                ✕
              </button>
            )}
          </form>

          {/* Status Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} style={{ color: 'var(--text-dim)' }} />
            <select
              className="form-input"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ padding: '8px 12px', fontSize: '13px' }}
            >
              <option value="">All Statuses</option>
              <option value="Paid">Paid Only</option>
              <option value="REFUNDED">Refunded Only</option>
              <option value="COMPLETED">Completed</option>
            </select>
          </div>

          <button className="btn-secondary" onClick={loadSales}>
            <RefreshCw size={16} />
            <span>Refresh Sales</span>
          </button>
        </div>

        <div className="table-wrapper">
          <table className="pos-table">
            <thead>
              <tr>
                <th>Invoice Number</th>
                <th>Date & Time</th>
                <th>Customer Details</th>
                <th>Cashier</th>
                <th>Payment Mode</th>
                <th>Items Count</th>
                <th>Grand Total</th>
                <th>Status</th>
                <th style={{ textAlign: 'center' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="9" className="table-empty">
                    Loading sales history and transactions...
                  </td>
                </tr>
              ) : sales.length === 0 ? (
                <tr>
                  <td colSpan="9" className="table-empty">
                    No sales matching the query criteria.
                  </td>
                </tr>
              ) : (
                sales.map((sale) => {
                  const isRefunded = sale.status === 'REFUNDED' || sale.status?.includes('REFUND');
                  return (
                    <tr key={sale.id}>
                      <td>
                        <strong className="invoice-link">{sale.invoice_number}</strong>
                      </td>
                      <td>
                        <div style={{ fontSize: '13px', color: '#fff' }}>
                          {new Date(sale.created_at).toLocaleDateString()}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                          {new Date(sale.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: '13px', fontWeight: '600', color: '#fff' }}>
                          {sale.customer_name || 'Walk-in Customer'}
                        </div>
                        {sale.customer_phone && (
                          <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                            {sale.customer_phone}
                          </div>
                        )}
                      </td>
                      <td>{sale.cashier_name || 'Cashier #01'}</td>
                      <td>
                        <span className={`pill-payment ${sale.payment_method?.toLowerCase()}`}>
                          {sale.payment_method}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '13px', color: '#cbd5e1' }}>
                          {sale.items?.length || 0} items
                        </span>
                      </td>
                      <td className="fw-bold" style={{ fontSize: '14px', color: isRefunded ? '#94a3b8' : '#34d399' }}>
                        ₹{Number(sale.total_amount).toFixed(2)}
                      </td>
                      <td>
                        {isRefunded ? (
                          <span
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              padding: '3px 8px',
                              borderRadius: '12px',
                              background: 'rgba(239, 68, 68, 0.15)',
                              color: '#f87171',
                              fontSize: '11px',
                              fontWeight: '700',
                            }}
                          >
                            <RotateCcw size={12} /> Refunded
                          </span>
                        ) : (
                          <span className="badge-active">
                            <CheckCircle size={12} /> {sale.status || 'Paid'}
                          </span>
                        )}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                          {/* Reprint Thermal Receipt */}
                          <button
                            className="btn-icon-subtle"
                            title="Print / View Thermal Receipt"
                            onClick={() => handleReprint(sale)}
                          >
                            <Printer size={16} />
                          </button>

                          {/* Process Return & Refund */}
                          <button
                            className="btn-secondary"
                            onClick={() => handleOpenReturn(sale)}
                            disabled={isRefunded}
                            title={isRefunded ? 'This invoice has already been fully refunded' : 'Select items to process return & refund'}
                            style={{
                              padding: '6px 10px',
                              fontSize: '12px',
                              gap: '4px',
                              borderColor: isRefunded ? 'transparent' : 'rgba(245, 158, 11, 0.4)',
                              color: isRefunded ? 'var(--text-dim)' : '#fbbf24',
                              opacity: isRefunded ? 0.4 : 1,
                              cursor: isRefunded ? 'not-allowed' : 'pointer',
                            }}
                          >
                            <RotateCcw size={13} />
                            <span>Return</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Return & Refund Processing Modal */}
      <ReturnModal
        sale={selectedSaleForReturn}
        isOpen={!!selectedSaleForReturn}
        onClose={() => setSelectedSaleForReturn(null)}
        onSuccess={handleReturnSuccess}
      />
    </div>
  );
}
