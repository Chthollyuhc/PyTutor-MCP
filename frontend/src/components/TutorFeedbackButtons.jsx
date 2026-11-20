import React, { useEffect, useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { submitTutorFeedback } from '../services/api';

const OPTIONS = [
  { value: 1, Icon: ThumbsUp, label: 'Hữu ích', on: 'bg-success-soft text-success-strong border-success-line' },
  { value: -1, Icon: ThumbsDown, label: 'Chưa giúp được', on: 'bg-destructive-soft text-destructive-strong border-destructive-line' },
];

/**
 * Nút đánh giá 👍/👎 cho một phản hồi AI (gợi ý ask_ai, tin nhắn chat, Pythonic Review).
 * Backend kiểm tra chủ sở hữu interaction; mỗi phản hồi chỉ ghi nhận một lần ở phía giao diện.
 */
export default function TutorFeedbackButtons({ interactionId, prompt = '', className = '' }) {
  const [rating, setRating] = useState(null);
  const [status, setStatus] = useState('idle'); // idle | saving | saved | error

  useEffect(() => {
    setRating(null);
    setStatus('idle');
  }, [interactionId]);

  if (!interactionId) return null;

  const locked = status === 'saving' || status === 'saved';

  const handleRate = async (value) => {
    if (locked) return;
    setStatus('saving');
    try {
      await submitTutorFeedback({ interaction_id: interactionId, rating: value });
      setRating(value);
      setStatus('saved');
    } catch (err) {
      console.error('Không thể lưu đánh giá phản hồi AI:', err);
      setStatus('error');
    }
  };

  return (
    <div className={`flex flex-wrap items-center gap-1.5 ${className}`} role="group" aria-label="Đánh giá phản hồi của Gia sư AI">
      {prompt && <span className="text-[0.8125rem] text-muted">{prompt}</span>}
      {OPTIONS.map((item) => (
        <button
          key={item.value}
          type="button"
          title={item.label}
          aria-label={item.label}
          aria-pressed={rating === item.value}
          onClick={() => handleRate(item.value)}
          disabled={locked}
          className={`inline-flex size-9 items-center justify-center rounded-md border transition-colors disabled:cursor-default ${
            rating === item.value
              ? item.on
              : 'border-transparent text-muted hover:bg-surface-raised hover:text-foreground disabled:opacity-50 disabled:hover:bg-transparent'
          }`}
        >
          <item.Icon aria-hidden="true" className="size-4" />
        </button>
      ))}
      <span className="text-[0.8125rem] text-muted" role="status" aria-live="polite">
        {status === 'saved' && 'Đã ghi nhận, cảm ơn bạn.'}
        {status === 'saving' && 'Đang lưu...'}
        {status === 'error' && 'Chưa lưu được, bạn thử lại nhé.'}
      </span>
    </div>
  );
}
