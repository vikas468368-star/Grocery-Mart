import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  ReceiptText,
  Maximize2,
  Laptop,
  ShieldCheck,
  TrendingUp,
  Settings as SettingsIcon,
  LogOut,
  Crown,
  Briefcase,
  CreditCard,
  Truck,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Header({ activeTab, setActiveTab }) {
  const { user, role, isOwner, isManager, logout } = useAuth();
  const [time, setTime] = useState(new Date().toLocaleTimeString());
  const [isElectron, setIsElectron] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
    if (window.electronAPI?.isElectron) {
      setIsElectron(true);
    }
    return () => clearInterval(timer);
  }, []);

  const handleToggleFullscreen = () => {
    if (window.electronAPI?.toggleKiosk) {
      window.electronAPI.toggleKiosk();
    } else if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  };

  const getRoleIcon = () => {
    if (role === 'Owner') return <Crown size={13} className="text-amber" />;
    if (role === 'Manager') return <Briefcase size={13} className="text-blue" />;
    return <CreditCard size={13} className="text-green" />;
  };

  const getRoleBadgeClass = () => {
    if (role === 'Owner') return 'badge-owner';
    if (role === 'Manager') return 'badge-manager';
    return 'badge-cashier';
  };

  return (
    <header className="pos-header">
      <div className="pos-header-left">
        <div className="pos-brand">
          <div className="brand-logo">🛒</div>
          <div>
            <h1 className="brand-title">GROCERY POS</h1>
            <span className="brand-subtitle">Retail Enterprise Billing System</span>
          </div>
        </div>

        <nav className="pos-nav">
          {/* Main Analytics Dashboard - Visible to All */}
          <button
            className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </button>

          {/* Billing Terminal - Visible to Cashier, Manager, Owner */}
          <button
            className={`nav-btn ${activeTab === 'pos' ? 'active' : ''}`}
            onClick={() => setActiveTab('pos')}
          >
            <ShoppingCart size={18} />
            <span>Billing Terminal</span>
          </button>

          {/* Inventory - Visible to Manager and Owner */}
          {isManager && (
            <button
              className={`nav-btn ${activeTab === 'inventory' ? 'active' : ''}`}
              onClick={() => setActiveTab('inventory')}
            >
              <Package size={18} />
              <span>Inventory & Stock</span>
            </button>
          )}

          {/* Suppliers & Procurement - Visible to Manager and Owner */}
          {isManager && (
            <button
              className={`nav-btn ${activeTab === 'suppliers' ? 'active' : ''}`}
              onClick={() => setActiveTab('suppliers')}
            >
              <Truck size={18} />
              <span>Suppliers & Orders</span>
            </button>
          )}

          {/* Sales History & Returns - Visible to All */}
          <button
            className={`nav-btn ${activeTab === 'transactions' ? 'active' : ''}`}
            onClick={() => setActiveTab('transactions')}
          >
            <ReceiptText size={18} />
            <span>Sales History</span>
          </button>

          {/* Owner Executive Reports - Restricted to Owner */}
          {isOwner && (
            <button
              className={`nav-btn ${activeTab === 'reports' ? 'active' : ''} owner-nav-highlight`}
              onClick={() => setActiveTab('reports')}
            >
              <TrendingUp size={18} />
              <span>👑 Executive Reports</span>
            </button>
          )}

          {/* Owner Settings - Restricted to Owner */}
          {isOwner && (
            <button
              className={`nav-btn ${activeTab === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveTab('settings')}
            >
              <SettingsIcon size={18} />
              <span>Store Settings</span>
            </button>
          )}
        </nav>
      </div>

      <div className="pos-header-right">
        <div className="status-badge platform-badge">
          {isElectron ? <Laptop size={14} /> : <ShieldCheck size={14} />}
          <span>{isElectron ? 'Electron Desktop' : 'Web Terminal'}</span>
        </div>

        <div className="status-badge live-clock">
          <span>{time}</span>
        </div>

        {/* Logged in Staff Badge */}
        <div className="staff-user-pill">
          <div className="staff-avatar-mini">
            {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
          </div>
          <div className="staff-text-col">
            <span className="staff-display-name">{user?.full_name || user?.username || 'Staff'}</span>
            <div className={`staff-role-chip ${getRoleBadgeClass()}`}>
              {getRoleIcon()}
              <span>{role || 'Cashier'}</span>
            </div>
          </div>
        </div>

        {/* Fullscreen Toggle */}
        <button
          className="icon-btn"
          title="Toggle POS Kiosk / Fullscreen Mode"
          onClick={handleToggleFullscreen}
        >
          <Maximize2 size={18} />
        </button>

        {/* Logout Button */}
        <button
          className="logout-header-btn"
          onClick={logout}
          title="Sign out of current register/session"
        >
          <LogOut size={16} />
          <span>Log Out</span>
        </button>
      </div>
    </header>
  );
}
