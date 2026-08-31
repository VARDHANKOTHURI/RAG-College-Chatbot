import React from 'react';
import SourceCard from './SourceCard';
import FeedbackButtons from './FeedbackButtons';
import { Bot, User } from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end animate-fadeIn">
        <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-2xl rounded-br-sm px-4 py-3 max-w-[85%] text-sm shadow-md shadow-indigo-600/20">
          {message.content}
        </div>
      </div>
    );
  }

  const sources = message.sources || [];

  return (
    <div className="flex items-start gap-3 bg-slate-900 border border-slate-800 rounded-2xl rounded-bl-sm p-4 sm:p-5 max-w-[85%] text-sm text-slate-200 animate-fadeIn">
      <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex-shrink-0 flex items-center justify-center text-white font-bold text-xs shadow-md shadow-indigo-500/20">
        <Bot className="w-4 h-4" />
      </div>

      <div className="space-y-3 flex-1 overflow-hidden">
        <div className="leading-relaxed whitespace-pre-wrap font-normal">
          {message.content}
        </div>

        {sources.length > 0 && (
          <div className="pt-3 border-t border-slate-800 space-y-2">
            <div className="text-xs font-semibold text-indigo-400">
              Verified Knowledge Base Sources ({sources.length})
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {sources.map((src, idx) => (
                <SourceCard key={idx} source={src} />
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between pt-1">
          <FeedbackButtons messageId={message.id} />
        </div>
      </div>
    </div>
  );
}
