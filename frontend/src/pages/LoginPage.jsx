import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { LogIn } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('student@college.edu');
  const [password, setPassword] = useState('Student@123');
  const { login, loading, error } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/chat';

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(email, password);
    if (success) {
      navigate(from, { replace: true });
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16 w-full animate-fadeIn">
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-8 space-y-6 shadow-2xl">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 mx-auto flex items-center justify-center text-indigo-400">
            <LogIn className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold text-white">Student & Staff Login</h2>
          <p className="text-xs text-slate-400">Sign in with your institutional credentials</p>
        </div>

        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-white rounded-xl px-4 py-2.5 text-sm outline-none transition"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full bg-slate-950 border border-slate-800 focus:border-indigo-500 text-white rounded-xl px-4 py-2.5 text-sm outline-none transition"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold py-2.5 rounded-xl text-sm transition shadow-lg shadow-indigo-600/30"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div className="text-center text-xs text-slate-400">
          New student?{' '}
          <Link to="/register" className="text-indigo-400 hover:underline font-semibold">
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
}
