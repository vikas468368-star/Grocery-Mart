import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, getProfile, logoutUser } from '../api/authApi';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('pos_token') || null);
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('pos_user');
    try {
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  // Validate or refresh session on startup if token exists
  useEffect(() => {
    async function verifySession() {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const profile = await getProfile();
        setUser(profile);
        localStorage.setItem('pos_user', JSON.stringify(profile));
      } catch (err) {
        console.warn('Session expired or invalid, logging out:', err.message);
        logout();
      } finally {
        setLoading(false);
      }
    }
    verifySession();
  }, [token]);

  const login = async (username, password) => {
    const res = await loginUser(username, password);
    const accessToken = res.access_token;
    const userData = res.user;

    localStorage.setItem('pos_token', accessToken);
    localStorage.setItem('pos_user', JSON.stringify(userData));

    setToken(accessToken);
    setUser(userData);

    return userData;
  };

  const logout = () => {
    logoutUser().catch(() => {});
    localStorage.removeItem('pos_token');
    localStorage.removeItem('pos_user');
    setToken(null);
    setUser(null);
  };

  const role = user?.role || null;
  const isOwner = role === 'Owner';
  const isManager = role === 'Manager' || isOwner;
  const isCashier = role === 'Cashier' || isManager;

  // Determine standard landing page / dashboard based on role
  const getDefaultTabForRole = (userRole) => {
    const r = userRole || role;
    if (r === 'Owner') return 'reports';
    if (r === 'Manager') return 'inventory';
    return 'pos';
  };

  const value = {
    token,
    user,
    role,
    isAuthenticated: Boolean(token && user),
    loading,
    login,
    logout,
    isOwner,
    isManager,
    isCashier,
    getDefaultTabForRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
