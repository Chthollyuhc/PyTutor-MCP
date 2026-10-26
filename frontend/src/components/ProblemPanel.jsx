import React from 'react';
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
  const getDifficultyColor = (diff) => {
    switch (diff) {
      case 'Dễ':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'Trung bình':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'Khó':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      default:
        return 'bg-slate-700/50 text-slate-300 border-slate-600';
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-900 border-r border-slate-800 text-slate-200 select-text overflow-hidden">
      {/* Header & Classroom / Session Context (Vị trí duy nhất hiển thị Lớp học phần) */}
      <div className="p-3 border-b border-slate-800 shrink-0 bg-slate-900/90 space-y-2">
        {/* Class Badge */}
        {currentClass && (
          <div className="flex items-center justify-between bg-slate-950/70 border border-slate-800 px-2.5 py-1.5 rounded-lg text-xs">
            <div className="flex items-center space-x-1.5 truncate">
              <School className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span className="font-semibold text-slate-300 truncate">
                Lớp: <span className="text-cyan-400 font-mono">{currentClass.class_code}</span>
                {currentClass.class_name && (
                  <span className="text-slate-400 font-normal text-[11px] ml-1.5 hidden sm:inline">
                    • {currentClass.class_name}
                  </span>
                )}
              </span>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 font-mono shrink-0 ml-1 border border-cyan-800/40">
              {currentClass.semester}
            </span>
          </div>
        )}

        {/* Chế độ làm bài Indicator (Static context badge) */}
        {activeExamSession ? (
          <div className="flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-xs">
            <span className="flex items-center space-x-1.5 text-amber-300 font-medium truncate">
              <GraduationCap className="w-3.5 h-3.5 shrink-0" />
              <span className="truncate">
                {activeExamSession.session_type === 'EXAM' ? '📝 Kỳ thi:' : '🎓 Đợt thực hành:'} {activeExamSession.title}
              </span>
            </span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono shrink-0 ml-1">
              {activeExamSession.session_type}
            </span>
          </div>
        ) : (
          <div className="flex items-center justify-between px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400">
            <span className="flex items-center space-x-1.5 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              <span>Chế độ Luyện tập Thích ứng</span>
            </span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 font-mono">
              PRACTICE
            </span>
          </div>
        )}

        {/* Metadata Bài tập (Độ khó, Chủ đề, Test cases) */}
        {exerciseDetail && (
          <div className="flex items-center space-x-1.5 pt-0.5 flex-wrap gap-y-1 text-xs">
            <span className={`px-2 py-0.5 rounded-full border text-[10px] font-medium ${getDifficultyColor(exerciseDetail.difficulty)}`}>
              {exerciseDetail.difficulty}
            </span>
            <span className="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-[10px] flex items-center space-x-1">
              <Tag className="w-2.5 h-2.5 text-slate-400" />
              <span>{exerciseDetail.category}</span>
            </span>
            <span className="px-2 py-0.5 rounded-full bg-slate-800/60 text-slate-400 text-[10px]">
              {exerciseDetail.test_cases?.length || 0} Test cases
            </span>
          </div>
        )}
      </div>

      {/* Body: Problem Description & Instructions */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 text-sm leading-relaxed">
        {isLoading ? (
          <div className="h-40 flex items-center justify-center text-slate-500 text-xs">
            <span className="animate-pulse">Đang tải đề bài từ MCP Server...</span>
          </div>
        ) : exerciseDetail ? (
          <>
            <div>
              <h2 className="text-lg font-bold text-white mb-2">{exerciseDetail.title}</h2>
              <div className="prose prose-invert prose-sm max-w-none text-slate-300 space-y-3">
                {/* Parse Markdown-like sections cleanly */}
                {renderFormattedContent(exerciseDetail.description)}
              </div>
            </div>

            {/* Test Cases Preview */}
            {exerciseDetail.test_cases && exerciseDetail.test_cases.length > 0 && (
              <div className="mt-4 pt-4 border-t border-slate-800">
                <h3 className="text-xs font-semibold text-slate-400 flex items-center space-x-1.5 mb-2.5">
                  <ListOrdered className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Ví dụ kiểm thử mẫu:</span>
                </h3>
                <div className="space-y-2">
                  {exerciseDetail.test_cases.slice(0, 3).map((tc, idx) => (
                    <div key={idx} className="bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 text-xs font-mono">
                      <div className="text-slate-400 text-[11px] mb-1 font-sans">
                        {tc.description || `Ví dụ #${idx + 1}`}
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-slate-300">
                        <div>
                          <span className="text-slate-500 text-[10px] uppercase font-sans">Đầu vào (Input):</span>
                          <div className="bg-slate-900 px-2 py-1 rounded text-emerald-400">{tc.input.trim() || '""'}</div>
                        </div>
                        <div>
                          <span className="text-slate-500 text-[10px] uppercase font-sans">Kết quả mong đợi (Output):</span>
                          <div className="bg-slate-900 px-2 py-1 rounded text-cyan-400">{tc.expected_output.trim()}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {exerciseDetail.test_cases.length > 3 && (
                    <p className="text-[11px] text-slate-500 italic text-center">
                      + {exerciseDetail.test_cases.length - 3} trường hợp kiểm thử kiểm tra toàn diện khác...
                    </p>
                  )}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-slate-500 text-center py-10">Không tìm thấy thông tin bài tập.</div>
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
          <div key={`tbl-${i}`} className="my-2.5 overflow-x-auto rounded border border-slate-800">
            <table className="min-w-full text-xs font-mono text-left">
              <thead className="bg-slate-800/80 text-slate-300 border-b border-slate-700">
                <tr>
                  {tableRows[0].map((th, thIdx) => (
                    <th key={thIdx} className="px-3 py-1.5 font-semibold">
                      {th}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-slate-950/40">
                {tableRows.slice(1).map((row, rIdx) => (
                  <tr key={rIdx}>
                    {row.map((cell, cIdx) => (
                      <td key={cIdx} className="px-3 py-1.5 text-slate-300">
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
        <h4 key={i} className="text-sm font-bold text-emerald-400 mt-3 mb-1 uppercase tracking-wide">
          {trimmed.replace('### ', '')}
        </h4>
      );
    } else if (trimmed.startsWith('- ')) {
      elements.push(
        <div key={i} className="ml-4 flex items-start space-x-2 text-slate-300 text-xs leading-relaxed">
          <span className="text-emerald-400 font-bold">•</span>
          <span>{trimmed.replace('- ', '')}</span>
        </div>
      );
    } else if (trimmed === '') {
      // Empty line
    } else {
      elements.push(
        <p key={i} className="text-xs text-slate-300 leading-relaxed">
          {trimmed}
        </p>
      );
    }
  });

  // Flush table nếu bảng nằm ở cuối cùng của đề bài
  if (inTable && tableRows.length > 0) {
    elements.push(
      <div key="tbl-end" className="my-2.5 overflow-x-auto rounded border border-slate-800">
        <table className="min-w-full text-xs font-mono text-left">
          <thead className="bg-slate-800/80 text-slate-300 border-b border-slate-700">
            <tr>
              {tableRows[0].map((th, thIdx) => (
                <th key={thIdx} className="px-3 py-1.5 font-semibold">
                  {th}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 bg-slate-950/40">
            {tableRows.slice(1).map((row, rIdx) => (
              <tr key={rIdx}>
                {row.map((cell, cIdx) => (
                  <td key={cIdx} className="px-3 py-1.5 text-slate-300">
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
