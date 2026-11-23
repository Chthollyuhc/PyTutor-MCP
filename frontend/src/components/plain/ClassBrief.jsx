import React from 'react';

/** Bản tin lớp: vài câu nói như trợ giảng báo cáo. Câu chữ lấy nguyên văn từ backend (khóa `plain`). */
export default function ClassBrief({ plain }) {
  if (!plain) return null;
  return (
    <section aria-labelledby="class-brief" className="space-y-2 rounded-2xl border border-border bg-surface-raised p-4">
      <h5 id="class-brief" className="text-sm font-bold text-foreground">Bản tin lớp</h5>
      <p className="text-sm leading-relaxed text-foreground">{(plain.brief_vi || []).join(' ')}</p>
      {plain.concept_focus_vi && <p className="text-sm font-medium text-foreground">{plain.concept_focus_vi}</p>}
      {(plain.skills_vi || []).map((s) => <p key={s} className="text-sm text-foreground">{s}</p>)}
      {plain.few_data_vi && <p className="text-[11px] text-muted">{plain.few_data_vi}</p>}
    </section>
  );
}
