import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { GraduationCap, MessageSquare, BookOpen, Shield, Settings, LogOut } from 'lucide-react';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <GraduationCap className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="text-lg font-bold bg-gradient-to-r from-indigo-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent block leading-tight">
              CampusAI
            </span>
            <span className="text-[10px] text-slate-400 font-mono tracking-widest uppercase">
              RAG College Assistant
            </span>
          </div>
        </Link>

        <div className="flex items-center gap-2 sm:gap-4">
          {isAuthenticated ? (
            <>
              <Link
                to="/chat"
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition flex items-center gap-1.5 ${
                  isActive('/chat') ? 'bg-indigo-600 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                <span>Chat</span>
              </Link>

              <Link
                to="/documents"
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition flex items-center gap-1.5 ${
                  isActive('/documents') ? 'bg-indigo-600 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <BookOpen className="w-4 h-4" />
                <span>Knowledge Base</span>
              </Link>

              {user?.role === 'admin' && (
                <Link
                  to="/admin"
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition flex items-center gap-1.5 ${
                    isActive('/admin') ? 'bg-indigo-600 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <Shield className="w-4 h-4" />
                  <span>Admin</span>
                </Link>
              )}

              <Link
                to="/settings"
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition flex items-center gap-1.5 ${
                  isActive('/settings') ? 'bg-indigo-600 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Settings className="w-4 h-4" />
                <span className="hidden sm:inline">{user?.name?.split(' ')[0] || 'Settings'}</span>
              </Link>

              <button
                onClick={handleLogout}
                className="text-slate-400 hover:text-rose-400 p-1.5 rounded-lg hover:bg-slate-800 transition"
                title="Sign Out"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="px-4 py-1.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800 transition">
                Sign In
              </Link>
              <Link to="/register" className="px-4 py-1.5 rounded-lg text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
