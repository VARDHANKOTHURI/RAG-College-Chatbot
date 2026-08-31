import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Check } from 'lucide-react';
import { chatService } from '../../services/chatService';

export default function FeedbackButtons({ messageId }) {
  const [submitted, setSubmitted] = useState(false);
  const [rating, setRating] = useState(null);

  const handleRating = async (val) => {
    try {
      await chatService.submitFeedback(messageId, val);
      setRating(val);
      setSubmitted(true);
    } catch (err) {
      console.error(err);
    }
  };

  if (submitted) {
    return (
      <div className="flex items-center gap-1 text-[11px] text-emerald-400">
        <Check className="w-3.5 h-3.5" />
        <span>Feedback recorded</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-xs text-slate-500">
      <span>Helpful?</span>
      <button
        onClick={() => handleRating(1)}
        className="hover:text-emerald-400 p-1 rounded transition"
        title="Yes, helpful"
      >
        <ThumbsUp className="w-3.5 h-3.5" />
      </button>
      <button
        onClick={() => handleRating(-1)}
        className="hover:text-rose-400 p-1 rounded transition"
        title="No, not helpful"
      >
        <ThumbsDown className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
