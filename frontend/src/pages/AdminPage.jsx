import React, { useState, useEffect } from 'react';
import MetricsCard from '../components/admin/MetricsCard';
import QuestionAnalytics from '../components/admin/QuestionAnalytics';
import UnansweredQuestions from '../components/admin/UnansweredQuestions';
import { adminService } from '../services/chatService';
import { FileText, MessageSquare, AlertCircle, ThumbsUp } from 'lucide-react';

export default function AdminPage() {
  const [analytics, setAnalytics] = useState(null);
  const [unanswered, setUnanswered] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [analyticsData, unansweredData] = await Promise.all([
        adminService.getAnalytics(),
        adminService.getUnanswered('open'),
      ]);
      setAnalytics(analyticsData);
      setUnanswered(unansweredData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleResolve = async (id) => {
    try {
      await adminService.updateUnanswered(id, 'resolved');
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8 animate-fadeIn w-full">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Administrator Control Panel</h1>
        <p className="text-sm text-slate-400">
          Monitor knowledge base health, query traffic, and unanswered student inquiries.
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <MetricsCard
          title="Documents"
          value={analytics?.totalDocuments || 0}
          subtext={`${analytics?.totalChunks || 0} vector chunks`}
          icon={FileText}
          color="indigo"
        />
        <MetricsCard
          title="Total Queries"
          value={analytics?.totalQuestions || 0}
          subtext={`${analytics?.answeredQuestions || 0} answered`}
          icon={MessageSquare}
          color="emerald"
        />
        <MetricsCard
          title="Knowledge Gaps"
          value={analytics?.unansweredQuestions || 0}
          subtext="Unresolved questions"
          icon={AlertCircle}
          color="amber"
        />
        <MetricsCard
          title="User Feedback"
          value={`${analytics?.positiveFeedbackCount || 0} 👍`}
          subtext={`${analytics?.negativeFeedbackCount || 0} 👎`}
          icon={ThumbsUp}
          color="cyan"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <QuestionAnalytics popularQuestions={analytics?.popularQuestions || []} />
        <UnansweredQuestions questions={unanswered} onResolve={handleResolve} />
      </div>
    </div>
  );
}
