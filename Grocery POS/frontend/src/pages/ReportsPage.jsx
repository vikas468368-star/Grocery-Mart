import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  DollarSign,
  Package,
  AlertTriangle,
  Receipt,
  PieChart as PieIcon,
  RefreshCw,
  Crown,
  ShieldAlert,
  ArrowUpRight,
  Boxes,
  Calendar,
  CheckCircle,
  BarChart3,
  Flame,
  ScrollText,
  Search,
  Filter,
  CheckCircle2,
  RotateCcw,
  Truck
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';
import { getReportsSummary, getTopProducts } from '../api/authApi';
import { getSalesTrends, getBestSellers, getAuditLogs } from '../api/reportsApi';
import { useAuth } from '../context/AuthContext';

export default function ReportsPage() {
  const { user, isOwner } = useAuth();
  const [activeReportTab, setActiveReportTab] = useState('trends'); // 'trends' | 'bestsellers' | 'audit' | 'valuation'
  const [trendPeriod, setTrendPeriod] = useState('daily'); // 'daily' | 'monthly'

  // Data States
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [bestSellers, setBestSellers] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditSearch, setAuditSearch] = useState('');
  const [auditTypeFilter, setAuditTypeFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAllReports();
  }, [trendPeriod]);

  const loadAllReports = async () => {
    setLoading(true);
    setError('');
    try {
      const [sumData, trendData, topData, logsData] = await Promise.all([
        getReportsSummary().catch(() => null),
        getSalesTrends(trendPeriod).catch(() => []),
        getBestSellers(15).catch(() => []),
        getAuditLogs(50).catch(() => []),
      ]);
      setSummary(sumData);
      setTrends(trendData || []);
      setBestSellers(topData || []);
      setAuditLogs(logsData || []);
    } catch (err) {
      setError(err.message || 'Failed to compile comprehensive reports.');
    } finally {
      setLoading(false);
    }
  };

  // RBAC Guard fallback if non-owner tries to render
  if (!isOwner) {
    return (
      <div className="unauthorized-page-state">
        <div className="unauthorized-card">
          <ShieldAlert size={56} className="unauthorized-icon" />
          <h2>Access Restricted to Store Owner</h2>
          <p>
            Your current role is <strong>{user?.role}</strong>. Financial analytics,
            revenue ledgers, and profit calculations are confidential and only visible to the Store Owner.
          </p>
        </div>
      </div>
    );
  }

  // Filtered Audit Logs
  const filteredAuditLogs = auditLogs.filter((log) => {
    const matchesSearch =
      log.action?.toLowerCase().includes(auditSearch.toLowerCase()) ||
      log.details?.toLowerCase().includes(auditSearch.toLowerCase()) ||
      log.user_name?.toLowerCase().includes(auditSearch.toLowerCase()) ||
      log.id?.toLowerCase().includes(auditSearch.toLowerCase());
    const matchesType = auditTypeFilter ? log.event_type === auditTypeFilter : true;
    return matchesSearch && matchesType;
  });

  const kpis = summary?.store_kpis || {};
  const inv = summary?.inventory_kpis || {};
  const categories = summary?.categories_distribution || [];

  return (
    <div className="reports-page-container" style={{ gap: '20px' }}>
      {/* Page Header */}
      <div className="reports-header-row">
        <div className="title-area">
          <div className="owner-badge-pill">
            <Crown size={14} />
            <span>Executive Business Intelligence</span>
          </div>
          <h2>Analytics & Store Reports</h2>
          <p className="reports-subtitle">
            Daily/monthly sales velocity, product best-sellers, inventory margin valuations, and full operational audit trail.
          </p>
        </div>

        <div className="reports-actions">
          <div className="date-badge">
            <Calendar size={14} />
            <span>Today ({new Date().toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })})</span>
          </div>
          <button className="refresh-btn" onClick={loadAllReports} title="Refresh reports">
            <RefreshCw size={15} />
            <span>Refresh All</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="reports-error-banner">
          <span>⚠️ {error}</span>
        </div>
      )}

      {/* Sub-Navigation Tabs */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '10px',
        }}
      >
        <button
          className={`nav-btn ${activeReportTab === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveReportTab('trends')}
          style={{ padding: '8px 16px', borderRadius: '8px' }}
        >
          <BarChart3 size={16} />
          <span>Daily & Monthly Sales</span>
        </button>

        <button
          className={`nav-btn ${activeReportTab === 'bestsellers' ? 'active' : ''}`}
          onClick={() => setActiveReportTab('bestsellers')}
          style={{ padding: '8px 16px', borderRadius: '8px' }}
        >
          <Flame size={16} />
          <span>Best-Selling Products</span>
        </button>

        <button
          className={`nav-btn ${activeReportTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveReportTab('audit')}
          style={{ padding: '8px 16px', borderRadius: '8px' }}
        >
          <ScrollText size={16} />
          <span>Operational Audit Logs</span>
        </button>

        <button
          className={`nav-btn ${activeReportTab === 'valuation' ? 'active' : ''}`}
          onClick={() => setActiveReportTab('valuation')}
          style={{ padding: '8px 16px', borderRadius: '8px' }}
        >
          <Boxes size={16} />
          <span>Inventory & Margins</span>
        </button>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <span>Loading Analytics, Best-Sellers & Audit Trail...</span>
        </div>
      ) : (
        <>
          {/* TAB 1: DAILY / MONTHLY SALES TRENDS */}
          {activeReportTab === 'trends' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div
                style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-lg)',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '16px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '17px', color: '#fff' }}>
                      {trendPeriod === 'daily' ? 'Daily Sales Velocity (Last 14 Days)' : 'Monthly Sales Velocity (Year to Date)'}
                    </h3>
                    <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                      Track gross sales, tax deductions, and realized profits over time
                    </span>
                  </div>

                  {/* Period Switcher */}
                  <div className="discount-pills">
                    <button
                      className={`disc-pill ${trendPeriod === 'daily' ? 'active' : ''}`}
                      onClick={() => setTrendPeriod('daily')}
                    >
                      Daily View
                    </button>
                    <button
                      className={`disc-pill ${trendPeriod === 'monthly' ? 'active' : ''}`}
                      onClick={() => setTrendPeriod('monthly')}
                    >
                      Monthly View
                    </button>
                  </div>
                </div>

                {/* Sales Trends Chart */}
                <div style={{ width: '100%', height: '300px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={trends} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                      <XAxis dataKey="label" stroke="var(--text-dim)" fontSize={12} />
                      <YAxis stroke="var(--text-dim)" fontSize={12} tickFormatter={(v) => `₹${v}`} />
                      <Tooltip
                        contentStyle={{
                          background: '#1e293b',
                          border: '1px solid var(--border-color)',
                          borderRadius: '8px',
                          color: '#fff',
                          fontSize: '12px',
                        }}
                        formatter={(val) => [`₹${Number(val).toFixed(2)}`, '']}
                      />
                      <Legend wrapperStyle={{ fontSize: '12px', color: 'var(--text-muted)' }} />
                      <Bar dataKey="revenue" fill="#10b981" name="Gross Revenue" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="profit" fill="#3b82f6" name="Gross Profit" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="tax" fill="#f59e0b" name="GST Tax" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Data Table of Sales Trends */}
              <div className="inventory-table-card">
                <div className="inventory-toolbar">
                  <h3 style={{ margin: 0, fontSize: '16px', color: '#fff' }}>Detailed Sales Breakdown</h3>
                </div>
                <div className="table-wrapper">
                  <table className="pos-table">
                    <thead>
                      <tr>
                        <th>Period Label</th>
                        <th>Orders Count</th>
                        <th>Gross Revenue</th>
                        <th>GST Tax</th>
                        <th>Gross Profit</th>
                        <th>Est. Margin %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trends.map((row, idx) => {
                        const margin = row.revenue > 0 ? ((row.profit / row.revenue) * 100).toFixed(1) : 0;
                        return (
                          <tr key={idx}>
                            <td><strong>{row.label}</strong></td>
                            <td>{row.orders} checkouts</td>
                            <td className="fw-bold" style={{ color: '#34d399' }}>₹{row.revenue.toFixed(2)}</td>
                            <td>₹{row.tax.toFixed(2)}</td>
                            <td style={{ color: '#60a5fa', fontWeight: 'bold' }}>₹{row.profit.toFixed(2)}</td>
                            <td>{margin}%</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: BEST-SELLING PRODUCTS */}
          {activeReportTab === 'bestsellers' && (
            <div className="inventory-table-card">
              <div className="inventory-toolbar">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Flame size={20} style={{ color: '#f59e0b' }} />
                  <div>
                    <h3 style={{ margin: 0, fontSize: '16px', color: '#fff' }}>Top Best-Selling Grocery Items</h3>
                    <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                      Ranked by transaction sales velocity and gross revenue contribution
                    </span>
                  </div>
                </div>
              </div>

              <div className="table-wrapper">
                <table className="pos-table">
                  <thead>
                    <tr>
                      <th style={{ width: '60px' }}>Rank</th>
                      <th>Product Name</th>
                      <th style={{ textAlign: 'right' }}>Units Sold</th>
                      <th style={{ textAlign: 'right' }}>Avg Unit Rate</th>
                      <th style={{ textAlign: 'right' }}>Total Sales Value</th>
                      <th style={{ width: '220px' }}>Velocity Share</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bestSellers.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="table-empty">
                          No product checkout records found. Complete sales in billing terminal to rank items.
                        </td>
                      </tr>
                    ) : (
                      bestSellers.map((item, idx) => {
                        const maxUnits = bestSellers[0]?.units_sold || 1;
                        const pct = Math.round((item.units_sold / maxUnits) * 100);
                        return (
                          <tr key={idx}>
                            <td>
                              <span
                                style={{
                                  display: 'inline-block',
                                  width: '24px',
                                  height: '24px',
                                  borderRadius: '50%',
                                  background: idx < 3 ? 'rgba(245, 158, 11, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                                  color: idx < 3 ? '#f59e0b' : 'var(--text-muted)',
                                  textAlign: 'center',
                                  lineHeight: '24px',
                                  fontSize: '12px',
                                  fontWeight: 'bold',
                                }}
                              >
                                #{idx + 1}
                              </span>
                            </td>
                            <td>
                              <strong style={{ color: '#fff' }}>{item.product_name}</strong>
                            </td>
                            <td style={{ textAlign: 'right', fontWeight: 'bold' }}>
                              {item.units_sold} units
                            </td>
                            <td style={{ textAlign: 'right' }}>
                              ₹{item.avg_unit_price.toFixed(2)}
                            </td>
                            <td style={{ textAlign: 'right', color: '#34d399', fontWeight: 'bold', fontSize: '14px' }}>
                              ₹{item.total_sales_value.toFixed(2)}
                            </td>
                            <td>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <div
                                  style={{
                                    flex: 1,
                                    height: '6px',
                                    background: 'rgba(255,255,255,0.08)',
                                    borderRadius: '3px',
                                    overflow: 'hidden',
                                  }}
                                >
                                  <div
                                    style={{
                                      width: `${pct}%`,
                                      height: '100%',
                                      background: idx === 0 ? '#10b981' : idx === 1 ? '#3b82f6' : '#f59e0b',
                                      borderRadius: '3px',
                                    }}
                                  ></div>
                                </div>
                                <span style={{ fontSize: '11px', color: 'var(--text-dim)', width: '32px' }}>
                                  {pct}%
                                </span>
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
          )}

          {/* TAB 3: OPERATIONAL AUDIT LOGS */}
          {activeReportTab === 'audit' && (
            <div className="inventory-table-card">
              <div className="inventory-toolbar">
                <div className="search-box">
                  <Search size={18} className="search-icon" />
                  <input
                    type="text"
                    placeholder="Search audit trail by invoice, user, action, or keyword..."
                    value={auditSearch}
                    onChange={(e) => setAuditSearch(e.target.value)}
                  />
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Filter size={16} style={{ color: 'var(--text-dim)' }} />
                  <select
                    className="form-input"
                    value={auditTypeFilter}
                    onChange={(e) => setAuditTypeFilter(e.target.value)}
                    style={{ padding: '8px 12px', fontSize: '13px' }}
                  >
                    <option value="">All Event Types</option>
                    <option value="CHECKOUT">Checkouts (Sales)</option>
                    <option value="RETURN">Customer Returns</option>
                    <option value="PROCUREMENT">Procurement POs</option>
                  </select>
                </div>
              </div>

              <div className="table-wrapper">
                <table className="pos-table">
                  <thead>
                    <tr>
                      <th>Event ID</th>
                      <th>Event Type</th>
                      <th>Action Description</th>
                      <th>Operational Details</th>
                      <th>Operator / Staff</th>
                      <th>Timestamp</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAuditLogs.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="table-empty">
                          No audit log entries match your filter.
                        </td>
                      </tr>
                    ) : (
                      filteredAuditLogs.map((log) => {
                        const isSuccess = log.status === 'SUCCESS' || log.status === 'RECEIVED';
                        const isWarning = log.status === 'REFUNDED' || log.severity === 'WARNING';
                        return (
                          <tr key={log.id}>
                            <td>
                              <code style={{ fontSize: '11px', color: '#94a3b8' }}>{log.id}</code>
                            </td>
                            <td>
                              <span
                                style={{
                                  display: 'inline-block',
                                  padding: '2px 8px',
                                  borderRadius: '4px',
                                  fontSize: '11px',
                                  fontWeight: 'bold',
                                  background:
                                    log.event_type === 'CHECKOUT'
                                      ? 'rgba(16, 185, 129, 0.15)'
                                      : log.event_type === 'RETURN'
                                      ? 'rgba(239, 68, 68, 0.15)'
                                      : 'rgba(59, 130, 246, 0.15)',
                                  color:
                                    log.event_type === 'CHECKOUT'
                                      ? '#34d399'
                                      : log.event_type === 'RETURN'
                                      ? '#f87171'
                                      : '#60a5fa',
                                }}
                              >
                                {log.event_type}
                              </span>
                            </td>
                            <td>
                              <strong style={{ color: '#fff' }}>{log.action}</strong>
                            </td>
                            <td style={{ fontSize: '12px', color: '#cbd5e1' }}>
                              {log.details}
                            </td>
                            <td>{log.user_name}</td>
                            <td style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                              {new Date(log.timestamp).toLocaleString()}
                            </td>
                            <td>
                              <span
                                style={{
                                  padding: '2px 8px',
                                  borderRadius: '12px',
                                  fontSize: '11px',
                                  fontWeight: 'bold',
                                  background: isSuccess
                                    ? 'rgba(16, 185, 129, 0.2)'
                                    : isWarning
                                    ? 'rgba(245, 158, 11, 0.2)'
                                    : 'rgba(255, 255, 255, 0.08)',
                                  color: isSuccess ? '#34d399' : isWarning ? '#fbbf24' : '#cbd5e1',
                                }}
                              >
                                {log.status}
                              </span>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: INVENTORY VALUATION & MARGIN OVERVIEW */}
          {activeReportTab === 'valuation' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {/* Executive KPI Cards */}
              <div className="kpi-cards-grid">
                <div className="kpi-card revenue-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Gross Revenue</span>
                    <div className="kpi-icon-badge bg-green">
                      <DollarSign size={20} />
                    </div>
                  </div>
                  <div className="kpi-value-row">
                    <span className="kpi-currency">₹</span>
                    <span className="kpi-number">{Number(kpis.total_revenue || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div className="kpi-footer text-green">
                    <ArrowUpRight size={14} />
                    <span>{kpis.total_transactions || 0} POS orders completed</span>
                  </div>
                </div>

                <div className="kpi-card profit-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Projected Catalog Profit</span>
                    <div className="kpi-icon-badge bg-blue">
                      <TrendingUp size={20} />
                    </div>
                  </div>
                  <div className="kpi-value-row">
                    <span className="kpi-currency">₹</span>
                    <span className="kpi-number">{Number(inv.projected_profit || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div className="kpi-footer text-blue">
                    <span>Catalog Margin: <strong>{inv.profit_margin_pct || 0}%</strong></span>
                  </div>
                </div>

                <div className="kpi-card inventory-card">
                  <div className="kpi-header">
                    <span className="kpi-title">Inventory Retail Value</span>
                    <div className="kpi-icon-badge bg-purple">
                      <Boxes size={20} />
                    </div>
                  </div>
                  <div className="kpi-value-row">
                    <span className="kpi-currency">₹</span>
                    <span className="kpi-number">{Number(inv.inventory_retail_valuation || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div className="kpi-footer text-purple">
                    <span>Cost basis: ₹{Number(inv.inventory_cost_valuation || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                </div>

                <div className="kpi-card tax-card">
                  <div className="kpi-header">
                    <span className="kpi-title">GST Tax Collected</span>
                    <div className="kpi-icon-badge bg-amber">
                      <Receipt size={20} />
                    </div>
                  </div>
                  <div className="kpi-value-row">
                    <span className="kpi-currency">₹</span>
                    <span className="kpi-number">{Number(kpis.total_tax_collected || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div className="kpi-footer text-amber">
                    <span>Discounts given: ₹{Number(kpis.total_discounts_given || 0).toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Department Distribution Bars */}
              <div className="report-panel">
                <div className="panel-header">
                  <div className="panel-title-with-icon">
                    <PieIcon size={18} />
                    <h3>Grocery Department Catalog Distribution</h3>
                  </div>
                  <span className="badge-count">{inv.total_catalog_items || 655} items total</span>
                </div>

                <div className="category-bars-list">
                  {categories.map((cat) => {
                    const totalItems = inv.total_catalog_items || 655;
                    const pct = Math.round((cat.item_count / totalItems) * 100);
                    return (
                      <div key={cat.category} className="cat-bar-row">
                        <div className="cat-bar-meta">
                          <span className="cat-name">{cat.category}</span>
                          <span className="cat-count">{cat.item_count} items ({pct}%)</span>
                        </div>
                        <div className="cat-progress-track">
                          <div
                            className="cat-progress-fill"
                            style={{ width: `${Math.max(5, pct)}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
