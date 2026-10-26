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

export default function EditorPanel({
  code,
  setCode,
  exerciseId,
  onResetCode,
  onRunTest,
  isRunningTest,
  onAskAI,
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

  const getStatusBadge = (status) => {
    switch (status) {
      case 'PASS':
      case 'SUCCESS':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            <span>ĐẠT (PASS)</span>
          </span>
        );
      case 'FAIL':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <XCircle className="w-3 h-3" />
            <span>CHƯA ĐẠT (FAIL)</span>
          </span>
        );
      case 'TIMEOUT':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Clock className="w-3 h-3" />
            <span>QUÁ THỜI GIAN (TIMEOUT)</span>
          </span>
        );
      case 'SYNTAX_ERROR':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <AlertTriangle className="w-3 h-3" />
            <span>LỖI CÚ PHÁP</span>
          </span>
        );
      case 'RUNTIME_ERROR':
      case 'ERROR':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <AlertTriangle className="w-3 h-3" />
            <span>LỖI CHẠY (RUNTIME)</span>
          </span>
        );
      case 'SKIPPED':
        return (
          <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
            BỎ QUA (SKIPPED)
          </span>
        );
      default:
        return <span className="text-[11px] text-slate-400">{status}</span>;
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-950 border-r border-slate-800 overflow-hidden">
      {/* Editor Toolbar */}
      <div className="h-11 bg-slate-900 border-b border-slate-800 px-3 flex items-center justify-between shrink-0 select-none">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span>TRÌNH SOẠN THẢO PYTHON 3</span>
        </div>

        <div className="flex items-center space-x-1.5 sm:space-x-2">
          {/* Nút Khôi phục code gốc */}
          <button
            onClick={onResetCode}
            disabled={isBusy}
            type="button"
            className="flex items-center space-x-1 px-2.5 py-1 text-xs text-slate-400 hover:text-white bg-slate-800/80 hover:bg-slate-800 rounded-lg border border-slate-700/60 transition-colors disabled:opacity-50 cursor-pointer"
            title="Khôi phục lại code ban đầu của bài tập"
          >
            <RotateCcw className="w-3 h-3" />
            <span className="hidden sm:inline">Khôi phục code gốc</span>
            <span className="sm:hidden">Gốc</span>
          </button>

          {/* Nút Chạy từng bước (Visualizer) */}
          {onOpenVisualizer && (
            <button
              onClick={onOpenVisualizer}
              disabled={isBusy}
              type="button"
              className="flex items-center space-x-1.5 px-2.5 py-1 text-xs font-medium text-amber-300 hover:text-amber-200 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 rounded-lg transition-all disabled:opacity-50 cursor-pointer shadow-sm group"
              title="Trực quan hóa từng bước thực thi code và xem biến thiên giá trị biến số (Visualizer)"
            >
              <Eye className="w-3.5 h-3.5 text-amber-400 group-hover:scale-110 transition-transform" />
              <span className="hidden sm:inline">👁️ Chạy từng bước</span>
              <span className="sm:hidden">👁️ Từng bước</span>
            </button>
          )}

          {/* Nút 1: Chạy thử (Ctrl + Enter) */}
          <button
            onClick={onRunTest}
            disabled={isBusy}
            type="button"
            className="flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold text-cyan-300 hover:text-cyan-200 bg-slate-800 hover:bg-slate-750 border border-cyan-500/40 hover:border-cyan-500/60 rounded-lg transition-all disabled:opacity-50 cursor-pointer shadow-sm group"
            title="Chạy thử code nhanh với các bộ test cases mẫu trong sandbox (Phím tắt: Ctrl + Enter)"
          >
            {isRunningTest ? (
              <svg className="animate-spin h-3.5 w-3.5 text-cyan-300" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            ) : (
              <Play className="w-3.5 h-3.5 fill-current text-cyan-400 group-hover:scale-110 transition-transform" />
            )}
            <span>▶ Chạy thử</span>
            <span className="text-[10px] text-slate-500 font-mono hidden md:inline">(Ctrl+↵)</span>
          </button>

          {/* Nút 2: Hỏi Gia sư AI (ẩn khi isExamMode) */}
          {!isExamMode && onAskAI && (
            <button
              onClick={onAskAI}
              disabled={isBusy}
              type="button"
              className="flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold text-amber-300 hover:text-amber-200 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/40 hover:border-amber-500/60 rounded-lg transition-all disabled:opacity-50 cursor-pointer shadow-sm group"
              title="Phân tích code và nhận gợi ý sư phạm ở Cột 3 từ Gia sư AI"
            >
              {isAskingAI ? (
                <>
                  <svg className="animate-spin h-3.5 w-3.5 text-amber-300" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  <span>Đang hỏi AI...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-amber-400 group-hover:scale-110 transition-transform" />
                  <span>🤖 Hỏi Gia sư AI</span>
                </>
              )}
            </button>
          )}

          {/* Nút 3: Nộp bài & Đánh giá (Ctrl + Shift + Enter) */}
          <button
            onClick={onSubmit}
            disabled={isBusy}
            type="button"
            className="flex items-center space-x-1.5 px-3.5 py-1 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow-md shadow-emerald-900/50 hover:shadow-emerald-900/70 border border-emerald-400/30 transition-all disabled:opacity-50 cursor-pointer group"
            title="Chính thức nộp bài, chấm điểm, ghi nhận số sao năng lực và mở khóa bài tiếp theo (Phím tắt: Ctrl + Shift + Enter)"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin h-3.5 w-3.5 text-white" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                <span>Đang chấm bài...</span>
              </>
            ) : (
              <>
                <Send className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform text-emerald-200" />
                <span>🚀 Nộp bài</span>
                <span className="text-[10px] text-emerald-200/80 font-mono hidden md:inline">(Ctrl+Shift+↵)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Upper Half: Monaco Code Editor */}
      <div className="flex-1 min-h-[220px] relative bg-slate-950">
        <Editor
          height="100%"
          language="python"
          theme={isDarkTheme ? 'vs-dark' : 'light'}
          value={code}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          options={{
            fontSize: 13.5,
            lineNumbers: 'on',
            minimap: { enabled: false },
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            scrollBeyondLastLine: false,
            fontFamily: 'Consolas, "Fira Code", monospace',
            cursorBlinking: 'smooth',
            roundedSelection: true,
            padding: { top: 8, bottom: 8 },
            acceptSuggestionOnCommitCharacter: false,
            quickSuggestions: { other: true, comments: false, strings: false },
          }}
        />
      </div>

      {/* Lower Half: Tabbed Execution Results Panel */}
      <div className="h-64 border-t border-slate-800 bg-slate-900/95 flex flex-col shrink-0 select-text">
        {/* Tab Navigation Header */}
        <div className="h-9 px-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-1 text-xs">
            {/* Tab 1: Bộ test chuẩn */}
            <button
              type="button"
              onClick={() => setActiveBottomTab('tests')}
              className={`px-3 py-1 font-semibold rounded-t border-b-2 transition-all cursor-pointer ${
                activeBottomTab === 'tests'
                  ? 'border-emerald-400 text-emerald-400 bg-slate-800/60'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>🧪 Bộ test chuẩn</span>
              {testResults && (
                <span className="ml-1.5 text-[10.5px] px-1.5 py-0.2 rounded-full bg-slate-800 font-mono">
                  {testResults.passed_tests}/{testResults.total_tests}
                </span>
              )}
            </button>

            {/* Tab 2: Tự nhập dữ liệu (Custom Stdin) */}
            <button
              type="button"
              onClick={() => setActiveBottomTab('custom')}
              className={`px-3 py-1 font-semibold rounded-t border-b-2 transition-all cursor-pointer ${
                activeBottomTab === 'custom'
                  ? 'border-cyan-400 text-cyan-300 bg-slate-800/60'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>💻 Tự nhập dữ liệu (Custom Stdin)</span>
            </button>
          </div>

          {activeBottomTab === 'tests' && testResults && (
            <span className="text-[11px] text-slate-400 hidden sm:inline">
              {testResults.summary}
            </span>
          )}
        </div>

        {/* Tab 1 Body: Standard Test Cases */}
        {activeBottomTab === 'tests' && (
          <div className="flex-1 overflow-y-auto p-2.5 space-y-2">
            {!testResults ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs text-center space-y-1">
                <Terminal className="w-6 h-6 opacity-40 mb-1" />
                <span className="font-medium text-slate-400">Chưa có kết quả kiểm thử.</span>
                <span className="text-[11px] text-slate-500">
                  Nhấn <span className="text-cyan-400">"▶ Chạy thử"</span> để kiểm tra hoặc <span className="text-emerald-400">"🚀 Nộp bài"</span> để chấm điểm chính thức.
                </span>
              </div>
            ) : (
              <>
                {/* Banner chúc mừng & nhắc nộp bài chính thức khi pass toàn bộ test cases */}
                {testResults.all_passed && (
                  <div className="p-3 rounded-xl bg-gradient-to-r from-emerald-950/80 via-teal-950/60 to-slate-900 border border-emerald-500/40 text-xs flex items-center justify-between shadow-lg mb-2">
                    <div className="flex items-center space-x-2.5">
                      <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                        <Sparkles className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="font-bold text-emerald-300">
                          🎉 Chúc mừng! Chương trình đã vượt qua toàn bộ {testResults.passed_tests}/{testResults.total_tests} kiểm thử.
                        </div>
                        <div className="text-[11px] text-emerald-400/80">
                          Hãy bấm nút <strong className="text-white">"🚀 Nộp bài"</strong> để hệ thống chính thức ghi nhận điểm số, sao năng lực và mở khóa bài tiếp theo!
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={onSubmit}
                      disabled={isBusy}
                      type="button"
                      className="ml-3 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg shadow-md flex items-center space-x-1.5 shrink-0 cursor-pointer transition-all hover:scale-105"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>🚀 Nộp bài ngay</span>
                    </button>
                  </div>
                )}
                {testResults.results.map((r, idx) => {
                const isSelected = selectedTestCaseIdx === idx;
                return (
                  <div
                    key={idx}
                    className={`border rounded-lg transition-all text-xs overflow-hidden ${
                      r.status === 'PASS'
                        ? 'border-emerald-500/30 bg-emerald-950/20'
                        : r.status === 'FAIL'
                        ? 'border-rose-500/30 bg-rose-950/20'
                        : r.status === 'TIMEOUT'
                        ? 'border-amber-500/30 bg-amber-950/20'
                        : 'border-slate-800 bg-slate-950/50'
                    }`}
                  >
                    {/* Summary Row */}
                    <div
                      onClick={() => setSelectedTestCaseIdx(isSelected ? null : idx)}
                      className="p-2 flex items-center justify-between cursor-pointer hover:bg-white/5 select-none"
                    >
                      <div className="flex items-center space-x-2">
                        {getStatusBadge(r.status)}
                        <span className="font-semibold text-slate-200">
                          Test #{r.test_idx}: {r.description || `Test case ${r.test_idx}`}
                        </span>
                      </div>

                      <div className="flex items-center space-x-2 text-slate-400 font-mono text-[11px]">
                        {r.execution_time_ms > 0 && <span>{r.execution_time_ms} ms</span>}
                        {isSelected ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                      </div>
                    </div>

                    {/* Expanded Detail */}
                    {isSelected && (
                      <div className="p-2.5 pt-1 border-t border-slate-800/80 bg-slate-950/70 font-mono space-y-2 text-[11.5px]">
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <span className="text-slate-500 font-sans text-[10px] uppercase block mb-0.5">Đầu vào (Input):</span>
                            <div className="bg-slate-900 p-1.5 rounded text-emerald-400 whitespace-pre-wrap">
                              {r.input || '(trống)'}
                            </div>
                          </div>
                          <div>
                            <span className="text-slate-500 font-sans text-[10px] uppercase block mb-0.5">Kết quả mong đợi (Expected):</span>
                            <div className="bg-slate-900 p-1.5 rounded text-cyan-400 whitespace-pre-wrap">
                              {r.expected_output || '(trống)'}
                            </div>
                          </div>
                        </div>

                        <div>
                          <span className="text-slate-500 font-sans text-[10px] uppercase block mb-0.5">Kết quả của bạn (Actual Output):</span>
                          <div
                            className={`p-1.5 rounded whitespace-pre-wrap ${
                              r.status === 'PASS'
                                ? 'bg-slate-900 text-emerald-300'
                                : 'bg-rose-950/40 text-rose-300 border border-rose-900/50'
                            }`}
                          >
                            {r.actual_output || (r.status === 'PASS' ? '(trống)' : '(không in ra dữ liệu)')}
                          </div>
                        </div>

                        {r.error_message && (
                          <div>
                            <span className="text-rose-400 font-sans text-[10px] uppercase block mb-0.5">Thông báo lỗi:</span>
                            <div className="bg-rose-950/60 p-1.5 rounded text-rose-300 text-[11px]">
                              {r.error_message}
                            </div>
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

        {/* Tab 2 Body: Custom Input Playground */}
        {activeBottomTab === 'custom' && (
          <div className="flex-1 p-3 overflow-y-auto grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            {/* Left: Input Textarea */}
            <div className="flex flex-col space-y-1.5">
              <label className="text-slate-400 font-medium text-[11px] flex items-center justify-between">
                <span>Nhập dữ liệu vào (Standard Input / stdin):</span>
                <span className="text-slate-500 text-[10px] italic">Ví dụ: số, chuỗi theo dòng</span>
              </label>
              <textarea
                value={customInput}
                onChange={(e) => setCustomInput(e.target.value)}
                placeholder="Nhập dữ liệu đầu vào tại đây (mỗi dòng tương ứng một lệnh input())..."
                className="flex-1 min-h-[90px] bg-slate-950 border border-slate-800 rounded-lg p-2 font-mono text-emerald-400 text-xs focus:outline-none focus:ring-1 focus:ring-cyan-500/50 resize-none"
              />
              <button
                type="button"
                onClick={handleRunCustom}
                disabled={isRunningCustom || !code.trim()}
                className="py-1.5 px-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg font-medium transition-colors cursor-pointer flex items-center justify-center space-x-1.5 disabled:opacity-50 text-xs shadow-sm shadow-cyan-900/30"
              >
                {isRunningCustom ? (
                  <>
                    <svg className="animate-spin h-3.5 w-3.5 text-white" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    <span>Đang thực thi...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>▶ Chạy với dữ liệu này</span>
                  </>
                )}
              </button>
            </div>

            {/* Right: Output Window */}
            <div className="flex flex-col space-y-1.5 bg-slate-950/70 p-2.5 rounded-lg border border-slate-800 overflow-hidden">
              <div className="flex items-center justify-between text-[11px] pb-1 border-b border-slate-800">
                <span className="font-semibold text-slate-300">Kết quả in ra (Standard Output):</span>
                {customResult && (
                  <div className="flex items-center space-x-2">
                    {getStatusBadge(customResult.status)}
                    <span className="text-slate-500 font-mono text-[10px]">
                      {customResult.execution_time_ms} ms
                    </span>
                  </div>
                )}
              </div>

              <div className="flex-1 overflow-y-auto font-mono text-[11px] p-2 bg-slate-900/90 rounded border border-slate-800/80 min-h-[90px]">
                {!customResult ? (
                  <span className="text-slate-600 italic">Nhập dữ liệu và bấm "Chạy với dữ liệu này" để xem output...</span>
                ) : customResult.error_message ? (
                  <div className="space-y-1">
                    <div className="text-rose-400 font-bold">⚠️ {customResult.error_message}</div>
                    {customResult.stderr && (
                      <pre className="text-rose-300 text-[10px] whitespace-pre-wrap">{customResult.stderr}</pre>
                    )}
                  </div>
                ) : (
                  <pre className="text-emerald-300 whitespace-pre-wrap">
                    {customResult.stdout || '(Chương trình chạy xong mà không in ra dữ liệu nào)'}
                  </pre>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
