import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { Play, RotateCcw, CheckCircle2, XCircle, Clock, AlertTriangle, Terminal, ChevronDown, ChevronUp, Sparkles, Send, FileCode, Eye } from 'lucide-react';
import { runCustomInput } from '../services/api';

export function parseErrorLine(errorMessage) {
  if (!errorMessage) return null;
  // Mẫu 1: SyntaxError line x
  const syntaxMatch = errorMessage.match(/line\s+(\d+)/i);
  if (syntaxMatch) return parseInt(syntaxMatch[1], 10);
  // Mẫu 2: Traceback File "solution.py", line x
  const tbMatch = errorMessage.match(/File\s+["'][^"']+["'],\s+line\s+(\d+)/i);
  if (tbMatch) return parseInt(tbMatch[1], 10);
  return null;
}

// Giao diện code riêng: nền và màu cú pháp cùng họ màu với giao diện (tím = từ khóa, xanh ngọc = chuỗi, cam = số).
function defineEditorThemes(monaco) {
  monaco.editor.defineTheme('pytutor-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'keyword', foreground: 'C4B5FD', fontStyle: 'bold' },
      { token: 'string', foreground: '6EE7B7' },
      { token: 'number', foreground: 'FDBA74' },
      { token: 'comment', foreground: '7F9CC4', fontStyle: 'italic' },
      { token: 'type', foreground: '67E8F9' },
      { token: 'identifier', foreground: 'E6EEF8' },
      { token: 'delimiter', foreground: '93C5FD' },
    ],
    colors: {
      'editor.background': '#071328',
      'editor.foreground': '#E6EEF8',
      'editorGutter.background': '#071328',
      'editorLineNumber.foreground': '#5B7BA6',
      'editorLineNumber.activeForeground': '#93C5FD',
      'editor.lineHighlightBackground': '#0F2547',
      'editorCursor.foreground': '#34D399',
      'editor.selectionBackground': '#1D4ED866',
      'editorIndentGuide.background1': '#16315A',
    },
  });
  monaco.editor.defineTheme('pytutor-light', {
    base: 'vs',
    inherit: true,
    rules: [
      { token: 'keyword', foreground: '6D28D9', fontStyle: 'bold' },
      { token: 'string', foreground: '047857' },
      { token: 'number', foreground: 'C2410C' },
      { token: 'comment', foreground: '4E7A65', fontStyle: 'italic' },
      { token: 'type', foreground: '0E7490' },
    ],
    colors: {
      'editor.background': '#FFFFFF',
      'editorGutter.background': '#F3FAF6',
      'editorLineNumber.foreground': '#5E8A75',
      'editorLineNumber.activeForeground': '#047857',
      'editor.lineHighlightBackground': '#ECF7F1',
      'editorCursor.foreground': '#047857',
      'editor.selectionBackground': '#A7F3D0AA',
    },
  });
}

export default function EditorPanel({
  code,
  setCode,
  exerciseId,
  onResetCode,
  onRunTest,
  isRunningTest,
  onAskAI,
  askAiLabel = 'Hỏi gia sư AI',
  isAskingAI,
  onSubmit,
  isSubmitting,
  testResults,
  isDarkTheme,
  onOpenVisualizer,
  isExamMode = false,
}) {
  const [selectedTestCaseIdx, setSelectedTestCaseIdx] = useState(null);
  const [activeBottomTab, setActiveBottomTab] = useState('tests'); // 'tests' | 'custom'
  const [customInput, setCustomInput] = useState('');
  const [customResult, setCustomResult] = useState(null);
  const [isRunningCustom, setIsRunningCustom] = useState(false);

  const isBusy = isSubmitting || isRunningTest || isAskingAI || isRunningCustom;
  const prefersReducedMotion = typeof window !== 'undefined'
    && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const onRunTestRef = useRef(onRunTest);
  const onSubmitRef = useRef(onSubmit);
  const isBusyRef = useRef(isBusy);

  const editorRef = useRef(null);
  const monacoRef = useRef(null);
  const decorationsRef = useRef([]);

  useEffect(() => {
    onRunTestRef.current = onRunTest;
    onSubmitRef.current = onSubmit;
    isBusyRef.current = isBusy;
  }, [onRunTest, onSubmit, isBusy]);

  // Thiết lập phím tắt toàn cục cho màn hình IDE
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        if (isBusyRef.current) return;

        if (e.shiftKey) {
          if (onSubmitRef.current) onSubmitRef.current();
        } else {
          if (onRunTestRef.current) onRunTestRef.current();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // 1. Ngăn chặn sự kiện Space bị nuốt hoặc bubbling ra ngoài container
    editor.onKeyDown((e) => {
      if (e.keyCode === monaco.KeyCode.Space || e.browserEvent?.key === ' ' || e.browserEvent?.code === 'Space') {
        e.stopPropagation();
      }
    });

    // 2. Bảo đảm cưỡng chế chèn dấu cách khi bấm Space (chống lỗi nuốt phím từ IME hoặc browser)
    editor.addCommand(monaco.KeyCode.Space, () => {
      editor.trigger('keyboard', 'type', { text: ' ' });
    });

    editor.addCommand(monaco.KeyMod.Shift | monaco.KeyCode.Space, () => {
      editor.trigger('keyboard', 'type', { text: ' ' });
    });

    // 3. Phím tắt chạy thử và nộp bài
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (!isBusyRef.current && onRunTestRef.current) {
        onRunTestRef.current();
      }
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter, () => {
      if (!isBusyRef.current && onSubmitRef.current) {
        onSubmitRef.current();
      }
    });
  };

  // Tự động tô đỏ dòng lỗi (Error Line Decoration) khi có kết quả test lỗi
  useEffect(() => {
    if (!editorRef.current || !monacoRef.current) return;
    const editor = editorRef.current;
    const monaco = monacoRef.current;

    if (!testResults || testResults.all_passed) {
      decorationsRef.current = editor.deltaDecorations(decorationsRef.current, []);
      return;
    }

    // Tìm test case đầu tiên có lỗi cú pháp hoặc lỗi runtime
    const errItem = testResults.results?.find(
      r => r.status === 'SYNTAX_ERROR' || r.status === 'RUNTIME_ERROR' || r.error_message
    );

    if (errItem && errItem.error_message) {
      const lineNum = parseErrorLine(errItem.error_message);
      if (lineNum && lineNum > 0) {
        const line = Math.min(lineNum, editor.getModel()?.getLineCount() || lineNum);
        decorationsRef.current = editor.deltaDecorations(decorationsRef.current, [
          {
            range: new monaco.Range(line, 1, line, 1),
            options: {
              isWholeLine: true,
              className: 'bg-rose-500/20 border-l-4 border-rose-500',
              hoverMessage: {
                value: `⚠️ **Lỗi tại dòng ${line}:** ${errItem.error_message}`
              }
            }
          }
        ]);
        return;
      }
    }

    // Nếu không có lỗi số dòng cụ thể thì xóa decoration cũ
    decorationsRef.current = editor.deltaDecorations(decorationsRef.current, []);
  }, [testResults]);

  // Xóa cảnh báo dòng lỗi khi học viên gõ thay đổi code
  const handleEditorChange = (val) => {
    setCode(val || '');
    if (editorRef.current && decorationsRef.current.length > 0) {
      decorationsRef.current = editorRef.current.deltaDecorations(decorationsRef.current, []);
    }
  };

  // Chạy thử với dữ liệu tự chọn (Custom Input)
  const handleRunCustom = async () => {
    if (!code.trim() || isRunningCustom) return;
    setIsRunningCustom(true);
    try {
      const res = await runCustomInput({
        exercise_id: exerciseId,
        code,
        custom_input: customInput,
      });
      setCustomResult(res);
    } catch (err) {
      console.error('Lỗi khi chạy thử custom input:', err);
      setCustomResult({
        stdout: '',
        stderr: '',
        execution_time_ms: 0,
        status: 'ERROR',
        error_message: 'Không thể kết nối Backend để chạy thử.'
      });
    } finally {
      setIsRunningCustom(false);
    }
  };

  // Trạng thái kiểm thử: luôn có biểu tượng + chữ (không chỉ dựa vào màu).
  const STATUS = {
    PASS: { Icon: CheckCircle2, text: 'Đạt', tone: 'border-success-line bg-success-soft text-success-strong' },
    SUCCESS: { Icon: CheckCircle2, text: 'Đạt', tone: 'border-success-line bg-success-soft text-success-strong' },
    FAIL: { Icon: XCircle, text: 'Chưa đạt', tone: 'border-destructive-line bg-destructive-soft text-destructive-strong' },
    TIMEOUT: { Icon: Clock, text: 'Quá thời gian', tone: 'border-warning-line bg-warning-soft text-warning-strong' },
    SYNTAX_ERROR: { Icon: AlertTriangle, text: 'Lỗi cú pháp', tone: 'border-ai-line bg-ai-soft text-ai-strong' },
    RUNTIME_ERROR: { Icon: AlertTriangle, text: 'Lỗi khi chạy', tone: 'border-ai-line bg-ai-soft text-ai-strong' },
    ERROR: { Icon: AlertTriangle, text: 'Lỗi khi chạy', tone: 'border-ai-line bg-ai-soft text-ai-strong' },
    SKIPPED: { Icon: null, text: 'Bỏ qua', tone: 'border-border bg-surface-raised text-muted' },
  };
  const getStatusBadge = (status) => {
    const s = STATUS[status];
    if (!s) return <span className="text-xs text-muted">{status}</span>;
    return (
      <span className={`inline-flex shrink-0 items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${s.tone}`}>
        {s.Icon && <s.Icon aria-hidden="true" className="size-3.5" />}
        {s.text}
      </span>
    );
  };

  const Spinner = () => (
    <span aria-hidden="true" className="size-3.5 animate-spin rounded-full border-2 border-current/30 border-t-current" />
  );
  const toolBtn = 'inline-flex min-h-8 items-center gap-1.5 rounded-full px-3.5 py-1 text-xs font-semibold transition-all active:scale-95 disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer shadow-soft';
  const secondaryBtn = `${toolBtn} border border-border/80 bg-surface text-foreground hover:bg-surface-raised`;
  const runBtn = `${toolBtn} bg-slate-950 text-white hover:bg-black dark:bg-slate-800 dark:hover:bg-slate-700`;
  const aiBtn = `${toolBtn} bg-purple-600 text-white hover:bg-purple-700`;
  const stepBtn = `${toolBtn} border border-amber-500/20 bg-amber-500/10 text-amber-600 dark:text-amber-400 hover:bg-amber-500/20`;
  const kbd = 'hidden rounded-full border border-white/20 px-1.5 py-0.2 font-mono text-[10px] font-normal opacity-80 2xl:inline';
  const tabBtn = (active) => `inline-flex min-h-8 items-center gap-1.5 rounded-full px-3.5 text-xs font-semibold transition-all ${
    active ? 'bg-surface text-foreground shadow-sm' : 'text-muted hover:text-foreground'
  }`;

  return (
    <div className="flex h-full flex-col overflow-hidden border-r border-border bg-canvas">
      {/* Thanh công cụ trình soạn thảo */}
      <div className="flex min-h-12 shrink-0 select-none flex-wrap items-center justify-between gap-2 border-b border-border bg-surface-raised/60 px-3 py-1.5">
        <p className="flex shrink-0 items-center gap-2 text-sm font-bold text-foreground">
          <Terminal aria-hidden="true" className="size-4 text-emerald-600 dark:text-emerald-400" />
          Python 3
        </p>

        <div role="toolbar" aria-label="Thao tác bài tập" className="flex flex-wrap items-center justify-end gap-2">
          <button
            onClick={onResetCode}
            disabled={isBusy}
            type="button"
            aria-label="Khôi phục code gốc"
            title="Khôi phục lại code ban đầu của bài tập"
            className={`${toolBtn} text-muted hover:bg-surface-raised hover:text-foreground`}
          >
            <RotateCcw aria-hidden="true" className="size-4" />
            <span className="hidden 2xl:inline">Khôi phục</span>
          </button>

          {onOpenVisualizer && (
            <button
              onClick={onOpenVisualizer}
              disabled={isBusy}
              type="button"
              aria-label="Chạy từng bước để xem biến đổi khi thực thi"
              title="Trực quan hóa từng bước thực thi code và xem giá trị biến"
              className={stepBtn}
            >
              <Eye aria-hidden="true" className="size-4" />
              <span className="hidden sm:inline">Chạy từng bước</span>
            </button>
          )}

          <button
            onClick={onRunTest}
            disabled={isBusy}
            type="button"
            aria-label={isRunningTest ? 'Đang chạy kiểm thử' : 'Chạy thử code (Ctrl + Enter)'}
            aria-busy={isRunningTest}
            title="Chạy thử với các bộ kiểm thử mẫu (Ctrl + Enter)"
            className={runBtn}
          >
            {isRunningTest ? <Spinner /> : <Play aria-hidden="true" className="size-4" />}
            <span>{isRunningTest ? 'Đang chạy…' : 'Chạy thử'}</span>
            <kbd aria-hidden="true" className={kbd}>Ctrl ↵</kbd>
          </button>

          {!isExamMode && onAskAI && (
            <button
              onClick={onAskAI}
              disabled={isBusy}
              type="button"
              aria-label={isAskingAI ? 'Đang nhận gợi ý từ gia sư AI' : askAiLabel}
              aria-busy={isAskingAI}
              title="Phân tích code và nhận gợi ý ở cột Gia sư AI"
              className={aiBtn}
            >
              {isAskingAI ? <Spinner /> : <Sparkles aria-hidden="true" className="size-4" />}
              <span>{isAskingAI ? 'Đang hỏi…' : askAiLabel}</span>
            </button>
          )}

          <button
            onClick={onSubmit}
            disabled={isBusy}
            type="button"
            aria-label={isSubmitting ? 'Đang chấm và ghi nhận bài nộp' : 'Nộp bài chính thức (Ctrl + Shift + Enter)'}
            aria-busy={isSubmitting}
            title="Nộp bài chính thức: chấm điểm, ghi nhận sao tự làm và mở khóa bài tiếp theo (Ctrl + Shift + Enter)"
            className={`${toolBtn} bg-emerald-500 hover:bg-emerald-600 text-white shadow-soft`}
          >
            {isSubmitting ? <Spinner /> : <Send aria-hidden="true" className="size-4" />}
            <span>{isSubmitting ? 'Đang chấm…' : 'Nộp bài'}</span>
            <kbd aria-hidden="true" className={kbd}>Ctrl ⇧ ↵</kbd>
          </button>
        </div>
      </div>

      {/* Trình soạn thảo Monaco */}
      <div className="relative min-h-[220px] flex-1 bg-canvas">
        <Editor
          height="100%"
          language="python"
          theme={isDarkTheme ? 'pytutor-dark' : 'pytutor-light'}
          beforeMount={defineEditorThemes}
          value={code}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          options={{
            fontSize: 14,
            lineNumbers: 'on',
            minimap: { enabled: false },
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            scrollBeyondLastLine: false,
            fontFamily: 'Consolas, "Fira Code", monospace',
            cursorBlinking: prefersReducedMotion ? 'solid' : 'smooth',
            smoothScrolling: !prefersReducedMotion,
            roundedSelection: true,
            padding: { top: 8, bottom: 8 },
            ariaLabel: 'Trình soạn thảo code Python. Ctrl+Enter để chạy thử, Ctrl+Shift+Enter để nộp bài. Nhấn Ctrl+M rồi Tab để rời khỏi trình soạn thảo.',
            acceptSuggestionOnCommitCharacter: false,
            quickSuggestions: { other: true, comments: false, strings: false },
          }}
        />
      </div>

      {/* Kết quả chạy */}
      <div className="flex h-64 shrink-0 select-text flex-col border-t border-border bg-surface">
        <div className="flex shrink-0 items-center justify-between gap-3 border-b border-border/80 px-3 py-2">
          <div role="tablist" aria-label="Kết quả chạy" className="inline-flex p-1 bg-surface-raised rounded-full border border-border/80 gap-1">
            <button
              type="button"
              role="tab"
              id="result-tab-tests"
              aria-selected={activeBottomTab === 'tests'}
              aria-controls="result-panel-tests"
              onClick={() => setActiveBottomTab('tests')}
              className={tabBtn(activeBottomTab === 'tests')}
            >
              Bộ kiểm thử chuẩn
              {testResults && (
                <span className="rounded bg-surface-raised px-1.5 text-[0.8125rem] tabular-nums">
                  {testResults.passed_tests}/{testResults.total_tests}
                </span>
              )}
            </button>
            <button
              type="button"
              role="tab"
              id="result-tab-custom"
              aria-selected={activeBottomTab === 'custom'}
              aria-controls="result-panel-custom"
              onClick={() => setActiveBottomTab('custom')}
              className={tabBtn(activeBottomTab === 'custom')}
            >
              Tự nhập dữ liệu
            </button>
          </div>
          {activeBottomTab === 'tests' && testResults && (
            <span className="hidden truncate text-[0.8125rem] text-muted sm:inline">{testResults.summary}</span>
          )}
        </div>

        {activeBottomTab === 'tests' && (
          <div id="result-panel-tests" role="tabpanel" aria-labelledby="result-tab-tests" aria-live="polite" className="flex-1 space-y-2 overflow-y-auto p-3">
            {!testResults ? (
              <div className="flex h-full flex-col items-center justify-center gap-1 text-center">
                <p className="text-sm font-medium">Chưa có kết quả kiểm thử.</p>
                <p className="text-[0.8125rem] text-muted">Bấm “Chạy thử” để kiểm tra, hoặc “Nộp bài” để chấm chính thức.</p>
              </div>
            ) : (
              <>
                {testResults.all_passed && (
                  <div className="mb-2 flex flex-col gap-3 rounded-lg border border-success-line bg-success-soft p-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-start gap-2.5">
                      <CheckCircle2 aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-success-strong" />
                      <div>
                        <p className="text-sm font-semibold">
                          Đã vượt qua toàn bộ {testResults.passed_tests}/{testResults.total_tests} kiểm thử.
                        </p>
                        <p className="text-[0.8125rem] text-muted">Bấm “Nộp bài” để hệ thống ghi nhận kết quả và mở khóa bài tiếp theo.</p>
                      </div>
                    </div>
                    <button
                      onClick={onSubmit}
                      disabled={isBusy}
                      type="button"
                      className={`${toolBtn} shrink-0 bg-primary text-on-solid hover:bg-primary-hover`}
                    >
                      <Send aria-hidden="true" className="size-4" />
                      Nộp bài ngay
                    </button>
                  </div>
                )}
                {testResults.results.map((r, idx) => {
                  const isSelected = selectedTestCaseIdx === idx;
                  const tone = r.status === 'PASS'
                    ? 'border-success-line bg-success-soft/40'
                    : r.status === 'FAIL'
                      ? 'border-destructive-line bg-destructive-soft/40'
                      : r.status === 'TIMEOUT'
                        ? 'border-warning-line bg-warning-soft/40'
                        : 'border-ai-line bg-ai-soft/40';
                  return (
                    <div key={idx} className={`overflow-hidden rounded-lg border text-sm ${tone}`}>
                      <button
                        type="button"
                        aria-expanded={isSelected}
                        aria-controls={`test-detail-${idx}`}
                        onClick={() => setSelectedTestCaseIdx(isSelected ? null : idx)}
                        className="flex min-h-11 w-full items-center justify-between gap-3 px-3 py-2 text-left hover:bg-surface-raised"
                      >
                        <span className="flex min-w-0 flex-wrap items-center gap-2">
                          {getStatusBadge(r.status)}
                          <span className="font-medium">Test #{r.test_idx}: {r.description || `Test case ${r.test_idx}`}</span>
                        </span>
                        <span className="flex shrink-0 items-center gap-2 text-[0.8125rem] tabular-nums text-muted">
                          {r.execution_time_ms > 0 && <span>{r.execution_time_ms} ms</span>}
                          {isSelected ? <ChevronUp aria-hidden="true" className="size-4" /> : <ChevronDown aria-hidden="true" className="size-4" />}
                        </span>
                      </button>

                      {isSelected && (
                        <div id={`test-detail-${idx}`} className="space-y-3 border-t border-border p-3">
                          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                            <div>
                              <p className="mb-1 text-[0.8125rem] font-medium text-muted">Đầu vào</p>
                              <pre className="whitespace-pre-wrap rounded bg-surface-raised p-2 font-mono text-[0.8125rem]">{r.input || '(trống)'}</pre>
                            </div>
                            <div>
                              <p className="mb-1 text-[0.8125rem] font-medium text-muted">Kết quả mong đợi</p>
                              <pre className="whitespace-pre-wrap rounded bg-surface-raised p-2 font-mono text-[0.8125rem]">{r.expected_output || '(trống)'}</pre>
                            </div>
                          </div>
                          <div>
                            <p className="mb-1 text-[0.8125rem] font-medium text-muted">Kết quả của bạn</p>
                            <pre className={`whitespace-pre-wrap rounded p-2 font-mono text-[0.8125rem] ${r.status === 'PASS' ? 'bg-success-soft text-success-strong' : 'border border-destructive-line bg-destructive-soft text-destructive-strong'}`}>
                              {r.actual_output || (r.status === 'PASS' ? '(trống)' : '(không in ra dữ liệu)')}
                            </pre>
                          </div>
                          {r.error_message && (
                            <div>
                              <p className="mb-1 text-[0.8125rem] font-medium text-danger">Thông báo lỗi</p>
                              <pre className="whitespace-pre-wrap rounded border border-destructive-line bg-destructive-soft p-2 font-mono text-[0.8125rem] text-destructive-strong">{r.error_message}</pre>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </>
            )}
          </div>
        )}

        {activeBottomTab === 'custom' && (
          <div id="result-panel-custom" role="tabpanel" aria-labelledby="result-tab-custom" className="grid flex-1 grid-cols-1 gap-3 overflow-y-auto p-3 md:grid-cols-2">
            <div className="flex flex-col gap-2">
              <label htmlFor="custom-stdin" className="text-sm font-medium">Dữ liệu vào (stdin)</label>
              <p id="custom-stdin-hint" className="-mt-1 text-[0.8125rem] text-muted">Mỗi dòng tương ứng một lệnh input().</p>
              <textarea
                id="custom-stdin"
                aria-describedby="custom-stdin-hint"
                value={customInput}
                onChange={(e) => setCustomInput(e.target.value)}
                placeholder="Ví dụ: 5"
                className="min-h-[90px] flex-1 resize-none rounded-md border border-field bg-surface p-2.5 font-mono text-sm text-foreground placeholder:text-muted outline-none focus:border-primary focus:ring-2 focus:ring-primary/25"
              />
              <button
                type="button"
                onClick={handleRunCustom}
                disabled={isRunningCustom || !code.trim()}
                aria-busy={isRunningCustom}
                className={`${runBtn} justify-center`}
              >
                {isRunningCustom ? <Spinner /> : <Play aria-hidden="true" className="size-4" />}
                {isRunningCustom ? 'Đang chạy…' : 'Chạy với dữ liệu này'}
              </button>
            </div>

            <div className="flex flex-col gap-2 overflow-hidden">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium">Kết quả in ra (stdout)</p>
                {customResult && (
                  <span className="flex items-center gap-2">
                    {getStatusBadge(customResult.status)}
                    <span className="text-[0.8125rem] tabular-nums text-muted">{customResult.execution_time_ms} ms</span>
                  </span>
                )}
              </div>
              <div aria-live="polite" className="min-h-[90px] flex-1 overflow-y-auto rounded-md border border-border bg-canvas p-2.5 font-mono text-[0.8125rem]">
                {!customResult ? (
                  <span className="font-sans text-muted">Nhập dữ liệu rồi bấm “Chạy với dữ liệu này” để xem kết quả.</span>
                ) : customResult.error_message ? (
                  <div className="space-y-1 text-danger">
                    <p className="flex items-start gap-1.5 font-sans font-semibold"><AlertTriangle aria-hidden="true" className="mt-0.5 size-4 shrink-0" />{customResult.error_message}</p>
                    {customResult.stderr && <pre className="whitespace-pre-wrap">{customResult.stderr}</pre>}
                  </div>
                ) : (
                  <pre className="whitespace-pre-wrap">{customResult.stdout || '(Chương trình chạy xong mà không in ra dữ liệu nào)'}</pre>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
