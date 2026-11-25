import React, { useCallback, useEffect, useRef, useState } from 'react';
import { AlertCircle, BookOpen, Info, Pencil, RefreshCw, ThumbsUp, Trash2, Upload, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { TableLoading } from './TableControls';
import { ChartEmpty, HBar, StackedBarRows, TrendLine } from './charts/ClassCharts';
import { ActionCards, ClassMatrix, ConceptRows, ERROR_SERIES, ExerciseDrawer, JourneyDrawer } from './classview/ClassViewParts';
import ClassBrief from './plain/ClassBrief';
import StudentGroups from './plain/StudentGroups';
import ExerciseProgressList from './plain/ExerciseProgressList';
import HowItWorks from './plain/HowItWorks';
import {
  deleteClassKnowledge, deleteGlobalKnowledge, fetchClassesAttention, fetchClassInsights, fetchClassKnowledge, fetchKnowledgeBaseCatalogue,
  fetchStudentLearnerModel, fetchTutorFeedbackSummary, markAttention, toggleClassKnowledge, undoAttentionMarks,
  toggleGlobalKnowledge, toggleSystemKnowledge, updateGlobalKnowledge, uploadClassKnowledge, uploadGlobalKnowledge,
} from '../services/api';

const KC_STATE_STYLE = {
  secure: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300',
  developing: 'border-sky-500/40 bg-sky-500/10 text-sky-700 dark:text-sky-300',
  struggling: 'border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300',
  no_evidence: 'border-border bg-surface-raised text-muted',
};

/** v5.6 — Mô hình người học của một sinh viên (tải khi giảng viên mở). Mô tả theo quy ước, không phải thang năng lực. */
function StudentLearnerModelDetail({ classId, username }) {
  const [state, setState] = useState({ loading: true, data: null, error: '' });

  // Tải ngay khi thẻ sinh viên hiện ra để chip khái niệm thấy được mà không cần mở mục thu gọn.
  useEffect(() => {
    let alive = true;
    setState({ loading: true, data: null, error: '' });
    fetchStudentLearnerModel(classId, username)
      .then((data) => { if (alive) setState({ loading: false, data, error: '' }); })
      .catch(() => { if (alive) setState({ loading: false, data: null, error: 'Không tải được mô hình người học.' }); });
    return () => { alive = false; };
  }, [classId, username]);

  const lm = state.data?.learner_model;
  const allConcepts = lm?.concepts || [];
  const evidenced = allConcepts.filter((c) => c.state && c.state !== 'no_evidence');
  // Ưu tiên khái niệm đang vướng; bỏ câu trùng lặp giữa các khái niệm (cùng bài, cùng dạng lỗi).
  const withError = [...evidenced.filter((c) => c.common_error_vi)]
    .sort((a, b) => Number(b.state === 'struggling') - Number(a.state === 'struggling'))
    .filter((c, i, arr) => arr.findIndex((x) => x.common_error_vi === c.common_error_vi) === i);
  return (
    <div className="mt-1.5 text-[11px]">
      {state.loading && <p className="text-muted">Đang tải khái niệm…</p>}
      {state.error && <p className="text-rose-600 dark:text-rose-300">{state.error}</p>}
      {lm && evidenced.length > 0 && (
        <ul className="flex flex-wrap gap-1.5" aria-label="Khái niệm đã có bài nộp">
          {evidenced.map((c) => (
            <li key={c.kc} title={c.explanation_vi || c.explanation} className={`rounded-full border px-2 py-0.5 ${KC_STATE_STYLE[c.state] || KC_STATE_STYLE.no_evidence}`}>
              {c.label_vi}: {c.state_label_vi || c.state}
            </li>
          ))}
        </ul>
      )}
      {lm && evidenced.length === 0 && <p className="text-muted">Chưa có khái niệm nào đủ bài nộp để nhận xét.</p>}
      {withError.length > 0 && (
        <ul className="mt-1 space-y-0.5 text-muted">
          {withError.slice(0, 1).map((c) => <li key={c.kc}><span className="font-semibold text-foreground">{c.label_vi}</span>. {c.common_error_vi}</li>)}
        </ul>
      )}
    <details className="mt-1.5">
      <summary className="cursor-pointer text-muted hover:text-foreground">Mô hình người học đầy đủ</summary>
      {lm && (
        <div className="mt-1.5 space-y-1.5">
          {allConcepts.length > 0 && (
            <ul className="space-y-1">
              {allConcepts.map((c) => (
                <li key={c.kc} className="text-muted">
                  <span className="font-semibold text-foreground">{c.label_vi}</span>: {c.explanation_vi || c.explanation || (c.state_label_vi || c.state)}
                </li>
              ))}
            </ul>
          )}
          {lm && (
            <>
              <p className="text-muted">
                Phụ thuộc gợi ý: {({ low: 'thấp', medium: 'trung bình', high: 'cao' })[lm.support_profile?.hint_reliance] || 'chưa đủ dữ liệu'} · {lm.support_profile?.ask_ai_count ?? 0} lượt hỏi Gia sư AI (mô tả quá trình, không tính vào chỉ số chính thức).
              </p>
              <p className="text-muted">{lm.disclaimer}</p>
            </>
          )}
        </div>
      )}
    </details>
    </div>
  );
}

// v5.3 (S3) — Không gian sư phạm cho giảng viên: góc nhìn theo lớp, tổng hợp 👍/👎, danh mục tài liệu RAG.
// Mọi số liệu đều kèm khoảng thời gian, cỡ mẫu và trạng thái dữ liệu; ngưỡng là quy ước vận hành.

const STATUS_META = {
  no_data: { label: 'Chưa có dữ liệu', className: 'border-border bg-surface-raised text-muted' },
  limited: { label: 'Mẫu nhỏ · chỉ mô tả', className: 'border-amber-500/40 bg-amber-500/10 text-amber-700 dark:text-amber-300' },
  sufficient: { label: 'Đủ dữ liệu mô tả', className: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300' },
};

export function DataStatusChip({ status }) {
  const meta = STATUS_META[status] || { label: 'Chưa rõ trạng thái', className: 'border-border bg-surface-raised text-muted' };
  return (
    <span className={`inline-flex shrink-0 items-center whitespace-nowrap rounded-md border px-2 py-0.5 text-[11px] font-semibold ${meta.className}`}>
      {meta.label}
    </span>
  );
}

export function DaysSelect({ value, onChange, label = 'Khoảng thời gian', options = [7, 14, 30, 90], disabled = false }) {
  return (
    <label className="inline-flex items-center gap-2 text-xs text-muted">
      <span className="sr-only sm:not-sr-only">{label}</span>
      <select
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(Number(event.target.value))}
        aria-label={label}
        className="min-h-9 rounded-xl border border-border bg-surface px-2.5 py-1.5 text-xs text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 disabled:opacity-50"
      >
        {options.map((days) => <option key={days} value={days}>{days} ngày gần nhất</option>)}
      </select>
    </label>
  );
}

function PanelError({ message, onRetry }) {
  return (
    <div role="alert" className="flex flex-col gap-3 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs text-rose-600 dark:text-rose-300 sm:flex-row sm:items-center sm:justify-between">
      <span className="flex items-start gap-2"><AlertCircle aria-hidden="true" className="mt-0.5 size-4 shrink-0" />{message}</span>
      <button
        type="button"
        onClick={onRetry}
        className="inline-flex min-h-9 shrink-0 items-center justify-center gap-1.5 rounded-xl border border-border bg-surface px-3 text-xs font-semibold text-foreground transition-colors hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 shadow-soft cursor-pointer"
      >
        <RefreshCw aria-hidden="true" className="size-3.5" /> Thử lại
      </button>
    </div>
  );
}

function RefreshButton({ onClick, busy, label }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      aria-label={label}
      title={label}
      className="inline-flex size-9 shrink-0 items-center justify-center rounded-lg border border-slate-700 text-slate-200 transition-colors hover:bg-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 disabled:opacity-50"
    >
      <RefreshCw aria-hidden="true" className={`size-4 ${busy ? 'animate-spin' : ''}`} />
    </button>
  );
}

/** Nạp dữ liệu theo tham số, bỏ qua phản hồi cũ khi tham số đã đổi. */
function useRemoteData(loader, deps) {
  const [state, setState] = useState({ data: null, isLoading: true, error: '' });
  const requestRef = useRef(0);
  const load = useCallback(async () => {
    const requestId = ++requestRef.current;
    setState((prev) => ({ ...prev, isLoading: true, error: '' }));
    try {
      const data = await loader();
      if (requestId === requestRef.current) setState({ data, isLoading: false, error: '' });
    } catch (err) {
      if (requestId !== requestRef.current) return;
      const detail = err?.response?.data?.detail;
      setState({ data: null, isLoading: false, error: typeof detail === 'string' ? detail : 'Không tải được dữ liệu. Kiểm tra kết nối tới máy chủ rồi thử lại.' });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(() => { load(); }, [load]);
  return { ...state, reload: load };
}

const ERROR_LABELS = {
  none: 'Không có lượt chưa đạt',
  syntax_or_runtime: 'Không đạt kiểm thử nào (thường cú pháp/runtime)',
  logic: 'Đạt một phần (thường logic/biên)',
};

function SampleCell({ label, value, hint }) {
  return (
    <div className="rounded-2xl border border-border bg-surface-raised p-4 shadow-soft">
      <dt className="text-xs text-muted font-medium">{label}</dt>
      <dd className="mt-1 font-mono text-xl font-bold tabular-nums text-foreground">{value}</dd>
      {hint && <dd className="text-[11px] text-muted mt-0.5">{hint}</dd>}
    </div>
  );
}

const PROCESS_STYLE = {
  independent_pass: 'bg-emerald-600',
  retry_pass: 'bg-sky-600',
  hint_pass: 'bg-violet-500',
  in_progress: 'bg-amber-400',
  stuck: 'bg-rose-500',
  practice_only: 'bg-slate-500',
};

const KC_STATE_SERIES = [
  { key: 'secure', label: 'Khá vững', fill: 'fill-emerald-600', bg: 'bg-emerald-600' },
  { key: 'developing', label: 'Đang hình thành', fill: 'fill-sky-600', bg: 'bg-sky-600' },
  { key: 'struggling', label: 'Đang vướng', fill: 'fill-amber-500', bg: 'bg-amber-500' },
  { key: 'no_evidence', label: 'Chưa có bằng chứng', fill: 'fill-slate-400', bg: 'bg-slate-400' },
];
function OverviewAction({ item, onOpenTab }) {
  if (item.target === 'edit_exercise' && item.exercise_id) {
    return <Link to={`/instructor/exercises/${encodeURIComponent(item.exercise_id)}/edit`} className="font-semibold text-emerald-600 underline underline-offset-2 dark:text-emerald-400">Sửa bài</Link>;
  }
  if (item.target === 'class_knowledge' && onOpenTab) {
    return <button type="button" onClick={() => onOpenTab('knowledge')} className="cursor-pointer font-semibold text-emerald-600 underline underline-offset-2 dark:text-emerald-400">Mở tài liệu lớp</button>;
  }
  if (item.target === 'curriculum' && onOpenTab) {
    return <button type="button" onClick={() => onOpenTab('curriculum')} className="cursor-pointer font-semibold text-emerald-600 underline underline-offset-2 dark:text-emerald-400">Mở lộ trình</button>;
  }
  return null;
}

function OverviewList({ title, tone, items, empty, onOpenTab }) {
  return (
    <div className={`rounded-xl border p-3 ${tone}`}>
      <h5 className="text-xs font-bold text-foreground">{title} ({items.length})</h5>
      {items.length === 0 ? <p className="mt-1.5 text-[11px] text-muted">{empty}</p> : (
        <ul className="mt-2 space-y-2">
          {items.map((it, i) => (
            <li key={`${it.code}-${it.student || it.exercise_id || it.kc || i}`} className="text-xs leading-relaxed">
              <p className="text-foreground">{it.text_vi}</p>
              {it.suggestion_vi && <p className="text-[11px] text-muted">→ {it.suggestion_vi} <OverviewAction item={it} onOpenTab={onOpenTab} /></p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function ClassOverviewSummary({ overview, onOpenTab }) {
  if (!overview) return null;
  return (
    <div className="space-y-3">
      <h5 className="text-xs font-bold text-foreground">Tóm tắt tình hình lớp</h5>
      {overview.insufficient_reason_vi && (
        <p className="flex items-start gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-700 dark:text-amber-300">
          <Info aria-hidden="true" className="mt-0.5 size-4 shrink-0" />{overview.insufficient_reason_vi}
        </p>
      )}
      <div className="grid gap-3 lg:grid-cols-3">
        <OverviewList title="Cần chú ý" tone="border-rose-500/30 bg-rose-500/5" items={overview.attention || []} empty="Chưa thấy sinh viên nào cần chú ý theo quy ước hiện tại." onOpenTab={onOpenTab} />
        <OverviewList title="Vấn đề chung" tone="border-amber-500/30 bg-amber-500/5" items={overview.class_issues || []} empty="Chưa thấy vấn đề chung rõ ràng." onOpenTab={onOpenTab} />
        <OverviewList title="Tiến triển tốt" tone="border-emerald-500/30 bg-emerald-500/5" items={overview.positives || []} empty="Chưa có điểm sáng nổi bật." onOpenTab={onOpenTab} />
      </div>
      <p className="text-[11px] text-muted">{overview.note} Danh sách nêu lý do, không xếp hạng sinh viên.</p>
    </div>
  );
}

function ClassChartsSection({ data }) {
  const kcRows = (data.kc_overview?.items || []).map((k) => ({ key: k.kc, label: k.label_vi, values: k.students }));
  const errRows = (data.error_breakdown_by_exercise || []).map((e) => {
    const values = { ...(e.submit || {}) };
    Object.entries(e.run || {}).forEach(([k, v]) => { values[k] = (values[k] || 0) + v; });
    delete values.passed;
    values.format_only = (e.format_only_submit || 0) + (e.format_only_run || 0);
    return { key: e.exercise_id, label: e.title, values };
  });
  const completion = (data.bottlenecks || []).map((b) => ({
    key: b.exercise_id, label: b.title, value: b.students_passed, max: Math.max(1, b.students_attempted), text: `${b.students_passed}/${b.students_attempted} SV`,
  }));
  const trend = (data.daily_trend || []).map((d) => ({ date: d.date, a: d.active_students, b: d.first_passes }));
  const failing = (data.failing_tests_by_exercise || []).flatMap((f) => (f.tests || []).slice(0, 1).map((t) => ({ ...t, title: f.title })));
  const ttp = data.time_to_pass_by_exercise || [];
  return (
    <div className="space-y-5">
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="space-y-2">
          <h5 className="text-xs font-bold text-foreground">Kiến thức: số sinh viên theo trạng thái</h5>
          <StackedBarRows rows={kcRows} series={KC_STATE_SERIES} ariaLabel="Số sinh viên theo trạng thái từng đơn vị kiến thức" />
        </div>
        <div className="space-y-2">
          <h5 className="text-xs font-bold text-foreground">Hoàn thành theo bài (SV đã qua / đã thử)</h5>
          <HBar rows={completion} ariaLabel="Số sinh viên đã qua trên số đã thử theo bài" />
        </div>
        <div className="space-y-2">
          <h5 className="text-xs font-bold text-foreground">Loại lỗi theo bài (nộp + chạy thử)</h5>
          <StackedBarRows rows={errRows} series={ERROR_SERIES} ariaLabel="Loại lỗi theo bài" />
          <p className="text-[11px] text-muted">Lượt trước v5.7 chưa có đặc trưng nên không có trong biểu đồ; tỉ lệ lượt có đặc trưng: {data.feature_coverage_percent ?? 0}%.</p>
        </div>
      </div>
      <div className="space-y-2">
        <h5 className="text-xs font-bold text-foreground">Xu hướng theo ngày</h5>
        <TrendLine points={trend} ariaLabel="Sinh viên hoạt động và lượt đạt lần đầu theo ngày" labelA="SV hoạt động" labelB="Đạt lần đầu" />
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="space-y-2">
          <h5 className="text-xs font-bold text-foreground">Test hay sai nhất mỗi bài</h5>
          {failing.length === 0 ? <ChartEmpty /> : (
            <ul className="space-y-1 text-xs">
              {failing.map((t) => (
                <li key={`${t.title}-${t.test_idx}`} className="rounded-lg border border-border p-2">
                  <span className="font-semibold text-foreground">{t.title}</span> · test #{t.test_idx} “{t.description}”{t.input ? <> (input <span className="font-mono">{t.input}</span>)</> : null}
                  <span className="text-muted"> — {t.attempts} lượt, {t.students} SV{t.format_attempts ? `, ${t.format_attempts} lượt chỉ sai định dạng` : ''}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="space-y-2">
          <h5 className="text-xs font-bold text-foreground">Khoảng thời gian tới khi đạt (trung vị)</h5>
          {ttp.length === 0 ? <ChartEmpty /> : (
            <ul className="space-y-1 text-xs">
              {ttp.map((t) => (
                <li key={t.exercise_id} className="flex justify-between gap-3 rounded-lg border border-border p-2">
                  <span className="truncate text-foreground" title={t.title}>{t.title}</span>
                  <span className="shrink-0 font-mono tabular-nums text-muted">{t.median_minutes} phút (n={t.n})</span>
                </li>
              ))}
            </ul>
          )}
          <p className="text-[11px] text-muted">Là khoảng giữa sự kiện đầu và lần nộp đạt đầu, không phải thời gian ngồi làm.</p>
        </div>
      </div>
    </div>
  );
}

export function ClassInsightsPanel({ classId, onOpenTab }) {
  const [days, setDays] = useState(7);
  const [onlyNeedingSupport, setOnlyNeedingSupport] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [journeyTarget, setJourneyTarget] = useState(null);
  const [exerciseTarget, setExerciseTarget] = useState(null);
  const { data, isLoading, error, reload } = useRemoteData(() => fetchClassInsights(classId, days), [classId, days]);

  const sample = data?.sample || {};
  const bottlenecks = data?.bottlenecks || [];
  const students = data?.students || [];
  const shownStudents = onlyNeedingSupport ? students.filter((s) => s.needs_support) : students;
  const shownBottlenecks = bottlenecks.slice(0, 10);
  const processDefs = data?.process_groups?.definitions || [];
  const processByExercise = data?.process_groups?.by_exercise || [];
  const processLabels = Object.fromEntries(processDefs.map((d) => [d.key, d.label]));
  const exerciseTitles = Object.fromEntries((data?.matrix?.exercises || []).map((e) => [e.exercise_id, e.title]));
  bottlenecks.forEach((b) => { exerciseTitles[b.exercise_id] = exerciseTitles[b.exercise_id] || b.title; });
  processByExercise.forEach((item) => { exerciseTitles[item.exercise_id] = exerciseTitles[item.exercise_id] || item.title; });

  const openJourney = (t) => { if (t?.exercise_id) setJourneyTarget(t); };

  // v5.13 — đánh dấu "đã xử lý" / "không cần" và hoàn tác; máy chủ tính lại danh sách rồi tải lại bản tin.
  const [markBusy, setMarkBusy] = useState(false);
  const [markError, setMarkError] = useState('');
  const runMark = async (action) => {
    setMarkBusy(true);
    setMarkError('');
    try {
      await action();
      await reload();
    } catch {
      setMarkError('Chưa lưu được dấu. Thầy/cô thử lại nhé.');
    } finally {
      setMarkBusy(false);
    }
  };
  const applyMark = (keys, status) => runMark(() => markAttention(classId, keys, status, days));
  const undoMark = (keys) => runMark(() => undoAttentionMarks(classId, keys));
  const handledItems = [...(data?.overview?.attention || []), ...(data?.overview?.class_issues || [])]
    .filter((it) => it.mark?.state === 'handled');

  return (
    <section aria-label="Tình hình lớp" className="space-y-5 rounded-2xl border border-border bg-surface p-4 sm:p-5 shadow-soft">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h4 className="text-sm font-bold text-foreground">Tình hình lớp</h4>
          <p className="mt-1 text-xs text-muted" aria-live="polite">
            {data ? `${data.days} ngày gần nhất · bản tin tự động, cập nhật mỗi lần mở` : 'Đang tải…'}
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-2">
          <DaysSelect value={days} onChange={setDays} disabled={isLoading} />
          <RefreshButton onClick={reload} busy={isLoading} label="Tải lại tình hình lớp" />
        </div>
      </div>

      {isLoading && !data ? (
        <TableLoading label="Đang tải tình hình lớp" />
      ) : error ? (
        <PanelError message={error} onRetry={reload} />
      ) : data ? (
        <div className={`space-y-6 ${isLoading ? 'opacity-60' : ''}`} aria-busy={isLoading}>
          {!data.plain || data.plain.active === 0 ? (
            <div className="rounded-xl border border-dashed border-border p-6 text-center text-sm text-muted">
              <p className="font-semibold text-foreground">Chưa có bạn nào chạy thử hay nộp bài trong {data.days} ngày qua.</p>
              <p className="mt-1">Thử chọn khoảng thời gian dài hơn.</p>
            </div>
          ) : (
            <>
              <ClassBrief plain={data.plain} />
              {markError && <p role="alert" className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-2.5 text-xs text-rose-600 dark:text-rose-300">{markError}</p>}
              <StudentGroups
                plain={data.plain}
                onOpenStudent={(p) => openJourney({ username: p.username, full_name: p.full_name, exercise_id: p.exercise_id })}
                onMark={applyMark}
                onUndo={undoMark}
                busy={markBusy}
              />
              <ExerciseProgressList exercises={data.plain.exercises} onOpenExercise={(exerciseId) => setExerciseTarget(exerciseId)} />
              <HowItWorks items={data.plain.how_it_works_vi} />

              {/* Tầng 3 — dữ liệu chi tiết */}
              <details open={detailsOpen} onToggle={(e) => setDetailsOpen(e.currentTarget.open)} className="rounded-2xl border border-border">
                <summary className="cursor-pointer select-none px-4 py-3 text-sm font-bold text-foreground">Xem số liệu đầy đủ</summary>
                {detailsOpen && (
                  <div className="space-y-6 border-t border-border p-4">
                    {data.data_status === 'limited' && (
                      <p className="flex items-start gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-700 dark:text-amber-300">
                        <Info aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
                        Dưới 3 sinh viên có hoạt động trong khoảng này: số liệu chỉ mang tính mô tả, chưa đại diện cho cả lớp.
                      </p>
                    )}

                    {/* Tầng 1 — việc nên xem */}
                    <ActionCards
                      actionCards={data.action_cards}
                      onOpenExercise={(exerciseId) => setExerciseTarget(exerciseId)}
                      onOpenJourney={openJourney}
                      onShowMore={() => setDetailsOpen(true)}
                      insufficientReason={data.overview?.insufficient_reason_vi}
                      handledItems={handledItems}
                      onMark={applyMark}
                      onUndo={undoMark}
                      busy={markBusy}
                    />

                    {/* Tầng 2 — ma trận lớp */}
                    <section aria-labelledby="class-matrix" className="space-y-2.5">
                      <div>
                        <h5 id="class-matrix" className="text-sm font-bold text-foreground">Ma trận lớp: sinh viên × bài</h5>
                        <p className="mt-0.5 text-[11px] text-muted">Mỗi ô là nhóm quá trình của một sinh viên ở một bài. Bấm vào ô để xem dấu chân, bấm tiêu đề cột để xem bài. Sinh viên xếp A→Z, không xếp hạng.</p>
                      </div>
                      <ClassMatrix
                        matrix={data.matrix}
                        groupCounts={data.process_groups?.overall}
                        onOpenCell={openJourney}
                        onOpenExercise={(exerciseId) => setExerciseTarget(exerciseId)}
                      />
                    </section>

                    <section aria-labelledby="class-concepts" className="space-y-2.5">
                      <div>
                        <h5 id="class-concepts" className="text-sm font-bold text-foreground">Theo khái niệm</h5>
                        <p className="mt-0.5 text-[11px] text-muted">Số sinh viên ở từng trạng thái của mỗi khái niệm: mỗi chấm là một sinh viên khi lớp nhỏ, thanh tỉ lệ khi lớp đông (quy tắc cố định, chưa hiệu chuẩn).</p>
                      </div>
                      <ConceptRows kcOverview={data.kc_overview} />
                    </section>

                    <ClassOverviewSummary overview={data.overview} onOpenTab={onOpenTab} />
                    <ClassChartsSection data={data} />

                    {processDefs.length > 0 && (
                      <details className="text-[11px] text-muted">
                        <summary className="cursor-pointer font-semibold text-foreground">Chú giải ngưỡng phân nhóm quá trình ({data.process_groups?.pairs ?? 0} cặp sinh viên–bài)</summary>
                        <ul className="mt-1.5 list-disc space-y-1 pl-4 leading-relaxed">
                          {processDefs.map((d) => <li key={d.key}><strong className="text-foreground">{d.label}:</strong> {d.rule}</li>)}
                        </ul>
                      </details>
                    )}

                    <div className="space-y-2">
                      <h5 className="text-xs font-bold text-foreground">Bài gây nghẽn (xếp theo số lượt chưa đạt)</h5>
                      <div className="overflow-x-auto rounded-xl border border-border">
                        <table className="table-stack w-full min-w-[40rem] text-left text-xs">
                          <thead className="bg-surface-raised">
                            <tr className="border-b border-border font-semibold text-muted">
                              <th scope="col" className="px-3 py-2.5">Bài tập</th>
                              <th scope="col" className="px-3 py-2.5 text-right">Lượt nộp</th>
                              <th scope="col" className="px-3 py-2.5 text-right">Chưa đạt</th>
                              <th scope="col" className="px-3 py-2.5 text-right">SV đã qua / đã thử</th>
                              <th scope="col" className="px-3 py-2.5 text-right">TB lượt / SV</th>
                              <th scope="col" className="px-3 py-2.5">Dạng lỗi chủ yếu</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-border">
                            {shownBottlenecks.map((item) => (
                              <tr key={item.exercise_id} className="transition-colors hover:bg-surface-raised">
                                <td className="px-3 py-2.5">
                                  <div className="font-semibold text-foreground">{item.title}</div>
                                  <div className="text-[11px] text-muted">{item.topic || 'Chưa gán chủ đề'} · <span className="font-mono">{item.exercise_id}</span></div>
                                </td>
                                <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{item.submissions}</td>
                                <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{item.unsuccessful}/{item.submissions}</td>
                                <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{item.students_passed}/{item.students_attempted}</td>
                                <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{item.avg_submissions_per_student}</td>
                                <td className="px-3 py-2.5 text-muted">{ERROR_LABELS[item.dominant_error] || item.dominant_error}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      {bottlenecks.length > shownBottlenecks.length && (
                        <p className="text-[11px] text-muted">Hiển thị {shownBottlenecks.length}/{bottlenecks.length} bài có nhiều lượt chưa đạt nhất.</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                        <h5 className="flex items-center gap-2 text-xs font-bold text-foreground">
                          <Users aria-hidden="true" className="size-4 text-emerald-500" />
                          Sinh viên có hoạt động ({students.length}) · cần hỗ trợ: {data.students_needing_support ?? 0}
                        </h5>
                        <label className="inline-flex min-h-9 cursor-pointer items-center gap-2 text-xs text-muted">
                          <input
                            type="checkbox"
                            checked={onlyNeedingSupport}
                            onChange={(event) => setOnlyNeedingSupport(event.target.checked)}
                            className="size-4 rounded border-border accent-emerald-600"
                          />
                          Chỉ hiện sinh viên cần hỗ trợ
                        </label>
                      </div>
                      <div className="max-h-[min(60vh,32rem)] overflow-auto rounded-xl border border-border">
                        <table className="table-stack w-full min-w-[40rem] text-left text-xs">
                          <thead className="sticky top-0 z-10 bg-surface-raised">
                            <tr className="border-b border-border font-semibold text-muted">
                              <th scope="col" className="px-3 py-2.5">Sinh viên</th>
                              <th scope="col" className="px-3 py-2.5 text-right">Bài đã qua / đã thử</th>
                              <th scope="col" className="px-3 py-2.5 text-right">Lượt chưa đạt / lượt nộp</th>
                              <th scope="col" className="px-3 py-2.5">Nhóm quá trình theo bài</th>
                              <th scope="col" className="px-3 py-2.5">Dữ liệu</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-border">
                            {shownStudents.length === 0 ? (
                              <tr><td colSpan={5} className="px-3 py-6 text-center text-muted">Không có sinh viên nào ở nhóm Mắc kẹt theo quy ước hiện tại.</td></tr>
                            ) : shownStudents.map((student) => (
                              <tr key={student.username} className="transition-colors hover:bg-surface-raised">
                                <td className="px-3 py-2.5">
                                  <div className="font-semibold text-foreground">{student.full_name}</div>
                                  <div className="font-mono text-[11px] text-muted">@{student.username}</div>
                                  <StudentLearnerModelDetail classId={classId} username={student.username} />
                                </td>
                                <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{student.exercises_passed}/{student.distinct_exercises}</td>
                                <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{student.unsuccessful}/{student.submissions}</td>
                                <td className="px-3 py-2.5 text-muted">
                                  {Object.keys(student.process_by_exercise || {}).length === 0
                                    ? <span className="text-muted">Chưa có</span>
                                    : (
                                      <ul className="flex flex-wrap gap-1.5">
                                        {Object.entries(student.process_by_exercise).map(([eid, group]) => (
                                          <li key={eid} className={`inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] ${group === 'stuck' ? 'border-rose-500/50 font-semibold text-rose-600 dark:text-rose-300' : 'border-border text-foreground'}`}>
                                            <span aria-hidden="true" className={`size-2 rounded-full ${PROCESS_STYLE[group] || 'bg-slate-500'}`} />
                                            <span>{exerciseTitles[eid] || eid}: {processLabels[group] || group}</span>
                                          </li>
                                        ))}
                                      </ul>
                                    )}
                                </td>
                                <td className="px-3 py-2.5"><DataStatusChip status={student.data_status} /></td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {Array.isArray(data.caveats) && data.caveats.length > 0 && (
                      <div className="border-t border-border pt-3">
                        <h5 className="text-[11px] font-semibold text-foreground">Giới hạn khi diễn giải</h5>
                        <ul className="mt-1.5 list-disc space-y-1 pl-4 text-[11px] leading-relaxed text-muted">
                          {data.caveats.map((caveat) => <li key={caveat}>{caveat}</li>)}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </details>
            </>
          )}

          {journeyTarget && (
            <JourneyDrawer
              classId={classId}
              target={journeyTarget}
              days={days}
              studentName={journeyTarget.full_name}
              exerciseTitle={exerciseTitles[journeyTarget.exercise_id] || journeyTarget.exercise_id}
              onClose={() => setJourneyTarget(null)}
            />
          )}
          {exerciseTarget && <ExerciseDrawer data={data} exerciseId={exerciseTarget} onClose={() => setExerciseTarget(null)} />}
        </div>
      ) : null}
    </section>
  );
}

const ATTENTION_PAGE = 8;

/** v5.8 — Lớp cần chú ý: một lần gọi tổng hợp cho mọi lớp; chỉ hiện lớp có việc cần xem, có tìm kiếm và "Xem thêm". */
export function ClassesAttentionList({ classes, onOpen }) {
  const [state, setState] = useState({ loading: true, error: false, data: null });
  const [query, setQuery] = useState('');
  const [shown, setShown] = useState(ATTENTION_PAGE);
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    let alive = true;
    setState((prev) => ({ ...prev, loading: true, error: false }));
    fetchClassesAttention()
      .then((data) => { if (alive) setState({ loading: false, error: false, data }); })
      .catch(() => { if (alive) setState({ loading: false, error: true, data: null }); });
    return () => { alive = false; };
  }, [classes, reloadKey]);
  if (!classes || classes.length === 0) return null;

  const all = state.data?.classes || [];
  const q = query.trim().toLowerCase();
  const matches = (c) => !q || `${c.class_code || ''} ${c.class_name || ''}`.toLowerCase().includes(q);
  const needing = all.filter((c) => c.total > 0 && matches(c));
  const quiet = all.filter((c) => c.total === 0 && matches(c));
  const byId = Object.fromEntries((classes || []).map((c) => [c.id, c]));
  const visible = needing.slice(0, shown);

  return (
    <section aria-label="Các lớp cần xem tuần này" className="space-y-3 rounded-2xl border border-border bg-surface p-5 shadow-soft">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-sm font-bold text-foreground">Các lớp cần xem tuần này</h3>
          <p className="mt-1 text-[11px] text-muted" aria-live="polite">
            {state.data ? `${state.data.needing_attention} trong ${state.data.total_classes} lớp có việc nên xem.` : ''}
          </p>
        </div>
        {all.length > ATTENTION_PAGE && (
          <input
            type="search" value={query} onChange={(e) => { setQuery(e.target.value); setShown(ATTENTION_PAGE); }}
            placeholder="Tìm lớp theo mã hoặc tên" aria-label="Tìm lớp"
            className="min-h-9 w-full rounded-xl border border-border bg-surface px-3 text-xs text-foreground placeholder:text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 sm:w-60"
          />
        )}
      </div>
      {state.loading ? <TableLoading label="Đang tải tình hình các lớp" /> : state.error ? (
        <PanelError message="Không tải được tình hình các lớp." onRetry={() => setReloadKey((k) => k + 1)} />
      ) : (
        <>
          {needing.length === 0 ? (
            <p className="rounded-xl border border-dashed border-border p-3 text-center text-xs text-muted">
              {q ? 'Không có lớp nào khớp và đang có việc cần xem.' : 'Tuần này chưa có lớp nào cần xem ngay.'}
            </p>
          ) : (
            <ul className="grid gap-2 sm:grid-cols-2">
              {visible.map((c) => (
                <li key={c.id}>
                  <button type="button" onClick={() => byId[c.id] && onOpen(byId[c.id])} className="flex min-h-11 w-full cursor-pointer items-center justify-between gap-3 rounded-xl border border-border bg-surface-raised px-3 py-2 text-left text-xs transition-colors hover:border-emerald-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400">
                    <span className="min-w-0 truncate font-semibold text-foreground">{c.class_code} · {c.class_name}</span>
                    <span className="shrink-0 text-muted">{c.brief_vi || `${c.attention} bạn cần chú ý`}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
          {needing.length > shown && (
            <button type="button" onClick={() => setShown((n) => n + ATTENTION_PAGE)} className="rounded-full border border-border px-3 py-1 text-xs font-semibold text-foreground hover:bg-surface-raised cursor-pointer">
              Xem thêm {needing.length - shown} lớp
            </button>
          )}
          {quiet.length > 0 && (
            <p className="text-[11px] text-muted">{quiet.length} lớp khác đang ổn, chưa có hoạt động hoặc các việc đã được đánh dấu.</p>
          )}
        </>
      )}
    </section>
  );
}

function isLlmSource(source) {
  const s = (source || '').toLowerCase();
  return s.includes('gemini') || s.includes('qwen');
}

/** Hiển thị **đậm** và *nghiêng* trong câu trả lời dạng văn bản (không dựng HTML từ chuỗi). */
function renderInlineMarkdown(text) {
  return String(text || '').split(/(\*\*[^*\n]+\*\*|\*[^*\n]+\*)/g).map((part, index) => {
    if (part.length > 4 && part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index} className="font-semibold text-foreground">{part.slice(2, -2)}</strong>;
    }
    if (part.length > 2 && part.startsWith('*') && part.endsWith('*')) {
      return <em key={index}>{part.slice(1, -1)}</em>;
    }
    return part;
  });
}

/** Câu trả lời Class Chat kèm khoảng thời gian, cỡ mẫu và trạng thái dữ liệu mà backend đã dùng. */
export function ClassChatAnswer({ result }) {
  if (!result) return null;
  if (result.error) {
    return <div role="alert" className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-600 dark:text-rose-300">{result.error}</div>;
  }
  const sample = result.sample || {};
  return (
    <div className="rounded-2xl border border-border bg-surface-raised shadow-soft">
      <div className="flex flex-col gap-2 border-b border-border px-4 py-2.5 text-[11px] text-muted sm:flex-row sm:items-center sm:justify-between">
        <span>
          Số liệu <strong className="text-foreground">{result.days} ngày gần nhất</strong> · <strong className="text-foreground">{sample.submissions ?? 0}</strong> lượt nộp chính thức · <strong className="text-foreground">{sample.active_students ?? 0}/{sample.enrolled_students ?? 0}</strong> SV có hoạt động
        </span>
        <span className="self-start sm:self-auto"><DataStatusChip status={result.data_status} /></span>
      </div>
      <div className="whitespace-pre-wrap break-words p-4 text-xs leading-relaxed text-foreground">{renderInlineMarkdown(result.reply)}</div>
      <p className="border-t border-border px-4 py-2 text-[11px] text-muted">
        {isLlmSource(result.llm_source) ? 'Câu trả lời do mô hình AI soạn từ số liệu tổng hợp' : 'Câu trả lời tự động dựng trực tiếp từ số liệu tổng hợp (không dùng mô hình AI)'}
        ; không chứa danh tính hay mã nguồn của sinh viên.
        {result.data_status === 'limited' && ' Mẫu nhỏ: chỉ nên đọc như mô tả, không suy rộng cho cả lớp.'}
        {result.data_status === 'no_data' && ' Chưa có lượt nộp trong khoảng này nên không có nhận định nào được đưa ra.'}
      </p>
    </div>
  );
}

const TASK_LABELS = {
  adaptive_hint: 'Gợi ý từ nút Hỏi Gia sư AI',
  student_chat: 'Trò chuyện với Gia sư',
};

export function TutorFeedbackPanel() {
  const [days, setDays] = useState(30);
  const { data, isLoading, error, reload } = useRemoteData(() => fetchTutorFeedbackSummary(days), [days]);
  const rows = data?.by_task || [];

  return (
    <section aria-label="Đánh giá của sinh viên về phản hồi AI" className="space-y-3 rounded-2xl border border-border bg-surface p-4 sm:p-5 shadow-soft">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h3 className="flex items-center gap-2 text-sm font-bold text-foreground"><ThumbsUp aria-hidden="true" className="size-4 text-emerald-500" /> Sinh viên đánh giá phản hồi AI</h3>
          <p className="mt-1 text-xs text-muted">Chỉ số đếm 👍/👎 theo loại tác vụ, trong các lớp bạn phụ trách. Không có nội dung phản hồi hay danh tính người đánh giá.</p>
        </div>
        <div className="flex shrink-0 flex-wrap items-center gap-2">
          {data && <DataStatusChip status={data.data_status} />}
          <DaysSelect value={days} onChange={setDays} options={[7, 30, 90]} disabled={isLoading} />
          <RefreshButton onClick={reload} busy={isLoading} label="Tải lại tổng hợp đánh giá" />
        </div>
      </div>

      {isLoading && !data ? (
        <TableLoading label="Đang tải tổng hợp đánh giá" />
      ) : error ? (
        <PanelError message={error} onRetry={reload} />
      ) : data ? (
        <div className={`space-y-2 ${isLoading ? 'opacity-60' : ''}`} aria-busy={isLoading}>
          {rows.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border p-6 text-center text-xs text-muted">
              Chưa có lượt tương tác AI nào của sinh viên trong {data.days} ngày gần nhất.
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="table-stack w-full min-w-[40rem] text-left text-xs">
                <thead className="bg-surface-raised">
                  <tr className="border-b border-border font-semibold text-muted">
                    <th scope="col" className="px-3 py-2.5">Loại tác vụ</th>
                    <th scope="col" className="px-3 py-2.5 text-right">Lượt tương tác</th>
                    <th scope="col" className="px-3 py-2.5 text-right">Đã đánh giá</th>
                    <th scope="col" className="px-3 py-2.5 text-right">👍 Hữu ích</th>
                    <th scope="col" className="px-3 py-2.5 text-right">👎 Chưa hữu ích</th>
                    <th scope="col" className="px-3 py-2.5 text-right">Tỷ lệ hữu ích</th>
                    <th scope="col" className="px-3 py-2.5 text-right">Dự phòng / bị chặn</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {rows.map((row) => (
                    <tr key={row.task_type} className="transition-colors hover:bg-surface-raised">
                      <th scope="row" className="px-3 py-2.5 font-semibold text-foreground">{TASK_LABELS[row.task_type] || row.task_type}</th>
                      <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{row.interactions}</td>
                      <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{row.rated}</td>
                      <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{row.helpful}</td>
                      <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{row.not_helpful}</td>
                      <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">
                        {row.helpful_percent == null ? <span className="text-muted">Chưa có đánh giá</span> : `${row.helpful_percent}%`}
                      </td>
                      <td className="px-3 py-2.5 text-right font-mono tabular-nums text-foreground">{row.fallback_or_blocked ?? 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="text-[11px] leading-relaxed text-muted">
            {data.total_rated}/{data.total_interactions} lượt được đánh giá trong {data.days} ngày. {data.note} “Dự phòng / bị chặn” là số lượt trả lời bằng luật tự động hoặc bị bộ lọc Anti-Spoil thay thế.
          </p>
        </div>
      ) : null}
    </section>
  );
}

const KB_FIELD = 'w-full min-h-10 rounded-xl border border-border bg-surface px-3 py-2 text-xs text-foreground placeholder:text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400';

/** v5.4 (C): giảng viên tải tài liệu cho Gia sư AI của đúng lớp này. */
export function ClassKnowledgePanel({ classId }) {
  const { data, isLoading, error, reload } = useRemoteData(() => fetchClassKnowledge(classId), [classId]);
  const [file, setFile] = useState(null);
  const [form, setForm] = useState({ title: '', license_type: '', license_detail: '', provenance: '', confirm: false });
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null); // {tone: 'ok' | 'error', text, warnings}
  const fileInputRef = useRef(null);
  const documents = data?.documents || [];
  const limits = data?.limits || { max_documents: 20, max_file_mb: 5, max_chars: 150000, formats: ['.md', '.txt', '.pdf', '.docx'] };
  const setField = (key) => (event) => setForm((prev) => ({ ...prev, [key]: event.target.type === 'checkbox' ? event.target.checked : event.target.value }));

  const submit = async (event) => {
    event.preventDefault();
    if (!file) { setMessage({ tone: 'error', text: 'Hãy chọn một tệp tài liệu.' }); return; }
    const body = new FormData();
    body.append('file', file);
    body.append('title', form.title);
    body.append('license_type', form.license_type);
    body.append('license_detail', form.license_detail);
    body.append('provenance', form.provenance);
    body.append('no_personal_data', form.confirm ? 'true' : 'false');
    setBusy(true); setMessage(null);
    try {
      const res = await uploadClassKnowledge(classId, body);
      setMessage({ tone: 'ok', text: `Đã lưu "${res.document.title}" (${res.document.chunk_count} đoạn). Gia sư AI của lớp này dùng được ngay.`, warnings: res.warnings });
      setFile(null); setForm({ title: '', license_type: '', license_detail: '', provenance: '', confirm: false });
      if (fileInputRef.current) fileInputRef.current.value = '';
      reload();
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setMessage({ tone: 'error', text: typeof detail === 'string' ? detail : 'Không tải lên được. Kiểm tra kết nối rồi thử lại.' });
    } finally { setBusy(false); }
  };

  const toggle = async (doc) => {
    try { await toggleClassKnowledge(classId, doc.id, !doc.is_active); reload(); }
    catch { setMessage({ tone: 'error', text: 'Không đổi được trạng thái tài liệu.' }); }
  };
  const remove = async (doc) => {
    if (!window.confirm(`Xóa tài liệu "${doc.title}"? Gia sư AI sẽ không dùng tài liệu này nữa và không thể hoàn tác.`)) return;
    try { await deleteClassKnowledge(classId, doc.id); reload(); }
    catch { setMessage({ tone: 'error', text: 'Không xóa được tài liệu.' }); }
  };

  return (
    <section aria-label="Tài liệu cho Gia sư AI" className="space-y-4 rounded-2xl border border-border bg-surface p-4 sm:p-5 shadow-soft">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h4 className="flex items-center gap-2 text-sm font-bold text-foreground"><BookOpen aria-hidden="true" className="size-4 text-emerald-500" /> Tài liệu cho Gia sư AI của lớp này</h4>
          <p className="mt-1 text-xs text-muted">Chỉ sinh viên đã ghi danh lớp này mới nhận được trích dẫn từ các tài liệu dưới đây. Tài liệu chung của hệ thống xem ở mục Giám sát.</p>
        </div>
        <RefreshButton onClick={reload} busy={isLoading} label="Tải lại danh sách tài liệu" />
      </div>

      <div className="rounded-xl border border-border bg-surface-raised p-3.5 text-[11px] leading-relaxed text-muted shadow-soft">
        <p className="font-semibold text-foreground">Tiêu chuẩn tài liệu</p>
        <ul className="mt-1 list-disc space-y-0.5 pl-4">
          <li>Định dạng: {limits.formats.join(', ')}. PDF phải có lớp chữ (không nhận bản scan).</li>
          <li>Tối đa {limits.max_file_mb} MB mỗi tệp, {Number(limits.max_chars).toLocaleString('vi-VN')} ký tự chữ sau khi trích, {limits.max_documents} tài liệu mỗi lớp.</li>
          <li>Nên tải: giải thích khái niệm, quy tắc viết mã, lỗi thường gặp; chia mục bằng tiêu đề để truy xuất tốt hơn.</li>
          <li>Không tải: dữ liệu cá nhân sinh viên, đề thi, đáp án bài tập của lớp. Chỉ văn bản trích ra được lưu, tệp gốc không được lưu.</li>
        </ul>
      </div>

      <form onSubmit={submit} className="space-y-3 text-xs" aria-busy={busy}>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="space-y-1">
            <span className="font-semibold text-foreground">Tệp tài liệu *</span>
            <input ref={fileInputRef} type="file" accept=".md,.txt,.pdf,.docx" onChange={(e) => setFile(e.target.files?.[0] || null)} className={KB_FIELD} />
          </label>
          <label className="space-y-1">
            <span className="font-semibold text-foreground">Tên hiển thị (không bắt buộc)</span>
            <input value={form.title} onChange={setField('title')} maxLength={200} placeholder="Ví dụ: Quy ước đặt tên biến của lớp" className={KB_FIELD} />
          </label>
          <label className="space-y-1">
            <span className="font-semibold text-foreground">Quyền sử dụng *</span>
            <select value={form.license_type} onChange={setField('license_type')} className={KB_FIELD}>
              <option value="">— Chọn —</option>
              <option value="own">Tự biên soạn</option>
              <option value="licensed">Được tác giả hoặc đơn vị cấp phép</option>
              <option value="open">Tài liệu mở có giấy phép</option>
            </select>
          </label>
          {form.license_type === 'open' && (
            <label className="space-y-1">
              <span className="font-semibold text-foreground">Giấy phép *</span>
              <input value={form.license_detail} onChange={setField('license_detail')} placeholder="Ví dụ: CC BY 4.0" className={KB_FIELD} />
            </label>
          )}
          <label className="space-y-1 sm:col-span-2">
            <span className="font-semibold text-foreground">Nguồn gốc * (tác giả, năm, đường dẫn nếu có)</span>
            <input value={form.provenance} onChange={setField('provenance')} maxLength={500} placeholder="Ví dụ: Nguyễn Văn A, 2026, tự biên soạn cho học phần" className={KB_FIELD} />
          </label>
        </div>
        <label className="flex min-h-9 cursor-pointer items-start gap-2 text-muted">
          <input type="checkbox" checked={form.confirm} onChange={setField('confirm')} className="mt-0.5 size-4 shrink-0 rounded border-border accent-emerald-600" />
          <span>Tôi cam kết tài liệu không chứa dữ liệu cá nhân sinh viên, đề thi hay đáp án bài tập của lớp. *</span>
        </label>
        <button type="submit" disabled={busy} className="inline-flex min-h-10 items-center gap-2 rounded-xl bg-emerald-600 px-4 text-xs font-semibold text-white transition-colors hover:bg-emerald-700 disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 shadow-soft cursor-pointer">
          <Upload aria-hidden="true" className="size-4" /> {busy ? 'Đang tải lên...' : 'Tải tài liệu lên'}
        </button>
        {message && (
          <div role={message.tone === 'error' ? 'alert' : 'status'} className={`rounded-xl border p-3 ${message.tone === 'error' ? 'border-rose-500/30 bg-rose-500/10 text-rose-600 dark:text-rose-300' : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'}`}>
            <p>{message.text}</p>
            {message.warnings?.length > 0 && (
              <ul className="mt-1 list-disc pl-4 text-amber-700 dark:text-amber-300">{message.warnings.map((w) => <li key={w}>{w}</li>)}</ul>
            )}
          </div>
        )}
      </form>

      {isLoading && !data ? (
        <TableLoading label="Đang tải danh sách tài liệu" />
      ) : error ? (
        <PanelError message={error} onRetry={reload} />
      ) : documents.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-6 text-center text-xs text-muted">Lớp này chưa có tài liệu riêng. Gia sư AI chỉ dùng tài liệu chung của hệ thống.</div>
      ) : (
        <ul className="divide-y divide-border rounded-xl border border-border">
          {documents.map((doc) => (
            <li key={doc.id} className={`space-y-1.5 p-3.5 ${doc.is_active ? '' : 'opacity-60'}`}>
              <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <p className="break-words text-xs font-semibold text-foreground">{doc.title}</p>
                  <p className="font-mono text-[11px] text-muted">{doc.filename} · {doc.chunk_count} đoạn · {Number(doc.char_count).toLocaleString('vi-VN')} ký tự</p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <button type="button" onClick={() => toggle(doc)} aria-pressed={doc.is_active} className="min-h-9 rounded-xl border border-border bg-surface px-3 text-xs font-semibold text-foreground transition-colors hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer shadow-soft">
                    {doc.is_active ? 'Đang bật' : 'Đang tắt'}
                  </button>
                  <button type="button" onClick={() => remove(doc)} aria-label={`Xóa tài liệu ${doc.title}`} title="Xóa tài liệu" className="inline-flex size-9 items-center justify-center rounded-xl border border-rose-500/40 text-rose-500 dark:text-rose-300 transition-colors hover:bg-rose-500/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-400 cursor-pointer">
                    <Trash2 aria-hidden="true" className="size-4" />
                  </button>
                </div>
              </div>
              <p className="text-[11px] leading-relaxed text-muted"><span className="font-semibold text-foreground">Nguồn gốc:</span> {doc.provenance}</p>
              {doc.sections?.length > 0 && <p className="text-[11px] leading-relaxed text-muted"><span className="font-semibold text-foreground">Các mục:</span> {doc.sections.join(' · ')}</p>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

const EMPTY_GLOBAL_FORM = { title: '', license_type: '', license_detail: '', provenance: '', confirm: false };

/** Form dùng chung cho "Thêm" và "Sửa" tài liệu chung. Khi sửa, tệp là tùy chọn (không chọn = giữ nội dung cũ). */
function GlobalDocForm({ mode, doc, limits, onDone, onCancel }) {
  const editing = mode === 'edit';
  const [file, setFile] = useState(null);
  const [form, setForm] = useState(editing
    ? { title: doc.title, license_type: doc.license_type, license_detail: '', provenance: doc.provenance, confirm: false }
    : EMPTY_GLOBAL_FORM);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null);
  const fileInputRef = useRef(null);
  const setField = (key) => (event) => setForm((prev) => ({ ...prev, [key]: event.target.type === 'checkbox' ? event.target.checked : event.target.value }));

  const submit = async (event) => {
    event.preventDefault();
    if (!editing && !file) { setMessage({ tone: 'error', text: 'Hãy chọn một tệp tài liệu.' }); return; }
    const body = new FormData();
    if (file) body.append('file', file);
    body.append('title', form.title);
    body.append('license_type', form.license_type);
    body.append('license_detail', form.license_detail);
    body.append('provenance', form.provenance);
    body.append('no_personal_data', form.confirm ? 'true' : 'false');
    setBusy(true); setMessage(null);
    try {
      const res = editing ? await updateGlobalKnowledge(doc.id, body) : await uploadGlobalKnowledge(body);
      onDone(res);
      if (!editing) {
        setFile(null); setForm(EMPTY_GLOBAL_FORM);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setMessage({ tone: 'error', text: typeof detail === 'string' ? detail : 'Không lưu được. Kiểm tra kết nối rồi thử lại.' });
    } finally { setBusy(false); }
  };

  return (
    <form onSubmit={submit} className="space-y-3 text-xs" aria-busy={busy}>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="space-y-1">
          <span className="font-semibold text-foreground">{editing ? 'Thay nội dung bằng tệp mới (không bắt buộc)' : 'Tệp tài liệu *'}</span>
          <input ref={fileInputRef} type="file" accept=".md,.txt,.pdf,.docx" onChange={(e) => setFile(e.target.files?.[0] || null)} className={KB_FIELD} />
        </label>
        <label className="space-y-1">
          <span className="font-semibold text-foreground">Tên hiển thị{editing ? ' *' : ' (không bắt buộc)'}</span>
          <input value={form.title} onChange={setField('title')} maxLength={200} placeholder="Ví dụ: Quy ước đặt tên biến" className={KB_FIELD} />
        </label>
        <label className="space-y-1">
          <span className="font-semibold text-foreground">Quyền sử dụng *</span>
          <select value={form.license_type} onChange={setField('license_type')} className={KB_FIELD}>
            <option value="">— Chọn —</option>
            <option value="own">Tự biên soạn</option>
            <option value="licensed">Được tác giả hoặc đơn vị cấp phép</option>
            <option value="open">Tài liệu mở có giấy phép</option>
          </select>
        </label>
        {!editing && form.license_type === 'open' && (
          <label className="space-y-1">
            <span className="font-semibold text-foreground">Giấy phép *</span>
            <input value={form.license_detail} onChange={setField('license_detail')} placeholder="Ví dụ: CC BY 4.0" className={KB_FIELD} />
          </label>
        )}
        <label className="space-y-1 sm:col-span-2">
          <span className="font-semibold text-foreground">Nguồn gốc * (tác giả, năm, đường dẫn nếu có)</span>
          <input value={form.provenance} onChange={setField('provenance')} maxLength={editing ? 700 : 500} placeholder="Ví dụ: Nguyễn Văn A, 2026, tự biên soạn" className={KB_FIELD} />
        </label>
      </div>
      {(!editing || file) && (
        <label className="flex min-h-9 cursor-pointer items-start gap-2 text-muted">
          <input type="checkbox" checked={form.confirm} onChange={setField('confirm')} className="mt-0.5 size-4 shrink-0 rounded border-border accent-emerald-600" />
          <span>Tôi cam kết tài liệu không chứa dữ liệu cá nhân sinh viên, đề thi hay đáp án bài tập của lớp. *</span>
        </label>
      )}
      <div className="flex flex-wrap items-center gap-2">
        <button type="submit" disabled={busy} className="inline-flex min-h-10 items-center gap-2 rounded-xl bg-emerald-600 px-4 text-xs font-semibold text-white transition-colors hover:bg-emerald-700 disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 shadow-soft cursor-pointer">
          {editing ? null : <Upload aria-hidden="true" className="size-4" />}
          {busy ? 'Đang lưu...' : editing ? 'Lưu thay đổi' : 'Thêm tài liệu chung'}
        </button>
        {editing && (
          <button type="button" onClick={onCancel} className="min-h-10 rounded-xl border border-border bg-surface px-4 text-xs font-semibold text-foreground transition-colors hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer">Hủy</button>
        )}
        <span className="text-[11px] text-muted">Định dạng {limits.formats.join(', ')} · tối đa {limits.max_file_mb} MB · tối đa {limits.max_documents} tài liệu chung. Chỉ văn bản trích ra được lưu.</span>
      </div>
      {message && (
        <div role="alert" className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-rose-600 dark:text-rose-300">{message.text}</div>
      )}
    </form>
  );
}

export function KnowledgeBasePanel() {
  const { data, isLoading, error, reload } = useRemoteData(() => fetchKnowledgeBaseCatalogue(), []);
  const systemDocs = data?.documents || [];
  const uploaded = data?.uploaded_documents || [];
  const limits = data?.limits || { max_documents: 20, max_file_mb: 5, formats: ['.md', '.txt', '.pdf', '.docx'] };
  const [editingId, setEditingId] = useState(null);
  const [message, setMessage] = useState(null); // {tone, text, warnings}

  const fail = (err, fallback) => {
    const detail = err?.response?.data?.detail;
    setMessage({ tone: 'error', text: typeof detail === 'string' ? detail : fallback });
  };
  const toggleSystem = async (doc) => {
    try { await toggleSystemKnowledge(doc.path, !doc.is_active); setMessage(null); reload(); }
    catch (err) { fail(err, 'Không đổi được trạng thái tài liệu hệ thống.'); }
  };
  const toggleUploaded = async (doc) => {
    try { await toggleGlobalKnowledge(doc.id, !doc.is_active); setMessage(null); reload(); }
    catch (err) { fail(err, 'Không đổi được trạng thái tài liệu.'); }
  };
  const removeUploaded = async (doc) => {
    if (!window.confirm(`Xóa tài liệu chung "${doc.title}"? Gia sư AI của mọi lớp sẽ không dùng tài liệu này nữa và không thể hoàn tác.`)) return;
    try { await deleteGlobalKnowledge(doc.id); setMessage(null); reload(); }
    catch (err) { fail(err, 'Không xóa được tài liệu.'); }
  };
  const afterSave = (res, verb) => {
    setMessage({ tone: 'ok', text: `Đã ${verb} "${res.document.title}" (${res.document.chunk_count} đoạn). Gia sư AI của mọi lớp dùng được ngay.`, warnings: res.warnings });
    setEditingId(null);
    reload();
  };
  const toggleBtn = 'min-h-9 rounded-xl border border-border bg-surface px-3 text-xs font-semibold text-foreground transition-colors hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer shadow-soft';

  return (
    <section aria-label="Nguồn kiến thức của Gia sư AI" className="space-y-3 rounded-2xl border border-border bg-surface p-4 sm:p-5 shadow-soft">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="flex items-center gap-2 text-sm font-bold text-foreground"><BookOpen aria-hidden="true" className="size-4 text-emerald-500" /> Nguồn kiến thức chung của Gia sư AI</h3>
          <p className="mt-1 text-xs text-muted">Tài liệu chung áp dụng cho mọi lớp; khung trò chuyện dùng để trích nguồn khi trả lời sinh viên.</p>
        </div>
        <RefreshButton onClick={reload} busy={isLoading} label="Tải lại danh mục tài liệu" />
      </div>

      {isLoading && !data ? (
        <TableLoading label="Đang tải danh mục tài liệu" />
      ) : error ? (
        <PanelError message={error} onRetry={reload} />
      ) : data ? (
        <div className="space-y-3">
          <p className="flex items-start gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-xs leading-relaxed text-amber-700 dark:text-amber-300">
            <Info aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
            {data.notice}
          </p>
          <p className="text-xs text-muted">
            <strong className="font-mono tabular-nums text-foreground">{data.active_documents ?? data.total_documents}</strong> tài liệu đang bật · <strong className="font-mono tabular-nums text-foreground">{data.total_chunks}</strong> đoạn trong tài liệu hệ thống
            {data.retrieval && <> · truy xuất: {data.retrieval.method}, lấy tối đa {data.retrieval.top_k} đoạn, ngưỡng liên quan tối thiểu {data.retrieval.min_relevance}</>}
          </p>

          {message && (
            <div role={message.tone === 'error' ? 'alert' : 'status'} className={`rounded-xl border p-3 text-xs ${message.tone === 'error' ? 'border-rose-500/30 bg-rose-500/10 text-rose-600 dark:text-rose-300' : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300'}`}>
              <p>{message.text}</p>
              {message.warnings?.length > 0 && <ul className="mt-1 list-disc pl-4 text-amber-700 dark:text-amber-300">{message.warnings.map((w) => <li key={w}>{w}</li>)}</ul>}
            </div>
          )}

          <h4 className="text-xs font-bold text-foreground">Tài liệu hệ thống <span className="font-normal text-muted">(chỉ tắt/bật, không sửa nội dung)</span></h4>
          {systemDocs.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border p-6 text-center text-xs text-muted">
              Chưa có tài liệu nào trong thư mục kiến thức.
            </div>
          ) : (
            <ul className="divide-y divide-border rounded-xl border border-border">
              {systemDocs.map((doc) => (
                <li key={doc.path} className={`p-3.5 ${doc.is_active ? '' : 'opacity-60'}`}>
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div className="min-w-0">
                      <span className="text-xs font-semibold text-foreground">{doc.title}</span>
                      <p className="font-mono text-[11px] text-muted">{doc.path} · {doc.chunk_count} đoạn · {Number(doc.char_count || 0).toLocaleString('vi-VN')} ký tự</p>
                    </div>
                    <button type="button" onClick={() => toggleSystem(doc)} aria-pressed={doc.is_active} className={`${toggleBtn} shrink-0`}>
                      {doc.is_active ? 'Đang bật' : 'Đang tắt'}
                    </button>
                  </div>
                  <p className="mt-1 text-[11px] leading-relaxed text-muted"><span className="font-semibold text-foreground">Nguồn gốc:</span> {doc.provenance}</p>
                  {doc.sections?.length > 0 && (
                    <details className="mt-2 text-xs text-muted">
                      <summary className="cursor-pointer rounded font-semibold text-emerald-600 dark:text-emerald-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400">
                        {doc.sections.length} mục có thể được trích dẫn
                      </summary>
                      <ul className="mt-2 grid list-disc gap-x-6 gap-y-1 pl-4 sm:grid-cols-2">
                        {doc.sections.map((section) => <li key={section}>{section}</li>)}
                      </ul>
                    </details>
                  )}
                </li>
              ))}
            </ul>
          )}

          <h4 className="pt-1 text-xs font-bold text-foreground">Tài liệu do giảng viên thêm <span className="font-normal text-muted">(chỉ người thêm sửa, tắt hoặc xóa được)</span></h4>
          {uploaded.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border p-5 text-center text-xs text-muted">Chưa có tài liệu chung nào do giảng viên thêm.</div>
          ) : (
            <ul className="divide-y divide-border rounded-xl border border-border">
              {uploaded.map((doc) => (
                <li key={doc.id} className={`space-y-1.5 p-3.5 ${doc.is_active ? '' : 'opacity-60'}`}>
                  {editingId === doc.id ? (
                    <GlobalDocForm mode="edit" doc={doc} limits={limits} onDone={(res) => afterSave(res, 'lưu')} onCancel={() => setEditingId(null)} />
                  ) : (
                    <>
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                        <div className="min-w-0">
                          <p className="break-words text-xs font-semibold text-foreground">{doc.title}</p>
                          <p className="font-mono text-[11px] text-muted">{doc.filename} · {doc.chunk_count} đoạn · {Number(doc.char_count).toLocaleString('vi-VN')} ký tự · thêm bởi {doc.can_edit ? 'bạn' : doc.uploaded_by}</p>
                        </div>
                        {doc.can_edit ? (
                          <div className="flex shrink-0 items-center gap-2">
                            <button type="button" onClick={() => toggleUploaded(doc)} aria-pressed={doc.is_active} className={toggleBtn}>
                              {doc.is_active ? 'Đang bật' : 'Đang tắt'}
                            </button>
                            <button type="button" onClick={() => { setEditingId(doc.id); setMessage(null); }} aria-label={`Sửa tài liệu ${doc.title}`} title="Sửa tài liệu" className="inline-flex size-9 items-center justify-center rounded-xl border border-border text-foreground transition-colors hover:bg-surface-raised focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 cursor-pointer">
                              <Pencil aria-hidden="true" className="size-4" />
                            </button>
                            <button type="button" onClick={() => removeUploaded(doc)} aria-label={`Xóa tài liệu ${doc.title}`} title="Xóa tài liệu" className="inline-flex size-9 items-center justify-center rounded-xl border border-rose-500/40 text-rose-500 dark:text-rose-300 transition-colors hover:bg-rose-500/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-400 cursor-pointer">
                              <Trash2 aria-hidden="true" className="size-4" />
                            </button>
                          </div>
                        ) : (
                          <span className="shrink-0 rounded-full border border-border px-2.5 py-1 text-[11px] text-muted">{doc.is_active ? 'Đang bật' : 'Đang tắt'} · chỉ xem</span>
                        )}
                      </div>
                      <p className="text-[11px] leading-relaxed text-muted"><span className="font-semibold text-foreground">Nguồn gốc:</span> {doc.provenance}</p>
                      {doc.sections?.length > 0 && <p className="text-[11px] leading-relaxed text-muted"><span className="font-semibold text-foreground">Các mục:</span> {doc.sections.join(' · ')}</p>}
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}

          <details className="rounded-xl border border-border bg-surface-raised p-3.5">
            <summary className="cursor-pointer rounded text-xs font-semibold text-emerald-600 dark:text-emerald-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400">Thêm tài liệu chung mới</summary>
            <div className="mt-3">
              <GlobalDocForm mode="create" limits={limits} onDone={(res) => afterSave(res, 'thêm')} />
            </div>
          </details>
        </div>
      ) : null}
    </section>
  );
}
