const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${endpoint}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Assets
export const assetsAPI = {
  list: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return fetchAPI<any>(`/api/v1/assets${query}`);
  },
  get: (id: string) => fetchAPI<any>(`/api/v1/assets/${id}`),
  create: (data: any) => fetchAPI<any>("/api/v1/assets", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: any) => fetchAPI<any>(`/api/v1/assets/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};

// Sensors
export const sensorsAPI = {
  history: (assetId: string, days = 7) =>
    fetchAPI<any[]>(`/api/v1/sensors/history?asset_id=${assetId}&days=${days}`),
  hourly: (assetId: string, days = 7) =>
    fetchAPI<any[]>(`/api/v1/sensors/hourly?asset_id=${assetId}&days=${days}`),
};

// Alerts
export const alertsAPI = {
  list: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return fetchAPI<any>(`/api/v1/alerts${query}`);
  },
  get: (id: string) => fetchAPI<any>(`/api/v1/alerts/${id}`),
  acknowledge: (id: string, userId?: string) =>
    fetchAPI<any>(`/api/v1/alerts/${id}/acknowledge`, { method: "POST", body: JSON.stringify({ acknowledged_by: userId || "operator" }) }),
  resolve: (id: string) =>
    fetchAPI<any>(`/api/v1/alerts/${id}/resolve`, { method: "POST", body: JSON.stringify({}) }),
};

// Work Orders
export const workOrdersAPI = {
  list: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return fetchAPI<any>(`/api/v1/workorders${query}`);
  },
  get: (id: string) => fetchAPI<any>(`/api/v1/workorders/${id}`),
  create: (data: any) => fetchAPI<any>("/api/v1/workorders", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: any) => fetchAPI<any>(`/api/v1/workorders/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  approve: (id: string, userId?: string) =>
    fetchAPI<any>(`/api/v1/workorders/${id}/approve`, { method: "POST", body: JSON.stringify({ approved_by: userId || "operator" }) }),
};

// Analytics
export const analyticsAPI = {
  dashboard: (municipalityId?: string) => {
    const query = municipalityId ? `?municipality_id=${municipalityId}` : "";
    return fetchAPI<any>(`/api/v1/analytics/dashboard${query}`);
  },
};

// Agents
export const agentsAPI = {
  list: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return fetchAPI<any>(`/api/v1/agents/runs${query}`);
  },
  listRuns: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return fetchAPI<any>(`/api/v1/agents/runs${query}`);
  },
  getRun: (id: string) => fetchAPI<any>(`/api/v1/agents/runs/${id}`),
  trigger: (data: any) => fetchAPI<any>("/api/v1/agents/trigger", { method: "POST", body: JSON.stringify(data) }),
};

// Reports
export const reportsAPI = {
  list: (params?: Record<string, string>) => {
    const query = params ? `?${new URLSearchParams(params)}` : "";
    return fetchAPI<any>(`/api/v1/reports${query}`);
  },
};
