import React, { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import SuggestedQuestions from './SuggestedQuestions';
import { useChatStore } from '../../store/chatStore';

export default function ChatWindow() {
  const { messages, loading, sendMessage } = useChatStore();
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="flex-1 flex flex-col bg-slate-950 h-full overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 max-w-4xl w-full mx-auto">
        {messages.length === 0 ? (
          <SuggestedQuestions onSelectQuestion={(q) => sendMessage(q)} />
        ) : (
          messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
        )}

        {loading && (
          <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 rounded-2xl rounded-bl-sm p-4 max-w-[85%] text-sm text-slate-400">
            <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div>
            <span>Searching knowledge base & synthesizing answer...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 border-t border-slate-800 bg-slate-900/60 backdrop-blur-lg">
        <ChatInput onSendMessage={(text) => sendMessage(text)} disabled={loading} />
      </div>
    </div>
  );
}
