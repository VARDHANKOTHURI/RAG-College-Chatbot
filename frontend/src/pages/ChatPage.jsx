import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import ChatWindow from '../components/chat/ChatWindow';
import { useChatStore } from '../store/chatStore';

export default function ChatPage() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const { fetchConversations, selectConversation, createNewConversation } = useChatStore();

  useEffect(() => {
    fetchConversations();
    if (conversationId) {
      selectConversation(conversationId);
    }
  }, [conversationId]);

  const handleSelectChat = (id) => {
    navigate(`/chat/${id}`);
  };

  const handleCreateChat = async () => {
    const id = await createNewConversation();
    if (id) navigate(`/chat/${id}`);
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      <Sidebar onSelectChat={handleSelectChat} onCreateChat={handleCreateChat} />
      <ChatWindow />
    </div>
  );
}
