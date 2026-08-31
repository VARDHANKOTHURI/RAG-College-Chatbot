import React from 'react';
import { AlertCircle, Check } from 'lucide-react';

export default function UnansweredQuestions({ questions = [], onResolve }) {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
      <div className="flex items-center gap-2">
        <AlertCircle className="w-5 h-5 text-amber-400" />
        <h3 className="text-lg font-bold text-white">Unanswered Inquiries (Knowledge Gaps)</h3>
      </div>

      <div className="space-y-3 max-h-80 overflow-y-auto">
        {questions.length === 0 ? (
          <div className="text-center py-6 text-slate-500 text-xs">
            No unresolved knowledge gaps!
          </div>
        ) : (
          questions.map((q) => (
            <div
              key={q.id}
              className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 flex items-start justify-between gap-4 text-sm"
            >
              <div>
                <div className="font-semibold text-white">{q.question}</div>
                <div className="text-xs text-slate-500 mt-1">Status: {q.status}</div>
              </div>
              <button
                onClick={() => onResolve(q.id)}
                className="text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 hover:bg-emerald-600 hover:text-white px-3 py-1.5 rounded-lg transition flex items-center gap-1 flex-shrink-0"
              >
                <Check className="w-3.5 h-3.5" />
                <span>Resolve</span>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
