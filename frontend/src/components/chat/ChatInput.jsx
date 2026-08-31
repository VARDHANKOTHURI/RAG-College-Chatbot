import React, { useState } from 'react';
import { Send } from 'lucide-react';

export default function ChatInput({ onSendMessage, disabled }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSendMessage(text.trim());
    setText('');
  };

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-3 max-w-4xl mx-auto w-full">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        placeholder="Ask a question about Greenwood College admissions, fees, hostel, or exams..."
        className="flex-1 bg-slate-950 border border-slate-800 focus:border-indigo-500 text-white rounded-xl px-4 py-3 text-sm outline-none transition disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white p-3 rounded-xl transition shadow-lg shadow-indigo-600/30 flex-shrink-0"
      >
        <Send className="w-5 h-5" />
      </button>
    </form>
  );
}
