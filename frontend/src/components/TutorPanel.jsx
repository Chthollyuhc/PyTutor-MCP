import React from 'react';
import { Sparkles, HelpCircle, AlertCircle, Compass, ShieldAlert, Cpu, CheckCircle, Code, Layers } from 'lucide-react';

export default function TutorPanel({
  hintLevel,
  setHintLevel,
  astAnalysis,
  tutorHint,
  llmSource,
  isSubmitting,
  testResults
}) {
  const levels = [
    {
      level: 1,
      title: 'Level 1: Gợi Mở Socratic',
      desc: 'Câu hỏi định hướng tư duy & gợi nhớ khái niệm, không tiết lộ vị trí lỗi.',
      badge: 'Gợi mở',
      color: 'hover:border-emerald-500/60'
    },
    {
      level: 2,
      title: 'Level 2: Chẩn Đoán Lỗi',
      desc: 'Khoanh vùng khối lệnh lỗi và giải thích sai lệch Actual vs Expected.',
      badge: 'Chẩn đoán',
      color: 'hover:border-amber-500/60'
    },
    {
      level: 3,
      title: 'Level 3: Hướng Dẫn & Mã Giả',
      desc: 'Chia nhỏ thuật toán từng bước & cung cấp pseudocode (không đưa code giải).',
      badge: 'Mã giả',
      color: 'hover:border-cyan-500/60'
    }
  ];

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-200 select-text overflow-hidden">
      {/* Panel Header */}
      <div className="h-11 bg-slate-900 border-b border-slate-800 px-3.5 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <span>AI TUTOR (SCAFFOLDING PEDAGOGY)</span>
        </div>
        {llmSource && (
          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400 font-mono">
            {llmSource.includes('qwen') ? 'Qwen2.5-14B' : 'Rule-Engine'}
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-3.5 space-y-3.5 text-xs leading-relaxed">
        {/* Section 1: Hint Level Selector */}
        <div>
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1">
            <Compass className="w-3.5 h-3.5 text-emerald-400" />
            <span>CHỌN MỨC ĐỘ GỢI Ý (HINT LEVEL):</span>
          </div>

          <div className="grid grid-cols-1 gap-1.5">
            {levels.map((item) => {
              const active = hintLevel === item.level;
              return (
                <button
                  key={item.level}
                  type="button"
                  onClick={() => setHintLevel(item.level)}
                  className={`p-2 rounded-lg border text-left transition-all cursor-pointer ${
                    active
                      ? 'bg-emerald-500/10 border-emerald-500/60 text-white shadow-sm'
                      : 'bg-slate-950/40 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  } ${item.color}`}
                >
                  <div className="flex items-center justify-between mb-0.5">
                    <span className={`font-semibold text-xs ${active ? 'text-emerald-400' : 'text-slate-300'}`}>
                      {item.title}
                    </span>
                    <span
                      className={`text-[10px] px-1.5 py-0.2 rounded ${
                        active ? 'bg-emerald-500/20 text-emerald-300 font-bold' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {item.badge}
                    </span>
                  </div>
                  <p className="text-[10.5px] leading-snug opacity-80">{item.desc}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Section 2: MCP AST Inspector Card */}
        {astAnalysis && (
          <div className="p-2.5 rounded-lg border border-slate-800 bg-slate-950/60 space-y-2">
            <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 border-b border-slate-800/80 pb-1.5">
              <span className="flex items-center space-x-1.5 text-slate-300">
                <Code className="w-3.5 h-3.5 text-cyan-400" />
                <span>PHÂN TÍCH CÚ PHÁP TĨNH (MCP AST)</span>
              </span>
              <span
                className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                  astAnalysis.valid ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                }`}
              >
                {astAnalysis.valid ? 'Cú pháp hợp lệ' : 'Lỗi cú pháp'}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
              <div className="bg-slate-900/80 p-1.5 rounded">
                <span className="text-slate-500 font-sans text-[10px]">Dòng code: </span>
                <span className="text-slate-200 font-bold">{astAnalysis.line_count} dòng</span>
              </div>
              <div className="bg-slate-900/80 p-1.5 rounded">
                <span className="text-slate-500 font-sans text-[10px]">Vòng lặp: </span>
                <span className="text-slate-200 font-bold">
                  {astAnalysis.has_loops ? `${astAnalysis.loop_details?.total || 1} vòng` : 'Không có'}
                </span>
              </div>
              <div className="bg-slate-900/80 p-1.5 rounded">
                <span className="text-slate-500 font-sans text-[10px]">Tích lũy (+=): </span>
                <span className="text-slate-200 font-bold">{astAnalysis.has_accumulator ? 'Phát hiện' : 'Không có'}</span>
              </div>
              <div className="bg-slate-900/80 p-1.5 rounded">
                <span className="text-slate-500 font-sans text-[10px]">Đệ quy: </span>
                <span className="text-slate-200 font-bold">{astAnalysis.has_recursion ? 'Có' : 'Không'}</span>
              </div>
            </div>

            <p className="text-[10.5px] text-slate-400 italic bg-slate-900/40 p-1.5 rounded border border-slate-800/40">
              💡 {astAnalysis.structural_summary}
            </p>
          </div>
        )}

        {/* Section 3: AI Tutor Response Card */}
        <div>
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
            <span className="flex items-center space-x-1">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              <span>PHẢN HỒI GIA SƯ SƯ PHẠM:</span>
            </span>
          </div>

          {isSubmitting ? (
            <div className="p-6 rounded-lg border border-slate-800 bg-slate-950/60 flex flex-col items-center justify-center text-center space-y-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-400" />
              <p className="text-slate-400 text-xs">AI Tutor đang đối chiếu kết quả MCP Sandbox & sinh gợi ý...</p>
            </div>
          ) : tutorHint ? (
            <div
              className={`p-3.5 rounded-xl border text-xs leading-relaxed space-y-2.5 transition-all shadow-sm ${
                testResults?.all_passed
                  ? 'border-emerald-500/40 bg-emerald-950/20 text-emerald-100'
                  : 'border-slate-700/80 bg-slate-950/80 text-slate-200'
              }`}
            >
              <div className="prose prose-invert prose-xs max-w-none space-y-2">
                {formatHintText(tutorHint)}
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10.5px] text-slate-500">
                <span>Nguồn: {llmSource || 'Qwen2.5-14B'}</span>
                <span>Ground Truth via MCP</span>
              </div>
            </div>
          ) : (
            <div className="p-6 rounded-xl border border-dashed border-slate-800 text-center text-slate-500 space-y-2">
              <HelpCircle className="w-7 h-7 mx-auto opacity-30 text-emerald-400" />
              <p className="text-xs">Chưa có gợi ý từ AI.</p>
              <p className="text-[11px] text-slate-600">
                Hãy chọn bài tập, viết code và bấm "Chạy & Nhận Gợi Ý AI" để bắt đầu quá trình gia sư thông minh.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function formatHintText(text) {
  if (!text) return null;

  const paragraphs = text.split('\n\n');
  return paragraphs.map((para, pIdx) => {
    const lines = para.split('\n');
    return (
      <div key={pIdx} className="space-y-1">
        {lines.map((line, lIdx) => {
          let content = line.trim();
          if (content.startsWith('### ')) {
            return (
              <h4 key={lIdx} className="font-bold text-emerald-400 text-xs mt-2 mb-1">
                {content.replace('### ', '')}
              </h4>
            );
          }
          if (content.startsWith('- ')) {
            return (
              <div key={lIdx} className="ml-3 flex items-start space-x-1.5 text-slate-300">
                <span className="text-emerald-400 font-bold">•</span>
                <span>{renderBold(content.replace('- ', ''))}</span>
              </div>
            );
          }
          return (
            <p key={lIdx} className="leading-relaxed">
              {renderBold(content)}
            </p>
          );
        })}
      </div>
    );
  });
}

function renderBold(str) {
  const parts = str.split(/(\*\*.*?\*\*|\`.*?\`)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="text-white font-bold">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={i} className="bg-slate-800 px-1 py-0.5 rounded text-emerald-400 font-mono text-[11px]">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}
