import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { User, Shield, Activity, LogOut } from 'lucide-react';
import api from '../services/api';

export default function SettingsPage() {
  const { user, logout } = useAuthStore();
  const [health, setHealth] = useState(null);

  useEffect(() => {
    api.get('/health').then((res) => setHealth(res.data)).catch(console.error);
  }, []);

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6 animate-fadeIn w-full">
      <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Profile & System Info</h1>

      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <User className="w-5 h-5 text-indigo-400" />
          <span>User Profile</span>
        </h3>
        <div className="flex items-center gap-4 pt-2">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center text-xl font-bold text-white">
            {user?.name?.charAt(0) || 'U'}
          </div>
          <div>
            <div className="text-lg font-bold text-white">{user?.name}</div>
            <div className="text-sm text-slate-400">{user?.email}</div>
            <span className="inline-block mt-1 text-xs font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2.5 py-0.5 rounded-full">
              {(user?.role || 'student').toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Activity className="w-5 h-5 text-emerald-400" />
          <span>System Status</span>
        </h3>
        <div className="space-y-2 text-sm text-slate-300">
          <div className="flex justify-between py-1 border-b border-slate-800">
            <span className="text-slate-400">RAG Pipeline Status:</span>
            <span className="font-mono text-emerald-400 font-bold">ACTIVE</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-800">
            <span className="text-slate-400">Vector Store (Qdrant):</span>
            <span className="font-mono text-cyan-400">{health?.vector_store?.total_vectors || 0} vectors</span>
          </div>
          <div className="flex justify-between py-1 border-b border-slate-800">
            <span className="text-slate-400">Database Engine:</span>
            <span className="font-mono text-slate-300">
              {health?.database?.is_fallback ? 'Embedded Async DB' : 'MongoDB Atlas'}
            </span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-slate-400">LLM Provider:</span>
            <span className="font-mono text-indigo-400">{health?.llm?.model || 'Gemini'}</span>
          </div>
        </div>
      </div>

      <div className="text-center pt-2">
        <button
          onClick={logout}
          className="bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 px-5 py-2.5 rounded-xl text-sm font-semibold transition flex items-center gap-2 mx-auto"
        >
          <LogOut className="w-4 h-4" />
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  );
}
