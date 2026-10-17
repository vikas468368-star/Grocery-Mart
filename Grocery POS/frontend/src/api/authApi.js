import { apiFetch } from './client';

export async function loginUser(username, password) {
  return await apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

export async function getProfile() {
  return await apiFetch('/auth/me');
}

export async function logoutUser() {
  try {
    return await apiFetch('/auth/logout', { method: 'POST' });
  } catch {
    return { success: true };
  }
}

// Owner Reports & KPIs
export async function getReportsSummary() {
  return await apiFetch('/reports/summary');
}

export async function getTopProducts(limit = 10) {
  return await apiFetch(`/reports/top-products?limit=${limit}`);
}

// Owner Store Settings
export async function getStoreSettings() {
  return await apiFetch('/settings/');
}

export async function updateStoreSettings(settingsData) {
  return await apiFetch('/settings/', {
    method: 'PUT',
    body: JSON.stringify(settingsData),
  });
}

// User / Staff Management
export async function getUsersList() {
  return await apiFetch('/users/');
}

export async function createStaffUser(userData) {
  return await apiFetch('/users/', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
}
