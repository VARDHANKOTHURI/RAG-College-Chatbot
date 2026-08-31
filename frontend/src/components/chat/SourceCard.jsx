import React from 'react';
import { BookOpen, FileText } from 'lucide-react';

export default function SourceCard({ source }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 hover:border-indigo-500/40 transition">
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5 truncate">
          <FileText className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
          <span className="font-semibold text-white text-xs truncate" title={source.title}>
            {source.title}
          </span>
        </div>
        <span className="bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 text-[10px] font-bold px-2 py-0.5 rounded-full flex-shrink-0">
          Page {source.pageNumber || 1}
        </span>
      </div>
      <p className="text-slate-400 text-[11px] line-clamp-2 leading-relaxed mb-2">
        {source.snippet}
      </p>
      <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800/60">
        <span>{source.category || 'General'}</span>
        <span>Relevance: {Math.round((source.score || 0.5) * 100)}%</span>
      </div>
    </div>
  );
}
