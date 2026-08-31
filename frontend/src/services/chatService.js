import api from './api';

export const chatService = {
  async askQuestion(message, conversationId, options = {}) {
    const response = await api.post('/chat', {
      message,
      conversationId,
      ...options,
    });
    return response.data;
  },

  async listConversations() {
    const response = await api.get('/chat/conversations');
    return response.data;
  },

  async createConversation(title, collectionId) {
    const response = await api.post('/chat/conversations', { title, collectionId });
    return response.data;
  },

  async getConversation(id) {
    const response = await api.get(`/chat/conversations/${id}`);
    return response.data;
  },

  async deleteConversation(id) {
    const response = await api.delete(`/chat/conversations/${id}`);
    return response.data;
  },

  async submitFeedback(messageId, rating, reason = '', comment = '') {
    const response = await api.post('/feedback', {
      messageId,
      rating,
      reason,
      comment,
    });
    return response.data;
  },
};

export const documentService = {
  async listDocuments(params = {}) {
    const response = await api.get('/documents', { params });
    return response.data;
  },

  async uploadDocument(formData) {
    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async reprocessDocument(id) {
    const response = await api.post(`/documents/${id}/reprocess`);
    return response.data;
  },

  async deleteDocument(id) {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  },
};

export const adminService = {
  async getAnalytics() {
    const response = await api.get('/admin/analytics');
    return response.data;
  },

  async getUnanswered(status = 'open') {
    const response = await api.get('/admin/unanswered', { params: { status } });
    return response.data;
  },

  async updateUnanswered(id, status, adminNotes = '') {
    const response = await api.put(`/admin/unanswered/${id}`, { status, adminNotes });
    return response.data;
  },

  async listFeedback() {
    const response = await api.get('/feedback');
    return response.data;
  },
};
