import React, { useState } from 'react';
import { Lock, User, Eye, EyeOff, ShieldCheck, ArrowRight, Sparkles, Store, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const QUICK_TEST_ACCOUNTS = [
  {
    role: 'Owner',
    username: 'owner',
    password: 'password123',
    title: 'Store Owner',
    tag: 'Full Access',
    color: 'badge-owner',
    desc: 'Executive Reports, Profit Margins, Staff & Store Settings',
    target: 'reports',
    icon: '👑',
  },
  {
    role: 'Manager',
    username: 'manager',
    password: 'password123',
    title: 'Store Manager',
    tag: 'Inventory & Purchasing',
    color: 'badge-manager',
    desc: 'Stock Reordering, Catalog Edits, Suppliers & Invoices',
    target: 'inventory',
    icon: '💼',
  },
  {
    role: 'Cashier',
    username: 'cashier1',
    password: 'password123',
    title: 'Terminal Cashier',
    tag: 'Billing Only',
    color: 'badge-cashier',
    desc: 'High-speed Barcode Scanning, Cart Billing & Receipts',
    target: 'pos',
    icon: '💳',
  },
];

export default function LoginPage({ onLoginSuccess }) {
  const { login, getDefaultTabForRole } = useAuth();
  const [username, setUsername] = useState('owner');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!username.trim() || !password) {
      setErrorMsg('Please enter both username and password.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg('');

    try {
      const loggedUser = await login(username.trim(), password);
      const defaultTab = getDefaultTabForRole(loggedUser.role);
      if (onLoginSuccess) {
        onLoginSuccess(defaultTab, loggedUser);
      }
    } catch (err) {
      setErrorMsg(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSelectQuickAccount = async (account) => {
    setUsername(account.username);
    setPassword(account.password);
    setErrorMsg('');
    setIsSubmitting(true);
    try {
      const loggedUser = await login(account.username, account.password);
      const targetTab = account.target || getDefaultTabForRole(loggedUser.role);
      if (onLoginSuccess) {
        onLoginSuccess(targetTab, loggedUser);
      }
    } catch (err) {
      setErrorMsg(err.message || 'Login failed.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-page-container">
      <div className="login-ambient-glow login-glow-1"></div>
      <div className="login-ambient-glow login-glow-2"></div>

      <div className="login-card-wrapper">
        <div className="login-branding">
          <div className="login-logo-circle">
            <Store size={36} className="login-store-icon" />
          </div>
          <h2 className="login-title">GROCERY POS ENTERPRISE</h2>
          <p className="login-subtitle">Secure Retail POS Terminal & Management System</p>
        </div>

        {errorMsg && (
          <div className="login-error-alert">
            <span>⚠️ {errorMsg}</span>
          </div>
        )}

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-field">
            <label>Username / Staff ID</label>
            <div className="input-with-icon">
              <User size={18} className="field-icon" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter staff username (e.g. owner, cashier1)"
                autoComplete="username"
                required
              />
            </div>
          </div>

          <div className="form-field">
            <label>Password</label>
            <div className="input-with-icon">
              <Lock size={18} className="field-icon" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter account password"
                autoComplete="current-password"
                required
              />
              <button
                type="button"
                className="toggle-password-btn"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex="-1"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="login-submit-btn"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <span className="btn-loading">
                <span className="spinner-small"></span> Authenticating Staff...
              </span>
            ) : (
              <>
                <span>Sign In to Terminal</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="quick-accounts-section">
          <div className="quick-accounts-header">
            <Sparkles size={14} />
            <span>Select Demo Staff Role to Test RBAC:</span>
          </div>

          <div className="quick-accounts-grid">
            {QUICK_TEST_ACCOUNTS.map((acc) => (
              <button
                key={acc.username}
                type="button"
                className={`quick-account-card ${acc.color}`}
                onClick={() => handleSelectQuickAccount(acc)}
                disabled={isSubmitting}
                title={`Quick sign in as ${acc.title}`}
              >
                <div className="acc-card-top">
                  <span className="acc-icon">{acc.icon}</span>
                  <div className="acc-title-col">
                    <span className="acc-role-name">{acc.title}</span>
                    <span className="acc-username">@{acc.username}</span>
                  </div>
                  <span className="acc-pill">{acc.tag}</span>
                </div>
                <p className="acc-desc">{acc.desc}</p>
                <span className="acc-redirect-hint">➜ Redirects to: <strong>{acc.target.toUpperCase()}</strong></span>
              </button>
            ))}
          </div>
        </div>

        <div className="login-footer">
          <ShieldCheck size={14} />
          <span>Role-Based Access Control (RBAC) Active • SHA-256 / JWT Secured</span>
        </div>
      </div>
    </div>
  );
}
