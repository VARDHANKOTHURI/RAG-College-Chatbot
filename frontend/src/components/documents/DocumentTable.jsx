import React from 'react';
import { RotateCw, Trash2, FileText, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export default function DocumentTable({ documents, onReprocess, onDelete }) {
  const { user } = useAuthStore();
  const isAdmin = user?.role === 'admin';

  const getStatusBadge = (status) => {
    switch (status) {
      case 'ready':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">
            <CheckCircle2 className="w-3 h-3" /> Ready
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-full">
            <Clock className="w-3 h-3 animate-spin" /> Processing
          </span>
        );
      case 'failed':
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[11px] font-bold text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-full">
            <AlertTriangle className="w-3 h-3" /> Failed
          </span>
        );
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-950/60 text-slate-400 text-xs uppercase font-semibold border-b border-slate-800">
            <tr>
              <th className="p-4">Document</th>
              <th className="p-4">Category</th>
              <th className="p-4">Pages</th>
              <th className="p-4">Chunks</th>
              <th className="p-4">Status</th>
              {isAdmin && <th className="p-4 text-right">Actions</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {documents.length === 0 ? (
              <tr>
                <td colSpan={isAdmin ? 6 : 5} className="text-center py-8 text-slate-500">
                  No documents in knowledge base yet.
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-800/30 transition">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 flex-shrink-0">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="font-semibold text-white truncate max-w-xs">{doc.title}</div>
                        <div className="text-xs text-slate-500 font-mono">{doc.fileName}</div>
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="text-xs bg-slate-800 text-slate-300 border border-slate-700 px-2.5 py-1 rounded-lg">
                      {doc.category}
                    </span>
                  </td>
                  <td className="p-4 text-slate-300">{doc.totalPages}</td>
                  <td className="p-4 font-mono text-indigo-400 font-semibold">{doc.totalChunks}</td>
                  <td className="p-4">{getStatusBadge(doc.status)}</td>
                  {isAdmin && (
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => onReprocess(doc.id)}
                          className="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-lg transition"
                          title="Reprocess Vectors"
                        >
                          <RotateCw className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onDelete(doc.id)}
                          className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
                          title="Delete Document"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
