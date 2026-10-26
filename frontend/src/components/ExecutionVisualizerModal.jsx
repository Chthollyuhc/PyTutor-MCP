import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  Terminal,
  Variable,
  AlertTriangle,
  Code,
  Layers,
  Sparkles
} from 'lucide-react';
import { fetchExecutionTrace } from '../services/api';

export default function ExecutionVisualizerModal({
  isOpen,
  onClose,
  initialCode = '',
  defaultStdin = '',
}) {
  const [code, setCode] = useState(initialCode);
  const [stdinInput, setStdinInput] = useState(defaultStdin);
  const [steps, setSteps] = useState([]);
  const [codeLines, setCodeLines] = useState([]);
  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playSpeed] = useState(1200); // 1.2s per step
  const [error, setError] = useState(null);
  const [truncated, setTruncated] = useState(false);
  const [showStdin, setShowStdin] = useState(false);

  const autoPlayTimerRef = useRef(null);
  const activeLineRef = useRef(null);

  // Khởi tạo và nạp trace khi modal mở
  useEffect(() => {
    if (!isOpen) {
      setIsPlaying(false);
      if (autoPlayTimerRef.current) clearInterval(autoPlayTimerRef.current);
      return;
    }
    setCode(initialCode);
    const initialStdin = stdinInput || defaultStdin || '';
    if (!stdinInput && defaultStdin) {
      setStdinInput(defaultStdin);
    }
    if (initialCode.includes('input(')) {
      setShowStdin(true);
    }
    loadTrace(initialCode, initialStdin);
  }, [isOpen, initialCode, defaultStdin]);

  // Quản lý Auto-play
  useEffect(() => {
    if (isPlaying) {
      autoPlayTimerRef.current = setInterval(() => {
        setCurrentStepIdx((prev) => {
          if (prev >= steps.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, playSpeed);
    } else {
      if (autoPlayTimerRef.current) {
        clearInterval(autoPlayTimerRef.current);
      }
    }
    return () => {
      if (autoPlayTimerRef.current) clearInterval(autoPlayTimerRef.current);
    };
  }, [isPlaying, steps.length, playSpeed]);

  // Tự động cuộn đến dòng đang thực thi
  useEffect(() => {
    if (activeLineRef.current) {
      activeLineRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'nearest',
      });
    }
  }, [currentStepIdx]);

  const loadTrace = async (codeToTrace, customStdin) => {
    if (!codeToTrace || !codeToTrace.trim()) return;
    setIsLoading(true);
    setIsPlaying(false);
    setError(null);
    try {
      const data = await fetchExecutionTrace({
        code: codeToTrace,
        stdin_input: customStdin,
        max_steps: 150,
      });

      if (data.error && !data.steps?.length) {
        setError(data.error);
        setSteps([]);
        setCodeLines(data.code_lines || codeToTrace.split('\n'));
      } else {
        setSteps(data.steps || []);
        setCodeLines(data.code_lines || codeToTrace.split('\n'));
        setCurrentStepIdx(0);
        setTruncated(Boolean(data.truncated));
        if (data.error) setError(data.error);
      }
    } catch (err) {
      console.error('Lỗi khi tải trace:', err);
      setError(err.response?.data?.detail || 'Không thể kết nối Backend để trace mã nguồn.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  const currentStep = steps[currentStepIdx] || null;
  const prevStep = currentStepIdx > 0 ? steps[currentStepIdx - 1] : null;

  // Xác định các biến vừa thay đổi giá trị
  const changedVars = new Set();
  if (currentStep && currentStep.locals) {
    const prevLocals = prevStep ? prevStep.locals : {};
    Object.entries(currentStep.locals).forEach(([varName, varData]) => {
      const prevData = prevLocals[varName];
      if (!prevData || prevData.value !== varData.value) {
        changedVars.add(varName);
      }
    });
  }

  // Điều hướng
  const handleFirst = () => setCurrentStepIdx(0);
  const handlePrev = () => setCurrentStepIdx((prev) => Math.max(0, prev - 1));
  const handleNext = () => setCurrentStepIdx((prev) => Math.min(steps.length - 1, prev + 1));
  const handleLast = () => setCurrentStepIdx(steps.length - 1);
  const handleTogglePlay = () => setIsPlaying((prev) => !prev);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-950/85 backdrop-blur-md select-text animate-fade-in">
      <div className="w-full max-w-5xl h-[92vh] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-5 py-3 border-b border-slate-800 bg-slate-950 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 font-bold">
              <Code className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-sm sm:text-base font-bold text-white tracking-wide">
                  👁️ Trực quan hóa Từng bước Thực thi
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                  MCP Tool 8: trace_code_execution
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                Theo dõi dòng lệnh đang chạy, biến đổi giá trị biến số và luồng stdout
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowStdin((prev) => !prev)}
              type="button"
              className="px-2.5 py-1 text-xs font-medium text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-800 border border-slate-700/60 rounded-lg transition-colors cursor-pointer"
            >
              ⌨️ {showStdin ? 'Ẩn Stdin' : 'Nhập Stdin'}
            </button>
            <button
              onClick={() => loadTrace(code, stdinInput)}
              disabled={isLoading}
              type="button"
              className="p-1.5 text-slate-400 hover:text-cyan-400 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
              title="Chạy lại Tracing"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
            <button
              onClick={onClose}
              type="button"
              className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
              title="Đóng cửa sổ"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Collapsible Stdin Input Bar */}
        {showStdin && (
          <div className="px-5 py-2.5 bg-slate-950/80 border-b border-slate-800/80 flex items-center space-x-3 text-xs">
            <span className="text-slate-400 shrink-0 font-medium">Dữ liệu đầu vào (Stdin):</span>
            <input
              type="text"
              value={stdinInput}
              onChange={(e) => setStdinInput(e.target.value)}
              placeholder="Ví dụ: 5 hoặc nguyen van a (dùng cho hàm input())"
              className="flex-1 bg-slate-900 border border-slate-700 rounded-md px-2.5 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-cyan-500"
            />
            <button
              onClick={() => loadTrace(code, stdinInput)}
              disabled={isLoading}
              className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded-md font-semibold text-xs transition-colors"
            >
              Áp dụng & Trace
            </button>
          </div>
        )}

        {/* Navigation / Playback Controls Toolbar */}
        <div className="px-5 py-2.5 bg-slate-900/90 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 shrink-0">
          <div className="flex items-center space-x-1.5 sm:space-x-2">
            {/* First */}
            <button
              onClick={handleFirst}
              disabled={steps.length === 0 || currentStepIdx === 0}
              className="p-1.5 text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-750 disabled:opacity-40 disabled:hover:text-slate-300 rounded-lg border border-slate-700/60 transition-colors cursor-pointer"
              title="Về bước đầu tiên"
            >
              <SkipBack className="w-3.5 h-3.5" />
            </button>

            {/* Prev */}
            <button
              onClick={handlePrev}
              disabled={steps.length === 0 || currentStepIdx === 0}
              className="flex items-center space-x-1 px-2.5 py-1 text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-750 disabled:opacity-40 disabled:hover:text-slate-300 rounded-lg border border-slate-700/60 transition-colors cursor-pointer"
              title="Lùi 1 bước"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Lùi 1 bước</span>
            </button>

            {/* Auto Play Toggle */}
            <button
              onClick={handleTogglePlay}
              disabled={steps.length === 0}
              className={`flex items-center space-x-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
                isPlaying
                  ? 'bg-amber-600 hover:bg-amber-500 text-white shadow-sm'
                  : 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-sm'
              }`}
              title="Tự động chạy từng bước"
            >
              {isPlaying ? (
                <>
                  <Pause className="w-3.5 h-3.5 fill-current" />
                  <span>Tạm dừng</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Tự chạy</span>
                </>
              )}
            </button>

            {/* Next */}
            <button
              onClick={handleNext}
              disabled={steps.length === 0 || currentStepIdx >= steps.length - 1}
              className="flex items-center space-x-1 px-2.5 py-1 text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-750 disabled:opacity-40 disabled:hover:text-slate-300 rounded-lg border border-slate-700/60 transition-colors cursor-pointer"
              title="Tiếp 1 bước"
            >
              <span className="hidden sm:inline">Tiếp 1 bước</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>

            {/* Last */}
            <button
              onClick={handleLast}
              disabled={steps.length === 0 || currentStepIdx >= steps.length - 1}
              className="p-1.5 text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-750 disabled:opacity-40 disabled:hover:text-slate-300 rounded-lg border border-slate-700/60 transition-colors cursor-pointer"
              title="Đến bước cuối cùng"
            >
              <SkipForward className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Step Counter & Slider */}
          <div className="flex-1 max-w-md flex items-center space-x-3">
            <input
              type="range"
              min="0"
              max={Math.max(0, steps.length - 1)}
              value={currentStepIdx}
              onChange={(e) => setCurrentStepIdx(parseInt(e.target.value, 10))}
              disabled={steps.length === 0}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
            <span className="font-mono text-xs font-semibold text-cyan-300 shrink-0">
              {steps.length > 0 ? `Bước ${currentStepIdx + 1} / ${steps.length}` : '0 / 0'}
            </span>
          </div>
        </div>

        {/* Truncated / Error Notice */}
        {(truncated || error) && (
          <div className="px-5 py-2.5 bg-amber-500/10 border-b border-amber-500/20 flex flex-wrap items-center justify-between gap-2 text-xs text-amber-300 shrink-0">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>
                {error
                  ? error
                  : 'Đã dừng tại giới hạn bước an toàn (150 bước / 3s) để bảo vệ hệ thống khỏi vòng lặp vô hạn.'}
              </span>
            </div>
            {error && error.includes('EOFError') && (
              <button
                type="button"
                onClick={() => {
                  const fallback = defaultStdin || '5';
                  setStdinInput(fallback);
                  setShowStdin(true);
                  loadTrace(code, fallback);
                }}
                className="px-2.5 py-1 bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 border border-amber-500/40 rounded text-xs font-semibold cursor-pointer transition-colors"
              >
                ⚡ Điền dữ liệu mẫu {defaultStdin ? `("${defaultStdin}")` : '("5")'} & Chạy lại
              </button>
            )}
          </div>
        )}

        {/* Main Content Split View (Code on Left, Variables & Stdout on Right) */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-12 gap-0 overflow-hidden">
          {/* Left Column: Code View with Active Line Highlight (~55%) */}
          <div className="md:col-span-7 border-r border-slate-800 flex flex-col bg-slate-950 overflow-hidden">
            <div className="px-4 py-2 border-b border-slate-800/80 bg-slate-900/40 flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold flex items-center space-x-1.5 text-slate-300">
                <Code className="w-3.5 h-3.5 text-cyan-400" />
                <span>MÃ NGUỒN PYTHON</span>
              </span>
              {currentStep && (
                <span className="font-mono text-[11px] text-cyan-400">
                  Đang chạy: Dòng {currentStep.line} ({currentStep.event})
                </span>
              )}
            </div>

            <div className="flex-1 overflow-auto p-3 font-mono text-xs leading-6 select-text">
              {isLoading ? (
                <div className="h-full flex items-center justify-center text-slate-400 space-x-2">
                  <RefreshCw className="w-5 h-5 animate-spin text-cyan-400" />
                  <span>Đang tracing mã nguồn qua MCP Server...</span>
                </div>
              ) : codeLines.length === 0 ? (
                <div className="h-full flex items-center justify-center text-slate-500">
                  Không có mã nguồn để hiển thị.
                </div>
              ) : (
                <div className="space-y-0.5">
                  {codeLines.map((lineText, idx) => {
                    const lineNum = idx + 1;
                    const isActive = currentStep?.line === lineNum;
                    return (
                      <div
                        key={lineNum}
                        ref={isActive ? activeLineRef : null}
                        className={`flex items-center rounded px-2 transition-colors ${
                          isActive
                            ? 'bg-cyan-500/20 border-l-4 border-cyan-400 text-white font-semibold shadow-sm'
                            : 'hover:bg-slate-900/60 text-slate-300'
                        }`}
                      >
                        {/* Arrow Pointer & Line Number */}
                        <span className="w-10 text-right pr-3 text-slate-500 select-none font-mono text-[11px] shrink-0 flex items-center justify-end space-x-1">
                          {isActive && <span className="text-cyan-400 font-bold">▶</span>}
                          <span>{lineNum}</span>
                        </span>
                        {/* Line Code */}
                        <pre className="flex-1 overflow-x-auto py-0.5 font-mono text-xs text-slate-200">
                          {lineText || ' '}
                        </pre>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Scope & Variables Table + Stdout (~45%) */}
          <div className="md:col-span-5 flex flex-col bg-slate-900 overflow-hidden">
            {/* Top Right: Variables Table (~65% height) */}
            <div className="flex-1 border-b border-slate-800 flex flex-col overflow-hidden">
              <div className="px-4 py-2 border-b border-slate-800 bg-slate-950/50 flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold flex items-center space-x-1.5 text-slate-300">
                  <Variable className="w-3.5 h-3.5 text-emerald-400" />
                  <span>CÁC BIẾN TRONG PHẠM VI</span>
                </span>
                {currentStep && (
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[11px]">
                    Phạm vi: {currentStep.func_name || '<main>'}
                  </span>
                )}
              </div>

              <div className="flex-1 overflow-auto p-3">
                {!currentStep || !currentStep.locals || Object.keys(currentStep.locals).length === 0 ? (
                  <div className="h-full flex items-center justify-center text-slate-500 text-xs italic">
                    Chưa có biến nào được gán ở bước này.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-slate-800 text-[11px] text-slate-400 font-semibold uppercase tracking-wider">
                          <th className="pb-2 pl-2">Tên biến</th>
                          <th className="pb-2">Kiểu</th>
                          <th className="pb-2 pr-2">Giá trị</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 font-mono">
                        {Object.entries(currentStep.locals).map(([name, info]) => {
                          const isChanged = changedVars.has(name);
                          return (
                            <tr
                              key={name}
                              className={`transition-colors ${
                                isChanged
                                  ? 'bg-emerald-500/15 text-emerald-300'
                                  : 'hover:bg-slate-800/40 text-slate-200'
                              }`}
                            >
                              <td className="py-2 pl-2 font-bold flex items-center space-x-1.5">
                                <span>{name}</span>
                                {isChanged && (
                                  <span className="text-[9px] px-1 py-0.2 rounded bg-emerald-500/30 text-emerald-300 font-sans font-normal">
                                    mới đổi
                                  </span>
                                )}
                              </td>
                              <td className="py-2 text-[11px] text-slate-400">{info.type}</td>
                              <td className="py-2 pr-2 font-semibold text-cyan-300 break-all">
                                {info.value}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Bottom Right: Stdout Terminal (~35% height) */}
            <div className="h-44 flex flex-col bg-slate-950 overflow-hidden">
              <div className="px-4 py-1.5 border-b border-slate-800 bg-slate-900/60 flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold flex items-center space-x-1.5 text-slate-300">
                  <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                  <span>KẾT QUẢ IN RA (STDOUT)</span>
                </span>
                <span className="text-[10px] text-slate-500 font-mono">
                  Tính đến bước {currentStepIdx + 1}
                </span>
              </div>

              <div className="flex-1 p-3 overflow-auto font-mono text-xs text-emerald-400 bg-slate-950 select-text whitespace-pre-wrap">
                {currentStep?.stdout ? (
                  currentStep.stdout
                ) : (
                  <span className="text-slate-600 italic">Chưa có kết quả in ra màn hình.</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
