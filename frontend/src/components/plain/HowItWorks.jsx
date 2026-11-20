import React from 'react';

/** Cách hệ thống chia nhóm, nói bằng lời (thu gọn mặc định). */
export default function HowItWorks({ items }) {
  if (!items?.length) return null;
  return (
    <details className="rounded-2xl border border-border px-4 py-3 text-xs text-muted">
      <summary className="cursor-pointer font-semibold text-foreground">Hệ thống nhận xét thế nào?</summary>
      <ul className="mt-2 list-disc space-y-1 pl-4 leading-relaxed">
        {items.map((s) => <li key={s}>{s}</li>)}
      </ul>
    </details>
  );
}
