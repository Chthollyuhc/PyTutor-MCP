import React from 'react';

const TONES = {
  check_in: { box: 'border-destructive-line bg-destructive-soft/40', title: 'text-destructive-strong', empty: 'Không có bạn nào.' },
  trying: { box: 'border-warning-line bg-warning-soft/40', title: 'text-warning-strong', empty: 'Không có bạn nào.' },
  doing_well: { box: 'border-success-line bg-success-soft/40', title: 'text-success-strong', empty: 'Chưa có bạn nào.' },
};

function Pile({ kind, title, items, onOpenStudent }) {
  const tone = TONES[kind];
  const withReason = kind !== 'doing_well';
  return (
    <div className={`rounded-2xl border p-3 ${tone.box}`}>
      <h6 className={`text-sm font-bold ${tone.title}`}>{title} · {items.length} bạn</h6>
      {items.length === 0 ? (
        <p className="mt-1.5 text-xs text-muted">{tone.empty}</p>
      ) : withReason ? (
        <ul className="mt-2 space-y-1">
          {items.map((p) => (
            <li key={p.username}>
              <button
                type="button"
                onClick={() => onOpenStudent && p.exercise_id && onOpenStudent(p)}
                className="w-full cursor-pointer rounded-xl px-2 py-1.5 text-left hover:bg-surface focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400"
              >
                <span className="block text-sm font-semibold text-foreground">{p.full_name}</span>
                <span className="block text-xs text-muted">{p.reason_vi}</span>
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <ul className="mt-2 flex flex-wrap gap-1.5">
          {items.map((p) => <li key={p.username} className="rounded-full bg-surface px-2.5 py-0.5 text-xs text-foreground">{p.full_name}</li>)}
        </ul>
      )}
    </div>
  );
}

/** Các bạn trong lớp chia 3 cột theo đèn giao thông, xếp A→Z. Bấm vào tên để xem câu chuyện của bạn đó ở bài liên quan. */
export default function StudentGroups({ plain, onOpenStudent }) {
  const g = plain?.groups;
  if (!g) return null;
  const t = plain.group_titles_vi || {};
  return (
    <section aria-labelledby="class-groups" className="space-y-3">
      <h5 id="class-groups" className="text-sm font-bold text-foreground">Các bạn trong lớp</h5>
      <div className="grid gap-3 md:grid-cols-3">
        <Pile kind="check_in" title={t.check_in} items={g.check_in || []} onOpenStudent={onOpenStudent} />
        <Pile kind="trying" title={t.trying} items={g.trying || []} onOpenStudent={onOpenStudent} />
        <Pile kind="doing_well" title={t.doing_well} items={g.doing_well || []} />
      </div>
      {(g.not_started || []).length > 0 && (
        <p className="text-xs text-muted">
          <strong className="text-foreground">{t.not_started} ({g.not_started.length}):</strong> {g.not_started.map((p) => p.full_name).join(', ')}
        </p>
      )}
    </section>
  );
}
