// Empty string = same-origin (nginx proxies /api/ → backend in Docker)
const API_BASE = import.meta.env.VITE_API_URL || '';

export function getToken(): string | null {
  return localStorage.getItem('skinintel_token');
}

export function setToken(token: string) {
  localStorage.setItem('skinintel_token', token);
}

export function clearToken() {
  localStorage.removeItem('skinintel_token');
  localStorage.removeItem('skinintel_user');
}

export function getUser(): User | null {
  const raw = localStorage.getItem('skinintel_user');
  return raw ? JSON.parse(raw) : null;
}

export function setUser(user: User) {
  localStorage.setItem('skinintel_user', JSON.stringify(user));
}

export interface User {
  user_id: string;
  full_name: string;
  email: string;
  country: string;
}

async function apiFetch(path: string, options: RequestInit = {}) {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const json = await res.json();
  return json;
}

export async function apiRegister(data: {
  full_name: string; email: string; password: string; country: string;
}) {
  return apiFetch('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(data) });
}

export async function apiLogin(data: { email: string; password: string }) {
  return apiFetch('/api/v1/auth/login', { method: 'POST', body: JSON.stringify(data) });
}

export function isLoggedIn(): boolean {
  return !!getToken();
}
