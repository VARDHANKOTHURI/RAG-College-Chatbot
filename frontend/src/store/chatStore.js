import { create } from 'zustand';
import { chatService } from '../services/chatService';

export const useChatStore = create((set, get) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  loading: false,
  streaming: false,
  error: null,

  fetchConversations: async () => {
    try {
      const data = await chatService.listConversations();
      set({ conversations: data });
    } catch (err) {
      console.error('Failed to fetch conversations', err);
    }
  },

  selectConversation: async (id) => {
    set({ loading: true, currentConversationId: id, messages: [] });
    try {
      const data = await chatService.getConversation(id);
      set({ messages: data.messages || [], loading: false });
    } catch (err) {
      set({ error: 'Failed to load conversation messages', loading: false });
    }
  },

  createNewConversation: async (title = 'New Conversation') => {
    try {
      const newConv = await chatService.createConversation(title);
      set((state) => ({
        conversations: [newConv, ...state.conversations],
        currentConversationId: newConv.id,
        messages: [],
      }));
      return newConv.id;
    } catch (err) {
      console.error('Failed to create new conversation', err);
      return null;
    }
  },

  deleteConversation: async (id) => {
    try {
      await chatService.deleteConversation(id);
      set((state) => {
        const remaining = state.conversations.filter((c) => c.id !== id);
        const nextId = state.currentConversationId === id ? (remaining[0]?.id || null) : state.currentConversationId;
        return {
          conversations: remaining,
          currentConversationId: nextId,
          messages: nextId ? state.messages : [],
        };
      });
      if (get().currentConversationId) {
        get().selectConversation(get().currentConversationId);
      }
    } catch (err) {
      console.error('Failed to delete conversation', err);
    }
  },

  sendMessage: async (text, options = {}) => {
    const { currentConversationId } = get();
    const tempUserMsg = {
      id: 'temp-' + Date.now(),
      role: 'user',
      content: text,
      createdAt: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, tempUserMsg],
      loading: true,
    }));

    try {
      const res = await chatService.askQuestion(text, currentConversationId, options);
      const asstMsg = {
        id: res.messageId,
        role: 'assistant',
        content: res.answer,
        sources: res.sources || [],
        isUnknown: res.isUnknown,
        createdAt: new Date().toISOString(),
      };

      set((state) => ({
        currentConversationId: res.conversationId,
        messages: [...state.messages, asstMsg],
        loading: false,
      }));
      get().fetchConversations();
    } catch (err) {
      set({ loading: false, error: 'Failed to send message' });
    }
  },
}));
