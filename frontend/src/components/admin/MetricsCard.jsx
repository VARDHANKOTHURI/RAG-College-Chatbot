import React from 'react';

export default function MetricsCard({ title, value, subtext, icon: Icon, color = 'indigo' }) {
  const colorMap = {
    indigo: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && (
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${colorMap[color]}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <div className="text-3xl font-extrabold text-white">{value}</div>
      {subtext && <div className="text-xs text-slate-500">{subtext}</div>}
    </div>
  );
}
