import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import Header from './components/Header';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import POSPage from './pages/POSPage';
import InventoryPage from './pages/InventoryPage';
import TransactionsPage from './pages/TransactionsPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';
import SupplierPage from './pages/SupplierPage';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import './index.css';

function MainAppContent() {
  const { isAuthenticated, loading, role, isOwner, isManager, getDefaultTabForRole } = useAuth();
  const [activeTab, setActiveTab] = useState('pos');

  // Set default tab when user logs in or role is available
  useEffect(() => {
    if (isAuthenticated && role) {
      setActiveTab(getDefaultTabForRole(role));
    }
  }, [isAuthenticated, role]);

  if (loading) {
    return (
      <div className="app-splash-screen">
        <div className="splash-card">
          <div className="spinner-large"></div>
          <h2>GROCERY POS ENTERPRISE</h2>
          <p>Verifying secure session token & RBAC permissions...</p>
        </div>
      </div>
    );
  }

  // If not authenticated, display the login page
  if (!isAuthenticated) {
    return (
      <LoginPage
        onLoginSuccess={(targetTab) => {
          setActiveTab(targetTab || 'pos');
        }}
      />
    );
  }

  // Access validation for restricted tabs
  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage setActiveTab={setActiveTab} />;

      case 'pos':
        return <POSPage />;

      case 'inventory':
        if (!isManager) {
          return (
            <div className="unauthorized-page-state">
              <div className="unauthorized-card">
                <ShieldAlert size={56} className="unauthorized-icon" />
                <h2>Access Restricted</h2>
                <p>
                  Your current role (<strong>{role}</strong>) does not permit access to Inventory &
                  Stock Procurement. Please return to the Billing Terminal.
                </p>
                <button className="btn-primary back-terminal-btn" onClick={() => setActiveTab('pos')}>
                  <ArrowLeft size={16} /> Return to Billing Terminal
                </button>
              </div>
            </div>
          );
        }
        return <InventoryPage />;

      case 'suppliers':
        if (!isManager) {
          return (
            <div className="unauthorized-page-state">
              <div className="unauthorized-card">
                <ShieldAlert size={56} className="unauthorized-icon" />
                <h2>Access Restricted</h2>
                <p>
                  Your current role (<strong>{role}</strong>) does not permit access to Supplier
                  Procurement and Purchase Orders.
                </p>
                <button className="btn-primary back-terminal-btn" onClick={() => setActiveTab('pos')}>
                  <ArrowLeft size={16} /> Return to Billing Terminal
                </button>
              </div>
            </div>
          );
        }
        return <SupplierPage />;

      case 'transactions':
        return <TransactionsPage />;

      case 'reports':
        if (!isOwner) {
          return (
            <div className="unauthorized-page-state">
              <div className="unauthorized-card">
                <ShieldAlert size={56} className="unauthorized-icon" />
                <h2>Store Owner Portal Only</h2>
                <p>
                  Executive financial statements, margin analytics, and store profitability are
                  confidential and restricted to the Store Owner.
                </p>
                <button className="btn-primary back-terminal-btn" onClick={() => setActiveTab('pos')}>
                  <ArrowLeft size={16} /> Return to Billing Terminal
                </button>
              </div>
            </div>
          );
        }
        return <ReportsPage />;

      case 'settings':
        if (!isOwner) {
          return (
            <div className="unauthorized-page-state">
              <div className="unauthorized-card">
                <ShieldAlert size={56} className="unauthorized-icon" />
                <h2>Owner Administration Only</h2>
                <p>Tax configuration and staff management are restricted to the Store Owner.</p>
                <button className="btn-primary back-terminal-btn" onClick={() => setActiveTab('pos')}>
                  <ArrowLeft size={16} /> Return to Billing Terminal
                </button>
              </div>
            </div>
          );
        }
        return <SettingsPage />;

      default:
        return <POSPage />;
    }
  };

  return (
    <CartProvider>
      <div className="app-container">
        {/* Navigation & POS Header with Role Badge */}
        <Header activeTab={activeTab} setActiveTab={setActiveTab} />

        {/* Dynamic View Panel with RBAC protection */}
        <main className="pos-body-content">{renderTabContent()}</main>
      </div>
    </CartProvider>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainAppContent />
    </AuthProvider>
  );
}
