import React from 'react';
import { TrendingUp, HelpCircle } from 'lucide-react';

export default function QuestionAnalytics({ popularQuestions = [] }) {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
      <div className="flex items-center gap-2">
        <TrendingUp className="w-5 h-5 text-indigo-400" />
        <h3 className="text-lg font-bold text-white">Frequently Asked Inquiries</h3>
      </div>

      <div className="space-y-3">
        {popularQuestions.length === 0 ? (
          <div className="text-center py-6 text-slate-500 text-xs">No query activity recorded yet</div>
        ) : (
          popularQuestions.map((item, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-sm"
            >
              <div className="flex items-center gap-2.5">
                <span className="text-xs font-mono font-bold text-indigo-400">#{idx + 1}</span>
                <span className="text-slate-200">{item.question}</span>
              </div>
              <span className="text-xs font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-2.5 py-0.5 rounded-full">
                {item.count} asks
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
