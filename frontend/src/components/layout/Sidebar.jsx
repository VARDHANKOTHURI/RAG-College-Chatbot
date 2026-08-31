import React from 'react';
import { Plus, MessageSquare, Trash2 } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';

export default function Sidebar({ onSelectChat, onCreateChat }) {
  const { conversations, currentConversationId, deleteConversation } = useChatStore();

  return (
    <aside className="w-72 bg-slate-900/90 border-r border-slate-800 flex flex-col h-full">
      <div className="p-4 border-b border-slate-800">
        <button
          onClick={onCreateChat}
          className="w-full bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-semibold py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 text-sm transition"
        >
          <Plus className="w-4 h-4" />
          <span>New Chat</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        {conversations.length === 0 ? (
          <div className="text-xs text-slate-500 text-center py-6">No previous conversations</div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => onSelectChat(conv.id)}
              className={`group flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition text-xs ${
                currentConversationId === conv.id
                  ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                  : 'text-slate-400 hover:bg-slate-800/80 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-2 truncate">
                <MessageSquare className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="truncate font-medium">{conv.title || 'Untitled Conversation'}</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteConversation(conv.id);
                }}
                className="opacity-0 group-hover:opacity-100 hover:text-rose-400 p-1 transition"
                title="Delete Chat"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
