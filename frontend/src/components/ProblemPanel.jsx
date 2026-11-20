import React from 'react';
import { Badge } from './ui';
import { difficultyVariant } from '../utils/tone';
import { BookOpen, Tag, Award, CheckCircle, Code2, ListOrdered, School, GraduationCap, ShieldAlert, Sparkles } from 'lucide-react';

export default function ProblemPanel({
  exercises,
  selectedExerciseId,
  onSelectExercise,
  exerciseDetail,
  isLoading,
  currentClass,
  examSessions = [],
  selectedSessionId = '',
  onSelectSession = () => {},
  isExamMode = false
}) {
  const activeExamSession = examSessions.find(s => s.id === selectedSessionId) || null;
  return (
    <div className="flex h-full select-text flex-col overflow-hidden border-r border-border bg-surface text-foreground">
      {/* Header: lớp, chế độ làm bài, độ khó */}
      <div className="shrink-0 space-y-2 border-b border-border bg-surface-raised/60 p-3">
        {currentClass && (
          <div className="flex items-center justify-between gap-2 rounded-2xl border border-sky-500/20 bg-sky-500/10 px-3.5 py-2 text-xs font-semibold text-sky-600 dark:text-sky-400">
            <span className="flex min-w-0 items-center gap-2">
              <School aria-hidden="true" className="size-4 shrink-0" />
              <span className="truncate">
                <span className="font-mono">{currentClass.class_code}</span>
                {currentClass.class_name && <span className="ml-1.5 hidden font-normal sm:inline">· {currentClass.class_name}</span>}
              </span>
            </span>
            {currentClass.semester && (
              <span className="shrink-0 rounded-full bg-sky-500 px-2 py-0.5 font-mono text-[10px] text-white font-semibold">{currentClass.semester}</span>
            )}
          </div>
        )}

        {activeExamSession ? (
          <div className="flex items-center justify-between gap-2 rounded-2xl border border-amber-500/20 bg-amber-500/10 px-3.5 py-2 text-xs font-semibold text-amber-600 dark:text-amber-400">
            <span className="flex min-w-0 items-center gap-2">
              <GraduationCap aria-hidden="true" className="size-4 shrink-0" />
              <span className="truncate">{activeExamSession.session_type === 'EXAM' ? 'Kỳ thi' : 'Đợt thực hành'}: {activeExamSession.title}</span>
            </span>
            <span className="shrink-0 rounded-full bg-amber-500 px-2 py-0.5 font-mono text-[10px] text-white font-semibold">{activeExamSession.session_type}</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-3.5 py-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
            <Sparkles aria-hidden="true" className="size-4 shrink-0" />
            Chế độ luyện tập thích ứng
          </div>
        )}

        {exerciseDetail && (
          <p className="flex flex-wrap items-center gap-1.5">
            <Badge variant={difficultyVariant(exerciseDetail.difficulty)}>{exerciseDetail.difficulty}</Badge>
            <Badge variant="info"><Tag aria-hidden="true" className="size-3" />{exerciseDetail.category}</Badge>
            <Badge variant="ai">{exerciseDetail.test_cases?.length || 0} test cases</Badge>
          </p>
        )}
      </div>

      {/* Body: Problem Description & Instructions */}
      <div className="min-h-0 flex-1 space-y-5 overflow-y-auto p-4 text-sm leading-6">
        {isLoading ? (
          <div className="space-y-4 py-2" role="status" aria-label="Đang tải đề bài">
            <span className="block h-6 w-3/4 animate-pulse rounded bg-surface-raised" />
            <span className="block h-3 w-full animate-pulse rounded bg-surface-raised" />
            <span className="block h-3 w-5/6 animate-pulse rounded bg-surface-raised" />
            <span className="block h-3 w-2/3 animate-pulse rounded bg-surface-raised" />
          </div>
        ) : exerciseDetail ? (
          <>
            <div>
              <h2 className="mb-3 text-xl font-semibold leading-snug text-foreground">{exerciseDetail.title}</h2>
              <div className="max-w-none space-y-3 text-foreground">
                {/* Parse Markdown-like sections cleanly */}
                {renderFormattedContent(exerciseDetail.description)}
              </div>
            </div>

            {/* Test Cases Preview */}
            {exerciseDetail.test_cases && exerciseDetail.test_cases.length > 0 && (
              <div className="mt-4 border-t border-border pt-4">
                <h3 className="mb-2.5 flex items-center gap-1.5 text-base font-semibold">
                  <ListOrdered aria-hidden="true" className="size-4 text-muted" />
                  Ví dụ kiểm thử mẫu
                </h3>
                <div className="space-y-2">
                  {exerciseDetail.test_cases.slice(0, 3).map((tc, idx) => (
                    <div key={idx} className="rounded-2xl border border-border/80 bg-surface-raised p-3 text-xs font-mono shadow-soft">
                      <div className="mb-1.5 font-sans text-xs font-semibold text-muted">
                        {tc.description || `Ví dụ #${idx + 1}`}
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="min-w-0">
                          <span className="font-sans text-[11px] text-muted">Đầu vào</span>
                          <div className="overflow-x-auto whitespace-pre-wrap break-words rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2.5 py-1.5 text-xs font-semibold border border-emerald-500/20">{tc.input.trim() || '""'}</div>
                        </div>
                        <div className="min-w-0">
                          <span className="font-sans text-[11px] text-muted">Kết quả mong đợi</span>
                          <div className="overflow-x-auto whitespace-pre-wrap break-words rounded-xl bg-sky-500/10 text-sky-600 dark:text-sky-400 px-2.5 py-1.5 text-xs font-semibold border border-sky-500/20">{tc.expected_output.trim()}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {exerciseDetail.test_cases.length > 3 && (
                    <p className="text-center text-[0.8125rem] text-muted">
                      + {exerciseDetail.test_cases.length - 3} trường hợp kiểm thử kiểm tra toàn diện khác...
                    </p>
                  )}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="py-10 text-center text-muted">Không tìm thấy thông tin bài tập.</div>
        )}
      </div>
    </div>
  );
}

function renderFormattedContent(text) {
  if (!text) return null;

  const lines = text.split('\n');
  const elements = [];
  let inTable = false;
  let tableRows = [];

  lines.forEach((line, i) => {
    const trimmed = line.trim();

    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      inTable = true;
      if (!trimmed.includes('---')) {
        const cells = trimmed
          .split('|')
          .slice(1, -1)
          .map((c) => c.trim());
        tableRows.push(cells);
      }
      return;
    } else if (inTable) {
      if (tableRows.length > 0) {
        elements.push(
          <div key={`tbl-${i}`} className="my-2.5 overflow-x-auto rounded border border-primary-line">
            <table className="min-w-full text-xs font-mono text-left">
              <thead className="border-b border-primary-line bg-primary-soft text-primary-strong">
                <tr>
                  {tableRows[0].map((th, thIdx) => (
                    <th key={thIdx} className="px-3 py-1.5 font-semibold">
                      {th}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-surface">
                {tableRows.slice(1).map((row, rIdx) => (
                  <tr key={rIdx}>
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-3 py-1.5 text-foreground">
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      inTable = false;
      tableRows = [];
    }

    if (trimmed.startsWith('### ')) {
      elements.push(
        <h3 key={i} className="mb-1 mt-4 text-base font-bold text-primary-strong">
          {trimmed.replace('### ', '')}
        </h3>
      );
    } else if (trimmed.startsWith('- ')) {
      elements.push(
        <div key={i} className="ml-1 flex items-start gap-2 text-sm leading-6 text-foreground">
          <span aria-hidden="true" className="text-muted">•</span>
          <span>{trimmed.replace('- ', '')}</span>
        </div>
      );
    } else if (trimmed === '') {
      // Empty line
    } else {
      elements.push(
        <p key={i} className="text-sm leading-6 text-foreground">
          {trimmed}
        </p>
      );
    }
  });

  // Flush table nếu bảng nằm ở cuối cùng của đề bài
  if (inTable && tableRows.length > 0) {
    elements.push(
      <div key="tbl-end" className="my-2.5 overflow-x-auto rounded border border-primary-line">
        <table className="min-w-full text-xs font-mono text-left">
          <thead className="border-b border-primary-line bg-primary-soft text-primary-strong">
            <tr>
              {tableRows[0].map((th, thIdx) => (
                <th key={thIdx} className="px-3 py-1.5 font-semibold">
                  {th}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border bg-surface">
            {tableRows.slice(1).map((row, rIdx) => (
              <tr key={rIdx}>
                {row.map((cell, cIdx) => (
                  <td key={cIdx} className="px-3 py-1.5 text-foreground">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return elements;
}
