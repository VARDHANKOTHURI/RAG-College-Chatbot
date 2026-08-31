import { create } from 'zustand';
import api from '../services/api';

export const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  token: localStorage.getItem('token') || null,
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      set({ user, token: access_token, isAuthenticated: true, loading: false });
      return true;
    } catch (err) {
      set({
        error: err.response?.data?.message || err.response?.data?.detail?.message || 'Login failed',
        loading: false,
      });
      return false;
    }
  },

  register: async (name, email, password, role = 'student') => {
    set({ loading: true, error: null });
    try {
      const response = await api.post('/auth/register', { name, email, password, role });
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      set({ user, token: access_token, isAuthenticated: true, loading: false });
      return true;
    } catch (err) {
      set({
        error: err.response?.data?.message || err.response?.data?.detail?.message || 'Registration failed',
        loading: false,
      });
      return false;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ user: null, token: null, isAuthenticated: false });
  },
}));
