import { apiFetch } from './client';

export async function getDashboardMetrics() {
  return apiFetch('/reports/dashboard');
}

export async function getSalesTrends(period = 'daily') {
  try {
    return await apiFetch(`/reports/sales-trends?period=${period}`);
  } catch {
    return [];
  }
}

export async function getBestSellers(limit = 10) {
  try {
    return await apiFetch(`/reports/best-sellers?limit=${limit}`);
  } catch {
    return [];
  }
}

export async function getAuditLogs(limit = 50) {
  try {
    return await apiFetch(`/reports/audit-logs?limit=${limit}`);
  } catch {
    return [];
  }
}

export async function getExecutiveSummary() {
  return await apiFetch('/reports/summary');
}
