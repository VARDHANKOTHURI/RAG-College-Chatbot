import React from 'react';
import { HelpCircle } from 'lucide-react';

export default function SuggestedQuestions({ onSelectQuestion }) {
  const suggestions = [
    "What is the annual hostel fee for a 2-sharing AC room?",
    "When do Odd Semester End theory examinations begin in 2026?",
    "What is the minimum attendance required for semester exams?",
    "What scholarships are available for merit students?",
    "What was the highest placement package in 2025-2026?",
    "What is the fee for examination revaluation per paper?"
  ];

  return (
    <div className="text-center py-10 space-y-6 max-w-2xl mx-auto">
      <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-cyan-500 mx-auto flex items-center justify-center shadow-xl shadow-indigo-500/20">
        <HelpCircle className="w-8 h-8 text-white" />
      </div>
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">How can I assist you today?</h2>
        <p className="text-sm text-slate-400">
          Ask any question regarding admissions, academics, fee schedules, hostel, scholarships, or placements.
        </p>
      </div>

      <div className="space-y-3 pt-2">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Suggested Inquiries
        </div>
        <div className="flex flex-wrap justify-center gap-2">
          {suggestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => onSelectQuestion(q)}
              className="text-xs bg-slate-900 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-800 text-slate-300 py-2 px-3 rounded-xl transition text-left"
            >
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
