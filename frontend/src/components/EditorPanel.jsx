import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import { Play, RotateCcw, CheckCircle2, XCircle, Clock, AlertTriangle, Terminal, ChevronDown, ChevronUp } from 'lucide-react';

export default function EditorPanel({
  code,
  setCode,
  onResetCode,
  onSubmit,
  isSubmitting,
  testResults,
  isDarkTheme,
}) {
  const [selectedTestCaseIdx, setSelectedTestCaseIdx] = useState(null);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'PASS':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            <span>PASS</span>
          </span>
        );
      case 'FAIL':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <XCircle className="w-3 h-3" />
            <span>FAIL</span>
          </span>
        );
      case 'TIMEOUT':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Clock className="w-3 h-3" />
            <span>TIMEOUT</span>
          </span>
        );
      case 'SYNTAX_ERROR':
      case 'RUNTIME_ERROR':
        return (
          <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <AlertTriangle className="w-3 h-3" />
            <span>{status}</span>
          </span>
        );
      case 'SKIPPED':
        return (
          <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
            SKIPPED
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
          <span>PYTHON 3 EDITOR</span>
          <span className="text-[11px] text-slate-500 font-mono">({isDarkTheme ? 'vs-dark' : 'light'})</span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onResetCode}
            disabled={isSubmitting}
            className="flex items-center space-x-1 px-2.5 py-1 text-xs text-slate-400 hover:text-white bg-slate-800/80 hover:bg-slate-800 rounded border border-slate-700/60 transition-colors disabled:opacity-50"
            title="Khôi phục code mẫu ban đầu"
          >
            <RotateCcw className="w-3 h-3" />
            <span className="hidden sm:inline">Code mẫu</span>
          </button>

          <button
            onClick={onSubmit}
            disabled={isSubmitting}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-500 rounded-lg shadow-sm shadow-emerald-900/40 transition-all disabled:opacity-50 cursor-pointer"
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
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Chạy & Nhận Gợi Ý AI</span>
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
          onChange={(value) => setCode(value || '')}
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
          }}
        />
      </div>

      {/* Lower Half: Test Results Panel */}
      <div className="h-64 border-t border-slate-800 bg-slate-900/95 flex flex-col shrink-0 select-text">
        {/* Results Header */}
        <div className="h-9 px-3.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-2 text-xs font-semibold">
            <span className="text-slate-300">KẾT QUẢ THỰC THI (MCP SANDBOX):</span>
            {testResults && (
              <span
                className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                  testResults.all_passed
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-rose-500/20 text-rose-400'
                }`}
              >
                {testResults.passed_tests} / {testResults.total_tests} ĐẠT
              </span>
            )}
          </div>
          {testResults && (
            <span className="text-[11px] text-slate-400 hidden sm:inline">
              {testResults.summary}
            </span>
          )}
        </div>

        {/* Results Content List */}
        <div className="flex-1 overflow-y-auto p-2.5 space-y-2">
          {!testResults ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs text-center space-y-1">
              <Terminal className="w-6 h-6 opacity-40 mb-1" />
              <span>Chưa có kết quả thực thi.</span>
              <span className="text-[11px] text-slate-600">Nhấn nút "Chạy & Nhận Gợi Ý AI" để kiểm thử mã nguồn qua MCP Server.</span>
            </div>
          ) : (
            testResults.results.map((r, idx) => {
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
                          <span className="text-slate-500 font-sans text-[10px] uppercase">Input:</span>
                          <div className="bg-slate-900 p-1.5 rounded text-emerald-400 whitespace-pre-wrap">
                            {r.input || '(trống)'}
                          </div>
                        </div>
                        <div>
                          <span className="text-slate-500 font-sans text-[10px] uppercase">Expected:</span>
                          <div className="bg-slate-900 p-1.5 rounded text-cyan-400 whitespace-pre-wrap">
                            {r.expected_output || '(trống)'}
                          </div>
                        </div>
                      </div>

                      <div>
                        <span className="text-slate-500 font-sans text-[10px] uppercase">Actual Output:</span>
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
                          <span className="text-rose-400 font-sans text-[10px] uppercase">Thông báo lỗi:</span>
                          <div className="bg-rose-950/60 p-1.5 rounded text-rose-300 text-[11px]">
                            {r.error_message}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
