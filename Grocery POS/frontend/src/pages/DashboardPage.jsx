import React, { useState, useEffect } from 'react';
import {
  ShoppingCart,
  Plus,
  ReceiptText,
  Truck,
  TrendingUp,
  AlertTriangle,
  DollarSign,
  CreditCard,
  ArrowUpRight,
  RefreshCw,
  PackagePlus,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { getDashboardMetrics } from '../api/reportsApi';

const PAYMENT_COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b'];

export default function DashboardPage({ setActiveTab }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMetrics();
  }, []);

  async function loadMetrics() {
    setLoading(true);
    setError(null);
    try {
      const data = await getDashboardMetrics();
      if (!data) {
        throw new Error('The dashboard API returned an empty response.');
      }
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load dashboard metrics.');
    } finally {
      setLoading(false);
    }
  }

  if (loading && !metrics) {
    return (
      <div className="inventory-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <span>Loading Real-time Executive Dashboard & Analytics...</span>
        </div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="inventory-page">
        <div className="loading-state" role="alert">
          <AlertTriangle size={28} style={{ color: '#f87171' }} />
          <span>Dashboard metrics could not be loaded: {error}</span>
          <button className="btn-secondary" onClick={loadMetrics} disabled={loading}>
            <RefreshCw size={16} />
            <span>Try again</span>
          </button>
        </div>
      </div>
    );
  }

  const { today_sales, payment_methods, low_stock, profit_loss, weekly_trend } = metrics;

  // Prepare Payment Pie Data
  const paymentPieData = [
    { name: 'Cash', value: payment_methods.cash.total || 0, count: payment_methods.cash.count },
    { name: 'Card', value: payment_methods.card.total || 0, count: payment_methods.card.count },
    { name: 'UPI / QR', value: payment_methods.upi.total || 0, count: payment_methods.upi.count },
    { name: 'Split', value: payment_methods.split.total || 0, count: payment_methods.split.count },
  ].filter((p) => p.value > 0);

  // If no transactions yet, show placeholder distribution
  const displayPieData = paymentPieData.length > 0 ? paymentPieData : [
    { name: 'Cash', value: 65, count: 0 },
    { name: 'Card', value: 20, count: 0 },
    { name: 'UPI', value: 15, count: 0 },
  ];

  return (
    <div className="inventory-page" style={{ gap: '22px' }}>
      {error && (
        <div
          role="alert"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
            padding: '12px 16px',
            border: '1px solid rgba(248, 113, 113, 0.4)',
            borderRadius: 'var(--radius-md)',
            color: '#fca5a5',
          }}
        >
          <span>Dashboard refresh failed: {error}</span>
          <button className="btn-secondary" onClick={loadMetrics} disabled={loading}>
            <RefreshCw size={16} />
            <span>Retry</span>
          </button>
        </div>
      )}
      {/* Top Banner with Quick Action CTA Buttons */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95))',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-lg)',
          padding: '18px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
          boxShadow: 'var(--shadow-md)',
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '800', color: '#fff' }}>
            Store Operations & Analytics Dashboard
          </h2>
          <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Real-time supermarket metrics, daily sales velocity, cash vs digital tenders, and stock health.
          </span>
        </div>

        {/* Quick Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button
            className="btn-primary"
            onClick={() => setActiveTab('pos')}
            style={{
              background: 'linear-gradient(135deg, #10b981, #059669)',
              padding: '10px 18px',
              fontWeight: '700',
              boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
            }}
          >
            <ShoppingCart size={16} />
            <span>New Sale (POS)</span>
          </button>

          <button
            className="btn-primary add-product-action"
            onClick={() => setActiveTab('inventory')}
            style={{
              padding: '10px 18px',
              fontWeight: '700',
            }}
          >
            <Plus size={16} />
            <span>Add Product</span>
          </button>

          <button
            className="btn-secondary"
            onClick={() => setActiveTab('transactions')}
            style={{ padding: '10px 16px' }}
          >
            <ReceiptText size={16} />
            <span>Sales History</span>
          </button>

          <button
            className="btn-secondary"
            onClick={() => setActiveTab('suppliers')}
            style={{ padding: '10px 16px' }}
          >
            <Truck size={16} />
            <span>Procurement</span>
          </button>

          <button
            className="btn-secondary"
            onClick={loadMetrics}
            title="Refresh dashboard data"
            style={{ padding: '10px 14px' }}
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* KPI 4-Card Grid */}
      <div className="inventory-stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
        {/* Today's Total Sales */}
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
            <DollarSign size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Today's Total Sales</span>
            <span className="stat-value">₹{today_sales.total_revenue.toFixed(2)}</span>
            <span style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
              {today_sales.transactions_count} orders • Avg: ₹{today_sales.avg_basket_value}
            </span>
          </div>
        </div>

        {/* Total Cash vs Card */}
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>
            <CreditCard size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Cash vs Digital Tenders</span>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1px', marginTop: '2px' }}>
              <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#34d399' }}>
                Cash: ₹{payment_methods.cash.total.toFixed(2)} ({payment_methods.cash.count})
              </div>
              <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#60a5fa' }}>
                Card: ₹{payment_methods.card.total.toFixed(2)} | UPI: ₹{payment_methods.upi.total.toFixed(2)}
              </div>
            </div>
          </div>
        </div>

        {/* Profit / Loss Estimation */}
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            <TrendingUp size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Gross Margin & Profit</span>
            <span className="stat-value" style={{ color: '#fbbf24' }}>
              ₹{profit_loss.net_profit.toFixed(2)}
            </span>
            <span style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
              Margin: {profit_loss.margin_pct}% • Revenue: ₹{profit_loss.gross_revenue.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Low-Stock Alert Count */}
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#f87171' }}>
            <AlertTriangle size={26} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Low-Stock Alerts</span>
            <span className="stat-value" style={{ color: '#f87171' }}>
              {low_stock.total_count} Products
            </span>
            <span style={{ fontSize: '11px', color: '#fca5a5', marginTop: '2px' }}>
              Items needing purchase orders
            </span>
          </div>
        </div>
      </div>

      {/* Visual Charts Grid (Recharts) */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Weekly Revenue & Profit Area Chart */}
        <div
          style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-lg)',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '16px', color: '#fff' }}>Weekly Sales & Profit Velocity</h3>
              <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                7-day gross sales revenue vs estimated gross profit
              </span>
            </div>
            <div style={{ display: 'flex', gap: '12px', fontSize: '12px' }}>
              <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                ● Revenue
              </span>
              <span style={{ color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '4px' }}>
                ● Profit
              </span>
            </div>
          </div>

          <div style={{ width: '100%', height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={weekly_trend} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                <XAxis dataKey="day" stroke="var(--text-dim)" fontSize={12} />
                <YAxis stroke="var(--text-dim)" fontSize={12} tickFormatter={(val) => `₹${val}`} />
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '12px',
                  }}
                  formatter={(value) => [`₹${Number(value).toFixed(2)}`, '']}
                />
                <Area type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={2.5} fillOpacity={1} fill="url(#colorRev)" name="Revenue" />
                <Area type="monotone" dataKey="profit" stroke="#3b82f6" strokeWidth={2.5} fillOpacity={1} fill="url(#colorProfit)" name="Gross Profit" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Payment Methods Donut / Pie Chart */}
        <div
          style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-lg)',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '14px',
          }}
        >
          <h3 style={{ margin: 0, fontSize: '16px', color: '#fff' }}>Payment Tenders Ratio</h3>
          <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
            Cash, Card, UPI, and Split transactions
          </span>

          <div style={{ width: '100%', height: '200px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={displayPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {displayPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PAYMENT_COLORS[index % PAYMENT_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: '#1e293b',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '12px',
                  }}
                  formatter={(val) => [`₹${Number(val).toFixed(2)}`, 'Amount']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '11px' }}>
            {displayPieData.map((p, idx) => (
              <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: PAYMENT_COLORS[idx % PAYMENT_COLORS.length] }}></span>
                <span style={{ color: 'var(--text-muted)' }}>{p.name}:</span>
                <strong style={{ color: '#fff' }}>₹{Number(p.value).toFixed(0)}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Critical Low Stock Alert Table */}
      <div className="inventory-table-card">
        <div className="inventory-toolbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={18} style={{ color: '#ef4444' }} />
            <h3 style={{ margin: 0, fontSize: '16px', color: '#fff' }}>
              Critical Low Stock Threshold Alerts ({low_stock.total_count} products)
            </h3>
          </div>
          <button className="btn-secondary" onClick={() => setActiveTab('inventory')}>
            <span>View All Stock</span>
            <ArrowUpRight size={15} />
          </button>
        </div>

        <div className="table-wrapper">
          <table className="pos-table">
            <thead>
              <tr>
                <th>Product Name</th>
                <th>Barcode</th>
                <th>Category</th>
                <th>Selling Price</th>
                <th>Current Stock</th>
                <th>Alert Threshold</th>
                <th>Status</th>
                <th>Quick Procurement</th>
              </tr>
            </thead>
            <tbody>
              {low_stock.products.length === 0 ? (
                <tr>
                  <td colSpan="8" className="table-empty">
                    All inventory levels are healthy above safety thresholds.
                  </td>
                </tr>
              ) : (
                low_stock.products.map((item) => (
                  <tr key={item.id}>
                    <td><strong style={{ color: '#fff' }}>{item.name}</strong></td>
                    <td><code style={{ fontSize: '12px', color: 'var(--text-dim)' }}>{item.barcode}</code></td>
                    <td>{item.category}</td>
                    <td>₹{Number(item.price).toFixed(2)}</td>
                    <td>
                      <strong style={{ color: item.stock_quantity <= 10 ? '#ef4444' : '#f59e0b', fontSize: '14px' }}>
                        {item.stock_quantity} {item.unit}
                      </strong>
                    </td>
                    <td>{item.min_stock_alert} {item.unit}</td>
                    <td>
                      <span className="badge-warning">
                        {item.stock_quantity === 0 ? 'Out of Stock' : 'Low Stock'}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-secondary"
                        onClick={() => setActiveTab('suppliers')}
                        style={{ padding: '4px 10px', fontSize: '11px', gap: '4px' }}
                      >
                        <PackagePlus size={13} />
                        <span>Order PO</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
