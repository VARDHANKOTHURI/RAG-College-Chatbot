import React, { useState, useEffect } from 'react';
import DocumentUpload from '../components/documents/DocumentUpload';
import DocumentTable from '../components/documents/DocumentTable';
import { documentService } from '../services/chatService';
import { useAuthStore } from '../store/authStore';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const { user } = useAuthStore();
  const isAdmin = user?.role === 'admin';

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await documentService.listDocuments();
      setDocuments(data);
    } catch (err) {
      console.error('Failed to load documents', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleReprocess = async (id) => {
    try {
      await documentService.reprocessDocument(id);
      loadDocuments();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    try {
      await documentService.deleteDocument(id);
      loadDocuments();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8 animate-fadeIn w-full">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">College Knowledge Base</h1>
        <p className="text-sm text-slate-400">
          Official documents, fee circulars, examination regulations, and hostel guidelines.
        </p>
      </div>

      {isAdmin && <DocumentUpload onUploadSuccess={loadDocuments} />}

      <DocumentTable
        documents={documents}
        onReprocess={handleReprocess}
        onDelete={handleDelete}
      />
    </div>
  );
}
