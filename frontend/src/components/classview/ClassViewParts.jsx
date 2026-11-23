import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, X } from 'lucide-react';
import StorySteps from '../plain/StorySteps';
import { MarkButtons, MarkedNote } from '../plain/MarkButtons';
import { HBar, StackedBarRows, ChartEmpty } from '../charts/ClassCharts';
import { fetchStudentExerciseJourney } from '../../services/api';
import { formatShare } from '../../utils/share';

/** v5.8 — các phần của "Tình hình lớp": thẻ việc nên xem, ma trận SV × bài, ngăn dấu chân / ngăn bài, hàng theo khái niệm.
 *  Mọi ngưỡng là quy ước vận hành chưa hiệu chuẩn; sinh viên xếp A→Z, không xếp hạng. */

export const ERROR_SERIES = [
  { key: 'syntax', label: 'Cú pháp', fill: 'fill-rose-500', bg: 'bg-rose-500' },
  { key: 'runtime', label: 'Runtime', fill: 'fill-orange-500', bg: 'bg-orange-500' },
  { key: 'timeout', label: 'Timeout', fill: 'fill-violet-500', bg: 'bg-violet-500' },
  { key: 'logic_partial', label: 'Logic một phần', fill: 'fill-amber-400', bg: 'bg-amber-400' },
  { key: 'logic_none', label: 'Logic không đạt test nào', fill: 'fill-slate-500', bg: 'bg-slate-500' },
  { key: 'format_only', label: 'Chỉ sai định dạng', fill: 'fill-sky-500', bg: 'bg-sky-500' },
];

// Màu đi kèm ký hiệu chữ để người mù màu vẫn đọc được. Họ màu: xanh lá = đạt; tím nhạt = đạt nhờ gợi ý; vàng/đỏ = chưa đạt; xám = chỉ chạy thử.
export const MATRIX_STATES = {
  independent_pass: { label: 'Đạt độc lập', glyph: '✓', cell: 'bg-emerald-600 text-white border-emerald-700' },
  retry_pass: { label: 'Đạt sau thử–sửa', glyph: '↻', cell: 'bg-emerald-300 text-emerald-950 border-emerald-500' },
  hint_pass: { label: 'Đạt nhờ gợi ý', glyph: 'G', cell: 'bg-violet-200 text-violet-900 border-violet-400 dark:bg-violet-400/30 dark:text-violet-100' },
  in_progress: { label: 'Đang tiến triển', glyph: '…', cell: 'bg-amber-200 text-amber-950 border-amber-400 dark:bg-amber-400/30 dark:text-amber-100' },
  stuck: { label: 'Mắc kẹt', glyph: '!', cell: 'bg-rose-500 text-white border-rose-800 border-[3px] font-bold' },
  practice_only: { label: 'Chỉ chạy thử', glyph: '○', cell: 'bg-slate-300 text-slate-800 border-slate-400 dark:bg-slate-600 dark:text-slate-100' },
};
const EMPTY_CELL = 'border-dashed border-border bg-transparent text-muted';

function useEscape(onClose) {
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);
}

function Drawer({ title, subtitle, onClose, children }) {
  const closeRef = useRef(null);
  useEscape(onClose);
  useEffect(() => { closeRef.current?.focus(); }, []);
  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <aside role="dialog" aria-modal="true" aria-label={title} className="flex h-full w-full max-w-md flex-col border-l border-border bg-surface shadow-bento">
        <header className="flex shrink-0 items-start justify-between gap-3 border-b border-border bg-surface-raised px-4 py-3">
          <div className="min-w-0">
            <h4 className="break-words text-sm font-bold text-foreground">{title}</h4>
            {subtitle && <p className="mt-0.5 text-[11px] text-muted">{subtitle}</p>}
          </div>
          <button ref={closeRef} type="button" onClick={onClose} aria-label="Đóng ngăn chi tiết" className="rounded-xl p-2 text-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer">
            <X aria-hidden="true" className="size-4" />
          </button>
        </header>
        <div className="flex-1 space-y-4 overflow-y-auto p-4 text-xs">{children}</div>
      </aside>
    </div>
  );
}

/** Ngăn câu chuyện của MỘT sinh viên ở MỘT bài (lời thường, không có mã nguồn). */
export function JourneyDrawer({ classId, target, days, exerciseTitle, studentName, onClose }) {
  const [state, setState] = useState({ loading: true, error: '', data: null });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let cancelled = false;
    setState({ loading: true, error: '', data: null });
    fetchStudentExerciseJourney(classId, target.username, target.exercise_id, days)
      .then((data) => { if (!cancelled) setState({ loading: false, error: '', data }); })
      .catch(() => { if (!cancelled) setState({ loading: false, error: 'Chưa tải được. Thử lại sau.', data: null }); });
    return () => { cancelled = true; };
  }, [classId, target.username, target.exercise_id, days, attempt]);
  const d = state.data;
  return (
    <Drawer title={`${studentName}: ${exerciseTitle}`} subtitle={`${days ? `${days} ngày gần nhất · ` : ''}không hiện code của sinh viên`} onClose={onClose}>
      {state.loading && <p role="status" className="text-muted">Đang tải…</p>}
      {state.error && (
        <div role="alert" className="space-y-2 rounded-xl border border-destructive-line bg-destructive-soft p-3 text-destructive-strong">
          <p>{state.error}</p>
          <button type="button" onClick={() => setAttempt((a) => a + 1)} className="cursor-pointer rounded-full border border-border bg-surface px-3 py-1 font-semibold text-foreground">Thử lại</button>
        </div>
      )}
      {d && (
        <>
          <StorySteps story={d.story} />
          {d.truncated && <p className="text-[11px] text-muted">Chỉ hiện {d.points.length} lần gần nhất trong tổng {d.total_points} lần.</p>}
        </>
      )}
    </Drawer>
  );
}

/** Ngăn của MỘT bài: test hay sai, loại lỗi (gồm chỉ sai định dạng), thời gian tới khi đạt, phân bố nhóm quá trình. */
export function ExerciseDrawer({ data, exerciseId, onClose }) {
  const mx = (data.matrix?.exercises || []).find((e) => e.exercise_id === exerciseId) || {};
  const plainItem = (data.plain?.exercises || []).find((e) => e.exercise_id === exerciseId);
  const failing = (data.failing_tests_by_exercise || []).find((f) => f.exercise_id === exerciseId);
  const err = (data.error_breakdown_by_exercise || []).find((e) => e.exercise_id === exerciseId);
  const ttp = (data.time_to_pass_by_exercise || []).find((t) => t.exercise_id === exerciseId);
  const groups = (data.process_groups?.by_exercise || []).find((e) => e.exercise_id === exerciseId)?.groups || {};
  const defs = data.process_groups?.definitions || [];
  const values = err ? { ...(err.submit || {}) } : {};
  if (err) {
    Object.entries(err.run || {}).forEach(([k, v]) => { values[k] = (values[k] || 0) + v; });
    delete values.passed;
    values.format_only = (err.format_only_submit || 0) + (err.format_only_run || 0);
  }
  return (
    <Drawer title={plainItem?.title || mx.title || exerciseId} subtitle={plainItem ? `Bài ${plainItem.number} trong lộ trình` : ''} onClose={onClose}>
      {plainItem && (
        <section className="space-y-1.5">
          <p className="text-sm text-foreground">{plainItem.done_vi}</p>
          {plainItem.mistake_vi && <p className="text-sm text-foreground">{plainItem.mistake_vi}</p>}
        </section>
      )}
      <Link className="inline-flex min-h-9 items-center rounded-full border border-border bg-surface px-4 text-xs font-semibold text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer" to={`/instructor/exercises/${encodeURIComponent(exerciseId)}/edit`}>Mở đề bài để xem hoặc sửa</Link>
      <details className="rounded-xl border border-border">
        <summary className="cursor-pointer px-3 py-2 font-semibold text-foreground">Số liệu chi tiết của bài</summary>
        <div className="space-y-4 border-t border-border p-3">
          <section className="space-y-1.5">
            <h5 className="font-bold text-foreground">Test hay sai</h5>
            {!failing?.tests?.length ? <ChartEmpty>Chưa ghi nhận test sai nào có đặc trưng.</ChartEmpty> : (
              <ul className="space-y-1">
                {failing.tests.map((t) => (
                  <li key={t.test_idx} className="rounded-lg border border-border p-2">
                    <span className="font-semibold text-foreground">Test #{t.test_idx}</span> “{t.description}”
                    <span className="text-muted"> — {t.attempts} lượt, {t.students} SV{t.format_attempts ? `, ${t.format_attempts} lượt chỉ sai định dạng` : ''}</span>
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section className="space-y-1.5">
            <h5 className="font-bold text-foreground">Loại lỗi (nộp + chạy thử)</h5>
            <StackedBarRows rows={err ? [{ key: exerciseId, label: 'Bài này', values }] : []} series={ERROR_SERIES} ariaLabel="Loại lỗi của bài" />
          </section>
          <section className="space-y-1.5">
            <h5 className="font-bold text-foreground">Thời gian tới khi đạt (trung vị)</h5>
            {ttp ? <p className="text-foreground"><span className="font-mono tabular-nums">{ttp.median_minutes}</span> phút (n={ttp.n}). Là khoảng giữa sự kiện đầu và lần nộp đạt đầu, không phải thời gian ngồi làm.</p> : <ChartEmpty>Chưa có SV nào đạt trong khoảng này.</ChartEmpty>}
          </section>
          <section className="space-y-1.5">
            <h5 className="font-bold text-foreground">Nhóm quá trình ở bài này</h5>
            <HBar
              ariaLabel="Số sinh viên theo nhóm quá trình ở bài này"
              rows={defs.map((d) => ({ key: d.key, label: d.label, value: groups[d.key] || 0, max: Math.max(1, mx.students_attempted || 1), text: formatShare(groups[d.key] || 0, mx.students_attempted || 0) }))}
            />
          </section>
        </div>
      </details>
    </Drawer>
  );
}

function IconArray({ k, n }) {
  if (n > 24) {
    return (
      <div role="img" aria-label={formatShare(k, n)} className="h-2.5 w-full overflow-hidden rounded bg-slate-200 dark:bg-slate-800">
        <div className="h-full bg-rose-500" style={{ width: `${Math.min(100, (k / Math.max(1, n)) * 100)}%` }} />
      </div>
    );
  }
  return (
    <div role="img" aria-label={formatShare(k, n)} className="flex flex-wrap gap-1">
      {Array.from({ length: n }, (_, i) => (
        <span key={i} className={`size-3 rounded-full border-2 ${i < k ? 'border-rose-600 bg-rose-500' : 'border-slate-400 bg-transparent dark:border-slate-500'}`} />
      ))}
    </div>
  );
}

function CardAction({ card, onOpenExercise, onOpenJourney }) {
  const { target, label_vi: label } = card.action;
  const btn = 'inline-flex min-h-9 items-center justify-center rounded-full border border-emerald-600 bg-emerald-600 px-4 text-xs font-semibold text-white hover:bg-emerald-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 cursor-pointer';
  if (target === 'exercise_detail' && card.exercise_id && onOpenExercise) {
    return <button type="button" className={btn} onClick={() => onOpenExercise(card.exercise_id)}>{label}</button>;
  }
  if (target === 'concepts') {
    return <button type="button" className={btn} onClick={() => document.getElementById('class-concepts')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>{label}</button>;
  }
  if (target === 'student_journey' && card.students?.[0]?.exercise_id) {
    const s = card.students[0];
    return <button type="button" className={btn} onClick={() => onOpenJourney({ username: s.username, full_name: s.full_name, exercise_id: s.exercise_id })}>{label}</button>;
  }
  return null;
}

/** Tầng 1 — tối đa 5 thẻ: kết luận + bằng chứng k/n + một nút hành động. */
export function ActionCards({ actionCards, onOpenExercise, onOpenJourney, onShowMore, insufficientReason, handledItems = [], onMark, onUndo, busy }) {
  const cards = actionCards?.cards || [];
  return (
    <section aria-labelledby="class-actions" className="space-y-3">
      <h5 id="class-actions" className="text-sm font-bold text-foreground">Việc nên xem</h5>
      {insufficientReason && <p className="text-[11px] text-muted">{insufficientReason}</p>}
      {cards.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-border p-4 text-center text-xs text-muted">{actionCards?.handled_cards > 0 ? 'Các việc đang có đều đã được đánh dấu.' : (actionCards?.empty_vi || 'Không có việc cần xử lý ngay theo quy ước hiện tại.')}</p>
      ) : (
        <ul className="grid gap-3 lg:grid-cols-2">
          {cards.map((card) => (
            <li key={`${card.code}-${card.exercise_id || card.kc || 'x'}`} className="flex flex-col gap-2.5 rounded-2xl border border-border bg-surface-raised p-3.5">
              <h6 className="break-words text-sm font-bold leading-snug text-foreground">{card.title_vi}</h6>
              <IconArray k={card.evidence.k} n={card.evidence.n} />
              <p className="text-[11px] text-muted"><strong className="font-mono tabular-nums text-foreground">{formatShare(card.evidence.k, card.evidence.n)}</strong> {card.evidence.unit_vi}</p>
              {card.students?.length > 0 && (
                <ul className="flex flex-wrap gap-1.5" aria-label="Sinh viên trong thẻ">
                  {card.students.slice(0, 6).map((s) => (
                    <li key={s.username} className={s.mark?.state === 'handled' ? 'opacity-60' : ''}>
                      <button
                        type="button"
                        disabled={!s.exercise_id}
                        onClick={() => onOpenJourney({ username: s.username, full_name: s.full_name, exercise_id: s.exercise_id })}
                        className="rounded-full border border-border bg-surface px-2.5 py-0.5 text-[11px] text-foreground hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer disabled:cursor-default"
                      >
                        {s.full_name}
                      </button>
                    </li>
                  ))}
                  {card.students.length > 6 && <li className="self-center text-[11px] text-muted">+{card.students.length - 6}</li>}
                </ul>
              )}
              {card.reopened_vi && <p className="text-[11px] font-semibold text-foreground">{card.reopened_vi}</p>}
              <div className="mt-auto flex flex-wrap items-center justify-between gap-2 pt-1">
                <CardAction card={card} onOpenExercise={onOpenExercise} onOpenJourney={onOpenJourney} />
                <MarkButtons keys={card.open_keys} onMark={onMark} busy={busy} who={card.title_vi} />
              </div>
            </li>
          ))}
        </ul>
      )}
      {(actionCards?.positives?.length > 0 || actionCards?.more_count > 0) && (
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
          {actionCards.positives?.length > 0 && (
            <p className="flex items-start gap-1.5 text-emerald-700 dark:text-emerald-300"><Sparkles aria-hidden="true" className="mt-0.5 size-3.5 shrink-0" /><span><strong>Điểm sáng:</strong> {actionCards.positives.map((p) => p.text_vi).join(' · ')}</span></p>
          )}
          {actionCards.more_count > 0 && (
            <button type="button" onClick={onShowMore} className="rounded-full border border-border px-3 py-1 font-semibold text-foreground hover:bg-surface-raised cursor-pointer">Xem thêm {actionCards.more_count}</button>
          )}
        </div>
      )}
      {handledItems.length > 0 && (
        <details className="rounded-2xl border border-border">
          <summary className="cursor-pointer select-none px-3 py-2 text-xs font-semibold text-foreground">Đã đánh dấu ({handledItems.length})</summary>
          <ul className="space-y-1.5 border-t border-border p-3">
            {handledItems.map((it) => (
              <li key={it.key} className="flex flex-col gap-0.5 text-xs sm:flex-row sm:items-center sm:justify-between sm:gap-3">
                <span className="min-w-0 break-words text-foreground">{it.text_vi}</span>
                <MarkedNote mark={it.mark} keys={[it.key]} onUndo={onUndo} busy={busy} />
              </li>
            ))}
          </ul>
        </details>
      )}
      <p className="text-[11px] text-muted">{actionCards?.note || 'Thẻ tính lại mỗi lần mở; ngưỡng là quy ước vận hành chưa hiệu chuẩn.'}</p>
    </section>
  );
}

/** Tầng 2 — lưới SV × bài. Cuộn ngang bên trong khung, tiêu đề cố định; mỗi ô là một nút có aria-label. */
export function ClassMatrix({ matrix, groupCounts, onOpenCell, onOpenExercise }) {
  const exercises = matrix?.exercises || [];
  const rows = matrix?.rows || [];
  if (!exercises.length || !rows.length) return <ChartEmpty>Lớp chưa có bài tập hoặc sinh viên ghi danh.</ChartEmpty>;
  return (
    <div className="space-y-2.5">
      <div className="max-h-[26rem] overflow-auto rounded-xl border border-border">
        <table className="w-full border-separate border-spacing-0 text-xs">
          <caption className="sr-only">Ma trận sinh viên theo bài: mỗi ô là nhóm quá trình của sinh viên ở bài đó</caption>
          <thead>
            <tr>
              <th scope="col" className="sticky left-0 top-0 z-30 min-w-[8.5rem] border-b border-r border-border bg-surface-raised px-3 py-2 text-left font-semibold text-muted">Sinh viên (A→Z)</th>
              {exercises.map((e) => (
                <th key={e.exercise_id} scope="col" className="sticky top-0 z-20 border-b border-border bg-surface-raised p-1 align-bottom">
                  <button type="button" onClick={() => onOpenExercise(e.exercise_id)} title={`${e.title} · bấm để xem chi tiết bài`} className="w-full min-w-[3.5rem] max-w-[6.5rem] rounded-lg px-1.5 py-1 text-left hover:bg-surface focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer">
                    <span className="block font-mono text-[10px] text-muted">#{e.order_idx}</span>
                    <span className="line-clamp-2 block break-words text-[11px] font-semibold leading-tight text-foreground">{e.title}</span>
                    <span className="block font-mono text-[10px] tabular-nums text-muted">{e.students_passed}/{e.students_attempted}</span>
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.username}>
                <th scope="row" className="sticky left-0 z-10 border-b border-r border-border bg-surface px-3 py-1.5 text-left font-semibold text-foreground">
                  <span className="block truncate" title={r.full_name}>{r.full_name}</span>
                </th>
                {exercises.map((e) => {
                  const g = r.cells?.[e.exercise_id];
                  const st = MATRIX_STATES[g];
                  return (
                    <td key={e.exercise_id} className="border-b border-border p-1 text-center">
                      {st ? (
                        <button
                          type="button"
                          aria-label={`${r.full_name} · ${e.title}: ${st.label}`}
                          title={`${r.full_name} · ${e.title}: ${st.label}`}
                          onClick={() => onOpenCell({ username: r.username, full_name: r.full_name, exercise_id: e.exercise_id })}
                          className={`size-8 rounded-lg border text-sm font-semibold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer ${st.cell}`}
                        >
                          <span aria-hidden="true">{st.glyph}</span>
                        </button>
                      ) : (
                        <span role="img" aria-label={`${r.full_name} · ${e.title}: chưa bắt đầu`} className={`mx-auto flex size-8 items-center justify-center rounded-lg border ${EMPTY_CELL}`} />
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <ul className="grid gap-x-4 gap-y-1.5 text-[11px] text-muted sm:grid-cols-2 lg:grid-cols-4" aria-label="Chú giải ma trận">
        {Object.entries(MATRIX_STATES).map(([key, st]) => (
          <li key={key} className="flex items-center gap-1.5">
            <span aria-hidden="true" className={`inline-flex size-5 shrink-0 items-center justify-center rounded border text-[11px] ${st.cell}`}>{st.glyph}</span>
            <span>{st.label}{groupCounts ? <strong className="ml-1 font-mono tabular-nums text-foreground">{groupCounts[key] || 0}</strong> : null}</span>
          </li>
        ))}
        <li className="flex items-center gap-1.5"><span aria-hidden="true" className={`inline-flex size-5 shrink-0 rounded border ${EMPTY_CELL}`} /><span>Chưa bắt đầu</span></li>
      </ul>
    </div>
  );
}

const DOT_MAX = 24; // quá ngưỡng này thì vẽ thanh tỉ lệ thay cho từng chấm
const KC_ORDER = [
  { key: 'secure', label: 'Khá vững', dot: 'border-emerald-700 bg-emerald-600', bar: 'bg-emerald-600 text-white' },
  { key: 'developing', label: 'Đang hình thành', dot: 'border-sky-600 bg-sky-400', bar: 'bg-sky-400 text-sky-950' },
  { key: 'struggling', label: 'Đang vướng', dot: 'border-amber-600 border-[3px] bg-amber-100', bar: 'border-y-[3px] border-amber-600 bg-amber-100 text-amber-900' },
  { key: 'no_evidence', label: 'Chưa có bằng chứng', dot: 'border-dashed border-slate-400 bg-transparent', bar: 'border-y border-dashed border-slate-400 bg-transparent text-muted' },
];

/** Theo khái niệm: mỗi dòng một dãy chấm (mỗi chấm một sinh viên) khi lớp nhỏ, hoặc một thanh tỉ lệ khi lớp đông (nối mô hình người học với màn giảng viên). */
export function ConceptRows({ kcOverview }) {
  const items = kcOverview?.items || [];
  if (!items.length) return <ChartEmpty>Chưa có dữ liệu mô hình người học theo khái niệm.</ChartEmpty>;
  return (
    <div className="space-y-2">
      <ul className="space-y-1.5">
        {items.map((it) => {
          const counts = it.students || {};
          const total = KC_ORDER.reduce((s, o) => s + (counts[o.key] || 0), 0);
          const summary = KC_ORDER.map((o) => `${o.label} ${counts[o.key] || 0}`).join(', ');
          return (
            <li key={it.kc} className="grid gap-1 sm:grid-cols-[minmax(0,11rem)_1fr_auto] sm:items-center sm:gap-3">
              <span className="truncate text-xs font-semibold text-foreground" title={it.label_vi}>{it.label_vi}</span>
              {total > DOT_MAX ? (
                <span role="img" aria-label={`${it.label_vi}: ${summary}`} className="flex h-5 w-full overflow-hidden rounded-md bg-slate-200 dark:bg-slate-800">
                  {KC_ORDER.filter((o) => counts[o.key]).map((o) => (
                    <span key={o.key} title={`${o.label}: ${counts[o.key]}`} style={{ width: `${(counts[o.key] / total) * 100}%` }} className={`flex items-center justify-center overflow-hidden text-[10px] font-semibold ${o.bar}`}>
                      {(counts[o.key] / total) >= 0.08 ? counts[o.key] : ''}
                    </span>
                  ))}
                </span>
              ) : (
                <span role="img" aria-label={`${it.label_vi}: ${summary}`} className="flex flex-wrap gap-1">
                  {KC_ORDER.flatMap((o) => Array.from({ length: counts[o.key] || 0 }, (_, i) => (
                    <span key={`${o.key}-${i}`} title={o.label} className={`size-3.5 rounded-full border-2 ${o.dot}`} />
                  )))}
                </span>
              )}
              <span className="font-mono text-[11px] tabular-nums text-muted">{formatShare(counts.struggling || 0, total)} đang vướng</span>
            </li>
          );
        })}
      </ul>
      <ul className="flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-muted" aria-hidden="true">
        {KC_ORDER.map((o) => <li key={o.key} className="flex items-center gap-1.5"><span className={`size-3 rounded-full border-2 ${o.dot}`} />{o.label}</li>)}
      </ul>
    </div>
  );
}
