import React, { useState } from 'react';
import { CheckCircle2, MessageCircle, Play, RotateCcw, Send } from 'lucide-react';

const ICONS = { play: Play, message: MessageCircle, send: Send, check: CheckCircle2 };
const DOT = {
  neutral: 'border-border bg-surface text-muted',
  done: 'border-success-line bg-success-soft text-success-strong',
};
const TAG = {
  good: 'bg-success-soft text-success-strong',
  info: 'bg-info-soft text-info-strong',
};

/** Câu chuyện của một bài: một câu tóm tắt và các bước theo thời gian. Câu chữ lấy nguyên văn từ backend (khóa `story`). */
export default function StorySteps({ story, onLoadCode }) {
  const [showAll, setShowAll] = useState(false);
  if (!story) return null;
  const steps = story.steps || [];
  const from = showAll ? 0 : Math.max(0, story.visible_from || 0);
  return (
    <div className="space-y-3">
      <p className="text-sm leading-relaxed text-foreground">{story.summary_vi}</p>
      {from > 0 && (
        <button type="button" onClick={() => setShowAll(true)} className="cursor-pointer text-xs font-semibold text-primary hover:underline">
          Xem cả {steps.length} bước
        </button>
      )}
      {steps.length > 0 && (
        <ol className="space-y-3 border-l-2 border-border pl-5">
          {steps.slice(from).map((s, i) => {
            const Icon = ICONS[s.icon] || Play;
            return (
              <li key={`${from + i}-${s.kind}`} className="relative">
                <span aria-hidden="true" className={`absolute -left-[2.06rem] top-0 flex size-6 items-center justify-center rounded-full border ${DOT[s.tone] || DOT.neutral}`}>
                  <Icon className="size-3.5" />
                </span>
                <p className="text-sm text-foreground">
                  {s.text_vi}
                  {s.tag_vi && <span className={`ml-2 inline-block rounded-full px-2 py-0.5 text-[11px] font-semibold ${TAG[s.tag_tone] || TAG.info}`}>{s.tag_vi}</span>}
                </p>
                {s.when_vi && <p className="text-[11px] text-muted">{s.when_vi}</p>}
                {s.code && onLoadCode && (
                  <button type="button" onClick={() => onLoadCode(s.code)} className="mt-1 inline-flex min-h-8 cursor-pointer items-center gap-1.5 rounded-full border border-border bg-surface px-3 text-xs font-semibold text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400">
                    <RotateCcw aria-hidden="true" className="size-3.5" /> Nạp lại code lần này
                  </button>
                )}
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
