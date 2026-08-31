import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { documentService } from '../../services/chatService';

export default function DocumentUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('General FAQ');
  const [academicYear, setAcademicYear] = useState('2026');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    setSuccess(false);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title || file.name);
    formData.append('category', category);
    formData.append('academic_year', academicYear);
    formData.append('description', description);

    try {
      await documentService.uploadDocument(formData);
      setSuccess(true);
      setFile(null);
      setTitle('');
      setDescription('');
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to upload document');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
      <h3 className="text-lg font-bold text-white flex items-center gap-2">
        <Upload className="w-5 h-5 text-indigo-400" />
        <span>Upload College Knowledge Document</span>
      </h3>

      {error && (
        <div className="flex items-center gap-2 text-rose-400 bg-rose-500/10 border border-rose-500/20 p-3 rounded-xl text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 p-3 rounded-xl text-xs">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>Document uploaded successfully! Ingestion pipeline started.</span>
        </div>
      )}

      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1">Select File (PDF, DOCX, TXT)</label>
        <input
          type="file"
          accept=".pdf,.docx,.txt"
          required
          onChange={(e) => {
            const f = e.target.files[0];
            setFile(f);
            if (f && !title) setTitle(f.name.replace(/\.[^/.]+$/, ''));
          }}
          className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Document Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Academic Calendar & Exam Rules"
            required
            className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl px-3 py-2 text-sm outline-none focus:border-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl px-3 py-2 text-sm outline-none"
          >
            <option value="General FAQ">General FAQ</option>
            <option value="Admissions">Admissions</option>
            <option value="Academics">Academics</option>
            <option value="Exams">Exams</option>
            <option value="Fees">Fees</option>
            <option value="Hostel">Hostel</option>
            <option value="Placements">Placements</option>
            <option value="Scholarships">Scholarships</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1">Description (Optional)</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Brief description of the document contents..."
          className="w-full bg-slate-950 border border-slate-800 text-white rounded-xl p-3 text-sm h-16 outline-none focus:border-indigo-500"
        />
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading || !file}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold px-5 py-2.5 rounded-xl text-sm transition flex items-center gap-2 shadow-lg shadow-indigo-600/20"
        >
          {loading ? 'Processing...' : 'Upload & Ingest'}
        </button>
      </div>
    </form>
  );
}
