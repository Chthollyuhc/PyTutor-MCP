import React, { useState, useEffect } from 'react';
import { Sparkles, HelpCircle, Compass, Code, ChevronRight, ChevronDown, ChevronUp, Send, MessageSquare, ShieldAlert, Lock } from 'lucide-react';
import { sendTutorChatMessage } from '../services/api';

export default function TutorPanel({
  hintLevel,
  setHintLevel,
  astAnalysis,
  tutorHint,
  llmSource,
  isAskingAI = false,
  isSubmitting,
  testResults,
  onAskAI,
  onEscalate,
  exerciseId,
  code,
  sessionId,
  onOpenPythonicReview,
  starsEarned = 3,
  isExamMode = false,
  currentSession = null,
}) {
  const [isAstOpen, setIsAstOpen] = useState(true);
  const [chatMessages, setChatMessages] = useState([]);
  const [userQuestion, setUserQuestion] = useState('');
  const [isSendingChat, setIsSendingChat] = useState(false);

  // Khi học viên đổi bài tập, đặt lại lịch sử chat làm rõ
  useEffect(() => {
    setChatMessages([]);
    setUserQuestion('');
  }, [exerciseId]);

  const levels = [
    {
      level: 1,
      title: '💡 Mức 1: Gợi Mở Tư Duy',
      desc: 'Câu hỏi Socratic kích thích tư duy & nhắc lại khái niệm cốt lõi (Bảo toàn 3 ⭐)',
      badge: 'Mức 1 (3⭐)',
      color: 'hover:border-emerald-500/60'
    },
    {
      level: 2,
      title: '🔍 Mức 2: Chẩn Đoán Dòng Lỗi',
      desc: 'Khoanh vùng chính xác dòng code bị sai và giải thích Test Case bị FAIL (Bảo toàn 2 ⭐)',
      badge: 'Mức 2 (2⭐)',
      color: 'hover:border-amber-500/60'
    },
    {
      level: 3,
      title: '📘 Mức 3: Dàn Ý & Khung Code',
      desc: 'Dàn ý 4 bước chi tiết + Khung code mẫu có chỗ trống điền khuyết (Bảo toàn 1 ⭐)',
      badge: 'Mức 3 (1⭐)',
      color: 'hover:border-cyan-500/60'
    }
  ];

  const getLlmBadgeLabel = (source) => {
    if (!source) return '✨ Gia sư AI';
    const s = source.toLowerCase();
    if (s.includes('gemini')) return '✨ Gia sư AI Gemini';
    if (s.includes('qwen')) return '✨ Gia sư AI Qwen';
    return '💡 Gợi ý tự động';
  };

  // Gửi câu hỏi làm rõ tới Gia sư AI (Phase 8: Multi-turn Follow-up Chat)
  const handleSendChat = async (e) => {
    if (e) e.preventDefault();
    if (!userQuestion.trim() || isSendingChat) return;

    const currentMsg = userQuestion.trim();
    setUserQuestion('');
    const newHistory = [...chatMessages, { role: 'user', content: currentMsg }];
    setChatMessages(newHistory);
    setIsSendingChat(true);

    try {
      const res = await sendTutorChatMessage({
        exercise_id: exerciseId,
        code: code,
        session_id: sessionId,
        user_message: currentMsg,
        history: chatMessages,
        exam_session_id: currentSession?.id || null,
      });

      if (res && res.reply) {
        setChatMessages(prev => [...prev, { role: 'assistant', content: res.reply }]);
      }
    } catch (err) {
      console.error('Lỗi khi gửi câu hỏi tới Gia sư AI:', err);
      setChatMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: '⚠️ Có lỗi kết nối khi trao đổi với Gia sư AI. Bạn vui lòng thử lại sau ít giây nhé!'
        }
      ]);
    } finally {
      setIsSendingChat(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-900 text-slate-200 select-text overflow-hidden">
      {/* Panel Header */}
      <div className="h-11 bg-slate-900 border-b border-slate-800 px-3.5 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <span>🤖 Trợ lý Học tập PyTutor</span>
        </div>
        <span className="text-[10.5px] px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 font-medium">
          {getLlmBadgeLabel(llmSource)}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3.5 space-y-3.5 text-xs leading-relaxed">
        {/* Section 1: Hint Level Selector or Exam Mode Lock Notice */}
        {isExamMode ? (
          <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/50 text-amber-200 text-xs space-y-2 shadow-md">
            <div className="flex items-center space-x-2 font-bold text-amber-400">
              <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
              <span>CHẾ ĐỘ KỲ THI / KIỂM TRA NGHIÊM NGẶT</span>
            </div>
            <p className="text-[11px] leading-relaxed text-slate-300">
              🔒 Đang trong chế độ Kiểm tra / Thi: Trợ lý AI tạm khóa để đảm bảo đánh giá công bằng. Bạn hãy sử dụng nút <strong>"Chạy thử code"</strong> và <strong>"Nộp bài chấm điểm"</strong> ở cột giữa.
            </p>
            <div className="pt-2 border-t border-amber-500/30 flex items-center justify-between text-[10.5px] text-amber-300/80">
              <span>MCP Sandbox & AST vẫn chấm điểm 100%</span>
              <span className="font-mono">AI Hints: LOCKED</span>
            </div>
          </div>
        ) : (
          <div>
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
              <Compass className="w-3.5 h-3.5 text-emerald-400" />
              <span>Bạn muốn mình gợi ý đến mức nào?</span>
            </div>

            <div className="grid grid-cols-1 gap-1.5">
              {levels.map((item) => {
                const active = hintLevel === item.level;
                return (
                  <button
                    key={item.level}
                    type="button"
                    onClick={() => setHintLevel(item.level)}
                    className={`p-2.5 rounded-lg border text-left transition-all cursor-pointer ${
                      active
                        ? 'bg-emerald-500/10 border-emerald-500/60 text-white shadow-sm ring-1 ring-emerald-500/20'
                        : 'bg-slate-950/40 border-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    } ${item.color}`}
                  >
                    <div className="flex items-center justify-between mb-0.5">
                      <span className={`font-semibold text-xs ${active ? 'text-emerald-400' : 'text-slate-300'}`}>
                        {item.title}
                      </span>
                      <span
                        className={`text-[10px] px-1.5 py-0.2 rounded font-medium ${
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

            {/* Nút bấm trực quan nhận gợi ý */}
            <button
              type="button"
              onClick={() => onAskAI && onAskAI(hintLevel)}
              disabled={isAskingAI || isSubmitting}
              className="w-full mt-2.5 py-2 px-3 flex items-center justify-center space-x-1.5 text-xs font-bold text-amber-300 bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/40 rounded-lg transition-all cursor-pointer shadow-sm disabled:opacity-50"
            >
              {isAskingAI ? (
                <>
                  <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-amber-300" />
                  <span>Đang xin gợi ý Mức {hintLevel}...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                  <span>🤖 Nhận gợi ý Mức {hintLevel} từ Gia sư AI</span>
                </>
              )}
            </button>
          </div>
        )}

        {/* Section 2: Code Structure Recognition Card (Collapsible) */}
        {astAnalysis && (
          <div className="rounded-lg border border-slate-800 bg-slate-950/60 overflow-hidden">
            <button
              type="button"
              onClick={() => setIsAstOpen(!isAstOpen)}
              className="w-full p-2.5 flex items-center justify-between text-[11px] font-semibold text-slate-300 hover:bg-slate-850 transition-colors cursor-pointer"
            >
              <span className="flex items-center space-x-1.5">
                <Code className="w-3.5 h-3.5 text-cyan-400" />
                <span>📋 Nhận diện nhanh code của bạn</span>
              </span>
              <div className="flex items-center space-x-2">
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                    astAnalysis.valid ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                  }`}
                >
                  {astAnalysis.valid ? 'Hợp lệ ✅' : 'Có lỗi cú pháp ⚠️'}
                </span>
                {isAstOpen ? <ChevronUp className="w-3.5 h-3.5 text-slate-400" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-400" />}
              </div>
            </button>

            {isAstOpen && (
              <div className="p-2.5 pt-0 border-t border-slate-800/60 space-y-2 mt-1">
                <div className="grid grid-cols-2 gap-2 text-[11px]">
                  <div className="bg-slate-900/80 p-1.5 rounded">
                    <span className="text-slate-500 text-[10px] block">Độ dài:</span>
                    <span className="text-slate-200 font-semibold">{astAnalysis.line_count} dòng lệnh</span>
                  </div>
                  <div className="bg-slate-900/80 p-1.5 rounded">
                    <span className="text-slate-500 text-[10px] block">Vòng lặp:</span>
                    <span className="text-slate-200 font-semibold">
                      {astAnalysis.has_loops ? `Có dùng (${astAnalysis.loop_details?.for_loops ? 'for' : ''}${astAnalysis.loop_details?.while_loops ? 'while' : ''})` : 'Chưa dùng'}
                    </span>
                  </div>
                  <div className="bg-slate-900/80 p-1.5 rounded">
                    <span className="text-slate-500 text-[10px] block">Biến cộng dồn / tích lũy:</span>
                    <span className="text-slate-200 font-semibold">{astAnalysis.has_accumulator ? 'Có' : 'Chưa có'}</span>
                  </div>
                  <div className="bg-slate-900/80 p-1.5 rounded">
                    <span className="text-slate-500 text-[10px] block">Đệ quy:</span>
                    <span className="text-slate-200 font-semibold">{astAnalysis.has_recursion ? 'Có' : 'Không'}</span>
                  </div>
                </div>

                {astAnalysis.structural_summary && (
                  <p className="text-[10.5px] text-slate-400 italic bg-slate-900/40 p-1.5 rounded border border-slate-800/40">
                    💡 {astAnalysis.structural_summary}
                  </p>
                )}
              </div>
            )}
          </div>
        )}

        {/* Thẻ Gamification & Nút Thử thách Tối ưu Code Pythonic (Khi pass 100%) */}
        {testResults?.all_passed && (
          <div className="p-3.5 rounded-xl bg-gradient-to-r from-emerald-950/40 via-slate-900 to-amber-950/30 border border-emerald-500/40 space-y-2.5 shadow-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-xl">🎉</span>
                <div>
                  <h4 className="text-xs font-bold text-emerald-300">Đã vượt qua 100% Test Cases!</h4>
                  <p className="text-[10.5px] text-slate-400">Đánh giá tự lực: {starsEarned || 3} Sao</p>
                </div>
              </div>
              <div className="flex items-center space-x-0.5 text-base text-amber-400">
                {Array.from({ length: 3 }).map((_, i) => (
                  <span key={i} className={i < (starsEarned || 3) ? 'text-amber-400' : 'text-slate-600'}>
                    ★
                  </span>
                ))}
              </div>
            </div>

            {onOpenPythonicReview && (
              <button
                onClick={onOpenPythonicReview}
                type="button"
                className="w-full py-2 px-3 flex items-center justify-center space-x-1.5 text-xs font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-lg shadow-md shadow-emerald-950/40 transition-all cursor-pointer group"
              >
                <Sparkles className="w-3.5 h-3.5 group-hover:rotate-12 transition-transform text-amber-300" />
                <span>🚀 Thử thách Tối ưu Code Chuẩn Pythonic</span>
              </button>
            )}
          </div>
        )}

        {/* Section 3: AI Tutor Response Card */}
        <div>
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
            <span className="flex items-center space-x-1.5">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              <span>Gợi ý hướng giải từ Gia sư:</span>
            </span>
          </div>

          {isAskingAI || (isSubmitting && !testResults?.all_passed) ? (
            <div className="p-6 rounded-lg border border-slate-800 bg-slate-950/60 flex flex-col items-center justify-center text-center space-y-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-amber-400" />
              <p className="text-slate-300 text-xs font-medium">Trợ lý AI đang phân tích bài giải của bạn...</p>
              <p className="text-[11px] text-slate-500">Đang chuẩn bị gợi ý Mức {hintLevel} phù hợp nhất với bài làm hiện tại</p>
            </div>
          ) : tutorHint ? (
            <div
              className={`p-3.5 rounded-xl border text-xs leading-relaxed space-y-3 transition-all shadow-sm ${
                testResults?.all_passed
                  ? 'border-emerald-500/40 bg-emerald-950/20 text-emerald-100'
                  : 'border-slate-700/80 bg-slate-950/80 text-slate-200'
              }`}
            >
              <div className="prose prose-invert prose-xs max-w-none space-y-2">
                {formatHintText(tutorHint)}
              </div>

              {/* Nút leo thang gợi ý thân thiện */}
              {tutorHint && !testResults?.all_passed && hintLevel < 3 && (
                <button
                  type="button"
                  onClick={() => {
                    const nextLevel = hintLevel + 1;
                    setHintLevel(nextLevel);
                    if (onAskAI) onAskAI(nextLevel);
                    else if (onEscalate) onEscalate(nextLevel);
                  }}
                  disabled={isAskingAI || isSubmitting}
                  className="w-full mt-2.5 py-2 px-3 flex items-center justify-center space-x-1.5 text-xs font-semibold text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 rounded-lg transition-all cursor-pointer shadow-sm disabled:opacity-50"
                >
                  <span>Vẫn thấy khó? Xem gợi ý chi tiết hơn (Mức {hintLevel + 1})</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              )}

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10.5px] text-slate-500">
                <span>{getLlmBadgeLabel(llmSource)}</span>
                <span>Dựa trên kết quả chạy thực tế & phân tích code</span>
              </div>
            </div>
          ) : (
            <div className="p-6 rounded-xl border border-dashed border-slate-800 text-center text-slate-500 space-y-2">
              <HelpCircle className="w-7 h-7 mx-auto opacity-30 text-emerald-400" />
              <p className="text-xs font-medium text-slate-400">Chưa có gợi ý từ Gia sư AI.</p>
              <p className="text-[11px] text-slate-500 leading-normal">
                Hãy viết code và bấm <span className="text-cyan-400 font-medium">"Chạy thử code"</span> hoặc <span className="text-emerald-400 font-medium">"Hỏi Gia sư AI"</span> để nhận hướng dẫn.
              </p>
            </div>
          )}
        </div>

        {/* Section 4: Multi-turn Chat với Gia sư AI (Phase 8) */}
        {tutorHint && (
          <div className="pt-3 border-t border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400">
              <span className="flex items-center space-x-1.5 text-cyan-300">
                <MessageSquare className="w-3.5 h-3.5 text-cyan-400" />
                <span>Trò chuyện làm rõ với Gia sư:</span>
              </span>
              {chatMessages.length > 0 && (
                <span className="text-[10px] text-slate-500 font-mono">
                  {chatMessages.length} tin nhắn
                </span>
              )}
            </div>

            {/* Chat History Bubbles */}
            <div className="space-y-2 max-h-56 overflow-y-auto pr-1 text-xs">
              {chatMessages.length === 0 ? (
                <p className="text-[11px] text-slate-500 italic p-2.5 bg-slate-950/40 rounded-lg border border-slate-800/60 leading-normal">
                  💬 Có điều gì chưa rõ trong bài làm hay gợi ý trên? Bạn hãy gõ câu hỏi phía dưới để Gia sư giải thích chi tiết hơn nhé.
                </p>
              ) : (
                chatMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex flex-col ${
                      msg.role === 'user' ? 'items-end' : 'items-start'
                    }`}
                  >
                    <span className="text-[9.5px] text-slate-500 px-1 mb-0.5">
                      {msg.role === 'user' ? 'Bạn' : '🤖 Gia sư PyTutor'}
                    </span>
                    <div
                      className={`p-2.5 rounded-xl max-w-[92%] leading-relaxed ${
                        msg.role === 'user'
                          ? 'bg-slate-800 text-cyan-200 border border-slate-700/80 rounded-br-sm'
                          : 'bg-slate-950 text-slate-200 border border-emerald-500/30 rounded-bl-sm'
                      }`}
                    >
                      {renderBold(msg.content)}
                    </div>
                  </div>
                ))
              )}

              {isSendingChat && (
                <div className="flex items-center space-x-1.5 text-slate-400 text-[11px] p-2 bg-slate-950/60 rounded-lg animate-pulse">
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce" />
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce delay-100" />
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce delay-200" />
                  <span className="ml-1 text-emerald-400 font-medium">Gia sư đang soạn câu trả lời...</span>
                </div>
              )}
            </div>

            {/* Chat Input Form */}
            <form onSubmit={handleSendChat} className="flex items-center space-x-1.5 mt-1">
              <input
                type="text"
                value={userQuestion}
                onChange={(e) => setUserQuestion(e.target.value)}
                placeholder={isExamMode ? "🔒 Gia sư AI bị khóa trong Chế độ Kỳ thi..." : "Hỏi Gia sư về bài làm (ví dụ: giải thích vòng lặp)..."}
                disabled={isSendingChat || isExamMode}
                className={`flex-1 bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-lg px-2.5 py-1.5 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-cyan-500/40 ${
                  isExamMode ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              />
              <button
                type="submit"
                disabled={isSendingChat || !userQuestion.trim() || isExamMode}
                className="p-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-white rounded-lg transition-colors cursor-pointer shadow-sm shadow-cyan-900/30"
                title={isExamMode ? "Gia sư AI bị khóa trong Chế độ Kỳ thi" : "Gửi câu hỏi tới Gia sư AI"}
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

function formatHintText(text) {
  if (!text) return null;

  const parts = text.split(/(```[\s\S]*?```)/g);

  return parts.map((part, pIdx) => {
    if (part.startsWith('```') && part.endsWith('```')) {
      const lines = part.slice(3, -3).trim().split('\n');
      const lang = lines[0].trim().startsWith('python') ? 'python' : '';
      const codeBody = lang ? lines.slice(1).join('\n') : lines.join('\n');

      return (
        <pre key={pIdx} className="my-2 p-2.5 rounded-lg bg-slate-900 border border-slate-800 font-mono text-[11px] text-emerald-300 overflow-x-auto">
          <code>{codeBody}</code>
        </pre>
      );
    }

    const paragraphs = part.split('\n\n');
    return paragraphs.map((para, paraIdx) => {
      const lines = para.split('\n');
      return (
        <div key={`${pIdx}-${paraIdx}`} className="space-y-1">
          {lines.map((line, lIdx) => {
            const content = line.trim();
            if (!content) return null;

            if (content.startsWith('# ')) {
              return (
                <h3 key={lIdx} className="font-bold text-emerald-400 text-sm mt-2 mb-1">
                  {content.replace('# ', '')}
                </h3>
              );
            }
            if (content.startsWith('## ')) {
              return (
                <h4 key={lIdx} className="font-bold text-emerald-400 text-xs mt-2 mb-1">
                  {content.replace('## ', '')}
                </h4>
              );
            }
            if (content.startsWith('### ')) {
              return (
                <h5 key={lIdx} className="font-bold text-emerald-400 text-xs mt-1.5 mb-0.5">
                  {content.replace('### ', '')}
                </h5>
              );
            }
            if (content.startsWith('- ') || content.startsWith('* ')) {
              return (
                <div key={lIdx} className="ml-3 flex items-start space-x-1.5 text-slate-300">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>{renderBold(content.replace(/^[-*]\s+/, ''))}</span>
                </div>
              );
            }
            const numMatch = content.match(/^(\d+)\.\s+(.*)/);
            if (numMatch) {
              return (
                <div key={lIdx} className="ml-3 flex items-start space-x-1.5 text-slate-300">
                  <span className="text-cyan-400 font-mono font-bold">{numMatch[1]}.</span>
                  <span>{renderBold(numMatch[2])}</span>
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
  });
}

function renderBold(str) {
  if (!str) return null;
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
