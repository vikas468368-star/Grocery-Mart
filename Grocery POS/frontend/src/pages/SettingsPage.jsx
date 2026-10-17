import React, { useState, useEffect } from 'react';
import {
  Settings as SettingsIcon,
  Store,
  Users,
  ShieldCheck,
  Save,
  Plus,
  Crown,
  Printer,
  FileText,
  CheckCircle,
  X,
  UserCheck,
} from 'lucide-react';
import { getStoreSettings, updateStoreSettings, getUsersList, createStaffUser } from '../api/authApi';
import { useAuth } from '../context/AuthContext';

export default function SettingsPage() {
  const { user, isOwner } = useAuth();
  const [activeSubTab, setActiveSubTab] = useState('store');
  const [settings, setSettings] = useState({
    store_name: '',
    tagline: '',
    address: '',
    city: '',
    state: '',
    postal_code: '',
    gstin: '',
    contact_phone: '',
    contact_email: '',
    receipt_header: '',
    receipt_footer: '',
    currency_symbol: '₹',
    enable_auto_print: true,
  });
  const [staffUsers, setStaffUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [newUserForm, setNewUserForm] = useState({
    username: '',
    full_name: '',
    password: '',
    role: 'Cashier',
    email: '',
    phone: '',
  });

  useEffect(() => {
    loadSettingsAndUsers();
  }, []);

  const loadSettingsAndUsers = async () => {
    setLoading(true);
    try {
      const [settData, usersData] = await Promise.all([
        getStoreSettings(),
        getUsersList(),
      ]);
      setSettings(settData || {});
      setStaffUsers(usersData || []);
    } catch (err) {
      console.warn('Could not load settings:', err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    try {
      await updateStoreSettings(settings);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert(`Failed to save settings: ${err.message}`);
    }
  };

  const handleCreateStaff = async (e) => {
    e.preventDefault();
    try {
      await createStaffUser(newUserForm);
      setShowAddUserModal(false);
      setNewUserForm({
        username: '',
        full_name: '',
        password: '',
        role: 'Cashier',
        email: '',
        phone: '',
      });
      loadSettingsAndUsers();
    } catch (err) {
      alert(`Failed to register staff: ${err.message}`);
    }
  };

  if (!isOwner) {
    return (
      <div className="unauthorized-page-state">
        <div className="unauthorized-card">
          <ShieldCheck size={56} className="unauthorized-icon" />
          <h2>Settings Restricted to Store Owner</h2>
          <p>
            Your current role is <strong>{user?.role}</strong>. Store tax rules, receipt configurations,
            and staff user permissions are only accessible by the Store Owner.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-page-container">
      <div className="settings-header">
        <div className="title-area">
          <div className="owner-badge-pill">
            <Crown size={14} />
            <span>Owner Administration</span>
          </div>
          <h2>Store Configuration & Staff Management</h2>
          <p className="settings-subtitle">Manage store details, tax GSTIN, thermal receipt printing, and staff roles.</p>
        </div>

        <div className="settings-subnav">
          <button
            className={`subnav-btn ${activeSubTab === 'store' ? 'active' : ''}`}
            onClick={() => setActiveSubTab('store')}
          >
            <Store size={16} />
            <span>Store Profile & Tax</span>
          </button>
          <button
            className={`subnav-btn ${activeSubTab === 'staff' ? 'active' : ''}`}
            onClick={() => setActiveSubTab('staff')}
          >
            <Users size={16} />
            <span>Staff & User Roles ({staffUsers.length})</span>
          </button>
        </div>
      </div>

      {savedSuccess && (
        <div className="save-success-banner">
          <CheckCircle size={18} />
          <span>Store settings successfully updated!</span>
        </div>
      )}

      {activeSubTab === 'store' && (
        <form className="settings-form-panel" onSubmit={handleSaveSettings}>
          <div className="form-section-card">
            <div className="section-title">
              <Store size={18} />
              <h3>Store Profile & GST Details</h3>
            </div>

            <div className="form-grid-2">
              <div className="form-field">
                <label>Supermarket / Store Name</label>
                <input
                  type="text"
                  value={settings.store_name || ''}
                  onChange={(e) => setSettings({ ...settings, store_name: e.target.value })}
                  required
                />
              </div>

              <div className="form-field">
                <label>Marketing Tagline</label>
                <input
                  type="text"
                  value={settings.tagline || ''}
                  onChange={(e) => setSettings({ ...settings, tagline: e.target.value })}
                />
              </div>

              <div className="form-field full-width">
                <label>Street Address</label>
                <input
                  type="text"
                  value={settings.address || ''}
                  onChange={(e) => setSettings({ ...settings, address: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label>City & State</label>
                <input
                  type="text"
                  value={`${settings.city || ''}, ${settings.state || ''}`}
                  onChange={(e) => setSettings({ ...settings, city: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label>GSTIN / Tax ID Number</label>
                <input
                  type="text"
                  value={settings.gstin || ''}
                  onChange={(e) => setSettings({ ...settings, gstin: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label>Contact Phone</label>
                <input
                  type="text"
                  value={settings.contact_phone || ''}
                  onChange={(e) => setSettings({ ...settings, contact_phone: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label>Support Email</label>
                <input
                  type="email"
                  value={settings.contact_email || ''}
                  onChange={(e) => setSettings({ ...settings, contact_email: e.target.value })}
                />
              </div>
            </div>
          </div>

          <div className="form-section-card">
            <div className="section-title">
              <Printer size={18} />
              <h3>Thermal Receipt Customization</h3>
            </div>

            <div className="form-grid-2">
              <div className="form-field">
                <label>Receipt Header Message</label>
                <input
                  type="text"
                  value={settings.receipt_header || ''}
                  onChange={(e) => setSettings({ ...settings, receipt_header: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label>Receipt Footer & Return Policy</label>
                <input
                  type="text"
                  value={settings.receipt_footer || ''}
                  onChange={(e) => setSettings({ ...settings, receipt_footer: e.target.value })}
                />
              </div>
            </div>
          </div>

          <div className="form-footer-action">
            <button type="submit" className="save-settings-btn">
              <Save size={16} />
              <span>Save Changes</span>
            </button>
          </div>
        </form>
      )}

      {activeSubTab === 'staff' && (
        <div className="staff-management-panel">
          <div className="staff-panel-header">
            <div>
              <h3>Active Store Staff & Cashiers</h3>
              <p>Role-Based Access Control determines permissions for Billing, Inventory, and Financial Reports.</p>
            </div>
            <button className="add-staff-btn" onClick={() => setShowAddUserModal(true)}>
              <Plus size={16} />
              <span>Register New Staff</span>
            </button>
          </div>

          <div className="staff-users-grid">
            {staffUsers.map((u) => {
              const roleLower = (u.role || '').toLowerCase();
              return (
                <div key={u.id} className="staff-user-card">
                  <div className="staff-card-top">
                    <div className="staff-avatar">{u.full_name?.charAt(0) || 'U'}</div>
                    <div className="staff-info">
                      <h4>{u.full_name}</h4>
                      <span className="staff-username">@{u.username}</span>
                    </div>
                    <span className={`staff-role-badge badge-${roleLower}`}>
                      {u.role === 'Owner' && '👑 '}
                      {u.role === 'Manager' && '💼 '}
                      {u.role === 'Cashier' && '💳 '}
                      {u.role}
                    </span>
                  </div>

                  <div className="staff-card-details">
                    <div className="detail-item">
                      <span className="detail-label">Email:</span>
                      <span className="detail-val">{u.email || 'None'}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Phone:</span>
                      <span className="detail-val">{u.phone || 'None'}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Permissions:</span>
                      <span className="detail-val">
                        {u.role === 'Owner' && 'Full Access (Financials, Settings, Inventory, Billing)'}
                        {u.role === 'Manager' && 'Inventory Control, Reordering, Catalog, Billing'}
                        {u.role === 'Cashier' && 'POS Billing Terminal Only'}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Add Staff Modal */}
      {showAddUserModal && (
        <div className="modal-backdrop">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Register New Staff Member</h3>
              <button className="modal-close-btn" onClick={() => setShowAddUserModal(false)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateStaff} className="modal-body form-grid-2">
              <div className="form-field">
                <label>Staff Username *</label>
                <input
                  type="text"
                  value={newUserForm.username}
                  onChange={(e) => setNewUserForm({ ...newUserForm, username: e.target.value })}
                  placeholder="e.g. cashier3, manager2"
                  required
                />
              </div>

              <div className="form-field">
                <label>Full Name *</label>
                <input
                  type="text"
                  value={newUserForm.full_name}
                  onChange={(e) => setNewUserForm({ ...newUserForm, full_name: e.target.value })}
                  placeholder="e.g. Ramesh Kumar"
                  required
                />
              </div>

              <div className="form-field">
                <label>Password *</label>
                <input
                  type="password"
                  value={newUserForm.password}
                  onChange={(e) => setNewUserForm({ ...newUserForm, password: e.target.value })}
                  placeholder="Minimum 4 characters"
                  required
                />
              </div>

              <div className="form-field">
                <label>Assigned Role *</label>
                <select
                  value={newUserForm.role}
                  onChange={(e) => setNewUserForm({ ...newUserForm, role: e.target.value })}
                >
                  <option value="Cashier">💳 Cashier (Billing Terminal Only)</option>
                  <option value="Manager">💼 Manager (Inventory & Billing)</option>
                  <option value="Owner">👑 Owner (Full Access)</option>
                </select>
              </div>

              <div className="form-field">
                <label>Email Address</label>
                <input
                  type="email"
                  value={newUserForm.email}
                  onChange={(e) => setNewUserForm({ ...newUserForm, email: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label>Phone Number</label>
                <input
                  type="text"
                  value={newUserForm.phone}
                  onChange={(e) => setNewUserForm({ ...newUserForm, phone: e.target.value })}
                />
              </div>

              <div className="modal-footer full-width">
                <button type="button" className="btn-secondary" onClick={() => setShowAddUserModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Create Staff Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
