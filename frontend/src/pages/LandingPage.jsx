import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { ShieldCheck, Search, Database, ArrowRight, BookOpen, MessageSquare } from 'lucide-react';

export default function LandingPage() {
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleQuickLogin = async (email, password) => {
    const success = await login(email, password);
    if (success) navigate('/chat');
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-12 space-y-16 animate-fadeIn">
      {/* Hero Section */}
      <div className="text-center space-y-6 max-w-3xl mx-auto pt-6">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-indigo-500/30 text-xs font-semibold text-indigo-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>RAG Academic Assistant Active</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight text-white">
          Autonomous AI Assistant for{' '}
          <span className="bg-gradient-to-r from-indigo-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Greenwood College
          </span>
        </h1>

        <p className="text-lg text-slate-400">
          Ask questions about admissions, exams, hostel facilities, fees, and scholarships with instant source citations from official college documents.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link
            to="/chat"
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-3 rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition"
          >
            <MessageSquare className="w-5 h-5" />
            <span>Launch Chat Assistant</span>
          </Link>
          <Link
            to="/documents"
            className="bg-slate-900 hover:bg-slate-800 border border-slate-800 text-white font-semibold px-6 py-3 rounded-xl flex items-center gap-2 transition"
          >
            <BookOpen className="w-5 h-5" />
            <span>View Knowledge Base</span>
          </Link>
        </div>
      </div>

      {/* Quick Demo Login Cards */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 max-w-2xl mx-auto space-y-3">
        <div className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
          Quick Demo Accounts (1-Click Login)
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            onClick={() => handleQuickLogin('student@college.edu', 'Student@123')}
            className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-indigo-500 text-left transition flex items-center justify-between group"
          >
            <div>
              <div className="font-semibold text-white text-sm">Demo Student</div>
              <div className="text-xs text-slate-500">student@college.edu</div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition" />
          </button>
          <button
            onClick={() => handleQuickLogin('admin@college.edu', 'Admin@123')}
            className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-indigo-500 text-left transition flex items-center justify-between group"
          >
            <div>
              <div className="font-semibold text-white text-sm">Admin Portal</div>
              <div className="text-xs text-slate-500">admin@college.edu</div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition" />
          </button>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Strict Grounding</h3>
          <p className="text-sm text-slate-400">
            Answers are strictly extracted from authorized college documents. Unverified queries are safely rejected.
          </p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Search className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Qdrant Vector Search</h3>
          <p className="text-sm text-slate-400">
            Semantic retrieval matches student inquiries by concept, keyword, and context with high accuracy.
          </p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <Database className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Multi-Format Ingestion</h3>
          <p className="text-sm text-slate-400">
            Admins can upload college PDFs, Word DOCX, and text circulars with automatic text cleaning and chunking.
          </p>
        </div>
      </div>
    </div>
  );
}
